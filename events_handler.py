from tkinter import *
import tkinter as tk
from ctypes import windll
from tkinter import Toplevel

##these functions handle resizing, minimizing, and click and dragging the custom tkinter title bar
##using a custom title bar necessitates disabling basic windows OS window handling so you have to fake it
def minimize_me(root):
    # Get the window handle
    hwnd = windll.user32.GetParent(root.winfo_id())

    # Minimize the window using the Windows API
    windll.user32.ShowWindow(hwnd, 6)  # 6 is the command to minimize the window

    # Create a temporary Toplevel widget to show in the taskbar while the main window is minimized
    root.temp_toplevel = Toplevel(root)
    root.temp_toplevel.withdraw()
    root.temp_toplevel.overrideredirect(1)
    # root.temp_toplevel.iconify()  # Remove this line
    root.temp_toplevel.protocol("WM_DELETE_WINDOW", lambda: deminimize(root))


def deminimize(root):
    if hasattr(root, 'temp_toplevel'):
        root.temp_toplevel.destroy()
        del root.temp_toplevel

    # Get the window handle
    hwnd = windll.user32.GetParent(root.winfo_id())

    # Restore the window using the Windows API
    windll.user32.ShowWindow(hwnd, 9)  # 9 is the command to restore the window


def maximize_me(root, expand_button):
    if root.maximized == False:  # if the window was not maximized
        root.normal_size = root.geometry()
        expand_button.config(text=" 🗗 ")
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
        root.maximized = not root.maximized
        # now it's maximized

    else:  # if the window was maximized
        expand_button.config(text=" 🗖 ")
        root.geometry(root.normal_size)
        root.maximized = not root.maximized
        # now it is not maximized


#def changex_on_hovering(event, close_button, RGRAY):
#    close_button['bg'] = 'red'


#def returnx_to_normalstate(event, close_button, RGRAY):
#    close_button['bg'] = RGRAY


#def change_size_on_hovering(event, expand_button, RGRAY):
#    expand_button['bg'] = RGRAY


#def return_size_on_hovering(event, expand_button, RGRAY):
#    expand_button['bg'] = RGRAY


def changem_size_on_hovering(event, minimize_button, LGRAY):
    minimize_button['bg'] = LGRAY


def returnm_size_on_hovering(event, minimize_button, RGRAY):
    minimize_button['bg'] = RGRAY


def get_pos(event, root, title_bar, title_bar_title, expand_button):
    if root.maximized == False:

        xwin = root.winfo_x()
        ywin = root.winfo_y()
        startx = event.x_root
        starty = event.y_root

        ywin = ywin - starty
        xwin = xwin - startx

        def move_window(event):  # runs when window is dragged
            root.config(cursor="fleur")
            root.geometry(f'+{event.x_root + xwin}+{event.y_root + ywin}')

        def release_window(event):  # runs when window is released
            root.config(cursor="arrow")

        title_bar.bind('<B1-Motion>', move_window)
        title_bar.bind('<ButtonRelease-1>', release_window)
        title_bar_title.bind('<B1-Motion>', move_window)
        title_bar_title.bind('<ButtonRelease-1>', release_window)
    else:
        expand_button.config(text=" 🗖 ")
        root.maximized = not root.maximized


def resizex(event, root, resizex_widget, DGRAY):
    xwin = root.winfo_x()
    difference = (event.x_root - xwin) - root.winfo_width()

    if root.winfo_width() > 150:  # 150 is the minimum width for the window
        try:
            root.geometry(f"{root.winfo_width() + difference}x{root.winfo_height()}")
        except:
            pass

              
    resizex_widget.config(bg=DGRAY)


def resizey(event, root, resizey_widget, DGRAY):
    ywin = root.winfo_y()
    difference = (event.y_root - ywin) - root.winfo_height()

    if root.winfo_height() > 150: # 150 is the minimum height for the window
        try:
            root.geometry(f"{ root.winfo_width()  }x{ root.winfo_height() + difference}")
        except:
            pass
    else:
        if difference > 0: # so the window can't be too small (150x150)
            try:
                root.geometry(f"{ root.winfo_width()  }x{ root.winfo_height() + difference}")
            except:
                pass

    resizey_widget.config(bg=DGRAY)
