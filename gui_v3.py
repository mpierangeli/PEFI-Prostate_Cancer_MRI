from itertools import count
from tkinter import *
from PIL import Image,ImageTk
from tkinter import filedialog

def draw_line(event):
    x, y = event.x, event.y
    if cv.old_coords:
        x1, y1 = cv.old_coords
        cv.create_line(x, y, x1, y1,tags="dibujos",fill="red")
    cv.old_coords = x,y

def clear_app(event):
    cv.old_coords = None

def canvas_clear():
    cv.delete("dibujos")

def img_selector(num):
    global pepe
    if num == 1:
        pepe = ImageTk.PhotoImage(Image.open("images\original.png"))
    else:
        pepe = ImageTk.PhotoImage(Image.open("images\\bordes.png"))
    cv.itemconfig(cv_ima,image=pepe)


def zoom_app(event):
    global zoom
    global pepe
    zoom+=round(event.delta/120)
    if zoom>20:
        zoom = 20
    if zoom<1:
        zoom = 1
    #x = cv.canvasx(event.x)
    #y = cv.canvasy(event.y)
    #factor = (1+0.001*zoom) ** event.delta
    #factor = zoom 
    cv.scale(ALL, 560/2, 560/2, (1+0.1*round(event.delta/120)), (1+0.1*round(event.delta/120)))
    pepe = ImageTk.PhotoImage(Image.open("images\original.png").resize((50*zoom,50*zoom)))
    cv.itemconfig(cv_ima,image=pepe)

#MAIN WINDOW SETUP
zoom = 1
root = Tk()
root.title("Software de Prueba PEFI 2022")
root.maxsize(800, 600)

root.config(bg="skyblue")
root.iconbitmap("unsam.ico")


#MAIN WINDOW DISPLAY
l_frame = Frame(root, width=200, height=580)
l_frame.grid(row=0, column=0, padx=10, pady=10)
l_frame.grid_propagate(0)
r_frame = Frame(root, width=560, height=580)
r_frame.grid(row=0, column=1, padx=10, pady=10)


# DIBUJAR EN CANVAS

cv = Canvas(r_frame, width=560,height=560)
cv.grid(row=0,column=0, padx=5, pady=5)
cv.old_coords = None

cv.bind('<B1-Motion>', draw_line)
cv.bind('<ButtonRelease-1>', clear_app)
cv.bind("<MouseWheel>", zoom_app)


tool_bar = Frame(l_frame, width=180, height=340)
tool_bar.grid(row=2, column=0, padx=5, pady=5)
Button(tool_bar, text="Clear",command = canvas_clear).grid(row=2, column=0, padx=5, pady=5)
Button(tool_bar, text="Insert Image",command = lambda: img_selector(1)).grid(row=3, column=0, padx=5, pady=5)
Button(tool_bar, text="Insert Image2",command = lambda: img_selector(2)).grid(row=4, column=0, padx=5, pady=5)
mm = ImageTk.PhotoImage(Image.open("images\original.png"))
cv_ima = cv.create_image(560/2, 560/2, anchor=CENTER, image=mm, tags="foto")

root.mainloop()