##GUI DEPENDENCIES
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
from ttkbootstrap.constants import *
import ttkbootstrap as tb

## FUNCTION DEPENDENCIES
import json
import os

## OUR MODULES
from draggable_treeview import DraggableTreeview
import custom_styles


class SettingsGUI:
    def __init__(self, parent, search_gui_instance):
        self.parent = parent
        self.search_gui_instance = search_gui_instance
        
        with open('config.json', 'r') as config_file:
            self.config = json.load(config_file)
        
        self.settings_func = SettingsFunctions(self.parent, 
                                               self.search_gui_instance)    
        self.settings_controller = SettingsController(self, self.settings_func)                                      
        self.open_menu()
        
    def open_menu(self):
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Options")
        self.popup.transient(self.parent)
        options_notebook = tb.Notebook(self.popup, bootstyle = 'info')
        options_notebook.grid(row=0, column=0, padx=10, pady=20)
        
        self.tab1= tb.Frame(options_notebook)
        self.tab2 = tb.Frame(options_notebook)
        self.tab3 = tb.Frame(options_notebook)
        # Add tabs to the notebook
        options_notebook.add(self.tab1, text="Theme")
        options_notebook.add(self.tab2, text="EVM Move Buttons")
        options_notebook.add(self.tab3, text="Search Parameters")
        
        #call the methods to populat the tab contents
        self.settings_buttons()
        self.first_tab_content()
        self.second_tab_content()
        self.third_tab_content()
        
        #center the pop up window
        self.popup.update()
        popup_width = self.popup.winfo_width()
        popup_height = self.popup.winfo_height()

        main_window_width = self.parent.winfo_width()
        main_window_height = self.parent.winfo_height()
        main_window_x = self.parent.winfo_x()
        main_window_y = self.parent.winfo_y()

        x_coordinate = int(main_window_x + (main_window_width / 2) - (popup_width / 2))
        y_coordinate = int(main_window_y + (main_window_height / 2) - (popup_height / 2))

        self.popup.geometry(f"{popup_width}x{popup_height}+{x_coordinate}+{y_coordinate}")
        
    def settings_buttons(self):
        confirm_button = tb.Button(self.popup, text="Apply All", 
                                    bootstyle = 'info.outline',
                                    command=self.settings_controller.apply_all_changes_controller)
        confirm_button.grid(row=1, column=0, padx=0, sticky=E)

        regenerate_button = tb.Button(self.popup, text= 'Reset All Settings', 
                                       bootstyle= 'danger.outline', 
                                       command=lambda: self.settings_controller.regenerate_button_controller())
        regenerate_button.grid(row=1, column=0, padx=0, sticky=W, columnspan=1)
        
    def first_tab_content(self):
         #create a dynamic list of themes
        our_themes = tb.Style().theme_names()
        # Add a combo box to the popup window
        self.theme_selector = tb.Combobox(self.tab1, state="readonly", bootstyle= 'info')
        self.theme_selector["values"] = our_themes
        self.theme_selector.grid(row=0, column=0, padx=10, pady=10)
             
    def second_tab_content(self):
        self.evm_move_tree = DraggableTreeview(master=self.tab2, 
                                  columns=[0, 2], 
                                  show="headings", height=8, 
                                  bootstyle="info", selectmode=BROWSE)
        self.evm_move_tree.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.buttons_frame = self.search_gui_instance.create_buttons_frame()

        self.evm_move_tree.set_settings_functions(self.settings_func)

        self.evm_move_tree.heading(0, text= 'Label', anchor= W)
        self.evm_move_tree.heading(1, text= 'Path', anchor= E)
        self.evm_move_tree.column(
            column=0,
            width= 25
        )
        self.evm_move_tree.column(
            column=1,
            width= 200
        )


        # Load the move_buttons data from the config
        move_buttons_data = self.config['move_buttons']

        # Iterate over the move_buttons_data and insert the items into the evm_move_tree
        for item in move_buttons_data:
            self.evm_move_tree.insert('', 'end', values=(item['text'], item['target']))
       
        button_creator_frame = tb.LabelFrame(self.tab2, 
                                             text="Button Editor", bootstyle='info')
        button_creator_frame.grid(row=3, column=0, padx=5, pady=10)

        new_button_label = tb.Label(button_creator_frame, text="Button Label")
        new_button_label.grid(row=0, column=0, padx=5, pady=5)


        self.new_button_name = tb.Entry(button_creator_frame)  # Use button_creator_frame as the parent
        self.new_button_name.grid(row=0, column=1, padx=5, pady=5)  # Call grid() on the widget, not the parent

        
        new_row_button = ttk.Button(button_creator_frame, text='Create New',
                            command=self.settings_controller.create_new_button_row_controller,
                            bootstyle='info')
        new_row_button.grid(row=2, column=0, padx= 2, pady=10)

        edit_row_button = ttk.Button(button_creator_frame, text='Edit Selected',
                             command=lambda: self.settings_controller.edit_button_row_controller(),
                             bootstyle='info')
        edit_row_button.grid(row=2, column=1, padx=2, pady=10)
        
        button_folder_selector_icon = ttk.Button(button_creator_frame, text='📁',
                                        command=lambda: self.settings_controller.button_folder_selector_controller(),
                                        bootstyle='info-outline')  # Use button_creator_frame as the parent
        button_folder_selector_icon.grid(row=1, column=0, padx=5, pady=5)  # Use button_creator_frame as the parent

        self.button_folder_selection = tb.Entry(button_creator_frame, textvariable=self.settings_func.destination_folder_var)
        self.button_folder_selection.grid(row=1, column=1, padx=5, pady=5)

        delete_button = tb.Button(button_creator_frame, text= 'Delete Selected', 
                                  bootstyle= 'danger', 
                                  command =lambda: self.settings_controller.delete_button_row_controller())
        delete_button.grid(row=2, column=3, padx=5, pady=10)
        
        self.settings_func.evm_move_tree = self.evm_move_tree
        
    def third_tab_content(self):
        self.search_folder_tree = ttk.Treeview(master=self.tab3, 
                                          columns=[0], 
                                          show="headings", height=8, 
                                          bootstyle="info", selectmode=BROWSE)
        self.search_folder_tree.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.search_folder_tree.heading(0, text='Folders', anchor="center")
        
        
        search_folder_data = self.config['search_folders']
        
        # Iterate over the search_folder_data and insert the items into the search_folder_tree
        for index, folder in enumerate(search_folder_data):
            self.search_folder_tree.insert('', index, values=(folder,))
            
            
        search_editor_frame = tb.LabelFrame(self.tab3, 
                                             text="Search Folder Editor", bootstyle='info')
        search_editor_frame.grid(row=3, column=0, padx=5, pady=10)

        
        self.search_folder_selection = tb.Entry(search_editor_frame, textvariable=self.settings_func.search_folder_var)
        self.search_folder_selection.grid(row=0, column=1, padx=5, pady=5)

        select_search_button = ttk.Button(search_editor_frame, text='📁',
                                  command=lambda: self.settings_controller.search_parameter_folder_selector_controller(),
                                  bootstyle='info')
        select_search_button.grid(row=0, column=0, padx=5, pady=5)   
        new_row_button = ttk.Button(search_editor_frame, text='Add New',
                            command=self.settings_controller.add_search_folder_controller,
                            bootstyle='info')
        new_row_button.grid(row=2, column=0, padx= 2, pady=10)

        delete_folder_button = tb.Button(search_editor_frame, text='Delete Selected', 
                            bootstyle='danger', 
                            command=lambda: self.settings_controller.delete_folder_row_controller())
        delete_folder_button.grid(row=2, column=2, padx=5, pady=10)
        
        self.settings_func.search_folder_tree = self.search_folder_tree
       
