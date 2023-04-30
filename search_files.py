import common_imports as ci
import drive_checker


##this class has three main functions search_files_in_folder, which runs the loop of checking all order numbers in each folder in the search_folders directory
## there is also search_files which handles cleaning and checking user input data to ensure it's usable
class SearchManager:
    def __init__(self, tree):
        self.stop_search = False
        self.thread_pool = ci.ThreadPoolExecutor(max_workers=ci.os.cpu_count())
        self.tree = tree
        self.single_occurrences = {}

## walks through individual folders, records found matches for search terms
    def search_files_in_folder(self, folder, fixed_input):
        self.stop_search
        order_type_pattern = ci.re.compile(r'^[^_]*_[^_]*_(.+?)_\[')  #regular expression to extract the product from EVM name 
        found_order_numbers = set() # creates an empty set of found order numbers 
        unmatched_order_numbers = set(fixed_input)  # Takes the fixed user input and creates a set of order numbers that haven't been found yet

        print(f"Searching in {folder}...")
        start_time = ci.time.time()

        # Create a regular expression pattern for the order numbers
        order_number_pattern = ci.re.compile(r'(' + '|'.join(fixed_input) + r')')

        for root, dirs, files in ci.os.walk(folder):
            if self.stop_search:
                break
            for file in files:
                match = order_number_pattern.search(file)
                if match and file.endswith(".evm"):
                    order_number, file_path, last_modified_date, containing_folder = self.process_file(match, root, file)
                    order_type = self.extract_order_type(order_type_pattern, file)
                    self.insert_tree_item(order_number, containing_folder, order_type, last_modified_date, file_path)
                    found_order_numbers.add(order_number)
                    unmatched_order_numbers.discard(order_number)  # Remove the found order number from unmatched set
                if len(found_order_numbers) == len(fixed_input):
                    break
            else:
                continue

        end_time = ci.time.time()
        search_duration = end_time - start_time
        print(f"Finished searching {folder}. Search took {search_duration:.4f} seconds.")

        return found_order_numbers, unmatched_order_numbers

## takes found matches, extracts order number, file path, last modified timestamp
    def process_file(self, match, root, file):
        order_number = match.group()
        file_path = ci.os.path.join(root, file)
        last_modified_timestamp = ci.os.path.getmtime(file_path)
        last_modified_date = ci.time.strftime(' %m/%d/%y %I:%M:%S %p', ci.time.localtime(last_modified_timestamp))
        # Get the parent folder path
        parent_folder_path = ci.os.path.dirname(file_path)
        # Get the parent folder name
        parent_folder_name = ci.os.path.basename(parent_folder_path)
        # Get the grandparent folder path
        grandparent_folder_path = ci.os.path.dirname(parent_folder_path)
        # Get the grandparent folder name
        grandparent_folder_name = ci.os.path.basename(grandparent_folder_path)
        containing_folder = f"{grandparent_folder_name}/{parent_folder_name}" if grandparent_folder_name else parent_folder_name
        return order_number, file_path, last_modified_date, containing_folder

## extracts the order product from the EVM name
    def extract_order_type(self, order_type_pattern, file):
        order_type_match = order_type_pattern.search(file)
        order_type = order_type_match.group(1) if order_type_match else "Unknown"
        return order_type

