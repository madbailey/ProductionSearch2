import common_imports as ci

class FileMover:
    def __init__(self, tree):
        self.tree = tree
        self.undo_history = []
        self.undo_triggered = False

##assigns a unique thread to each file move operation
    def move_file_threaded(self, destination_folder):
        move_thread = ci.threading.Thread(target=self.move_file, args=(destination_folder,))
        move_thread.start()

## assigns a unique thread to each undo operation
    def undo_last_move_threaded(self):
        undo_thread = ci.threading.Thread(target=self.undo_last_move)
        undo_thread.start()

## moves files 
    def move_single_file(self, file_path, destination_folder):
        try:
            destination_path = ci.join(destination_folder, ci.basename(file_path))

            # Check if the destination file already exists
            if ci.exists(destination_path):
                # Prompt the user to decide whether to overwrite or skip
                user_choice = ci.tk.messagebox.askyesnocancel("File exists", f"A file with the same name already exists at {destination_path}. Do you want to overwrite it? This can not be undone")
                if user_choice is None:  # Cancel
                    return
                elif user_choice:  # Overwrite
                    ci.shutil.move(file_path, destination_path)
                    print(f"Moved {file_path} to {destination_folder}")
                    return (file_path, destination_path)
                else:  # Skip
                    print(f"Skipped moving {file_path} to {destination_folder}")
                    return
            else:
                ci.shutil.move(file_path, destination_path)
                print(f"Moved {file_path} to {destination_folder}")
                return (file_path, destination_path)

        except ci.shutil.Error as e:
            print(f"Error moving file: {e}")
            ci.tk.messagebox.showerror("Error", f"Error moving file: {e}")
        except PermissionError as e:
            print(f"Permission denied: {e}")
            ci.tk.messagebox.showerror("Permission Error", f"Permission denied while moving file: {e}")
        except OSError as e:
            print(f"OS error occurred: {e}")
            ci.tk.messagebox.showerror("OS Error", f"An OS error occurred while moving file: {e}")

## processes move operations and checks for exceptions before trigering the move_single_file function
    def move_file(self, destination_folder):
        self.undo_triggered
        selected_items = self.tree.selection()
        current_move = []  # Store the paths of the current move operation

        for selected_item in selected_items:
            if self.undo_triggered:
                self.undo_triggered = False
                break

            file_path = self.tree.item(selected_item)["values"][4]

            if ci.os.path.exists(file_path):
                result = self.move_single_file(file_path, destination_folder)  # Call the move_single_file function
                if result:
                    current_move.append(result)  # Save the source and destination paths
                    self.tree.delete(selected_item)  # Remove the file from the tree view
            else:
                ci.tk.messagebox.showerror("Error", "File not found.")

        if current_move:
            self.undo_history.append(current_move)  # Add the current move operation to the undo history

## handles the operations of the undo button 
    def undo_last_move(self):
        if not self.undo_history:
            ci.tk.messagebox.showinfo("Info", "Nothing to undo.")
            return

        last_move = self.undo_history.pop()

        for source_path, destination_path in last_move:
            if ci.os.path.exists(destination_path):
                try:
                    ci.shutil.move(destination_path, source_path)
                    print(f"Moved {destination_path} back to {source_path}")
                    self.tree.insert("", "end", values=(source_path, ci.os.path.basename(source_path)))  # Add the file back to the tree view
                except Exception as e:
                    print(f"Error undoing move: {e}")
                    ci.tk.messagebox.showerror("Error", f"Error undoing move: {e}")
        else:
            ci.tk.messagebox.showerror("Error", "File not found.")
    