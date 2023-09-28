import common_imports as ci
import drive_checker
import requests

MAPPED_DRIVE = "S"

class SearchManager:
    def __init__(self, tree):
        self.stop_search = False
        self.thread_pool = ci.ThreadPoolExecutor(max_workers=ci.os.cpu_count())
        self.tree = tree
        self.single_occurrences = {}

    ##normalize config file data :D
    def search_folder_normalizer(self):
        with open('config.json', 'r') as config_file:
            config = ci.json.load(config_file)
        search_folder_data = config['search_folders']
        normalized_search_folders = [ci.os.path.normpath(folder) for folder in search_folder_data]
        return normalized_search_folders
    def start_search(self, order_number_entry, event=None):
        ci.threading.Thread(target=self.search_files, args=(order_number_entry,)).start()

        
    def search_files(self, order_number_entry, event=None):
        # Clear the previous search results
        self.clear_search_results()

        if not drive_checker.is_drive_connected(MAPPED_DRIVE):
            ci.tk.messagebox.showerror("Error", "Network drive S: is not connected.")
            return

        fixed_input = self.process_input(order_number_entry)
        if fixed_input is None:
            return
        normalized_search_folders = self.search_folder_normalizer()
        print(normalized_search_folders)
        total_start_time = ci.time.time()  # Record the start time of the entire search
        all_unmatched_order_numbers = self.perform_search(fixed_input, normalized_search_folders)

        total_end_time = ci.time.time()  # Record the end time of the entire search
        total_search_duration = total_end_time - total_start_time
        print(f"Finished searching. Search took {total_search_duration:.4f} seconds.")

        # Print the unmatched order numbers after the entire search
        if all_unmatched_order_numbers:
            print(f"No results for {', '.join(all_unmatched_order_numbers)}")

    ##goes through every folder that needs to be searched and calls search_files_in_folder
    def perform_search(self, fixed_input, normalized_search_folders):
        folder_list = normalized_search_folders
        # Search through the folders using the global thread pool
        results = list(self.thread_pool.map(lambda folder: self.search_files_in_folder(folder, fixed_input), folder_list))

        # Combine the unmatched order numbers from all folders
        all_unmatched_order_numbers = set(fixed_input)
        for found_order_numbers, unmatched_order_numbers in results:
            all_unmatched_order_numbers -= found_order_numbers

        return all_unmatched_order_numbers
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
                    try: order_number, file_path, last_modified_date, containing_folder, task_state, file_size, hipster_present, walls_present = self.process_file(match, root, file)
                    except: 
                        if order_number: 
                            found_order_numbers.discard(order_number)
                            unmatched_order_numbers.add(order_number)
                        continue
                    if order_number is not None:
                        order_type = self.extract_order_type(order_type_pattern, file)
                        self.insert_tree_item(order_number, containing_folder, order_type, last_modified_date, file_path, task_state, file_size, hipster_present, walls_present)
                        found_order_numbers.add(order_number)
                        unmatched_order_numbers.discard(order_number)  # Remove
                if len(found_order_numbers) == len(fixed_input):
                    break
            else:
                continue

        end_time = ci.time.time()
        search_duration = end_time - start_time
        #print(f"Finished searching {folder}. Search took {search_duration:.4f} seconds.")

        return found_order_numbers, unmatched_order_numbers

    def get_taskstate(self, order_number):
        url = f"https://api.cmh.platform-prod2.evinternal.net/operations-center/api/TaskTrafficView/reports?reportIDs={order_number}"
        headers = {
            "User-Agent": "FileMoverScript/1.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()  # Assuming that the response is JSON format
            if isinstance(data, list) and len(data) > 0:  # if response is a list and not empty
                taskState = data[0].get('taskState') if 'taskState' in data[0] else None  # Extract the task state field if it exists
            else:  # if response is not a list or is empty
                taskState = None
            print(f"Current taskState for {order_number}: {taskState}")
        
            return taskState
        else:
            print(f'Request failed for report ID: {order_number}, status code: {response.status_code}')
            print('Response text:', response.text)
            return None
        
    def get_measurement_data(self, order_number):
        url = f"https://api.cmh.platform-prod2.evinternal.net/operations-center/api/TaskTrafficView/reports?reportIDs={order_number}"
        headers = {
            "User-Agent": "FileMoverScript/1.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()  # Assuming that the response is JSON format
            if isinstance(data, list) and len(data) > 0:  # if response is a list and not empty
                measurement_items = data[0].get('measurementItems') if 'measurementItems' in data[0] else None  # Extract the task state field if it exists
            else:  # if response is not a list or is empty
                measurement_items = None
            print(f"Current measurement items for {order_number}: {measurement_items}")
        
            return measurement_items
        else:
            print(f'Request failed for report ID: {order_number}, status code: {response.status_code}')
            print('Response text:', response.text)
            return None
        
    def check_walls (self, order_number):
        measurement_items = self.get_measurement_data(order_number)
        item_list = [int(item.strip()) for item in measurement_items.split(',') if item.strip().isdigit()]
        walls = any(item in [2, 14, 37] for item in item_list)
        return walls
    
    def check_hipster (self, order_number):
        measurement_items = self.get_measurement_data(order_number)
        item_list = [int(item.strip()) for item in measurement_items.split(',') if item.strip().isdigit()]
        hipster = 36 in item_list
        return hipster
## takes found matches, extracts order number, file path, last modified timestamp
    def process_file(self, match, root, file):
        try:
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
            #get the task state from the oc
            task_state = self.get_taskstate(order_number)
            #get the file size 
            file_size = self.get_readable_file_size(file_path)
            #is hipster
            hipster_present = self.check_hipster(order_number)
            #is walls 
            walls_present = self.check_walls(order_number)
            # Get the grandparent folder name
            grandparent_folder_name = ci.os.path.basename(grandparent_folder_path)
            containing_folder = f"{grandparent_folder_name}/{parent_folder_name}" if grandparent_folder_name else parent_folder_name
            return order_number, file_path, last_modified_date, containing_folder, task_state, file_size, hipster_present, walls_present

        except FileNotFoundError:
            print(f"The file {file} was moved or deleted before it could be processed.")
            return None, None, None, None

## extracts the order product from the EVM name
    def extract_order_type(self, order_type_pattern, file):
        order_type_match = order_type_pattern.search(file)
        order_type = order_type_match.group(1) if order_type_match else "Unknown"
        return order_type


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
    def get_readable_file_size(self, file_path):
        size_in_bytes = ci.os.path.getsize(file_path)
        
        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024.0
        
        return size_in_bytes

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
    
    ## adds relevant search items into the treeview
    def insert_tree_item(self, order_number, containing_folder, order_type, last_modified_date, file_path, task_state, file_size, hipster_present, walls_present):
        file = ci.os.path.basename(file_path)
        #print(f"Found {order_number} in {file_path}")

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
                parent_item = self.tree.insert("", "end", text=order_number, values=("+ " + order_number , "", "", "", "", "", ))
                self.tree.insert(parent_item, "end", values=values)
                # Insert the second occurrence as a child item under the parent_item
                self.tree.insert(parent_item, "end", values=("⎣", containing_folder, order_type, task_state, file_size, hipster_present, walls_present, last_modified_date, file_path, file))
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
                self.tree.insert(parent_item, "end", values=("∟", containing_folder, order_type, task_state, file_size, hipster_present, walls_present, last_modified_date, file_path, file))
        else:
            # If the order_number is not in the single_occurrences dictionary, this is the first occurrence
            item = self.tree.insert("", "end", values=("    " + order_number,  containing_folder, order_type, task_state, file_size, hipster_present, walls_present, last_modified_date, file_path, file ))
            self.single_occurrences[order_number] = {'item': item}


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