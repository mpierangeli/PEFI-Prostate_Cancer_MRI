from tkinter import *
from PIL import Image,ImageTk
from tkinter import filedialog
import pydicom
import cv2 as opencv
import numpy as np
import math
import imutils


def windows_creator():

    global main_frame, bot_frame

    main_frame = Frame(root, width=MF_W.get(), height=MF_H.get(), background="#222") # 20 de botframe 20 menu 20 windows tab 40 windows taskbar
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
    global cv1,cv2,cv3,cv4, focused_cv
    focused_cv = 0
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
    cv1.bind("<Leave>", unfocus_cv)
    cv2.bind("<Leave>", unfocus_cv)
    cv3.bind("<Leave>", unfocus_cv)
    cv4.bind("<Leave>", unfocus_cv)

    cv1.bind("<Control-MouseWheel>", slice_selection)
    cv3.bind("<Control-MouseWheel>", slice_selection)  
    cv4.bind("<Control-MouseWheel>", slice_selection)
    cv2.bind("<Control-MouseWheel>", depth_selection)

    cv1.bind("<Button-3>", zoom_gen)

    root.bind("<F3>",clear_cv)
    root.bind("<F4>",reset_cv)
    root.bind("<Control-z>",go_back_1)
    patient_loader()

def go_back_1(event):
    temp_cv = obj_master[-1].incv
    temp_cv.delete(obj_master[-1].name)
    obj_master.pop()

def zoom_gen (event):
    global xi,yi
    root.config(cursor="tcross")
    xi,yi = event.x,event.y
    cv.bind('<B3-Motion>', temp_zoom)
    cv.bind('<ButtonRelease-3>', finish_zoom)
def temp_zoom(event):
    cv.delete("temp_zoom","temp_text_z")
    cv.create_line(xi,yi,event.x,yi,fill="#0F0",dash=(3,),tags="temp_zoom")
    cv.create_line(xi,yi,xi,event.y,fill="#0F0",dash=(3,),tags="temp_zoom")
    cv.create_line(event.x,yi,event.x,event.y,fill="#0F0",dash=(3,),tags="temp_zoom")
    cv.create_line(xi,event.y,event.x,event.y,fill="#0F0",dash=(3,),tags="temp_zoom")
    cv.create_text((event.x+xi)/2,yi-10,text="zoom in",fill="#0F0",font=("Roboto", 9),tags="temp_text_z")
def finish_zoom(event):
    global xf, yf, xi, yi, zoomed
    xf, yf = event.x, event.y
    root.config(cursor="arrow")
    if xf == xi or yf == yi:
        print("NO SUELTE EL MOUSE")
        return
    cv.delete("temp_zoom","temp_text_z")
    #correciones a xi,yi,xf,yf segun posicion en canvas
    if xf < xi: xi, xf = xf, xi
    if yf < yi: yi, yf = yf, yi
    
    xi = int(xi-(CV_W.get()-axial_t2.width())/2)
    xf = int(xf-(CV_W.get()-axial_t2.width())/2)
    yi = int(yi-(CV_H.get()-axial_t2.height())/2)
    yf = int(yf-(CV_H.get()-axial_t2.height())/2)       # CAMBIAR AXIAL POR MENU PARA CADA CANVAS 
    zoomed = True
    set_img(slice_num,depth_num)
    cv.old_coords = None

def clear_cv (event):
    global obj_master
    for obj in obj_master:                                      # CON ESTO BORRO EL CANVAS PERO NO EL OBJETO
        if obj.incv == cv:
            cv.delete(obj.name)
    obj_master = [obj for obj in obj_master if obj.incv != cv]  # CON ESTO BORRO EL OBJETO PERO NO EL CANVAS
def focus_cv(event,arg):
    global cv
    cv = arg
    cv.create_text(50,CV_H.get()-20,text="FOCUSED",font=("Roboto",5),fill="#FFF",tag="focus_check")
def unfocus_cv(event):
    cv.delete("focus_check")
