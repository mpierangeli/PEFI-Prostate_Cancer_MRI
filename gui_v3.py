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
    zoom = round(zoom+event.delta/1200,1)
    if zoom>2:
        zoom = 2
    if zoom<1:
        zoom = 1
    x = cv.canvasx(event.x)
    y = cv.canvasy(event.y)
    
    factor = 1+0.1*event.delta/120
    print(factor)
    #factor = zoom 
    cv.scale(ALL, 560/2, 560/2, factor, factor)
    #pep = Image.open("images\original.png")
    #pepe = ImageTk.PhotoImage(pep.resize(round((pep.width+zoom)),round(pep.height+zoom)))
    #cv.itemconfig(cv_ima,image=pepe)
    #print (zoom)

#MAIN WINDOW SETUP
zoom = 1
root = Tk()
root.title("Software de Prueba PEFI 2022")
root.maxsize(800, 600)
root.minsize(800, 600)

root.config(bg="#2DD")
root.iconbitmap("unsam.ico")


#MAIN WINDOW DISPLAY
l_frame = Frame(root, width=130, height=600, background="#FFF")
l_frame.grid(row=0, column=0,padx=(0,20))
l_frame.grid_propagate(0)
r_frame = Frame(root, width=650, height=600, background="#222")
r_frame.grid(row=0, column=1)
r_frame.grid_propagate(0)

#MENU

l1 = Label(l_frame, text="MENU",bg="#FFF",font=("Roboto",20)).grid(row=0,column=0,pady=(10,20))
b1 = Button(l_frame, text="Clear Canvas",font=("Roboto",12),command = canvas_clear, relief=FLAT, bg="#555",fg="#FFF",activebackground="#555",activeforeground="#2DD",bd=0,height=2,width=15,justify=CENTER).grid(row=2, column=0,pady=10)
b2 = Button(l_frame, text="IMG1",font=("Roboto",12),command = lambda: img_selector(1), relief=FLAT, bg="#555",fg="#FFF",activebackground="#555",activeforeground="#2DD",bd=0,height=2,width=15,justify=CENTER).grid(row=3, column=0,pady=10)
b3 = Button(l_frame, text="IMG2",font=("Roboto",12),command = lambda: img_selector(2), relief=FLAT, bg="#555",fg="#FFF",activebackground="#555",activeforeground="#2DD",bd=0,height=2,width=15,justify=CENTER).grid(row=4, column=0,pady=10)


# DIBUJAR EN CANVAS

cv = Canvas(r_frame, width=600,height=550,bg="#666",bd=0,relief=FLAT)
cv.grid(row=0,column=0, padx=25, pady=25)
cv.old_coords = None

cv.bind('<B1-Motion>', draw_line)
cv.bind('<ButtonRelease-1>', clear_app)
cv.bind("<MouseWheel>", zoom_app)

#mm = ImageTk.PhotoImage(Image.open("images\original.png"))
#cv_ima = cv.create_image(560/2, 560/2, anchor=CENTER, image=mm, #tags="foto")




root.mainloop()