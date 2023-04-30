import common_imports as ci

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
        selected_item = self.tree.selection()
        item_id = self.tree.identify("item", event.x, event.y)
        if not item_id:
            return

        self.tree.selection_set(item_id)
        if selected_item and not self.is_parent(selected_item[0]):
            self.context_menu.post(event.x_root, event.y_root)
        else:
            self.context_menu.unpost()

## handles text copy pasting 
    def copy_text(self, column_index, is_order_number=False):
        selected_item = self.tree.selection()[0]
        if not selected_item:
            return
    
        if is_order_number:
            if self.is_parent(selected_item):
                column_text = self.tree.item(selected_item)["values"][column_index]
            else:
                # Get the parent of the selected item
                parent_item = self.tree.parent(selected_item)
                # Get the order number value of the parent item
                column_text = self.tree.item(parent_item)["values"][column_index]
                # Remove the "+ " prefix from the order number
                column_text = column_text[2:]
        else:
            column_text = self.tree.item(selected_item)["values"][column_index]
    
        self.root.clipboard_clear()
        self.root.clipboard_append(column_text)