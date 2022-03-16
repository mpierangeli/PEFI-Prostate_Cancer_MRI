from tkinter import *
from PIL import Image,ImageTk
from tkinter import filedialog
import pydicom
import cv2
#import tempfile
from skimage.filters.rank import gradient
from skimage.morphology import disk, erosion
#from skimage import io



def canvas_clear():
    cv.delete("dibujos")
    cv.old_coords = None

def img_selector():
    global ima_resized
    global ima_r
    global full_dicom
    filepath = filedialog.askopenfilename()
    full_dicom = pydicom.dcmread(filepath)
    img = full_dicom.pixel_array
    img = (img/img.max())*255
    aspect = img.shape[0]/img.shape[1]

    if img.shape[0] > img.shape[1]:
        ima_r = cv2.resize(img,(1000,int(1000/aspect))) #1000 = 1250*0.8 Width BASE
    elif img.shape[1] < img.shape[0]:
        ima_r = cv2.resize(img,(int(720*aspect),720))   #720 = 900*0.8  Height BASE
    else:
        ima_r = cv2.resize(img,(720,720))

    ima_resized = ImageTk.PhotoImage(image=Image.fromarray(ima_r))

    CV_W.set(ima_resized.width())
    CV_H.set(ima_resized.height())

    cv.config(width=CV_W.get(), height=CV_H.get())
    cv.grid(row=0,column=0, padx=(RF_W.get()-CV_W.get())/2, pady=(RF_H.get()-CV_H.get())/2)
    cv_ima = cv.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=ima_resized, tags="foto")
    cv.itemconfig(cv_ima,image=ima_resized)

def start_square(event):
    global x0, y0
    cv.delete("dibujos")
    x0, y0 = event.x, event.y
    
def finish_square(event):
    global x1, y1
    x1, y1 = event.x, event.y
    if x1 == x0 or y1 == y0:
        print("NO SUELTE EL MOUSE")
        return
    cv.create_rectangle(x0,y0,x1,y1,outline="#F00",tags="dibujos",width=brushSize.get())
    cv.delete("temp_line")
    cv.old_coords = None
    root.config(cursor="arrow")

def temp_square(event):
    cv.delete("temp_line")
    cv.create_line(x0,y0,event.x,y0,fill="#F00",dash=(7,),tags="temp_line")
    cv.create_line(x0,y0,x0,event.y,fill="#F00",dash=(7,),tags="temp_line")
    cv.create_line(event.x,y0,event.x,event.y,fill="#F00",dash=(7,),tags="temp_line")
    cv.create_line(x0,event.y,event.x,event.y,fill="#F00",dash=(7,),tags="temp_line")

def cuadra_gen():
    root.config(cursor="tcross")
    cv.bind('<Button-1>', start_square)
    cv.bind('<B1-Motion>', temp_square)
    cv.bind('<ButtonRelease-1>', finish_square)

def gen_info():
    global m_frame
    m_frame = Frame(root, width=MF_W.get(), height=MF_H.get(), background="#AAA")
    m_frame.grid(row=0, column=1)
    m_frame.grid_propagate(0)
    l2 = Label(m_frame, text="INFO",bg="#AAA",font=("Roboto",10)).grid(row=0,column=0,pady=(10,20))
    temp_ima = Label(m_frame,image=ima_cropped,borderwidth=0,bg="#AAA").grid(row=1,column=0,padx=(int((MF_W.get()-ima_cropped.width())/2)), pady=20)
    #IMPORTANT DATA
    # VER Q MOSTRAR EN EL PANEL DE INFO!!
    i1 = Label(m_frame, text="Orig. Img. Size = "+str(CV_W.get())+"x"+str(CV_H.get()),bg="#AAA",font=("Roboto",8)).grid(row=2,column=0,pady=(0,10))
    i2 = Label(m_frame, text="Crop. Img. Size = "+str(ima_cropped.width())+"x"+str(ima_cropped.height()),bg="#AAA",font=("Roboto",8)).grid(row=3,column=0,pady=(0,10))
    i3 = Label(m_frame, text="Paciente = "+str(full_dicom[0x0010, 0x0010].value),bg="#AAA",font=("Roboto",8)).grid(row=4,column=0,pady=(0,10))


def crop_ima():
    global ima_cropped
    #global cont
    global ima_c_n
    x0c = int(x0 + (zoom-1)*CV_W.get()/2)
    y0c = int(y0 + (zoom-1)*CV_H.get()/2)
    x1c = int(x1 + (zoom-1)*CV_W.get()/2)
    y1c = int(y1 + (zoom-1)*CV_H.get()/2)
    if zoom != 1:
        ima_c = ima_z[y0c:y1c,x0c:x1c]
    else:
        ima_c = ima_r[y0:y1,x0:x1]
    #----------------------
    ima_c = ima_c.astype(int)
    ima_c = gradient(ima_c, disk(2)) ## TRABAJAR SOBRE ESTO 
    ima_c = erosion(ima_c)
    #---------------------
    ima_cropped = ImageTk.PhotoImage(image=Image.fromarray(ima_c))
    #io.imsave(temp_dir.name+"\ima_c_"+str(cont)+".png",ima_c)
    #ima_c_n=ImageTk.PhotoImage(Image.open(temp_dir.name+"\ima_c_"+str(cont)+".png"))
    try:
        m_frame.destroy()
    except:
        pass
    ima_c_size = int(ima_cropped.width()*1.1)
    if  ima_c_size > 200:
        MF_W.set(ima_c_size)
    else:
        MF_W.set(200)
    gen_info()
    
    RF_W.set(1450-MF_W.get())
    cv.grid(row=0,column=0, padx=(RF_W.get()-CV_W.get())/2, pady=(RF_H.get()-CV_H.get())/2)
    
    #cont+=1

