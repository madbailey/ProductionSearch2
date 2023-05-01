import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from tkinter import ttk
from ttkthemes import ThemedTk
from PIL import Image, ImageTk




def apply_styles(tk_title, user_style, root=None):
    if root is None:
        root = tb.Window(themename=user_style)
    style = tb.Style()
    style.theme_use(user_style)  # Change the theme
    root.overrideredirect(True)  # turns off title bar, geometry
    image = Image.open('magnify.ico')
    photo = ImageTk.PhotoImage(image)
    root.wm_iconphoto(False, photo)

    ui_font = "Helvetica"
    
    style.configure('danger.Tbutton', font=(ui_font, 9), bootstyle='danger')
    style.configure('RightAligned.TButton', font=(ui_font, 9), width=12)

    style.configure('custom.TLabelframe', font=(ui_font, 9))
    return root, style, ui_font