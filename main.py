import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from custom_titlebar import CustomTitleBar
from custom_styles import apply_styles
from prod_search_gui import SearchGUI
import read_config

# Set Window Title
tk_title = "Production Search"

config = read_config.read_config()
user_style = config['user_style']

root, style, DGRAY, LGRAY, RGRAY, ui_font = apply_styles(tk_title, user_style)
root.minimized = False  # only to know if root is minimized
root.maximized = False  # only to know if root is maximized
# a window to rest the title bar in
window = tb.Frame(root)

# Create a custom title bar
search_gui = SearchGUI(window, style, DGRAY, LGRAY, RGRAY, ui_font, tk_title, root)  # Instantiate SearchGUI
title_bar = CustomTitleBar(root, tk_title, window, style, DGRAY, LGRAY, RGRAY, search_gui.frame, ui_font) #handles the custom title bar
title_bar.set_appwindow(root) ##

window.pack(fill=tk.BOTH, expand=True)  # pack the window frame after the custom title bar

root.mainloop()