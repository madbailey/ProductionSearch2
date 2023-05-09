import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from draggable_treeview import DraggableTreeview
import json
from settings_functions import SettingsFunctions


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

        button_folder_selection = tb.Entry(button_creator_frame, textvariable=self.settings_func.destination_folder_var)
        button_folder_selection.grid(row=1, column=1, padx=5, pady=5)

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

        self.search_folder_var = tk.StringVar()
        self.search_folder_selection = tb.Entry(search_editor_frame, textvariable=self.search_folder_var)
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
                self.settings_functions.add_new_folder(self.settings_gui.search_folder_var.get())
                self.settings_functions.clear_folder_entries(self.settings_gui.search_folder_selection)
            except ValueError as e:
                tk.messagebox.showerror("Error", str(e))
                self.settings_functions.clear_folder_entries(self.settings_gui.search_folder_selection)
    def delete_folder_row_controller(self):
        self.settings_functions.delete_folder(self.settings_gui.popup)