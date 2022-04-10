from tkinter import *
from PIL import Image,ImageTk
from tkinter import filedialog
import pydicom
import cv2
import numpy as np
import math
import imutils


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
    reportmenu.add_command(label="Nuevo Reporte",command=report_window_gen)

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Ayuda")
    helpmenu.add_command(label="Acerca de...")
    helpmenu.add_separator()
    helpmenu.add_command(label="Salir", command=root.quit)

    menubar.add_cascade(label="Abrir", menu=filemenu)
    menubar.add_cascade(label="Herramientas", menu=editmenu)
    menubar.add_cascade(label="Reportar", menu=reportmenu)
    menubar.add_cascade(label="Ayuda", menu=helpmenu)

def report_window_gen():
    global report_window

    report_window = Toplevel(root)
    report_window.minsize(500,500)

def canvas_creator():
    global cv1,cv2,cv3,cv4
    CV_W.set(int(MF_W.get()/2)-5)
    CV_H.set(int(MF_H.get()/2)-5)
    cv1 = Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0)
    cv1.grid(row=0,column=0,padx=(0,5),pady=(0,5))
    cv1.old_coords = None
    cv2 = Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0)
    cv2.grid(row=0,column=1,padx=(5,0),pady=(0,5))
    cv2.old_coords = None
    cv3 = Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0)
    cv3.grid(row=1,column=0,padx=(0,5),pady=(5,0))
    cv3.old_coords = None
    cv4 = Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0)
    cv4.grid(row=1,column=1,padx=(5,0),pady=(5,0))
    cv4.old_coords = None

    cv1.bind("<Enter>",lambda event, arg=cv1: focus_cv(event,arg))
    cv2.bind("<Enter>",lambda event, arg=cv2: focus_cv(event,arg))
    cv3.bind("<Enter>",lambda event, arg=cv3: focus_cv(event,arg))
    cv4.bind("<Enter>",lambda event, arg=cv4: focus_cv(event,arg))
    cv1.bind("<Leave>",lambda event, arg=cv1: unfocus_cv(event,arg))
    cv2.bind("<Leave>",lambda event, arg=cv2: unfocus_cv(event,arg))
    cv3.bind("<Leave>",lambda event, arg=cv3: unfocus_cv(event,arg))
    cv4.bind("<Leave>",lambda event, arg=cv4: unfocus_cv(event,arg))

    cv1.bind("<MouseWheel>", slice_selection)
    cv3.bind("<MouseWheel>", slice_selection)  
    cv4.bind("<MouseWheel>", slice_selection)
    cv2.bind("<MouseWheel>", depth_selection)  
    patient_loader()

def focus_cv(event,arg):
    global cv
    cv = arg
    cv.create_text(50,CV_H.get()-20,text="FOCUSED",font=("Roboto",5),fill="#FFF",tag="focus_check")
def unfocus_cv(event,arg):
    global cv
    cv = arg
    cv.delete("focus_check")
def slice_selection(event):
    global slice_num,depth_num
    if event.delta > 0 and slice_num < len(axiales)-1: slice_num+=1
    elif event.delta < 0 and slice_num > 0: slice_num-=1
    set_img(slice_num,depth_num)
def depth_selection(event):
    global depth_num
    if event.delta > 0 and depth_num < len(coronales)-1: depth_num+=1
    elif event.delta < 0 and depth_num > 0: depth_num-=1
    set_img(slice_num,depth_num)
def patient_loader():
    global filepaths, axiales, coronales, slice_num, depth_num, factor, init_dcm, init_img, px_info_var

    filepaths = filedialog.askopenfilenames()
    filepaths = list(filepaths)
    
    #-------------------------------------------------
    #GENERO PLANO CORONAL CON IMAGENES T2 (VER COMO SELECCIONAR ESAS EN PARTICULAR)
    init_dcm = pydicom.dcmread(filepaths[0])
    init_img = init_dcm.pixel_array

    px_info_var = [float(init_dcm[0x0028,0x0030].value[0]),float(init_dcm[0x0028,0x0030].value[1])]
    axiales = np.zeros((len(filepaths),init_img.shape[0],init_img.shape[1]))
    factor = int(init_dcm[0x0018, 0x0050].value/px_info_var[0])
    #factor = 6 #factor = ancho de corte / ancho de pixel => cantidad de pixeles por tajo
    coronales  =  np.zeros((axiales.shape[1],factor*axiales.shape[0],axiales.shape[2]))

    slice_num = 0
    depth_num = int(coronales.shape[0]/2)

    for n, dcm in enumerate(filepaths):
        full_dicom = pydicom.dcmread(dcm)
        axiales[n] = full_dicom.pixel_array
    max = axiales.max()
    for n in range(len(axiales)):
        axiales[n] = (axiales[n]/max)*255

    for p in range(axiales.shape[1]): # por cada fila de las axiales -> profundidad de la coronal
        for i in range(axiales.shape[0]): # por cada imagen axial -> altura de la coronal
            for j in range(factor): # por ancho de tomo axial, repito misma muestra
                coronales[p,i*factor+j] = axiales[i,p,:]
    #------------------------------------------------
    set_img(slice_num,depth_num) # por default inicia mostrando esto



    #-------------------------------------
    root.bind("<F1>",info_tab_gen)