def reset_cv(event):
    global zoomed
    zoomed = False
    set_img(slice_num,depth_num)

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
    global filepaths, axiales, coronales, slice_num, depth_num, factor, init_dcm, init_img, px_info_var, px_info_static, zoomed, obj_master

    #GENERO CONTAINER DE OBJETOS VERVERVER
    obj_master = []

    filepaths = filedialog.askopenfilenames()
    filepaths = list(filepaths)
    
    #-------------------------------------------------
    #GENERO PLANO CORONAL CON IMAGENES T2 (VER COMO SELECCIONAR ESAS EN PARTICULAR)
    init_dcm = pydicom.dcmread(filepaths[0])
    init_img = init_dcm.pixel_array

    px_info_static = [float(init_dcm[0x0028,0x0030].value[0]),float(init_dcm[0x0028,0x0030].value[1])]
    px_info_var = [float(init_dcm[0x0028,0x0030].value[0]),float(init_dcm[0x0028,0x0030].value[1])]
    axiales = np.zeros((len(filepaths),init_img.shape[0],init_img.shape[1]))
    factor = int(init_dcm[0x0018, 0x0050].value/px_info_static[0])
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
    zoomed = False
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
    i4 = Label(info_tab, text="FOV = "+str(int(init_img.shape[1]*px_info_static[0]))+"x"+str(int(init_img.shape[0]*px_info_static[1]))+" [mm x mm]",bg="#222",font=("Roboto",9),fg="#FFF").grid(row=6,column=0,pady=(0,10))
    ##si la secuencia es 2d o 3d cambia el slice thickness:
    if init_dcm[0x0018,0x0023].value == "2D":
        ST = round(init_dcm[0x0018, 0x0050].value*(1+init_dcm[0x0018, 0x0088].value/100),1)
    elif init_dcm[0x0018,0x0023].value == "3D":
        ST = round(init_dcm[0x0018, 0x0050].value,1)
    else:
        ST = 1000000
    i5 = Label(info_tab, text="Slice Thickness = "+str(ST)+"mm",bg="#222",font=("Roboto",9),fg="#FFF").grid(row=7,column=0,pady=(0,10))

    root.bind("<F1>",info_tab_destroy)
def info_tab_destroy(event):
    info_tab.destroy()
    root.bind("<F1>",info_tab_gen)

def set_img(slice,depth):
    global cv,cv1,cv2,cv3,cv4,axial_t2,coronal_t2, xcf_axial_t2, ycf_axial_t2, xcf_coronal_t2, ycf_coronal_t2, px_info_var, xi,yi,xf,yf
    
    temp_axial_t2 = imutils.resize(axiales[slice], height=CV_H.get())
    init_width = temp_axial_t2.shape[1]
    xcf_axial_t2 = axiales[slice].shape[0]/temp_axial_t2.shape[0] #x factor correction -> por el resize inicial
    ycf_axial_t2 = axiales[slice].shape[1]/temp_axial_t2.shape[1] #y factor correction -> por el resize inicial
    if zoomed:
        crop = temp_axial_t2[yi:yf,xi:xf]
        if (abs(yf-yi) >= abs(xf-xi)):
            temp_axial_t2 = imutils.resize(crop, height=CV_H.get())     #CORREGIR ZOOM PARA CORTES SEMI-CUADRADOS
        else:
            temp_axial_t2 = imutils.resize(crop, width=CV_W.get())
        xcf_axial_t2 *= crop.shape[0]/temp_axial_t2.shape[0] #x factor correction -> por el resize inicial
        ycf_axial_t2 *= crop.shape[1]/temp_axial_t2.shape[1] #y factor correction -> por el resize inicial
        

    temp_coronal_t2 = imutils.resize(coronales[depth], width=init_width) # ver error aca con el resize y el muestro en iamgen
    xcf_coronal_t2 = coronales[depth].shape[0]/temp_coronal_t2.shape[0] #x factor correction -> por el resize
    ycf_coronal_t2 = coronales[depth].shape[1]/temp_coronal_t2.shape[1] #y factor correction -> por el resize
    
    axial_t2 = ImageTk.PhotoImage(Image.fromarray(temp_axial_t2))
    coronal_t2 = ImageTk.PhotoImage(Image.fromarray(temp_coronal_t2))
    
    
    px_info_var = [float(init_dcm[0x0028,0x0030].value[0])*xcf_axial_t2,float(init_dcm[0x0028,0x0030].value[1])*ycf_axial_t2]

    
    cv1.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=axial_t2, tags="axial_t2")
    cv2.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=coronal_t2, tags="coronal_t2")
    cv2.delete("slice_marker")
    cv2.create_line(CV_W.get()/2-coronal_t2.width()/2, slice*factor/ycf_coronal_t2+CV_H.get()/2-coronal_t2.height()/2, coronal_t2.width()/2+CV_W.get()/2, slice*factor/ycf_coronal_t2+CV_H.get()/2-coronal_t2.height()/2, fill="#2DD", tags="slice_marker")
    cv2.create_line(CV_W.get()/2-coronal_t2.width()/2, (slice+1)*factor/ycf_coronal_t2+CV_H.get()/2-coronal_t2.height()/2, coronal_t2.width()/2+CV_W.get()/2, (slice+1)*factor/ycf_coronal_t2+CV_H.get()/2-coronal_t2.height()/2, fill="#2DD", tags="slice_marker")
    cv2.delete("cv2_info")
    cv2.create_text(80,20,text="Axial/height: "+str(slice+1),fill="#2CC",font=("Roboto", 12),tags="cv2_info")
    cv2.create_text(80,40,text="Coronal/depth: "+str(depth+1),fill="#2CC",font=("Roboto", 12),tags="cv2_info")

