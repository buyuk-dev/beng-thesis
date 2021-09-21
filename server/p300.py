""" 2021 Created by michal@buyuk-dev.com
"""


import tkinter as tk
import random


window = tk.Tk()
window.geometry("600x400")

text = tk.StringVar()
text.set("START")

btn = tk.Button(
    textvariable=text,
    height=400,
    width=600,
    bg="lightgrey",
    fg="black"
)

btn['font'] = ('times', 300, 'bold')
btn.pack()


event_counter = 0
NUMBER_OF_TRIALS = 100


def pause():
    global text
    global window
    if event_counter == NUMBER_OF_TRIALS:
        exit()

    text.set("")
    window.after(1000, show_letter)


def show_letter():
    global text
    global window
    text.set(random.choice("ABCDE"))
    window.after(500, pause)


def click():
    show_letter()


btn.config(command=click)
window.mainloop()