#connecting buttons to functions              
class SettingsController: 
    def __init__(self, settings_gui, settings_functions):
        self.settings_gui = settings_gui
        self.settings_functions = settings_functions
        
    def apply_all_changes_controller(self):
        self.settings_functions.update_style(self.settings_gui.theme_selector.get(), self.settings_gui.popup)
        self.settings_functions.apply_changes()
        
    def regenerate_button_controller(self):
        print("pressed regenerate")
        self.settings_functions.regenerate_json()
    
    def create_new_button_row_controller(self):
            try:
                self.settings_functions.create_new_row(self.settings_gui.new_button_name.get(), 
                                                  self.settings_functions.destination_folder_var.get())
                self.settings_functions.clear_button_entries(self.settings_gui.new_button_name, 
                                                        self.self.settings_gui.button_folder_selection)
            except ValueError as e:
                tk.messagebox.showerror("Error", str(e))
                
    def edit_button_row_controller(self):
        self.settings_functions.edit_row(self.settings_gui.new_button_name.get(),
                                         self.settings_functions.destination_folder_var.get())
        self.settings_functions.clear_button_entries(self.settings_gui.new_button_name, 
                                                 self.settings_gui.button_folder_selection)
        
    def button_folder_selector_controller(self):
        self.settings_functions.select_destination(output_var=self.settings_functions.destination_folder_var)
    
    def search_parameter_folder_selector_controller(self):
        self.settings_functions.select_destination(output_var=self.settings_functions.search_folder_var) 
           
    def delete_button_row_controller(self):
        self.settings_functions.delete_button(self.settings_gui.popup)
        
    def add_search_folder_controller(self):
            try:
                self.settings_functions.add_new_folder(self.settings_functions.search_folder_var.get())
                self.settings_functions.clear_folder_entries(self.settings_gui.search_folder_selection)
            except ValueError as e:
                tk.messagebox.showerror("Error", str(e))
                self.settings_functions.clear_folder_entries(self.settings_gui.search_folder_selection)
    
    def delete_folder_row_controller(self):
        self.settings_functions.delete_folder(self.settings_gui.popup)
        
       