## HERRAMIENTAS
def square_gen():
    root.config(cursor="tcross")
    root.bind('<Button-1>', start_square)
    root.bind('<B1-Motion>', temp_square)
    root.bind('<ButtonRelease-1>', finish_square)
def start_square(event):
    obj_master.append(1)
    obj_master[-1] = roi_square("s"+str(len(obj_master)),cv)
    obj_master[-1].init_coord(event.x,event.y)
def temp_square(event):
    obj_master[-1].end_coord(event.x,event.y)
    obj_master[-1].draw(True)
def finish_square(event):
    if obj_master[-1].xi == event.x or obj_master[-1].yi == event.y:
        print("NO SUELTE EL MOUSE")
        obj_master.pop()
        return
    obj_master[-1].end_coord(event.x,event.y)
    obj_master[-1].draw(False)
    root.config(cursor="arrow")
    root.unbind('<Button-1>')
    root.unbind('<B1-Motion>')
    root.unbind('<ButtonRelease-1>')

## OBJETOS
class roi_square:
    def __init__(self,name,incv):
        self.name = name
        self.incv = incv
    def init_coord(self,xi,yi):
        self.xi = xi
        self.yi = yi
    def end_coord(self,xf,yf):
        self.xf = xf
        self.yf = yf
    def draw(self,temporal):
        cv.delete(self.name)
        if temporal:
            cv.create_rectangle(self.xi,self.yi,self.xf,self.yf,outline="#A00",tags=self.name,dash=(7,))
        else:
            self.name = self.name + "_"
            cv.create_rectangle(self.xi,self.yi,self.xf,self.yf,outline="#F00",tags=self.name)
        dx = self.xf-self.xi
        dy = self.yf-self.yi
        a = -10 if dx>0 else 10
        b = -10 if dy>0 else 10
        self.xdis = abs(round(px_info_var[0]*dx,2))
        self.ydis = abs(round(px_info_var[1]*dy,2))
        cv.create_text((self.xf+self.xi)/2,self.yi+b,text=str(self.xdis)+"mm",fill="#F00",font=("Roboto", 9),tags=self.name)
        cv.create_text(self.xi+a,(self.yf+self.yi)/2,text=str(self.ydis)+"mm",fill="#F00",font=("Roboto", 9),tags=self.name,angle=90)

#-------------- MAIN LOOP ---------------------------------------------------------

root = Tk()
root.title("S A U R U S")
root.config(bg="#F00") #para debug
root.iconbitmap("unsam.ico")

# GLOBAL VARIABLES
MF_W = IntVar(value=1920)
MF_H = IntVar(value=980)
CV_W = IntVar(value=0)
CV_H = IntVar(value=0)

#MAIN WINDOW DISPLAY
windows_creator()
menu_creator()

root.mainloop()

#------------------------------------------------------------------------------