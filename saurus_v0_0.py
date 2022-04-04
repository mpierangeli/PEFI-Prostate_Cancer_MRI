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
    editmenu.add_command(label="ROI Rectangular",command=square_gen)
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

    cv1.bind("<Enter>",lambda event, arg=1: focus_cv(event,arg))
    cv2.bind("<Enter>",lambda event, arg=2: focus_cv(event,arg))
    cv3.bind("<Enter>",lambda event, arg=3: focus_cv(event,arg))
    cv4.bind("<Enter>",lambda event, arg=4: focus_cv(event,arg))

def focus_cv(event,arg):
    global focused_cv, cv
    if arg == 1: cv = cv1
    elif arg == 2: cv = cv2
    elif arg == 3: cv = cv3
    elif arg == 4: cv = cv4

## HERRAMIENTAS

def start_square(event):
    global x0, y0, cv
    cv.delete("temp_lines","dibujos","temp_text")
    x0, y0 = event.x, event.y
def finish_square(event):
    global x1, y1, cv
    x1, y1 = event.x, event.y
    if x1 == x0 or y1 == y0:
        print("NO SUELTE EL MOUSE")
        return
    cv.create_rectangle(x0,y0,x1,y1,outline="#F00",tags="dibujos",width=1)
    cv.delete("temp_line")
    cv.old_coords = None
    root.config(cursor="arrow")
    root.unbind('<Button-1>')
    root.unbind('<B1-Motion>')
    root.unbind('<ButtonRelease-1>')
def temp_square(event):
    global cv
    cv.delete("temp_line","temp_text")
    cv.create_line(x0,y0,event.x,y0,fill="#A00",dash=(7,),tags="temp_line")
    cv.create_line(x0,y0,x0,event.y,fill="#A00",dash=(7,),tags="temp_line")
    cv.create_line(event.x,y0,event.x,event.y,fill="#A00",dash=(7,),tags="temp_line")
    cv.create_line(x0,event.y,event.x,event.y,fill="#A00",dash=(7,),tags="temp_line")
    cv.create_text((event.x+x0)/2,y0-10,text=str(abs(round(px_info_var*(event.x-x0),2)))+"mm",fill="#F00",font=("Roboto", 9),tags="temp_text")
    cv.create_text(x0-10,(event.y+y0)/2,text=str(abs(round(px_info_var*(event.y-y0),2)))+"mm",fill="#F00",font=("Roboto", 9),tags="temp_text",angle=90)
def square_gen():
    global cv

    root.config(cursor="tcross")
    root.bind('<Button-1>', start_square)
    root.bind('<B1-Motion>', temp_square)
    root.bind('<ButtonRelease-1>', finish_square)

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
px_info_var = 1
focused_cv = 0

#MAIN WINDOW DISPLAY

windows_creator()
menu_creator()

root.mainloop()