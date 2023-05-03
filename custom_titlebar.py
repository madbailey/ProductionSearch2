from tkinter import ttk
from ttkthemes import ThemedTk
import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from ctypes import windll
from events_handler import *
#this handles the aesthetics and some basic mechanics of the custom tkinter title bar, more utility functions like resizing, moving the window, minimizing and 
#restoring after minimizing are found in events_handler.py
class CustomTitleBar:
    def __init__(self, root, title, window, style, main_content, ui_font):
        self.root = root
        self.title = title
        self.window = window
        self.style = style
        self.FG_COLOR = style.lookup("TEntry", "foreground")
        self.BG_COLOR = style.lookup("TFrame", "background")
        self.SELECT_BG_COLOR = style.lookup("TEntry", "selectbackground")
        self.font = ui_font
        self.main_content = main_content
        self.create_title_bar()
        self.root.minimized = False
        self.root.maximized = False
        self.first_map_event = True  # Add this flag to track whether the <Map> event has been triggered for the first time
        
   
## created the tkinter objects, frame and buttons and binds them to events 
    def create_title_bar(self):
        title_bar_bootstyle = 'dark'
        title_bar = tb.Frame(bootstyle=title_bar_bootstyle)
        close_button = tb.Button(title_bar, text='  ⮽  ', command=self.root.destroy, bootstyle = title_bar_bootstyle)
        expand_button = tb.Button(title_bar, text=' 🗖 ', command=lambda: maximize_me(self.root, expand_button), bootstyle = title_bar_bootstyle)
        minimize_button = tb.Button(title_bar, text=' ⚊ ', command=lambda: minimize_me(self.root), bootstyle = title_bar_bootstyle)
        title_bar_title = tb.Label(title_bar, text=self.title, bootstyle = f"{title_bar_bootstyle}.inverse", font = (self.font, 10))
        title_bar.bind('<Button-1>', lambda event: get_pos(event, self.root, title_bar, title_bar_title, expand_button))
        title_bar_title.bind('<Button-1>', lambda event: get_pos(event, self.root, title_bar, title_bar_title, expand_button))




        # button effects in the title bar when hovering over buttons
        #close_button.bind('<Enter>', lambda event: changex_on_hovering(event, close_button))
        #close_button.bind('<Leave>', lambda event: returnx_to_normalstate(event, close_button))
        #expand_button.bind('<Enter>', lambda event: change_size_on_hovering(event, expand_button))
        #expand_button.bind('<Leave>', lambda event: return_size_on_hovering(event, expand_button))
        #minimize_button.bind('<Enter>', lambda event: changem_size_on_hovering(event, minimize_button))
        #minimize_button.bind('<Leave>', lambda event: returnm_size_on_hovering(event, minimize_button,))

        # resize the window width
        resizex_widget = tk.Frame(self.window, cursor='sb_h_double_arrow')
        resizex_widget.pack(side=RIGHT, ipadx=2, fill=Y)

        resizex_widget.bind("<B1-Motion>", lambda event: resizex(event, self.root, resizex_widget, self.BG_COLOR))


        resizex_widget.bind("<B1-Motion>", lambda event: resizex(event, self.root, resizex_widget, self.BG_COLOR))

        # resize the window height
        resizey_widget = tb.Frame(self.window,  cursor='sb_v_double_arrow')
        resizey_widget.pack(side=BOTTOM, ipadx=2, fill=X)
        resizey_widget.bind("<B1-Motion>", lambda event: resizey(event, self.root, resizey_widget, self.BG_COLOR))
        # pack the widgets
        title_bar.pack(fill=X)
        close_button.pack(side=RIGHT, ipadx=7, ipady=1)
        expand_button.pack(side=RIGHT, ipadx=7, ipady=1)
        minimize_button.pack(side=RIGHT, ipadx=7, ipady=1)
        title_bar_title.pack(side=LEFT, padx=10)
        self.main_content.pack(in_=self.window, expand=1, fill=tk.BOTH)

## using a custom title bar means no icon shows on the task bar and you can't alt tab switch to it, so this turns that stuff back on
    def set_appwindow(self, mainWindow):
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        # Magic
        hwnd = windll.user32.GetParent(mainWindow.winfo_id())
        stylew = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        stylew = stylew & ~WS_EX_TOOLWINDOW
        stylew = stylew | WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, stylew)

        mainWindow.wm_withdraw()
        mainWindow.after(10, lambda: mainWindow.wm_deiconify())

        # Bind deminimize function to the root window
        mainWindow.bind("<Map>", self.handle_map_event)  # Call handle_map_event method instead of deminimize

##handles minimizing and reopening 
    def handle_map_event(self, event):
        if self.first_map_event:
            self.first_map_event = False
        else:
            deminimize(event.widget)

    