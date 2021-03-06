from tkinter import *
from PIL import Image,ImageTk
#from tkinter import filedialog

def clear_app(event):
    cv.old_coords = None

def canvas_clear():
    cv.delete("dibujos","foto")
    cv.old_coords = None

def img_selector(num):
    global pepe
    if num == 1:
        pepe = ImageTk.PhotoImage(Image.open("images\original.png"))
        #print(pepe.height()) VER VER
    else:
        pepe = ImageTk.PhotoImage(Image.open("images\\bordes.png"))

    cv_ima = cv.create_image(600/2, 520/2, anchor=CENTER, image=pepe, tags="foto")
    cv.itemconfig(cv_ima,image=pepe)

def start_square(event):
    global x0, y0
    x0, y0 = event.x, event.y
    
def finish_square(event):
    x1, y1 = event.x, event.y
    if x1 == x0 or y1 == y0:
        print("NO SUELTE EL MOUSE")
        return
    cv.create_rectangle(x0,y0,x1,y1,outline="#FFF",tags="dibujos",width=brushSize.get())
    cv.delete("temp_line")
    cv.old_coords = None

def draw_line(event):
    x, y = event.x, event.y
    if cv.old_coords:
        x1, y1 = cv.old_coords
        cv.create_line(x, y, x1, y1,tags="dibujos",fill="#F00",width=brushSize.get(),smooth=True,capstyle=ROUND,joinstyle=ROUND)
    cv.old_coords = x,y

def temp_square(event):
    cv.delete("temp_line")
    cv.create_line(x0,y0,event.x,event.y,fill="#DDD",dash=(3,),tags="temp_line")


def cuadra_gen():
    cv.bind('<Button-1>', start_square)
    cv.bind('<B1-Motion>', temp_square)
    cv.bind('<ButtonRelease-1>', finish_square)

def free_gen():
    cv.bind('<B1-Motion>', draw_line)
    cv.bind('<ButtonRelease-1>', clear_app)

def zoom_app(event):
    global zoom
    global pepe

    zoom = round(zoom+0.1*event.delta/120,1)
    if zoom>2: zoom = 2
    elif zoom<1: zoom = 1
    else: 
        factor = 1.001**event.delta
        x = cv.canvasx(event.x) 
        y = cv.canvasy(event.y)
        cv.scale(ALL, x, y, factor, factor) # x e y, irian en origins, para zoomear donde apunto...
        #cv.scale(ALL, 650/2, 600/2, factor, factor) # x e y, irian en origins, para zoomear donde apunto...
    zoom_info.set("Zoom = "+str(int(zoom*100))+"%")
   
    #pep = Image.open("images\original.png")
    #pepe = ImageTk.PhotoImage(pep.resize(round((pep.width+zoom)),round(pep.height+zoom)))
    #cv.itemconfig(cv_ima,image=pepe)

#MAIN WINDOW SETUP
root = Tk()
root.title("Software de Prueba PEFI 2022")
root.maxsize(800, 600)
root.minsize(800, 600)

root.config(bg="#2DD")
root.iconbitmap("unsam.ico")
zoom = 1 #canvas empieza en 100%



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
b4 = Button(l_frame, text="Pintar",font=("Roboto",12),command = free_gen, relief=FLAT, bg="#555",fg="#FFF",activebackground="#555",activeforeground="#2DD",bd=0,height=2,width=15,justify=CENTER).grid(row=6, column=0,pady=10)
#---
brushSize = IntVar(l_frame, value=1)
brushSlider = Scale(l_frame, from_=1,to=10,variable=brushSize,bg="#555",activebackground="#2DD",fg="#FFF",orient=HORIZONTAL,label="Brush Size",width=30,troughcolor="#BBB",font=("Roboto",12)).grid(row=5,column=0,pady=10)
#---
b5 = Button(l_frame, text="Selector",font=("Roboto",12),command = cuadra_gen, relief=FLAT, bg="#555",fg="#FFF",activebackground="#555",activeforeground="#2DD",bd=0,height=2,width=15,justify=CENTER).grid(row=7, column=0,pady=10)


# CANVAS

cv = Canvas(r_frame, width=600,height=520,bg="#666",highlightthickness=0)
cv.grid(row=0,column=0, padx=25, pady=25)
cv.old_coords = None


# TECLAS DE CONTROL (algunas)
cv.bind("<MouseWheel>", zoom_app)

# PANEL DE INFO
zoom_info = StringVar(r_frame,value="Zoom = 100%")
infolabel = Label(r_frame, textvariable=zoom_info,bg="#222",fg="#FFF",font=("Roboto",12)).grid(row=1,column=0)


root.mainloop()