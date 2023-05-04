import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from search_files import SearchManager
from TreeView_Event_Handler import Treeview_Handler
import read_config as readconfig
import threading
import sys
from file_mover import FileMover
from settings_functions import settings_functions
import json


    

class DraggableTreeview(tb.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings_functions = None
        self.bind("<Up>", self.move_up)
        self.bind("<Button-1>", self.focus_treeview)
        self.bind("<Down>", self.move_down)

    def move_up(self, event):
        item = self.selection()
        if item:
            index = self.index(item)
            if index > 0:
                self.move(item, '', index - 1)
                self.selection_set(item)
        return 'break'

    def move_down(self, event):
        item = self.selection()
        if item:
            index = self.index(item)
            if index < len(self.get_children()) - 1:
                self.move(item, '', index + 1)
                self.selection_set(item)
        return 'break'
    def focus_treeview(self, event):
        self.focus_set()

    def set_settings_functions(self, settings_functions):
        self.settings_functions = settings_functions

class SearchGUI:
    def __init__(self, parent, style, ui_font, tk_title, root):
        self.frame = tb.Frame(parent) # , bg=parent.cget('bg'), padx=10, pady=10
        self.frame.columnconfigure(0, weight=1)
        self.style = style
        self.font = ui_font
        self.tk_title= tk_title
        self.root = root
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.config = readconfig.read_config()
        self.create_treeview()
        self.create_input_frame()
        self.create_buttons_frame()
        self.create_log_display()
        

    def create_treeview(self):
        columns = ("Order #", "Location", "Product", "Last Modified", "File Path")
        column_widths = (5, 20, 10, 20, 30)
        self.style.configure("Treeview.Heading", font = (self.font, 9))

        self.tree = tb.Treeview(self.frame, columns=columns, show="headings", bootstyle = "dark", selectmode='extended') #
        self.search_manager = SearchManager(self.tree)
        self.treeview_handler = Treeview_Handler(self.tree, self.frame, self.context_menu)
        self.file_mover = FileMover(self.tree)

        for i, column in enumerate(columns):
            self.tree.heading(f"#{i+1}", text=column, command=lambda col=column: self.treeview_handler.treeview_sort_column(col, False))
            self.tree.column(f"#{i+1}", stretch=True, width=column_widths[i]) #

        self.tree.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        # Create a vertical scrollbar
        self.scrollbar = tb.Scrollbar(self.frame, orient="vertical", command=self.tree.yview, bootstyle = 'light.rounded')
        self.scrollbar.grid(row=2, column=1, padx=5, pady=5, sticky="ns")

        # Configure the treeview to use the scrollbar
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.bind("<Double-1>", self.treeview_handler.open_file_location)
        self.tree.bind("<Button-3>", self.treeview_handler.treeview_right_click)
        self.tree.bind("<Control-c>", self.treeview_handler.copy_text)

        self.context_menu.add_command(label="Copy Order #", 
                              command=lambda: self.treeview_handler.copy_text(column_index=0))

        self.context_menu.add_command(label="Copy File Path", 
                                      command=lambda: self.treeview_handler.copy_text(column_index=4))
        export_button = tb.Button(self.frame, text="Export", 
                                    bootstyle='link',
                                      command= lambda: self.treeview_handler.export_to_csv("output.csv"))
        export_button.grid(row=6, column=2, padx=1, pady=1, sticky="e")
    #created the frame where the search bar, search button, and refresh button go

    def create_input_frame(self):
        input_frame = tb.Frame(self.frame)
        input_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        order_number_label = tb.Label(input_frame, text="Order Numbers:", font= (self.font, 9))
        order_number_label.grid(row=0, column=0, padx=(0, 2), pady=5, sticky="w")

        order_number_entry = tb.Entry(input_frame, width=70)
        order_number_entry.grid(row=0, column=1, padx=(0, 2), pady=5)

        search_button = tb.Button(input_frame, text=" ⮩", command=lambda: threading.Thread(target=self.search_manager.search_files, args=(order_number_entry,)).start(), bootstyle="secondary-outline")
        search_button.grid(row=0, column=2, padx=(0, 0), pady=5)


        refresh_button = tb.Button(input_frame, text="⟳", command=lambda: threading.Thread(target=self.search_manager.refresh, args=(order_number_entry,)).start(), width=5, bootstyle= "primary")
        refresh_button.grid(row=0, column=3, padx=(75,0), pady=0)
        
    #creates the frame for EVM move buttons and the undo button
    def create_buttons_frame(self):
        buttons_frame = tb.Labelframe(self.frame, text="Move EVM", style= 'custom.TLabelframe')
        buttons_frame.grid(row=2, column=2, padx=0, pady=0)

        self.inner_buttons_frame = self.create_move_buttons(buttons_frame)

        undo_button = tb.Button(buttons_frame, text="Undo", width=13,bootstyle = 'danger' , command=self.file_mover.undo_last_move_threaded) #,
        undo_button.grid(row=30, column=0, padx=0, pady=(30,0), sticky='sw')

        return self.inner_buttons_frame
    
    def refresh_move_buttons(self):
        print("refresh move buttons executed")

        # Remove old widgets
        for widget in self.inner_buttons_frame.winfo_children():
            widget.destroy()

        # Create a new inner_buttons_frame
        new_inner_buttons_frame = tk.Frame(self.inner_buttons_frame.master)
        new_inner_buttons_frame.grid(row=0, column=0, padx=0, pady=0, sticky='w')

        # Update the reference
        self.inner_buttons_frame = new_inner_buttons_frame

        # Load the move_buttons data from the config
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        move_buttons_data = config['move_buttons']

        # Repopulate the inner_buttons_frame with the updated move_buttons data
        for item in move_buttons_data:
            button = tb.Button(
                self.inner_buttons_frame,
                text=item['text'], 
                command=lambda target=item['target']: self.file_mover.move_file_threaded(target),
                bootstyle='default.link',
            )
            button.grid(row=item['row'], column=0, padx=0, pady=0, sticky="ew")

        # Update the frame
        self.inner_buttons_frame.update_idletasks()

    def create_move_buttons(self, buttons_frame):
        self.buttons_list = []  # Add this line to store the buttons
        inner_buttons_frame = tk.Frame(buttons_frame)
        inner_buttons_frame.grid(row=0, column=0, padx=0, pady=0, sticky='ew')
        config = readconfig.read_config()
        move_buttons_config = config["move_buttons"]
    
        for button_config in move_buttons_config:
            text, row, target = button_config["text"], button_config["row"], button_config["target"]
            button = tb.Button(inner_buttons_frame, text=text, bootstyle = 'default.link', 
                               command=lambda target=target: self.file_mover.move_file_threaded(target))
            button.grid(row=row, column=0, padx=0, pady=0, sticky='ew')
            self.buttons_list.append(button)  # Add this line to store the button in the list
        return inner_buttons_frame
    
    #creates the action log 
    def create_log_display(self):
        log_text = tb.Text(self.frame, wrap="word", state="disabled", height=10)
        text_redirector = self.search_manager.TextRedirector(log_text)
        sys.stdout = text_redirector

        scrollbar = tb.Scrollbar(self.frame, orient="vertical", bootstyle = 'light-round', command=log_text.yview)
        log_text.config(yscrollcommand=scrollbar.set)

        log_text.grid(row=5, column=0, 
                      columnspan=2, padx=5, pady=5, 
                      sticky="nsew")
        scrollbar.grid(row=5, column=1, padx=1, pady=5, sticky="ns")

        settings_button = tb.Button(self.frame, text="⚙", 
                                    bootstyle='link', command= lambda: self.open_menu())
        settings_button.grid(row=6, column=0, padx=1, pady=1, sticky="w")

        
       
    def open_menu(self):
        # Create a new Toplevel window
        popup = tk.Toplevel(self.frame)
        popup.title("Options")
        popup.transient(self.frame)
        options_notebook = tb.Notebook(popup, bootstyle = 'info')
        options_notebook.grid(row=0, column=0, padx=10, pady=20)

        def combined_button_function():
            self.settings_func.update_style(theme_selector.get(), popup)
            self.settings_func.apply_changes()

        confirm_button = tb.Button(popup, text="Apply All", 
                                    bootstyle = 'info.outline',
                                    command=combined_button_function)
        confirm_button.grid(row=1, column=0, padx=0, sticky=E)

        regenerate_button = tb.Button(popup, text= 'Reset All Settings', 
                                       bootstyle= 'danger.outline', 
                                       command=lambda: self.settings_func.regenerate_json())
        regenerate_button.grid(row=1, column=0, padx=0, sticky=W, columnspan=1)


        tab1= tb.Frame(options_notebook)
        tab2 = tb.Frame(options_notebook)
        tab3 = tb.Frame(options_notebook)
        # Add tabs to the notebook
        options_notebook.add(tab1, text="Misc")
        options_notebook.add(tab2, text="EVM Move Buttons")
        options_notebook.add(tab3, text="Search Parameters")


        ## FIRST TAB
        #create a dynamic list of themes
        our_themes = tb.Style().theme_names()
        # Add a combo box to the popup window
        theme_selector = tb.Combobox(tab1, state="readonly", bootstyle= 'info')
        theme_selector["values"] = our_themes
        theme_selector.grid(row=0, column=0, padx=10, pady=10)



        ## SECOND TAB

        evm_move_tree = DraggableTreeview(master=tab2, 
                                  columns=[0, 2], 
                                  show="headings", height=8, 
                                  bootstyle="info", selectmode=BROWSE)
        evm_move_tree.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.buttons_frame = self.create_buttons_frame()

        ## THIRD TAB
        search_folder_tree = ttk.Treeview(master=tab3, 
                                          columns=[0], 
                                          show="headings", height=8, 
                                          bootstyle="info", selectmode=BROWSE)
        search_folder_tree.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        search_folder_tree.heading(0, text='Folders', anchor="center")

        # Load the move_buttons data from the config
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        search_folder_data = config['search_folders']

        # Iterate over the search_folder_data and insert the items into the search_folder_tree
        for index, folder in enumerate(search_folder_data):
            search_folder_tree.insert('', index, values=(folder,))

        #instantiate the settings functions
        self.settings_func = settings_functions(self.root, self.tk_title, evm_move_tree, self.buttons_frame, self, search_folder_tree)

        evm_move_tree.set_settings_functions(self.settings_func)

        evm_move_tree.heading(0, text= 'Label', anchor= W)
        evm_move_tree.heading(1, text= 'Path', anchor= E)
        evm_move_tree.column(
            column=0,
            width= 25
        )
        evm_move_tree.column(
            column=1,
            width= 200
        )


        # Load the move_buttons data from the config
        move_buttons_data = config['move_buttons']

        # Iterate over the move_buttons_data and insert the items into the evm_move_tree
        for item in move_buttons_data:
            evm_move_tree.insert('', 'end', values=(item['text'], item['target']))
       
        button_creator_frame = tb.LabelFrame(tab2, 
                                             text="Button Editor", bootstyle='info')
        button_creator_frame.grid(row=3, column=0, padx=5, pady=10)

        new_button_label = tb.Label(button_creator_frame, text="Button Label")
        new_button_label.grid(row=0, column=0, padx=5, pady=5)


        new_button_name = tb.Entry(button_creator_frame)  # Use button_creator_frame as the parent
        new_button_name.grid(row=0, column=1, padx=5, pady=5)  # Call grid() on the widget, not the parent

        button_folder_selector_icon = ttk.Button(button_creator_frame, text='📁',
                                  command=lambda: self.settings_func.select_destination(output_var=self.settings_func.destination_folder_var),
                                  bootstyle='info-outline')  # Use button_creator_frame as the parent
        button_folder_selector_icon.grid(row=1, column=0, padx=5, pady=5)  

        button_folder_selection = tb.Entry(button_creator_frame, textvariable=self.settings_func.destination_folder_var)
        button_folder_selection.grid(row=1, column=1, padx=5, pady=5)

        delete_button = tb.Button(button_creator_frame, text= 'Delete Selected', 
                                  bootstyle= 'danger', 
                                  command =lambda: self.settings_func.delete_button(popup))
        delete_button.grid(row=2, column=3, padx=5, pady=10)

        def create_new_row_wrapper():
            try:
                self.settings_func.create_new_row(new_button_name.get(), self.settings_func.destination_folder_var.get())
                self.settings_func.clear_button_entries(new_button_name, button_folder_selection)
            except ValueError as e:
                tk.messagebox.showerror("Error", str(e))

        new_row_button = ttk.Button(button_creator_frame, text='Create New',
                            command=create_new_row_wrapper,
                            bootstyle='info')
        new_row_button.grid(row=2, column=0, padx= 2, pady=10)

        edit_row_button = ttk.Button(button_creator_frame, text='Edit Selected',
                                 command=lambda: [self.settings_func.edit_row(new_button_name.get(),
                                                                                  self.settings_func.destination_folder_var.get()),
                                                    self.settings_func.clear_button_entries(new_button_name, button_folder_selection)],
                                                    bootstyle = 'info')
        edit_row_button.grid(row=2, column=1, padx=2, pady=10)

        ##third tab


        search_editor_frame = tb.LabelFrame(tab3, 
                                             text="Search Folder Editor", bootstyle='info')
        search_editor_frame.grid(row=3, column=0, padx=5, pady=10)

        search_folder_var = tk.StringVar()
        search_folder_selection = tb.Entry(search_editor_frame, textvariable=search_folder_var)
        search_folder_selection.grid(row=0, column=1, padx=5, pady=5)

        select_search_button = ttk.Button(search_editor_frame, text='📁',
                                  command=lambda: self.settings_func.select_destination(output_var=search_folder_var),
                                  bootstyle='info')
        select_search_button.grid(row=0, column=0, padx=5, pady=5)

        def new_search_folder_wrapper():
            try:
                self.settings_func.add_new_folder(search_folder_var.get())
                self.settings_func.clear_folder_entries(search_folder_selection)
            except ValueError as e:
                tk.messagebox.showerror("Error", str(e))
                self.settings_func.clear_folder_entries(search_folder_selection)
        
        new_row_button = ttk.Button(search_editor_frame, text='Add New',
                            command=new_search_folder_wrapper,
                            bootstyle='info')
        new_row_button.grid(row=2, column=0, padx= 2, pady=10)

        delete_folder_button = tb.Button(search_editor_frame, text='Delete Selected', 
                            bootstyle='danger', 
                            command=lambda: self.settings_func.delete_folder(popup))
        delete_folder_button.grid(row=2, column=2, padx=5, pady=10)



        # Center the popup window
        popup.update()
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()

        main_window_width = self.root.winfo_width()
        main_window_height = self.root.winfo_height()
        main_window_x = self.root.winfo_x()
        main_window_y = self.root.winfo_y()

        x_coordinate = int(main_window_x + (main_window_width / 2) - (popup_width / 2))
        y_coordinate = int(main_window_y + (main_window_height / 2) - (popup_height / 2))

        popup.geometry(f"{popup_width}x{popup_height}+{x_coordinate}+{y_coordinate}")

