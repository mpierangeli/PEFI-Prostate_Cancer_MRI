from tkinter import *
from PIL import Image,ImageTk
from tkinter import filedialog
import pydicom
import cv2
import numpy as np
import math


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
    editmenu.add_command(label="ROI Circular", command=circle_gen)
    editmenu.add_command(label="Medición",command=ruler_gen)

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

    cv1.bind("<Enter>",lambda event, arg=cv1: focus_cv(event,arg))
    cv2.bind("<Enter>",lambda event, arg=cv2: focus_cv(event,arg))
    cv3.bind("<Enter>",lambda event, arg=cv3: focus_cv(event,arg))
    cv4.bind("<Enter>",lambda event, arg=cv4: focus_cv(event,arg))
def focus_cv(event,arg):
    global cv
    cv = arg

## HERRAMIENTAS
def square_gen():
    root.config(cursor="tcross")
    root.bind('<Button-1>', start_square)
    root.bind('<B1-Motion>', temp_square)
    root.bind('<ButtonRelease-1>', finish_square)
def start_square(event):
    global x0, y0
    cv.delete("temp_square","square","temp_text_s")
    x0, y0 = event.x, event.y
def temp_square(event):
    cv.delete("temp_square","temp_text_s")
    cv.create_line(x0,y0,event.x,y0,fill="#A00",dash=(7,),tags="temp_square")
    cv.create_line(x0,y0,x0,event.y,fill="#A00",dash=(7,),tags="temp_square")
    cv.create_line(event.x,y0,event.x,event.y,fill="#A00",dash=(7,),tags="temp_square")
    cv.create_line(x0,event.y,event.x,event.y,fill="#A00",dash=(7,),tags="temp_square")
    cv.create_text((event.x+x0)/2,y0-10,text=str(abs(round(px_info_var*(event.x-x0),2)))+"mm",fill="#F00",font=("Roboto", 9),tags="temp_text_s")
    cv.create_text(x0-10,(event.y+y0)/2,text=str(abs(round(px_info_var*(event.y-y0),2)))+"mm",fill="#F00",font=("Roboto", 9),tags="temp_text_s",angle=90)
def finish_square(event):
    global x1, y1
    x1, y1 = event.x, event.y
    if x1 == x0 or y1 == y0:
        print("NO SUELTE EL MOUSE")
        return
    cv.create_rectangle(x0,y0,x1,y1,outline="#F00",tags="square",width=1)
    cv.delete("temp_line")
    cv.old_coords = None
    root.config(cursor="arrow")
    root.unbind('<Button-1>')
    root.unbind('<B1-Motion>')
    root.unbind('<ButtonRelease-1>')

def circle_gen():
    root.config(cursor="tcross")
    root.bind('<Button-1>', start_circle)
    root.bind('<B1-Motion>', temp_circle)
    root.bind('<ButtonRelease-1>', finish_circle)
def start_circle(event):
    global x0, y0
    cv.delete("temp_circle","circle","temp_text")
    x0, y0 = event.x, event.y
def temp_circle(event):
    cv.delete("temp_circle","temp_text_c")
    dx = abs(event.x-x0)
    dy = abs(event.y-y0)
    r = math.sqrt(dx**2+dy**2)
    cv.create_oval(x0-r,y0-r,x0+r,y0+r,outline="#A00",dash=(7,),tags="temp_circle")
    cv.create_text(x0,y0+r+10,text="r: "+str(abs(round(px_info_var*r,2)))+"mm",fill="#F00",font=("Roboto", 9),tags="temp_text_c")
def finish_circle(event):
    global x1, y1
    x1, y1 = event.x, event.y
    dx = abs(x1-x0)
    dy = abs(y1-y0)
    r = math.sqrt(dx**2+dy**2)
    if x1 == x0 or y1 == y0:
        print("NO SUELTE EL MOUSE")
        return
    cv.create_oval(x0-r,y0-r,x0+r,y0+r,outline="#F00",tags="circle")
    cv.delete("temp_circle")
    cv.old_coords = None
    root.config(cursor="arrow")
    root.unbind('<Button-1>')
    root.unbind('<B1-Motion>')
    root.unbind('<ButtonRelease-1>')

def ruler_gen():
    root.config(cursor="tcross")
    root.bind('<Button-1>', start_ruler)
    root.bind('<B1-Motion>', temp_ruler)
    root.bind('<ButtonRelease-1>', finish_ruler)
def start_ruler(event):
    global x0, y0
    cv.delete("temp_ruler","medicion","temp_text_r")
    x0, y0 = event.x, event.y
def temp_ruler(event):
    
    cv.delete("temp_ruler","temp_text_r")
    cv.create_line(x0,y0,event.x,event.y,fill="#1BB",dash=(3,),tags="temp_ruler")
    dx = event.x-x0
    dy = event.y-y0
    ang = abs(math.degrees(math.atan((-dy)/(-dx+1e-6))))
    a = 10
    b = 10
    if int(dx) == 0: b -= 10
    elif int(dy) == 0: a -= 10
    elif dx*dy > 0: 
        ang = -ang
        a -= 20

    cv.create_text((event.x+x0)/2+a,(event.y+y0)/2+b,text=str(abs(round(px_info_var*(math.sqrt(dx**2+dy**2)),1)))+"mm",fill="#2CC",font=("Roboto", 9),tags="temp_text_r",angle=ang)
def finish_ruler(event):
    global x1, y1
    x1, y1 = event.x, event.y
    if x1 == x0 and y1 == y0:
        print("NO SUELTE EL MOUSE")
        return
    cv.create_line(x0,y0,x1,y1,fill="#2CC",tags="medicion")
    cv.delete("temp_ruler")
    cv.old_coords = None
    root.config(cursor="arrow")
    root.unbind('<Button-1>')
    root.unbind('<B1-Motion>')
    root.unbind('<ButtonRelease-1>')

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