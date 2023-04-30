import json
import read_config as readconfig
import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *
import ttkbootstrap as tb
import custom_styles
import prod_search_gui
import time





class settings_functions:
    def __init__(self, root, tk_title, evm_move_tree, buttons_frame,  search_gui_instance):
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

        # Load the entire config
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        # Update the config
        del config['move_buttons'][index_to_remove]  # Remove the item from the move_buttons_data list

        # Save the entire config back to the file
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=2)
        
        toplevel.after(100, self.search_gui_instance.refresh_move_buttons)
        print("refresh move buttons called")

    def edit_button(self, new_button_name, row_selector):
        selected_item = self.evm_move_tree.selection()[0]
        button_data = self.evm_move_tree.item(selected_item)['values']

        new_button_name.delete(0, 'end')
        new_button_name.insert(0, button_data[0])

        row_selector.set(button_data[1])

        self.destination_folder.set(button_data[2])

    def select_destination(self):
        folder_path = tk.filedialog.askdirectory()
        self.destination_folder.set(folder_path)
        print(f"Init destination_folder: {self.destination_folder}, type: {type(self.destination_folder)}")
        return folder_path

    def apply_changes(self, new_button_name, button_row, destination_folder):
        self.button_name = new_button_name
        self.button_row = button_row
        self.destination_folder = destination_folder
        print(f"Init destination_folder: {self.destination_folder}, type: {type(self.destination_folder)}")
        selected_item = self.evm_move_tree.selection()

        if selected_item:
            index_to_edit = self.evm_move_tree.index(selected_item) - 1
        else:
            index_to_edit = len(self.move_buttons_data)

        new_button_data = {
            "text": self.button_name,
            "row": int(self.button_row),
            "target": self.destination_folder
        }

        if selected_item:
            self.move_buttons_data[index_to_edit] = new_button_data
            self.evm_move_tree.item(selected_item, values=(new_button_data['text'], new_button_data['row'], new_button_data['target']))
        else:
            self.move_buttons_data.append(new_button_data)
            self.evm_move_tree.insert('', 'end', values=(new_button_data['text'], new_button_data['row'], new_button_data['target']))
        # Load the entire config
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        # Update the move_buttons key with the modified move_buttons_data
        config['move_buttons'] = self.move_buttons_data

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=2)

        self.search_gui_instance.refresh_move_buttons()
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