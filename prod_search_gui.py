import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from search_files import SearchManager
from TreeView_Event_Handler import Treeview_Handler
import read_config as readconfig
import threading
import sys
import custom_styles
from file_mover import FileMover
from settings_functions import settings_functions
import json
import time
def get_default_search_folders():
    return [
        r"S:\1_InBox\Shift Supervisor",
        r"S:\1_InBox\Day Shift\[TeamLead]",
        r"S:\2_Measured\QC\[TeamLead]\InProgress",
        r"S:\2_Measured\QC\003PreviouslyMeasured",
        r"S:\2_Measured\QC\004NeedsPlanarization",
        r"S:\3.1_AutoDelivery",
        r"S:\3.1_ManualDelivery",
        r"S:\3.8_StatusFailures",
        r"S:\3.9_AutoDeliveryFailures",
        r"S:\3_QCPassed",
        r"S:\3_QCPassed_1",
        r"S:\3_QCPassed_2",
        r"S:\3_QCPassed_3",
        r"S:\3_QCPassed_4",
        r"S:\3_QCPassed_New",
        r"S:\14_BacktoQCpassed",
        r"S:\8_Canceled Orders",
        r"S:\AutoHouseReport",
        r"S:\2_Measured\QC\PlanarizeThis"
        # Add more folders to search as needed
    ]

config = readconfig.read_config()

if config:
    search_folders = config["search_folders"]
    for folder in search_folders:
        print(folder)
else:
    print("JSON not readable, using default values")
    search_folders = get_default_search_folders()



