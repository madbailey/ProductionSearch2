import json
import read_config as readconfig
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
from ttkbootstrap.constants import *
import ttkbootstrap as tb
import custom_styles
import prod_search_gui
import time





class settings_functions:
    def __init__(self, root, tk_title, evm_move_tree, buttons_frame, search_gui_instance):
        self.root = root
        self.tk_title = tk_title
        self.destination_folder = tk.StringVar()
        self.evm_move_tree = evm_move_tree
        self.destination_folder.set('')
        self.buttons_frame = buttons_frame
        self.search_gui_instance = search_gui_instance
        print(f"Init destination_folder: {self.destination_folder}, type: {type(self.destination_folder)}")
        # Load the move_buttons data from the config
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        self.move_buttons_data = config['move_buttons']
        self.selected_theme = config['user_style']
        self.destination_folder_var = StringVar()

    def update_style(self, new_theme, popup):
        self.selected_theme = new_theme

        # Update the user_style in the config dictionary
        # Write the updated config to the config.json file
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        config['user_style'] = self.selected_theme

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=2)
        # Apply the new style
        custom_styles.apply_styles(self.tk_title, self.selected_theme, root=self.root)
        print(f"Selected theme: {self.selected_theme}")

    def delete_button(self, toplevel):
        selected_item = self.evm_move_tree.selection()[0]  # Get the ID of the selected item
        index_to_remove = self.evm_move_tree.index(selected_item)  # Get the index of the selected item
        self.evm_move_tree.delete(selected_item)  # Remove the item from the treeview
        
        self.update_move_buttons_data()
      

    def select_destination(self):
        folder_path = tk.filedialog.askdirectory()
        self.destination_folder_var.set(folder_path)
        print(f"Init destination_folder_var: {self.destination_folder_var.get()}, type: {type(self.destination_folder_var)}")
        return folder_path

    def create_new_row(self, new_button_name, destination_folder):
       self.button_name = new_button_name
       self.destination_folder = destination_folder
       index_to_edit = len(self.evm_move_tree.get_children())
       print(f"Init destination_folder: {self.destination_folder}, type: {type(self.destination_folder)}")

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
        print(f"Init destination_folder: {self.destination_folder}, type: {type(self.destination_folder)}")

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
            print(f"Config BEFORE update: {config}")
        config['move_buttons'] = move_buttons_data
        print(f"Config AFTER update: {config}")
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=2)

    def apply_changes(self):
        self.update_move_buttons_data()
        self.search_gui_instance.refresh_move_buttons()
        print("Refresh Move Buttons Called")
    def clear_entries(self, new_button_name, folder_selection):
        new_button_name.delete(0, 'end')
        folder_selection.delete(0, 'end')

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
                {"text": "ADF", "row": 6, "target": "S:\\3.1_AutoDelivery\\ADF"}
            ],
            "user_style": "old"
        }

        with open("config.json", "w") as config_file:
            json.dump(data, config_file, indent=2)
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        config['user_style'] = self.selected_theme

        print("Reset Settings to Default Config")
        self.search_gui_instance.refresh_move_buttons()