## adds relevant search items into the treeview
    def insert_tree_item(self, order_number, containing_folder, order_type, last_modified_date, file_path):
        file = ci.os.path.basename(file_path)
        print(f"Found {order_number} in {file_path}")

        # If the order_number is in the single_occurrences dictionary, this is a duplicate
        if order_number in self.single_occurrences:
            # If the single_occurrence value is not None, this is the second occurrence of the order_number
            if self.single_occurrences[order_number] is not None:
                # Store the single_occurrence item values before deleting it from the tree
                values = self.tree.item(self.single_occurrences[order_number]['item'])['values']
                # Set the order number in the values list to an empty string
                values[0] = "⎢"
                # Remove the single occurrence item from the tree
                self.tree.delete(self.single_occurrences[order_number]['item'])
                parent_item = self.tree.insert("", "end", text=order_number, values=("+ " + order_number , "", "", "", ""))
                self.tree.insert(parent_item, "end", values=values)
                # Insert the second occurrence as a child item under the parent_item
                self.tree.insert(parent_item, "end", values=("⎣", containing_folder, order_type, last_modified_date, file_path, file))
                # Set the single_occurrence value for the order_number to None
                self.single_occurrences[order_number] = None
            else:
                # Get the parent_item corresponding to the order_number
                parent_item = None
                for item in self.tree.get_children():
                    if self.tree.item(item, "text") == order_number:
                        parent_item = item
                        break
                # Insert the file details as a child item under the parent_item
                self.tree.insert(parent_item, "end", values=("∟", containing_folder, order_type, last_modified_date, file_path, file))
        else:
            # If the order_number is not in the single_occurrences dictionary, this is the first occurrence
            item = self.tree.insert("", "end", values=("    " + order_number, containing_folder, order_type, last_modified_date, file_path, file))
            self.single_occurrences[order_number] = {'item': item}
            

## starting point for search process, checks if we are connected to the shared drive, sends user input to be fixed, records start time and search duration
    def search_files(self, order_number_entry, search_folders):
        # Clear the previous search results
        self.clear_search_results()

        if not drive_checker.is_drive_connected("S"):
            ci.tk.messagebox.showerror("Error", "Network drive S: is not connected.")
            return

        fixed_input = self.process_input(order_number_entry)
        if fixed_input is None:
            return

        total_start_time = ci.time.time()  # Record the start time of the entire search
        all_unmatched_order_numbers = self.perform_search(fixed_input, search_folders)

        total_end_time = ci.time.time()  # Record the end time of the entire search
        total_search_duration = total_end_time - total_start_time
        print(f"Finished searching. Search took {total_search_duration:.4f} seconds.")

        # Print the unmatched order numbers after the entire search
        if all_unmatched_order_numbers:
            print(f"No results for {', '.join(all_unmatched_order_numbers)}")

## clears treeview results on refresh
    def clear_search_results(self):
        for item in self.tree.get_children():
            if self.stop_search:
                break
            self.tree.delete(item)
        self.single_occurrences.clear()

## processes user input, throws exceptions for invalid entries
    def process_input(self, order_number_entry):
        order_numbers_input = order_number_entry.get()

        # Split the input by commas and then split by spaces
        split_by_commas = order_numbers_input.split(',')
        split_by_spaces = [num.strip().split() for num in split_by_commas]

        # Flatten the list of lists
        fixed_input = [num for sublist in split_by_spaces for num in sublist]

        # Check if the input is empty
        if not fixed_input:
            ci.tk.messagebox.showerror("Invalid input", "Please enter at least one number.")
            return None

        # Check if all the elements in the fixed_input list are valid numbers
        if not all(ci.re.match(r'^\d+$', num) for num in fixed_input):
            ci.tk.messagebox.showerror("Invalid input", "Please enter only numbers separated by commas and/or spaces.")
            return None

        return fixed_input

##goes through every folder that needs to be searched and calls search_files_in_folder
    def perform_search(self, fixed_input, search_folders):
        folder_list = search_folders
        # Search through the folders using the global thread pool
        results = list(self.thread_pool.map(lambda folder: self.search_files_in_folder(folder, fixed_input), folder_list))

        # Combine the unmatched order numbers from all folders
        all_unmatched_order_numbers = set(fixed_input)
        for found_order_numbers, unmatched_order_numbers in results:
            all_unmatched_order_numbers -= found_order_numbers

        return all_unmatched_order_numbers

## handles refresh functionality 
    def refresh(self, order_number_entry):
        self.stop_search

        # Set the stop_search flag to True
        self.stop_search = True

        # Wait a short period for the search functions to stop
        ci.time.sleep(0.1)

        # Clear the search bar
        order_number_entry.delete(0, ci.tk.END)

        # Clear search results
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Reset the stop_search flag to False
        self.stop_search = False


    ## collect log info 
    class TextRedirector:
        def __init__(self, widget):
            self.widget = widget

        def write(self, text):
            self.widget.configure(state="normal")
            self.widget.insert("end", text)
            self.widget.see("end")
            self.widget.configure(state="disabled")

        def flush(self):
            pass