def info_tab_gen(event):
    global info_tab
    info_tab = Frame(root,background="#222")
    info_tab.place(relx=0,rely=0, width=200, height=MF_H.get())
    l2 = Label(info_tab, text="INFORMACIÓN",bg="#222",font=("Roboto",10),fg="#FFF").grid(row=0,column=0,pady=(10,20))

    #IMPORTANT DATA
    # VER Q MOSTRAR EN EL PANEL DE INFO!!
    i1 = Label(info_tab, text="Paciente = "+str(init_dcm[0x0010, 0x0010].value),bg="#222",font=("Roboto",9),fg="#FFF").grid(row=2,column=0,pady=(0,10))
    i2 = Label(info_tab, text="Canvas Size = "+str(CV_W.get())+"x"+str(CV_H.get()),bg="#222",font=("Roboto",9),fg="#FFF").grid(row=3,column=0,pady=(0,10))
    i3 = Label(info_tab, text="Orig. Img. Size = "+str(init_img.shape[1])+"x"+str(init_img.shape[0]),bg="#222",font=("Roboto",9),fg="#FFF").grid(row=4,column=0,pady=(0,10))
    #i4 = Label(info_tab, text="Crop. Img. Size = "+str(ima_cropped.width())+"x"+str(ima_cropped.height()),bg="#AAA",font=("Roboto",9)).grid(row=5,column=0,pady=(0,10))
    i5 = Label(info_tab, text="FOV = "+str(int(init_img.shape[1]*px_info_var[0]))+"x"+str(int(init_img.shape[0]*px_info_var[1]))+" [mm x mm]",bg="#222",font=("Roboto",9),fg="#FFF").grid(row=6,column=0,pady=(0,10))
    ##si la secuencia es 2d o 3d cambia el slice thickness:
    if init_dcm[0x0018,0x0023].value == "2D":
        ST = round(init_dcm[0x0018, 0x0050].value*(1+init_dcm[0x0018, 0x0088].value/100),1)
    elif init_dcm[0x0018,0x0023].value == "3D":
        ST = round(init_dcm[0x0018, 0x0050].value,1)
    else:
        ST = 1000000
    i6 = Label(info_tab, text="Slice Thickness = "+str(ST)+"mm",bg="#222",font=("Roboto",9),fg="#FFF").grid(row=7,column=0,pady=(0,10))

    root.bind("<F1>",info_tab_destroy)
def info_tab_destroy(event):
    info_tab.destroy()
    root.bind("<F1>",info_tab_gen)
def set_img(num,depth):
    global cv,cv1,cv2,cv3,cv4,axial_t2,coronal_t2

    temp_axial_t2 = imutils.resize(axiales[num], height=CV_H.get())
    temp_coronal_t2 = imutils.resize(coronales[depth], width=temp_axial_t2.shape[0])
    axial_t2 = ImageTk.PhotoImage(Image.fromarray(temp_axial_t2))
    coronal_t2 = ImageTk.PhotoImage(Image.fromarray(temp_coronal_t2))
    #axial_t2 = ImageTk.PhotoImage(Image.fromarray(axiales[num]))
    #coronal_t2 = ImageTk.PhotoImage(Image.fromarray(coronales[depth]))
    
    cv1.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=axial_t2, tags="axial_t2")
    cv2.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=coronal_t2, tags="coronal_t2")
    cv2.delete("slice_marker")
    cv2.create_line(CV_W.get()/2-coronal_t2.width()/2, num*factor+CV_H.get()/2-coronal_t2.height()/2, coronal_t2.width()/2+CV_W.get()/2, num*factor+CV_H.get()/2-coronal_t2.height()/2, fill="#2DD", tags="slice_marker")
    cv2.create_line(CV_W.get()/2-coronal_t2.width()/2, (num+1)*factor+CV_H.get()/2-coronal_t2.height()/2, coronal_t2.width()/2+CV_W.get()/2, (num+1)*factor+CV_H.get()/2-coronal_t2.height()/2, fill="#2DD", tags="slice_marker")
    cv2.delete("cv2_info")
    cv2.create_text(80,20,text="Axial/height: "+str(num+1),fill="#2CC",font=("Roboto", 12),tags="cv2_info")
    cv2.create_text(80,40,text="Coronal/depth: "+str(depth+1),fill="#2CC",font=("Roboto", 12),tags="cv2_info")