def zoom_app(event):
    global zoom
    global ima_zoomed
    global ima_z
    zoom = round(zoom+0.1*event.delta/120,1)
    if zoom>2: zoom = 2
    elif zoom<1: zoom = 1
    else: 
        cv.delete("foto")

        ima_z = cv2.resize(ima_r,(int(ima_r.shape[1]*zoom),int(ima_r.shape[0]*zoom)))
        ima_zoomed = ImageTk.PhotoImage(image=Image.fromarray(ima_z))
        cv_ima = cv.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=ima_zoomed, tags="foto")
        cv.itemconfig(cv_ima,image=ima_zoomed)

    zoom_info.set("Zoom = "+str(int(zoom*100))+"%")
    
#MAIN WINDOW SETUP
root = Tk()
root.title("Software de Prueba PEFI 2022")
root.maxsize(1600, 900)
root.minsize(1600, 900)

root.config(bg="#2DD")
root.iconbitmap("unsam.ico")
zoom = 1 #canvas empieza en 100%
#cont = 0 #cantidad de crops en el panel
#temp_dir = tempfile.TemporaryDirectory()
#print(temp_dir.name)


#MAIN WINDOW DISPLAY

MF_W = IntVar(root,value=0)
MF_H = IntVar(root,value=900)
RF_W = IntVar(root,value=1450)
RF_H = IntVar(root,value=900)

l_frame = Frame(root, width=130, height=900, background="#FFF")
l_frame.grid(row=0, column=0,padx=(0,20))
l_frame.grid_propagate(0)

r_frame = Frame(root, width=RF_W.get(), height=RF_H.get(), background="#222")
r_frame.grid(row=0, column=2)
r_frame.grid_propagate(0)

#MENU

l1 = Label(l_frame, text="MENU",bg="#FFF",font=("Roboto",20)).grid(row=0,column=0,pady=(10,20))

b1 = Button(l_frame, text="Selección Imágen",font=("Roboto",11),command = img_selector, relief=FLAT, bg="#555",fg="#FFF",activebackground="#555",activeforeground="#2DD",bd=0,height=2,width=15,justify=CENTER).grid(row=2, column=0,pady=10)
b2 = Button(l_frame, text="Recortar",font=("Roboto",11),command = cuadra_gen, relief=FLAT, bg="#555",fg="#FFF",activebackground="#555",activeforeground="#2DD",bd=0,height=2,width=15,justify=CENTER).grid(row=3, column=0,pady=10)
b3 = Button(l_frame, text="Borrar Selección",font=("Roboto",11),command = canvas_clear, relief=FLAT, bg="#555",fg="#FFF",activebackground="#555",activeforeground="#2DD",bd=0,height=2,width=15,justify=CENTER).grid(row=4, column=0,pady=10)
b4 = Button(l_frame, text="Confirmar",font=("Roboto",11),command = crop_ima, relief=FLAT, bg="#555",fg="#FFF",activebackground="#555",activeforeground="#2DD",bd=0,height=2,width=15,justify=CENTER).grid(row=5, column=0,pady=10)

#---
brushSize = IntVar(l_frame, value=1)
#brushSlider = Scale(l_frame, from_=1,to=10,variable=brushSize,bg="#555",activebackground="#2DD",fg="#FFF",orient=HORIZONTAL,label="Brush Size",width=20,troughcolor="#BBB",font=("Roboto",12)).grid(row=8,column=0,pady=10)
#---


# CANVAS
CV_W = IntVar(root,value=600)
CV_H = IntVar(root,value=600)

cv = Canvas(r_frame, width=CV_W.get(),height=CV_H.get(),bg="#666",highlightthickness=0)
cv.grid(row=0,column=0, padx=(RF_W.get()-CV_W.get())/2, pady=(RF_H.get()-CV_H.get())/2)
cv.old_coords = None

# TECLAS DE CONTROL (algunas)
cv.bind("<MouseWheel>", zoom_app)

# PANEL DE INFO
zoom_info = StringVar(l_frame,value="Zoom = 100%")
infolabel = Label(l_frame, textvariable=zoom_info,bg="#FFF",fg="#000",font=("Roboto",8)).grid(row=9,column=0,pady=10)


root.mainloop()
#temp_dir.cleanup()