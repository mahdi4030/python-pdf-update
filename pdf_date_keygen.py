import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

import tkinter as tk
from tkinter import *

from tkinter import Tk, Button, X
from tkinter.messagebox import showinfo, showwarning

def generate_key():
    #key generation code here


if __name__ == "__main__":
    r = Tk()
    r.resizable(width=False, height=False)
    screen_width = r.winfo_screenwidth()
    screen_height = r.winfo_screenheight()
    x = -200 + (screen_width/2)
    y = -35 + (screen_height/2)
    r.geometry('%dx%d+%d+%d' % (400, 70, x, y))
    r.title('PDF date key gen')

    #PDF file label
    l2 = Label(r, text='Date :')
    l2.pack()
    l2.place(height=25, width=50, x=10, y=20)

    #date input entry
    dateEntry = Entry(r)
    dateEntry.pack()
    dateEntry.place(height=25, width=150, x=70, y=20)

    #convert button
    b_convert = Button(r)
    b_convert['text'] = "Generate"
    b_convert['command'] = generate_key
    b_convert.pack()
    b_convert.place(height=25, width=70, x=300, y=20)
    r.mainloop()