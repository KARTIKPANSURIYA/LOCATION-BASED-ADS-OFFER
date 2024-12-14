"""
Below code provides utility functions to create fade-in and fade-out animations for tkinter widgets.
The animations are achieved by gradually adjusting the transparency of the tkinter window.
"""

import tkinter as tk

def fade_in(widget, steps=10, interval=50):
    """
    Creating a fade-in animation for a tkinter widget.

    Args:
        widget (tk.Widget): The tkinter widget to animate.
        steps (int): The number of steps for the fade-in effect.
        interval (int): The time interval (ms) between each step.
    """
    for i in range(steps + 1):
        alpha = i / steps
        widget.master.attributes("-alpha", alpha)
        widget.master.update_idletasks()
        widget.after(interval)

def fade_out(widget, steps=10, interval=50):
    """
    Creating a fade-out animation for a tkinter widget.

    Args:
        widget (tk.Widget): The tkinter widget to animate.
        steps (int): The number of steps for the fade-out effect.
        interval (int): The time interval (ms) between each step.
    """
    for i in range(steps + 1):
        alpha = 1 - (i / steps)
        widget.master.attributes("-alpha", alpha)
        widget.master.update_idletasks()
        widget.after(interval)
