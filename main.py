#graphical dependencies
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk
from ttkbootstrap.constants import *
import ttkbootstrap as tb

#my modules
from custom_titlebar import CustomTitleBar
from custom_styles import apply_styles
from prod_search_gui import SearchGUI
from IRtoolcleaner import UltimateIRTool
import read_config


config = read_config.read_config()
user_style = config['user_style']



# Set Window Title
tk_title = "Production Control Tool"
root, style, ui_font = apply_styles(tk_title, user_style)
root.minimized = False  # only to know if root is minimized
root.maximized = False  # only to know if root is maximized

#prompt for log in information
username = simpledialog.askstring("Input", "Username:")
password = simpledialog.askstring("Input", "Password:", show='*')

# a window to rest the title bar in
window = tb.Frame(root)

# Create a notebook (tabbed layout)
notebook = ttk.Notebook(window)

# Create a frame for the first tab
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='EVM Search')

# Create a frame for the second tab
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Queue Tracker')

# Create a custom title bar
search_gui = SearchGUI(tab1, style, ui_font, tk_title, root, username)  # Instantiate SearchGUI
search_gui.frame.pack(fill=tk.BOTH, expand=True)  # pack the search_gui's frame

queue_monitor = UltimateIRTool(tab2, username, password)
queue_monitor.frame.pack(fill=tk.BOTH, expand=True)

title_bar = CustomTitleBar(root, tk_title, window, style, window, ui_font)  # handles the custom title bar
title_bar.set_appwindow(root)  ##

# Pack the notebook into the window
notebook.pack(fill=tk.BOTH, expand=True)  # pack the notebook into the window
window.pack(fill=tk.BOTH, expand=True)  # pack the window frame after the custom title bar

window.pack(fill=tk.BOTH, expand=True)  # pack the window frame after the custom title bar



root.mainloop()