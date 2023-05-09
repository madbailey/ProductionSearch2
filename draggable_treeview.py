##graphics dependencies
import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *
import ttkbootstrap as tb

##functional dependencies
import os
from datetime import datetime
import csv
class DraggableTreeview(tb.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SettingsFunctions = None
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

    def set_settings_functions(self, SettingsFunctions):
        self.SettingsFunctions = SettingsFunctions
        
        
