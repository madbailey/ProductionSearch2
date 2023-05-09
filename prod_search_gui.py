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
from settings_functions import SettingsFunctions
from Settings_GUI import SettingsGUI
import json


    



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

        search_button = tb.Button(input_frame, text=" ⮩", 
                                  command=lambda: self.search_manager.start_search(order_number_entry), 
                                  bootstyle="secondary-outline")      
        search_button.grid(row=0, column=2, padx=(0, 0), pady=5)
        order_number_entry.bind('<Return>', lambda event: self.search_manager.start_search(order_number_entry, event))

        refresh_button = tb.Button(input_frame, text="⟳", command=lambda: threading.Thread(target=self.search_manager.refresh, args=(order_number_entry,)).start(), width=5, bootstyle= "primary")
        refresh_button.grid(row=0, column=3, padx=(75,0), pady=0)
        
    #creates the frame for EVM move buttons and the undo button
    def create_buttons_frame(self):
        buttons_frame = tb.Labelframe(self.frame, text="Move EVM", style= 'custom.TLabelframe')
        buttons_frame.grid(row=2, column=2, padx=0, pady=0)

        self.inner_buttons_frame = self.create_move_buttons(buttons_frame)

        undo_button = tb.Button(buttons_frame, text="Undo", width=13,bootstyle = 'danger' , command=self.file_mover.undo_last_move_threaded) #,
        undo_button.grid(row=30, column=0, padx=0, pady=(30,0), sticky='sw')
        self.buttons_frame = buttons_frame 
        return self.inner_buttons_frame
    
    def refresh_move_buttons(self):
        #print("refresh move buttons executed")

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
                                    bootstyle='link', command= lambda: self.open_settings())
        settings_button.grid(row=6, column=0, padx=1, pady=1, sticky="w")
        
    def open_settings(self):
        self.settings_gui = SettingsGUI(self.frame, self)   
        


     
     




        

      