class SettingsFunctions:
    """
    This class receives inputs from the SettingsController class and modifies config.json
    """
    def __init__(self, parent, search_gui_instance):
        self.parent = parent
        self.search_gui_instance = search_gui_instance
        self.destination_folder = tk.StringVar()
        self.evm_move_tree = None
        self.search_folder_tree = None
        self.destination_folder.set('')
        
        # Load the move_buttons data from the config
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        self.config=config
        self.move_buttons_data = config['move_buttons']
        self.selected_theme = config['user_style']
        self.destination_folder_var = StringVar()
        self.search_folder_var = StringVar()

    def update_style(self, new_theme, popup):
        # Check if the new_theme is an empty string
        if new_theme == "":
            return

        self.selected_theme = new_theme
        # Update the user_style in the config dictionary
        # Write the updated config to the config.json file
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        config['user_style'] = self.selected_theme

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=2)
        # Apply the new style
        custom_styles.apply_styles(self.search_gui_instance.tk_title, self.selected_theme, 
                                   root=self.search_gui_instance.root)
        print(f"Selected theme: {self.selected_theme}")

    def delete_button(self, toplevel):
        selected_item = self.evm_move_tree.selection()[0]  # Get the ID of the selected item
        index_to_remove = self.evm_move_tree.index(selected_item)  # Get the index of the selected item
        self.evm_move_tree.delete(selected_item)  # Remove the item from the treeview

    def select_destination(self, output_var):
        default_folder = os.path.abspath("s:/")  # This will set the default folder to the S drive
        folder_path = tk.filedialog.askdirectory(initialdir=default_folder)
        output_var.set(folder_path)
        #print(f"Init output_var: {output_var.get()}, type: {type(output_var)}")
        return folder_path

    def create_new_row(self, new_button_name, destination_folder):
        # Check if both new_button_name and destination_folder are not empty strings
        if new_button_name == "" or destination_folder == "":
            raise ValueError("New buttons need name and destination folder.")

        # Check if the destination_folder is a valid directory
        if not os.path.isdir(destination_folder):
            raise ValueError(f"The destination folder '{destination_folder}' is not a valid directory.")

        self.button_name = new_button_name
        self.destination_folder = destination_folder
        index_to_edit = len(self.evm_move_tree.get_children())
        #print(f"Init destination_folder: {self.destination_folder}, type: {type(self.destination_folder)}")

        new_button_data = {
            "text": self.button_name,
            "row": index_to_edit + 1,
            "target": self.destination_folder
        }

        self.evm_move_tree.insert('', 'end', values=(new_button_data['text'], new_button_data['target']))  # Insert at the end of the Treeview
        self.update_move_buttons_data()

    def edit_row(self, new_button_name, destination_folder):
        self.button_name = new_button_name
        self.destination_folder = destination_folder
        #print(f"Init destination_folder: {self.destination_folder}, type: {type(self.destination_folder)}")

        selected_item = self.evm_move_tree.selection()
        if selected_item:
            index_to_edit = self.evm_move_tree.index(selected_item) - 1
            item_values = self.evm_move_tree.item(selected_item, 'values')

            # Use the new values if provided, otherwise keep the original values
            new_button_name = self.button_name if self.button_name else item_values[0]
            new_destination_folder = self.destination_folder if self.destination_folder else item_values[1]

            new_button_data = {
                "text": new_button_name,
                "row": index_to_edit + 1,
                "target": new_destination_folder
            }

            self.evm_move_tree.item(selected_item, values=(new_button_data['text'], new_button_data['target']))
            self.update_move_buttons_data()
        else:
            print("No row is selected for editing")
        
    def update_move_buttons_data(self):
        move_buttons_data = []
        for index, item_id in enumerate(self.evm_move_tree.get_children(), start=1):
            item_values = self.evm_move_tree.item(item_id, 'values')

            # Check if the target value is available in the item_values
            target_value = item_values[1] if len(item_values) > 1 else ''

            move_buttons_data.append({'text': item_values[0], 'row': index, 'target': target_value})

        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            
        config['move_buttons'] = move_buttons_data
        
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=2)

    def apply_changes(self):
        self.update_move_buttons_data()
        self.search_gui_instance.refresh_move_buttons()
        self.update_search_data()
        print("Refresh Move Buttons Called")

    def clear_button_entries(self, new_button_name, folder_selection):
        new_button_name.delete(0, 'end')
        folder_selection.delete(0, 'end')

    def clear_folder_entries(self, search_folder_selection):
        search_folder_selection.delete(0, 'end')
    
    
    def update_move_treeview(self):
        # Clear the treeview
        for item in self.evm_move_tree.get_children():
            self.evm_move_tree.delete(item)    
        # Load the move_buttons data from the config
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        move_buttons_data = config['move_buttons']    
        # Repopulate the treeview with the updated data
        for item in move_buttons_data:
            self.evm_move_tree.insert('', 'end', values=(item['text'], item['target'])) 

    def add_new_folder(self, search_folder_var):
        # Check if both new_button_name and destination_folder are not empty strings
        if search_folder_var == "":
            raise ValueError("No Folder Selected")

        # Check if the destination_folder is a valid directory
        if not os.path.isdir(search_folder_var):
            raise ValueError(f"The destination folder '{search_folder_var}' is not a valid directory.")

        # Normalize the folder path
        search_folder_var = os.path.normpath(search_folder_var)

        # Get the folder data from the search_folder_tree treeview
        existing_folders = [os.path.normpath(self.search_folder_tree.item(item)['values'][0]) for item in self.search_folder_tree.get_children()]

        # Check if the new folder is a duplicate or a subfolder of an existing folder
        for folder in existing_folders:
            # Normalize and make absolute paths
            folder_abs = os.path.abspath(os.path.normpath(folder))
            search_folder_var_abs = os.path.abspath(os.path.normpath(search_folder_var))

            # Compare the paths
            if search_folder_var_abs == folder_abs:
                raise ValueError(f"The folder '{search_folder_var}' is already in the search.")

            # Check if one is a subfolder of the other
            if os.path.commonpath([search_folder_var_abs, folder_abs]) == folder_abs:
                raise ValueError(f"The folder '{search_folder_var}' is a subfolder of an existing folder.")


    def delete_folder(self, toplevel):
        selected_item = self.search_folder_tree.selection()[0]  # Get the ID of the selected item
        index_to_remove = self.search_folder_tree.index(selected_item)  # Get the index of the selected item
        self.search_folder_tree.delete(selected_item)  # Remove the item from the treeview
 
    def update_search_data(self):
        # Get the folder data from the search_folder_tree treeview
        search_folder_data = [self.search_folder_tree.item(item)['values'][0] for item in self.search_folder_tree.get_children()]
        #print("Search folder data from treeview:", search_folder_data)

        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        #print("Config before update:", config)

        config['search_folders'] = search_folder_data

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=2)
        #print("Updated config:", config)

    def regenerate_search_treeview(self):
        # Clear the treeview
        for item in self.search_folder_tree.get_children():
            self.search_folder_tree.delete(item)    
        # Load the move_buttons data from the config
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        search_folder_data = config['search_folders']

        # Iterate over the search_folder_data and insert the items into the search_folder_tree
        for index, folder in enumerate(search_folder_data):
            self.search_folder_tree.insert('', index, values=(folder,))

    def regenerate_json(self):
        data = {
            "search_folders": [
                "S:\\1_InBox\\Shift Supervisor",
                "S:\\1_InBox\\Day Shift\\[TeamLead]",
                "S:\\2_Measured\\QC\\[TeamLead]\\InProgress",
                "S:\\2_Measured\\QC\\003PreviouslyMeasured",
                "S:\\2_Measured\\QC\\004NeedsPlanarization",
                "S:\\3.1_AutoDelivery",
                "S:\\3.1_ManualDelivery",
                "S:\\3.8_StatusFailures",
                "S:\\3.9_AutoDeliveryFailures",
                "S:\\3_QCPassed",
                "S:\\3_QCPassed_1",
                "S:\\3_QCPassed_2",
                "S:\\3_QCPassed_3",
                "S:\\3_QCPassed_4",
                "S:\\3_QCPassed_New",
                "S:\\14_BacktoQCpassed",
                "S:\\8_Canceled Orders",
                "S:\\AutoHouseReport",
                "S:\\2_Measured\\QC\\PlanarizeThis"
            ],
            "move_buttons": [
                {"text": "Canceled", "row": 1, "target": "S:\\8_Canceled Orders"},
                {"text": "BackToQCP", "row": 2, "target": "S:\\14_BacktoQCpassed"},
                {"text": "PrevMeasured", "row": 3, "target": "S:\\2_Measured\\QC\\003PreviouslyMeasured\\new"},
                {"text": "HelpDesk", "row": 4, "target": "S:\\3.1_ManualDelivery\\HELPDESK"},
                {"text": "Holding", "row": 5, "target": "S:\\AutoHouseReport"},
                {"text": "ADF", "row": 6, "target": "S:\\3.1_ManualDelivery\\ADF"}
            ],
            "user_style": "old"
        }

        with open("config.json", "w") as config_file:
            json.dump(data, config_file, indent=2)
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        config['user_style'] = self.selected_theme

        print("Reset Settings to Default Config")
        self.update_move_treeview()
        self.regenerate_search_treeview()
        self.search_gui_instance.refresh_move_buttons()