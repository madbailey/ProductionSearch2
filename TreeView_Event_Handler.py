import common_imports as ci
import csv
from datetime import datetime
##this class handles click interactions with the tkinter treeview, sorting, double click to open files, and right click to copy/paste
##the treeview itself is handled within the prod_search_gui.py module
class Treeview_Handler:
    def __init__(self, tree, root, context_menu):
        self.tree = tree
        self.root = root
        self.context_menu = context_menu
    def is_parent(self, item):
        if self.tree.exists(item):
            return len(self.tree.get_children(item)) > 0
        return False

## sorts columns when you click on the column label, reverse sorts when you click again
    def treeview_sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        # Reverse sort next time
        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))

# double clicking on a row will open the coresponding file location
    def open_file_location(self, event):
        selected_item = self.tree.selection()
        if selected_item and not self.is_parent(selected_item[0]):
            file_path = self.tree.item(selected_item[0])["values"][4]

            if ci.os.path.exists(file_path):
                ci.os.system(f'explorer /select,"{file_path}"')
            else:
                ci.tk.messagebox.showerror("Error", "File not found.")

## right clicking will open up a context menu that gives the options to copy text 
    def treeview_right_click(self, event):
        item = self.tree.identify("item", event.x, event.y)

        if item not in self.tree.selection():
            # Add the right-clicked item to the selection
            self.tree.selection_set(self.tree.selection() + (item,))

        self.context_menu.post(event.x_root, event.y_root)

## handles text copy pasting 
    def copy_text(self, event=None, column_index=None):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        if event:
            column_index = 0

        column_texts = []

        for selected_item in selected_items:
            if column_index == 0:
                if self.is_parent(selected_item):
                    column_text = self.tree.item(selected_item)["values"][column_index]
                else:
                    # Get the parent of the selected item
                    parent_item = self.tree.parent(selected_item)
                    if parent_item:
                        # Get the order number value of the parent item
                        values = self.tree.item(parent_item)["values"]
                        print(f"Values: {values}, Column index: {column_index}")  # debugging - remove this later
                        column_text = self.tree.item(parent_item)["values"][column_index]

                        # Remove the "+ " prefix from the order number
                        column_text = column_text[2:]
                    else:
                        # If there's no parent item, use the selected item's values
                        column_text = self.tree.item(selected_item)["values"][column_index]

                        # Convert column_text to string and trim
                        column_text = str(column_text).lstrip()
            else:
                column_text = self.tree.item(selected_item)["values"][column_index]

            column_texts.append(str(column_text))

        comma_delimited_text = ','.join(column_texts)

        self.root.clipboard_clear()
        self.root.clipboard_append(comma_delimited_text)

    def export_to_csv(self, filename):
        # Get the current date and time
        now = datetime.now()
        timestamp = now.strftime("%m_%d_%Y_%H-%M")

        # Set the filename with the date and time
        filename = f"Search Results {timestamp}.csv"

        # Create the 'dataexports' directory if it doesn't exist
        output_directory = 'dataexports'
        if not ci.os.path.exists(output_directory):
            ci.os.makedirs(output_directory)

        # Join the output directory and the filename
        output_path = ci.os.path.join(output_directory, filename)

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.tree["columns"])  # Write the column headers
            for row in self.tree.get_children():
                row_data = [self.tree.set(row, col) for col in self.tree["columns"]]
                writer.writerow(row_data)

                # Write child rows
                for child in self.tree.get_children(row):
                    child_data = [self.tree.set(child, col) for col in self.tree["columns"]]
                    writer.writerow(child_data)
        print(f"Finished Exporting {filename} to {output_directory}")