## HERRAMIENTAS
def square_gen():
    root.config(cursor="tcross")
    root.bind('<Button-1>', start_square)
    root.bind('<B1-Motion>', temp_square)
    root.bind('<ButtonRelease-1>', finish_square)
def start_square(event):
    global x0, y0
    #cv.delete("temp_square","square","temp_text_s")
    x0, y0 = event.x, event.y
def temp_square(event):
    cv.delete("temp_square","temp_text_s")
    cv.create_line(x0,y0,event.x,y0,fill="#A00",dash=(7,),tags="temp_square")
    cv.create_line(x0,y0,x0,event.y,fill="#A00",dash=(7,),tags="temp_square")
    cv.create_line(event.x,y0,event.x,event.y,fill="#A00",dash=(7,),tags="temp_square")
    cv.create_line(x0,event.y,event.x,event.y,fill="#A00",dash=(7,),tags="temp_square")
    dx = event.x-x0
    dy = event.y-y0
    a = 0
    b = 0
    if dx>0: a = -10
    else: a = 10
    if dy>0: b = -10
    else: b = 10
    cv.create_text((event.x+x0)/2,y0+b,text=str(abs(round(px_info_var[0]*dx,2)))+"mm",fill="#F00",font=("Roboto", 9),tags="temp_text_s")
    cv.create_text(x0+a,(event.y+y0)/2,text=str(abs(round(px_info_var[1]*dy,2)))+"mm",fill="#F00",font=("Roboto", 9),tags="temp_text_s",angle=90)
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
    #cv.delete("temp_circle","circle","temp_text")
    x0, y0 = event.x, event.y
def temp_circle(event):
    cv.delete("temp_circle","temp_text_c")
    dx = abs(event.x-x0)
    dy = abs(event.y-y0)
    r = math.sqrt(dx**2+dy**2)
    r_real = math.sqrt((dx*px_info_var[0])**2+(dy*px_info_var[1])**2) # Porq distancia real depende del ancho de pixel en cada dirección.
    cv.create_oval(x0-r,y0-r,x0+r,y0+r,outline="#A00",dash=(7,),tags="temp_circle")
    cv.create_text(x0,y0+r+10,text="r: "+str(round(r_real,2))+"mm",fill="#F00",font=("Roboto", 9),tags="temp_text_c")
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
    #cv.delete("temp_ruler","medicion","temp_text_r")
    x0, y0 = event.x, event.y
def temp_ruler(event):
    
    cv.delete("temp_ruler","temp_text_r")
    cv.create_line(x0,y0,event.x,event.y,fill="#1BB",dash=(3,),arrow=BOTH,tags="temp_ruler")
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
    r_real = math.sqrt((dx*px_info_var[0])**2+(dy*px_info_var[1])**2)
    cv.create_text((event.x+x0)/2+a,(event.y+y0)/2+b,text=str(round(r_real,2))+"mm",fill="#2CC",font=("Roboto", 9),tags="temp_text_r",angle=ang)
def finish_ruler(event):
    global x1, y1
    x1, y1 = event.x, event.y
    if x1 == x0 and y1 == y0:
        print("NO SUELTE EL MOUSE")
        return
    cv.create_line(x0,y0,x1,y1,fill="#2CC",arrow=BOTH,tags="medicion")
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
CV_W = IntVar(value=0)
CV_H = IntVar(value=0)
focused_cv = 0

#MAIN WINDOW DISPLAY

windows_creator()
menu_creator()

root.mainloop()