class SearchGUI:
    def __init__(self, parent, style, DGRAY, LGRAY, RGRAY, ui_font, tk_title, root):
        self.frame = tb.Frame(parent) # , bg=parent.cget('bg'), padx=10, pady=10
        self.frame.columnconfigure(0, weight=1)
        self.DGRAY = DGRAY
        self.LGRAY = LGRAY
        self.RGRAY = RGRAY
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

        self.tree.bind("<Double-1>", self.treeview_handler.open_file_location)
        self.tree.bind("<Button-3>", self.treeview_handler.treeview_right_click)

        self.context_menu.add_command(label="Copy Order #", command=lambda: self.treeview_handler.copy_text(0, is_order_number=True))
        self.context_menu.add_command(label="Copy File Path", command=lambda: self.treeview_handler.copy_text(4, is_order_number=False))
    #created the frame where the search bar, search button, and refresh button go

    def create_input_frame(self):
        input_frame = tb.Frame(self.frame)
        input_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        order_number_label = tb.Label(input_frame, text="Order Numbers:", font= (self.font, 9))
        order_number_label.grid(row=0, column=0, padx=(0, 2), pady=5, sticky="w")

        order_number_entry = tb.Entry(input_frame, width=70)
        order_number_entry.grid(row=0, column=1, padx=(0, 2), pady=5)

        search_button = tb.Button(input_frame, text=" ⮩", command=lambda: threading.Thread(target=self.search_manager.search_files, args=(order_number_entry, search_folders)).start(), bootstyle="secondary-outline")
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
        for widget in self.inner_buttons_frame.winfo_children():
            widget.destroy()

        self.inner_buttons_frame = self.create_move_buttons(self.inner_buttons_frame.master)
        self.inner_buttons_frame.grid(row=0, column=0, padx=0, pady=0, sticky='w')
        self.buttons_frame.grid_rowconfigure(0, weight=1)  # Add this line
        self.buttons_frame.grid_columnconfigure(0, weight=1)  # Add this line
        self.inner_buttons_frame.update_idletasks()  # Ensures that the frame updates after clearing old widgets
   
    def create_move_buttons(self, buttons_frame):
        inner_buttons_frame = tk.Frame(buttons_frame)
        inner_buttons_frame.grid(row=0, column=0, padx=0, pady=0, sticky='w')
        config = readconfig.read_config()
        if config and "move_buttons" in config:
            move_buttons_config = config["move_buttons"]
        else:
            print("JSON not readable or missing move_buttons configuration, using default values")
            move_buttons_config = [
                {"text": "Canceled", "row": 1, "target": r"S:\8_Canceled Orders"},
                {"text": "BackToQCP", "row": 2, "target": r"S:\14_BacktoQCpassed"},
                {"text": "PrevMeasured", "row": 3, "target": r"S:\2_Measured\QC\003PreviouslyMeasured\New"},
                {"text": "Holding", "row": 5, "target": r"S:\AutoHouseReport"},
                {"text": "HelpDesk", "row": 4, "target": r"S:\3.1_ManualDelivery\HELPDESK"}
            ]
    
        for button_config in move_buttons_config:
            text, row, target = button_config["text"], button_config["row"], button_config["target"]
            button = tb.Button(buttons_frame, text=text, width=13, command=lambda target=target: self.file_mover.move_file_threaded(target), bootstyle= 'secondary-link')
            button.grid(row=row, column=0, padx=0, pady=1, sticky='w')
        return inner_buttons_frame
    
    #creates the action log 
    def create_log_display(self):
        log_text = tb.Text(self.frame, wrap="word", state="disabled", height=10, bg=self.DGRAY)
        text_redirector = self.search_manager.TextRedirector(log_text)
        sys.stdout = text_redirector

        scrollbar = tb.Scrollbar(self.frame, orient="vertical", bootstyle = 'light-round', command=log_text.yview)
        log_text.config(yscrollcommand=scrollbar.set)

        log_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        scrollbar.grid(row=5, column=1, padx=1, pady=5, sticky="ns")
        settings_button = tb.Button(self.frame, text="⚙", bootstyle='link', command= lambda: self.open_menu())
        settings_button.grid(row=6, column=0, padx=1, pady=1, sticky="w")
    def open_menu(self):
        # Create a new Toplevel window
        popup = tk.Toplevel(self.frame)
        popup.title("Options")
        popup.transient(self.frame)
        options_notebook = tb.Notebook(popup, bootstyle = 'info')
        options_notebook.grid(row=0, column=0, padx=10, pady=10)

        tab1= tb.Frame(options_notebook)
        tab2 = tb.Frame(options_notebook)
        tab3 = tb.Frame(options_notebook)
        # Add tabs to the notebook
        options_notebook.add(tab1, text="Customize Style")
        options_notebook.add(tab2, text="EVM Move Buttons")
        options_notebook.add(tab3, text="Advanced")
        #create a dynamic list of themes
        our_themes = tb.Style().theme_names()
        # Add a combo box to the popup window
        theme_selector = tb.Combobox(tab1, state="readonly", bootstyle= 'info')
        theme_selector["values"] = our_themes
        theme_selector.grid(row=0, column=1, padx=10, pady=10)

        
        #confirm button to apply changes
        confirm_button = tb.Button(tab1, text="Confirm", command=lambda: self.settings_func.update_style(theme_selector.get(), popup))
        confirm_button.grid(row=1, column=0, columnspan=2, pady=10)
        # Create the second tab with options for the EVM move buttons
        evm_move_columns = ("Label", "Row", "Destination Folder")

        evm_move_tree = ttk.Treeview(tab2, columns=evm_move_columns, show="headings", height=8, bootstyle="info", selectmode=BROWSE)
        evm_move_tree.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.buttons_frame = self.create_buttons_frame()
        self.settings_func = settings_functions(self.root, self.tk_title, evm_move_tree, self.buttons_frame, self)

        # Configure column headings
        for col in evm_move_columns:
            evm_move_tree.heading(col, text=col)

        # Load the move_buttons data from the config
        move_buttons_data = config['move_buttons']

        # Iterate over the move_buttons_data and insert the items into the evm_move_tree
        for item in move_buttons_data:
            evm_move_tree.insert('', 'end', values=(item['text'], item['row'], item['target']))

        delete_button = tb.Button(tab2, text= 'Remove Button', bootstyle= 'danger', command =lambda: self.settings_func.delete_button(popup))
        delete_button.grid(row=2, column=0, padx=5, pady=5)

        edit_button = tb.Button(tab2, text='Edit Button', bootstyle='info',
                         command=lambda: self.settings_func.edit_button(new_button_name, row_selector))
        edit_button.grid(row=2, column=1, padx=5, pady=5)

        button_creator_frame = tb.LabelFrame(tab2, text="Create Button", bootstyle='info')
        button_creator_frame.grid(row=3, column=0, padx=5, pady=5)

        new_button_name = tb.Entry(button_creator_frame)  # Use button_creator_frame as the parent
        new_button_name.grid(row=0, column=0, padx=5, pady=5)  # Call grid() on the widget, not the parent

        num_rows = len(config['move_buttons']) + 1
        row_options = list(range(1, num_rows + 1))

        row_selector = tb.Combobox(button_creator_frame, values=row_options, state="readonly")
        row_selector.grid(row=0, column=1, padx=5, pady=5)

        folder_selector = tb.Button(button_creator_frame, text='Select Destination Folder', command=lambda: self.settings_func.select_destination())  # Use button_creator_frame as the parent
        folder_selector.grid(row=0, column=2, padx=5, pady=5)  # Call grid() on the widget, not the parent

        folder_selection = tb.Label(button_creator_frame, textvariable=self.settings_func.destination_folder)
        folder_selection.grid(row=1, column=0, padx=5, pady=5)

        apply_change_button = ttk.Button(button_creator_frame, text='Apply Changes',
                                 command=lambda: self.settings_func.apply_changes(new_button_name.get(),
                                                                                  row_selector.get(),
                                                                                  self.settings_func.destination_folder.get()))
        apply_change_button.grid(row=2, column=0)

        regenerate_button = tb.Button(tab3, text= 'Reset Settings to Default', bootstyle= 'danger', command =lambda: self.settings_func.regenerate_json())
        regenerate_button.grid(row=0, column=0, padx=5, pady=5)
        
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

        