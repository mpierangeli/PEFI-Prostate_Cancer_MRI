from tkinter import *
from PIL import Image,ImageTk
from tkinter import filedialog
import pydicom
import cv2
import numpy as np


def windows_creator():

    global main_frame, bot_frame

    main_frame = Frame(root, width=MF_W.get(), height=MF_H.get(), background="#222")
    main_frame.grid(row=1, column=0)
    main_frame.grid_propagate(0)

    bot_frame = Frame(root, width=MF_W.get(), height=20, background="#2CC")
    bot_frame.grid(row=2, column=0)
    bot_frame.grid_propagate(0)

def menu_creator():
    
    menubar = Menu(root)
    root.config(menu=menubar)

    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Selección Paciente", command=canvas_creator)
    
    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="ROI Rectangular")
    editmenu.add_command(label="ROI Circular")
    editmenu.add_command(label="Medición")

    reportmenu = Menu(menubar, tearoff=0)
    reportmenu.add_command(label="Nuevo Reporte")

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Ayuda")
    helpmenu.add_command(label="Acerca de...")
    helpmenu.add_separator()
    helpmenu.add_command(label="Salir", command=root.quit)

    menubar.add_cascade(label="Abrir", menu=filemenu)
    menubar.add_cascade(label="Herramientas", menu=editmenu)
    menubar.add_cascade(label="Reportar", menu=reportmenu)
    menubar.add_cascade(label="Ayuda", menu=helpmenu)

def canvas_creator():
    global cv1,cv2,cv3,cv4

    cv1 = Canvas(main_frame, width=int(MF_W.get()/2)-5,height=int(MF_H.get()/2)-5,bg="#666",highlightthickness=0)
    cv1.grid(row=0,column=0,padx=(0,5),pady=(0,5))
    cv1.old_coords = None
    cv2 = Canvas(main_frame, width=int(MF_W.get()/2)-5,height=int(MF_H.get()/2)-5,bg="#666",highlightthickness=0)
    cv2.grid(row=0,column=1,padx=(5,0),pady=(0,5))
    cv2.old_coords = None
    cv3 = Canvas(main_frame, width=int(MF_W.get()/2)-5,height=int(MF_H.get()/2)-5,bg="#666",highlightthickness=0)
    cv3.grid(row=1,column=0,padx=(0,5),pady=(5,0))
    cv3.old_coords = None
    cv4 = Canvas(main_frame, width=int(MF_W.get()/2)-5,height=int(MF_H.get()/2)-5,bg="#666",highlightthickness=0)
    cv4.grid(row=1,column=1,padx=(5,0),pady=(5,0))
    cv4.old_coords = None
## MAIN LOOP

#MAIN WINDOW SETUP
root = Tk()
root.title("S A U R U S")
#root.maxsize(1600, 900)
root.minsize(1600, 900)
root.config(bg="#F00")
root.iconbitmap("unsam.ico")

# GLOBAL VARIABLES
MF_W = IntVar(value=1600)
MF_H = IntVar(value=880)

#MAIN WINDOW DISPLAY

windows_creator()
menu_creator()

root.mainloop()