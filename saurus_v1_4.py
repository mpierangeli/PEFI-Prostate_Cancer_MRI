from tkinter import *
from PIL import Image, ImageTk#, ImageGrab
from tkinter import filedialog
import pydicom
import numpy as np
import math
import imutils
import os
import cv2

## OBJETOS

class roi_square:
    def __init__(self, name, sec):
        self.name = name
        self.insec = sec
        self.inslice = sec.slice
    def init_coord(self,xi,yi):
        self.xi = xi
        self.yi = yi
    def end_coord(self,xf,yf):
        self.xf = xf
        self.yf = yf
        self.dx = self.xf-self.xi
        self.dy = self.yf-self.yi
    def draw(self,temporal):
        cv.delete(self.name)
        if temporal:
            cv.create_rectangle(self.xi,self.yi,self.xf,self.yf,outline="#A00",tags=self.name,dash=(7,))
        else:
            self.name = self.name + "_"
            cv.create_rectangle(self.xi,self.yi,self.xf,self.yf,outline="#F00",tags=self.name)
        a = -10 if self.dx>0 else 10
        b = -10 if self.dy>0 else 10
        self.xdis = abs(round(self.insec.realx*self.dx,2))
        self.ydis = abs(round(self.insec.realy*self.dy,2))
        cv.create_text((self.xf+self.xi)/2,self.yi+b,text=str(self.xdis)+"mm",fill="#F00",font=("Roboto", 9),tags=self.name)
        cv.create_text(self.xi+a,(self.yf+self.yi)/2,text=str(self.ydis)+"mm",fill="#F00",font=("Roboto", 9),tags=self.name,angle=90)
class roi_circle:
    def __init__(self,name,sec):
        self.name = name
        self.insec = sec
        self.inslice = sec.slice
    def init_coord(self,xi,yi):
        self.xi = xi
        self.yi = yi
    def end_coord(self,xf,yf):
        self.dx = abs(xf-self.xi)
        self.dy = abs(yf-self.yi)
        self.r = math.sqrt(self.dx**2+self.dy**2)
    def draw(self,temporal):
        cv.delete(self.name)
        if temporal:
            cv.create_oval(self.xi-self.r,self.yi-self.r,self.xi+self.r,self.yi+self.r,outline="#A00",dash=(7,),tags=self.name)
        else:
            self.name = self.name + "_"
            cv.create_oval(self.xi-self.r,self.yi-self.r,self.xi+self.r,self.yi+self.r,outline="#F00",tags=self.name)
        self.rdis = math.sqrt((self.dx*self.insec.realx)**2+(self.dy*self.insec.realy)**2) # Porq distancia real depende del ancho de pixel en cada dirección.
        cv.create_text(self.xi,self.yi+self.r+10,text="r: "+str(round(self.rdis,2))+"mm",fill="#F00",font=("Roboto", 9),tags=self.name)
class roi_ruler:
    def __init__(self,name,sec):
        self.name = name
        self.insec = sec
        self.inslice = sec.slice
    def init_coord(self,xi,yi):
        self.xi = xi
        self.yi = yi
    def end_coord(self,xf,yf):
        self.xf = xf
        self.yf = yf
        self.dx = self.xf-self.xi
        self.dy = self.yf-self.yi
    def draw(self,temporal):
        cv.delete(self.name)
        if temporal:
            cv.create_line(self.xi,self.yi,self.xf,self.yf,fill="#1BB",dash=(3,),arrow=BOTH,tags=self.name)
        else:
            self.name = self.name + "_"
            cv.create_line(self.xi,self.yi,self.xf,self.yf,fill="#2CC",arrow=BOTH,tags=self.name)
        self.ang = abs(math.degrees(math.atan((-self.dy)/(-self.dx+1e-6))))
        self.rdis = math.sqrt((self.dx*self.insec.realx)**2+(self.dy*self.insec.realy)**2) # Porq distancia real depende del ancho de pixel en cada dirección.
        a = 10
        b = 10
        if int(self.dx) == 0: b -= 10
        elif int(self.dy) == 0: a -= 10
        elif self.dx*self.dy > 0: 
            self.ang = -self.ang
            a -= 20
        cv.create_text((self.xf+self.xi)/2+a,(self.yf+self.yi)/2+b,text=str(round(self.rdis,2))+"mm",fill="#2CC",font=("Roboto", 9),tags=self.name,angle=self.ang)
class secuencia:
    def __init__(self,name):
        self.name = name    # nombre de secuencia -> name+TE+TR+Modes
        self.dcm_serie = [] # serie de dicoms pertenecientes al mismo UID
        self.incv = 0       # en que cv la quiero mostrar
        self.width = 0      # w del pixel_array de las dicom
        self.height = 0     # h del pixel_array de las dicom
        self.incv_width = 0     # w en que estoy mostrando la secuencia
        self.incv_height = 0    # h en que estoy mostrando la secuencia
        self.realx = 0      # tamaño en mm del pixel en x
        self.realy = 0      # tamaño en mm del pixel en y
        self.plano = ""     # axial/sagital/coronal/mixto(ver si no conviene separar, borrar secuencia o khe)
        self.isloaded = False   # flag para saber si ya estan cargadas las imagenes de la secuencia
        self.aux_view = False   # False = secuencia de vista original / True = secuencia de vista artificial
    def add_dcm(self,dcm):
        self.dcm_serie.append(dcm)  # serie de dicoms
        if dcm.pixel_array.shape[0] > self.height: self.height = dcm.pixel_array.shape[0] 
        if dcm.pixel_array.shape[1] > self.width: self.width = dcm.pixel_array.shape[1]
    def load_img_serie(self,*kwargs):
        self.isloaded = True
        if not self.aux_view:
            self.depth = len(self.dcm_serie)    # cantidad de slices de la secuencia
            self.img_serie = np.zeros((self.depth,self.height,self.width))  # serie de imagenes
            planos = [0,0,0] # [axial,sagital,coronal]
            for n, dcm in enumerate(self.dcm_serie):
                try:
                    self.img_serie[n] = dcm.pixel_array
                except: # en caso de que las imagenes no sean del mismo tamaño, paddeo con 0s y asigno un cachito
                    self.img_serie[n,int((self.width-dcm.pixel_array.shape[0])/2):int((self.width-dcm.pixel_array.shape[0])/2)+dcm.pixel_array.shape[0],int((self.height-dcm.pixel_array.shape[1])/2):int((self.height-dcm.pixel_array.shape[1])/2)+dcm.pixel_array.shape[1]] = dcm.pixel_array
                codif = [round(n) for n in dcm.ImageOrientationPatient]
                if  codif == [1, 0, 0, 0, 1, 0]: planos[0] += 1
                elif codif == [0, 1, 0, 0, 0, -1]: planos[1] += 1
                elif codif == [1, 0, 0, 0, 0, -1]: planos[2] += 1
            if planos[1] == 0 and planos[2] == 0: self.plano = "axial"
            elif planos[0] == 0 and planos[2] == 0: self.plano = "sagital"
            elif planos[0] == 0 and planos[1] == 0: self.plano = "coronal"
            else: self.plano = "mixta"
        else:
            self.parent,tipo = kwargs   # parent es la secuencia a la que le hago la vista artificial
            self.factor = int(self.parent.dcm_serie[0].SliceThickness/self.parent.dcm_serie[0].PixelSpacing[0]) # cantidad de pixeles q tengo q poner por tomo para llenar el ST
            
            if tipo == "atos":
                self.depth = self.parent.img_serie.shape[2]
                self.width = self.parent.img_serie.shape[1]
                self.height = self.factor*self.parent.img_serie.shape[0]
                self.img_serie = np.zeros((self.depth,self.height,self.width))
                for i in range(self.depth): # por cada columna de las axiales -> profundidad de la sagital
                    for j in range(self.parent.img_serie.shape[0]): # por cada imagen axial -> altura de la sagital
                        for k in range(self.factor): # por ancho de tomo axial, repito misma muestra
                            self.img_serie[i,j*self.factor+k] = self.parent.img_serie[j,:,i]
                self.realx = self.parent.realy
                self.realy = self.realx
            elif tipo == "atoc":
                self.depth = self.parent.img_serie.shape[1]
                self.width = self.parent.img_serie.shape[2]
                self.height = self.factor*self.parent.img_serie.shape[0]
                self.img_serie = np.zeros((self.depth,self.height,self.width))
                for i in range(self.parent.img_serie.shape[1]): # por cada fila de las axiales -> profundidad de la coronal
                    for j in range(self.parent.img_serie.shape[0]): # por cada imagen axial -> altura de la coronal
                        for k in range(self.factor): # por ancho de tomo axial, repito misma muestra
                            self.img_serie[i,j*self.factor+k] = self.parent.img_serie[j,i,:]
                self.realx = self.parent.realx
                self.realy = self.realx
            elif tipo == "stoa":
                pass
            elif tipo == "stoc":
                pass
            elif tipo == "ctoa":
                pass
            elif tipo == "ctos":
                pass
                
        self.slice = int(self.depth/2)    # en que slice tengo posicionada la secuencia para mostrarla
        self.img_serie_cte = np.zeros((self.depth,self.img_serie.shape[1],self.img_serie.shape[2]))  # serie de imagenes
        
        if self.aux_view:   self.alpha = 1    # parametro de contraste
        else:               self.alpha = 0.15 
        self.beta = 0       # parametro de brillo
            
        for n in range(self.depth):
            self.img_serie_cte[n] = self.img_serie[n]
            if not self.aux_view:
                self.img_serie[n] = cv2.convertScaleAbs(self.img_serie_cte[n], alpha=self.alpha, beta=self.beta)
        
    def adjust_img_serie(self,a,b):
        self.alpha += a
        self.beta += b
        for n in range(self.depth):
            self.img_serie[n] = cv2.convertScaleAbs(self.img_serie_cte[n], alpha=self.alpha, beta=self.beta)
            
## FUNCIONES

def windows_creator():

    global main_frame, bot_frame, info_label

    main_frame = Frame(root, width=MF_W.get(), height=MF_H.get(), background="#222") # 20 de botframe 20 menu 20 windows tab 40 windows taskbar
    main_frame.grid(row=1, column=0)
    main_frame.grid_propagate(0)

    bot_frame = Frame(root, width=MF_W.get(), height=20, background="#2CC")
    bot_frame.grid(row=2, column=0)
    bot_frame.grid_propagate(0)

    info_label = Label(bot_frame, textvariable=info_text,bg="#2CC",font=("Roboto",9),fg="#000").grid(row=0,column=0,padx=10)

def menu_creator():
    
    menubar = Menu(root)
    root.config(menu=menubar)

    filemenu = Menu(menubar, tearoff = 0)
    filemenu.add_command(label="Selección Paciente", command=patient_loader)
    filemenu.add_separator()
    filemenu.add_command(label="Panel de Secuencias", command=sec_selector)
    
    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="ROI Rectangular",command=lambda tipo="s": roi_gen(tipo))
    editmenu.add_command(label="ROI Circular",command=lambda tipo="c": roi_gen(tipo))
    editmenu.add_command(label="Medición",command=lambda tipo="r": roi_gen(tipo))

    reportmenu = Menu(menubar, tearoff = 0)
    reportmenu.add_command(label="Nuevo Reporte")

    helpmenu = Menu(menubar, tearoff = 0)
    helpmenu.add_command(label="Keybinds")
    helpmenu.add_command(label="Acerca de...")
    helpmenu.add_separator()
    helpmenu.add_command(label="Salir", command=root.quit)

    global layoutmenu
    layoutmenu = Menu(root, tearoff = 0)
    layoutmenu.add_command(label="1x1",command=lambda layout=1: canvas_creator(layout))
    layoutmenu.add_command(label="1x2",command=lambda layout=2: canvas_creator(layout))
    layoutmenu.add_command(label="2x2",command=lambda layout=4: canvas_creator(layout))
    displaymenu = Menu(menubar, tearoff = 0)
    displaymenu.add_cascade(label="Layout", menu = layoutmenu)
    displaymenu.add_separator()
    displaymenu.add_checkbutton(label="Información ON/OFF", onvalue=True, offvalue=False, variable=info_cv)
    displaymenu.add_checkbutton(label="AXIS ON/OFF", onvalue=True, offvalue=False, variable=axis_cv)
    
    menubar.add_cascade(label="Abrir", menu=filemenu)
    menubar.add_cascade(label="Pantalla", menu=displaymenu)
    menubar.add_cascade(label="Herramientas", menu=editmenu)
    menubar.add_cascade(label="Reportar", menu=reportmenu)
    menubar.add_cascade(label="Ayuda", menu=helpmenu)
    
    global portablemenu
    portablemenu = Menu(root, tearoff = 0)
    
    #portablemenu.add_command(label = "zoom? VER")
    
    portableeditmenu = Menu(portablemenu, tearoff = 0)
    portableeditmenu.add_command(label = "Rectangular", command = lambda tipo="s": roi_gen(tipo))
    portableeditmenu.add_command(label = "Circular", command = lambda tipo="c": roi_gen(tipo))
    portablemenu.add_cascade(label = "ROIs", menu = portableeditmenu)
    portablemenu.add_command(label = "Medición", command = lambda tipo="r": roi_gen(tipo))
    portablemenu.add_separator()
    portableviewmenu = Menu(portablemenu, tearoff = 0)
    portableviewmenu.add_command(label = "Sagital", command = lambda tipo="s": view_sec_gen(tipo))
    portableviewmenu.add_command(label = "Coronal", command = lambda tipo="c": view_sec_gen(tipo))
    portableviewmenu.add_command(label = "Axial", command = lambda tipo="a": view_sec_gen(tipo))
    portablemenu.add_cascade(label = "Agregar Vista", menu = portableviewmenu)
    portablemenu.add_separator()
    portablemenu.add_command(label = "Metadata", command = info_tab_gen)
    portablemenu.add_command(label = "Limpiar", command = clear_cv)
    portablemenu.add_command(label = "Cargar Secuencia", command = sec_selector)
    

def canvas_creator(layout: int):
    global cv_master, img2cv, info_switch
    img2cv = [0,0,0,0]
    try:
        for temp_cv in cv_master:
            temp_cv.destroy()
    except:
        pass
    for sec in secuencias:
        sec.incv = 0 # VER ESTO
    cv_master = []

    match layout:   # VER DE SACAR ESTO SI FUERZA A USAR python 3.10
        case 1:
            CV_W.set(MF_W.get()-40)
            CV_H.set(MF_H.get()-40)
            cv_master.append(Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0))
            cv_master[0].grid(row=0,column=0,padx=20,pady=20)
        case 2:
            CV_W.set(int(MF_W.get()/2)-10)
            CV_H.set(MF_H.get()-40)
            for n in range(layout):
                cv_master.append(Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0))
            cv_master[0].grid(row=0,column=0,padx=(0,10),pady=20)
            cv_master[1].grid(row=0,column=1,padx=(10,0),pady=20)        
        case 4:
            CV_W.set(int(MF_W.get()/2)-5)
            CV_H.set(int(MF_H.get()/2)-5)
            for n in range(layout):
                cv_master.append(Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0))
            cv_master[0].grid(row=0,column=0,padx=(0,5),pady=(0,5))
            cv_master[1].grid(row=0,column=1,padx=(5,0),pady=(0,5))
            cv_master[2].grid(row=1,column=0,padx=(0,5),pady=(5,0))
            cv_master[3].grid(row=1,column=1,padx=(5,0),pady=(5,0))

    for temp_cv in cv_master:
        temp_cv.bind("<Enter>",lambda event, arg=temp_cv: focus_cv(event,arg))
        temp_cv.bind("<Leave>", unfocus_cv)
        temp_cv.bind("<Button-3>", popupmenu)

# CONTROLES DE USUARIO
    root.bind("<Control-MouseWheel>", slice_selector)
    root.bind("<Control-z>",go_back_1)
    root.bind("<Right>",lambda event, arg="c+": bnc(event,arg))
    root.bind("<Left>",lambda event, arg="c-": bnc(event,arg))
    root.bind("<Up>",lambda event, arg="b+": bnc(event,arg))
    root.bind("<Down>",lambda event, arg="b-": bnc(event,arg))
    
    
def clear_cv ():
    global obj_master
    for obj in obj_master:                                      # CON ESTO BORRO EL CANVAS PERO NO EL OBJETO
        if obj.insec.incv == cv:
            obj.insec.incv.delete(obj.name)
    obj_master = [obj for obj in obj_master if obj.insec.incv != cv]  # CON ESTO BORRO EL OBJETO PERO NO EL CANVAS
def focus_cv(event, arg: Canvas):
    global cv
    cv = arg
    cv.create_text(50,CV_H.get()-20,text="FOCUSED",font=("Roboto",5),fill="#FFF",tag="focus_check")
    if info_cv.get(): 
        for sec in secuencias:
            if sec.incv == cv:
                info_cv_gen(sec)
                break
def unfocus_cv(event):
    cv.delete("focus_check","cv_info")

def info_cv_gen(sec: secuencia):
    sec.incv.delete("focus_check","cv_info")
    if sec.aux_view:
        sec.incv.create_text(10,20,text="Seq. Name: "+sec.parent.dcm_serie[0].SequenceName+"_artificial",font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,40,text="Orientation: "+sec.plano,font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,60,text="Slice: "+str(sec.slice+1)+"/"+str(sec.depth),font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,80,text="Img. size: "+str(sec.width)+"x"+str(sec.height)+" px.",font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,100,text="FoV: "+str(int(sec.width*sec.parent.dcm_serie[0].PixelSpacing[1]))+"x"+str(int(sec.height*sec.parent.dcm_serie[0].PixelSpacing[0]))+" mm2",font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,120,text="TE: "+str(sec.parent.dcm_serie[0].EchoTime)+" ms",font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,140,text="TR: "+str(sec.parent.dcm_serie[0].RepetitionTime)+" ms",font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,160,text="ST: "+str(sec.parent.dcm_serie[0].SliceThickness)+" mm (parent)",font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
    else:
        sec.incv.create_text(10,20,text="Seq. Name: "+sec.dcm_serie[0].SequenceName,font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,40,text="Orientation: "+sec.plano,font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,60,text="Slice: "+str(sec.slice+1)+"/"+str(sec.depth),font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,80,text="Img. size: "+str(sec.width)+"x"+str(sec.height)+" px.",font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,100,text="FoV: "+str(int(sec.width*sec.dcm_serie[0].PixelSpacing[1]))+"x"+str(int(sec.height*sec.dcm_serie[0].PixelSpacing[0]))+" mm2",font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,120,text="TE: "+str(sec.dcm_serie[0].EchoTime)+" ms",font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,140,text="TR: "+str(sec.dcm_serie[0].RepetitionTime)+" ms",font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,160,text="ST: "+str(sec.dcm_serie[0].SliceThickness)+" mm",font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
                
def popupmenu(event):
    try:
        portablemenu.tk_popup(event.x_root, event.y_root)
    finally:
        portablemenu.grab_release()

def go_back_1(event):
    obj_master[-1].insec.incv.delete(obj_master[-1].name)
    obj_master.pop()

def patient_loader():
    global secuencias, obj_master
    
    filepath = filedialog.askdirectory()
    if not filepath: return
    
    # MASTER DE SECUENCIAS CARGADAS
    secuencias = []
    # auxiliar de secuencias
    sec_uids = []
    # MASTER DE DIBUJOS
    obj_master = []
    # MASTER DE OBSERVACIONES PARA REPORTE
    #observations = []
    
    for file in sorted(os.listdir(filepath)):
        name, ext = os.path.splitext(file)
        if ext == ".IMA":
            temp_dcm = pydicom.dcmread(filepath+"/"+file)
            temp_uid = temp_dcm.SeriesInstanceUID
            if  temp_uid not in sec_uids:
                secuencias.append(secuencia(temp_dcm.SequenceName+"-> TE: "+str(temp_dcm.EchoTime)+", TR: "+str(temp_dcm.RepetitionTime)+", "+str(temp_dcm.ScanOptions)+", UID: "+temp_uid[-4:-1]))
                sec_uids.append(temp_uid)
            secuencias[-1].add_dcm(temp_dcm)
    canvas_creator(1)
    sec_selector()              

def sec_selector():
    global seq_tab,sec_list

    seq_tab = Frame(root,background="#2CC")
    seq_tab.place(relx=0,rely=0, height=MF_H.get())
    Label(seq_tab, text="SECUENCIAS DISPONIBLES",bg="#2CC",font=("Roboto",12),fg="#000").grid(row=0,column=0,pady=20)

    sec_list = Listbox(seq_tab, height=100, width=50, relief=FLAT, bg="#2CC",font=("Roboto",9), fg="#000",selectbackground="#222",highlightthickness=0)
    sec_list.grid(row=1,column=0,padx=10)
    for sec in secuencias:
        if not sec.aux_view:
            sec_list.insert(END,sec.name)
    seq_tab.bind('<Leave>', sec_move)
def sec_move(event):
    seq = sec_list.get(ANCHOR)
    seq_tab.destroy()
    root.config(cursor="plus")
    root.bind('<Button-1>', lambda event, seq=seq: sec_setup(event, seq))  
def sec_setup(event, sec_name: str):
    for sec in secuencias:
        if sec.incv == cv: sec.incv = 0
        elif sec.name == sec_name:
            if sec.incv != 0: sec.incv.delete(ALL)
            sec.incv = cv
            sec.incv.delete(ALL)
            if not sec.isloaded: sec.load_img_serie()
            refresh_canvas(sec)
    root.config(cursor="arrow")
    root.unbind('<Button-1>')

def refresh_canvas(sec: secuencia):
    global img2cv
    layout = len(cv_master)
   
    if not sec.aux_view:
        if layout == 2:
            temp_img = imutils.resize(sec.img_serie[sec.slice], width=CV_W.get())
        else:
            temp_img = imutils.resize(sec.img_serie[sec.slice], height=CV_H.get())
        sec.realx = sec.dcm_serie[0].PixelSpacing[0]*sec.width/temp_img.shape[1]
        sec.realy = sec.dcm_serie[0].PixelSpacing[1]*sec.height/temp_img.shape[0]  
    else:
        if sec.parent.plano == "axial" and sec.plano == "sagital": 
            temp_width = sec.parent.incv_height
        if sec.parent.plano == "axial" and sec.plano == "coronal": 
            temp_width = sec.parent.incv_width
        temp_img = imutils.resize(sec.img_serie[sec.slice], width=temp_width)
    sec.incv_height = temp_img.shape[0]
    sec.incv_width =  temp_img.shape[1]
        
    
    if layout == 1: img2cv = [0,0,0,0]
    img2cv_master(sec,temp_img)
    
    # REDIBUJO LOS OBJETOS GUARDADOS EN LOS CANVAS
    for obj in obj_master:
        if obj.insec == sec and obj.inslice == sec.slice:
            obj.draw(False)
            
    if info_cv.get(): info_cv_gen(sec)
    if axis_cv.get(): axis_gen()
    pos_info(sec)

def img2cv_master(sec: secuencia,temp_img):
    global img2cv
    for n,cvs in enumerate(cv_master):
        if sec.incv == cvs:
            img2cv[n] = ImageTk.PhotoImage(Image.fromarray(temp_img))
            cvs.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=img2cv[n])


def axis_gen():
    
    for sec in secuencias:
        if sec.incv != 0 and sec.aux_view and sec.parent.incv != 0:
            
            if sec.parent.plano == "axial":
                # AXIS AXIAL EN IMAGEN HIJO
                sec.incv.delete("axial_depth_marker")
                offset = CV_H.get()/2-sec.incv_height/2
                sec.incv.create_line(0, int(sec.incv_height*(sec.parent.slice/sec.parent.depth))+offset, CV_W.get(), int(sec.incv_height*(sec.parent.slice/sec.parent.depth))+offset, fill="#2DD", tags="axial_depth_marker")
                sec.incv.create_line(0, int(sec.incv_height*((sec.parent.slice+1)/sec.parent.depth))+offset, CV_W.get(), int(sec.incv_height*((sec.parent.slice+1)/sec.parent.depth))+offset, fill="#2DD", tags="axial_depth_marker")
                
                if sec.plano == "coronal":
                    # AXIS CORONAL EN IMAGEN AXIAL
                    sec.parent.incv.delete("coronal_depth_marker")
                    offset = CV_H.get()/2-sec.parent.incv_height/2
                    sec.parent.incv.create_line(0, int(sec.parent.incv_height*(sec.slice/sec.depth))+offset, CV_W.get(), int(sec.parent.incv_height*(sec.slice/sec.depth))+offset, fill="#F80", tags="coronal_depth_marker")
                    sec.parent.incv.create_line(0, int(sec.parent.incv_height*((sec.slice+1)/sec.depth))+offset, CV_W.get(), int(sec.parent.incv_height*((sec.slice+1)/sec.depth))+offset, fill="#F80", tags="coronal_depth_marker")
                    
                    for sec2 in secuencias:
                        if sec2.aux_view and (sec2.parent == sec.parent) and sec2.plano == "sagital" and (sec != sec2):
                            # AXIS CORONAL EN IMAGEN SAGITAL
                            sec2.incv.delete("coronal_depth_marker")
                            offset = CV_W.get()/2-sec2.incv_width/2
                            sec2.incv.create_line(int(sec2.incv_width*(sec.slice/sec.depth))+offset, 0, int(sec2.incv_width*(sec.slice/sec.depth))+offset, CV_H.get(), fill="#F80", tags="coronal_depth_marker")
                            sec2.incv.create_line(int(sec2.incv_width*((sec.slice+1)/sec.depth))+offset, 0, int(sec2.incv_width*((sec.slice+1)/sec.depth))+offset, CV_H.get(), fill="#F80", tags="coronal_depth_marker") 
                            break 
                            
                if sec.plano == "sagital":
                    # AXIS SAGITAL EN IMAGEN AXIAL
                    sec.parent.incv.delete("sagital_depth_marker")
                    offset = CV_W.get()/2-sec.parent.incv_width/2
                    sec.parent.incv.create_line(int(sec.parent.incv_width*(sec.slice/sec.depth))+offset, 0, int(sec.parent.incv_width*(sec.slice/sec.depth))+offset, CV_H.get(), fill="#5D0", tags="sagital_depth_marker")
                    sec.parent.incv.create_line(int(sec.parent.incv_width*((sec.slice+1)/sec.depth))+offset, 0, int(sec.parent.incv_width*((sec.slice+1)/sec.depth))+offset, CV_H.get(), fill="#5D0", tags="sagital_depth_marker")      

                    for sec2 in secuencias:
                        if sec2.aux_view and (sec2.parent == sec.parent) and sec2.plano == "coronal" and (sec != sec2):
                            # AXIS SAGITAL EN IMAGEN CORONAL
                            sec2.incv.delete("sagital_depth_marker")
                            offset = CV_W.get()/2-sec2.incv_width/2
                            sec2.incv.create_line(int(sec2.incv_width*(sec.slice/sec.depth))+offset, 0, int(sec2.incv_width*(sec.slice/sec.depth))+offset, CV_H.get(), fill="#5D0", tags="sagital_depth_marker")
                            sec2.incv.create_line(int(sec2.incv_width*((sec.slice+1)/sec.depth))+offset, 0, int(sec2.incv_width*((sec.slice+1)/sec.depth))+offset, CV_H.get(), fill="#5D0", tags="sagital_depth_marker")
                            break
                            
def pos_info(sec: secuencia):
    sec.incv.delete("pos_info")
    if sec.plano == "axial":        temp_pos = ["A","P","L","R"] # UP, DOWN , LEFT, RIGHT 
    elif sec.plano == "sagital":    temp_pos = ["S","I","A","P"]
    elif sec.plano == "coronal":    temp_pos = ["S","I","L","R"]
    else:                           temp_pos = ["U","U","U","U"]
    sec.incv.create_text(CV_W.get()/2,10,text=temp_pos[0],fill="#FFF",font=("Roboto", 9),tags="pos_info")
    sec.incv.create_text(CV_W.get()/2,CV_H.get()-10,text=temp_pos[1],fill="#FFF",font=("Roboto", 9),tags="pos_info")
    sec.incv.create_text(10,CV_H.get()/2,text=temp_pos[2],fill="#FFF",font=("Roboto", 9),tags="pos_info")
    sec.incv.create_text(CV_W.get()-10,CV_H.get()/2,text=temp_pos[3],fill="#FFF",font=("Roboto", 9),tags="pos_info")
    
def slice_selector(event):
    for sec in secuencias:
        if sec.incv == cv:
            if event.delta > 0 and sec.slice < sec.depth-1: sec.slice += 1
            elif event.delta < 0 and sec.slice > 0: sec.slice -= 1
            break
    refresh_canvas(sec) 


def info_tab_gen():
    global info_tab
    info = ""
    for sec in secuencias:
        if sec.incv == cv:
            if sec.aux_view: return
            else:
                for item in sec.dcm_serie[sec.slice]:
                    info += (str(item) + "\n")
    info_tab = Frame(root,background="#2CC")
    info_tab.place(relx=0,rely=0, height=MF_H.get())
    Label(info_tab, text="DICOM METADATA",bg="#2CC",font=("Roboto",12),fg="#000").grid(row=0,column=0,pady=10)
    print(cv)
    text_box = Text(info_tab,width=100,height=58,font=("Roboto",10),fg="#000",bg="#2CC",bd=0)
    text_box.grid(row=1, column=0)
    text_box.insert(END,info)
    sb = Scrollbar(info_tab,orient=VERTICAL)
    sb.grid(row=1, column=1, sticky=NS)
    text_box.config(yscrollcommand=sb.set)
    sb.config(command=text_box.yview)
    
    root.bind("<Escape>",info_tab_destroy)
    
def info_tab_destroy(event):
    info_tab.destroy()

def bnc(event,tipo: str):
    for sec in secuencias:
        if sec.incv == cv:
            if tipo == "c+" and sec.alpha < 0.5:
                sec.adjust_img_serie(0.005,0)
                break
            elif tipo == "c-" and sec.alpha >= 0.01:
                sec.adjust_img_serie(-0.005,0)
                break
            elif tipo == "b+" and sec.beta < 100:
                sec.adjust_img_serie(0,5)
                break
            elif tipo == "b-" and sec.beta >= 5:
                sec.adjust_img_serie(0,-5)
                break
    refresh_canvas(sec) 

def view_sec_gen(tipo: str):
    for sec in secuencias:
        if sec.incv == cv:
            if sec.plano == "axial" and (tipo == "s" or tipo == "c"):
                for sec2 in secuencias:
                    if sec2.name == sec.name+"_"+tipo:
                        root.config(cursor="plus")
                        root.bind('<Button-1>', lambda event, seq=sec2.name: sec_setup(event, seq))
                        return
                secuencias.append(secuencia(sec.name+"_"+tipo))
                secuencias[-1].aux_view = True
                if tipo == "s": 
                    secuencias[-1].load_img_serie(sec,"atos")
                    secuencias[-1].plano = "sagital"
                if tipo == "c": 
                    secuencias[-1].load_img_serie(sec,"atoc")
                    secuencias[-1].plano = "coronal"
            # PARA ABAJO NO IMPLEMENTADAS
            elif sec.plano == "sagital"  and (tipo == "a" or tipo == "c"):  
                secuencias.append(secuencia(sec.name+"_"+tipo))
                secuencias[-1].aux_view = True
                if tipo == "a": 
                    secuencias[-1].load_img_serie(sec,"stoa")
                    secuencias[-1].plano = "axial"
                if tipo == "c": 
                    secuencias[-1].load_img_serie(sec,"stoc")
                    secuencias[-1].plano = "coronal"
            elif sec.plano == "coronal"  and (tipo == "a" or tipo == "s"):      
                secuencias.append(secuencia(sec.name+"_"+tipo))
                secuencias[-1].aux_view = True
                if tipo == "a": 
                    secuencias[-1].load_img_serie(sec,"ctoa")
                    secuencias[-1].plano = "axial"
                if tipo == "s": 
                    secuencias[-1].load_img_serie(sec,"ctos")
                    secuencias[-1].plano = "sagital"
            
            root.config(cursor="plus")
            root.bind('<Button-1>', lambda event, seq=secuencias[-1].name: sec_setup(event, seq))  
                
                
## HERRAMIENTAS

#ROI GENERATORS
def roi_gen(tipo: str):
    root.config(cursor="tcross")
    root.bind('<Button-1>', lambda event, arg=tipo: roi_start(event,arg))
    root.bind('<B1-Motion>', roi_temp)
    root.bind('<ButtonRelease-1>', roi_end)
    root.bind("<Escape>", lambda event, arg=False: roi_escape(event,arg))
def roi_start(event,tipo: str):
    root.bind("<Escape>", lambda event, arg=True: roi_escape(event,arg))
    for sec in secuencias:
        if sec.incv == cv:  break
    if tipo == "s":
        obj_master.append(roi_square(tipo+str(len(obj_master)),sec))
    elif tipo == "c":
        obj_master.append(roi_circle(tipo+str(len(obj_master)),sec))
    elif tipo == "r":
        obj_master.append(roi_ruler(tipo+str(len(obj_master)),sec))
    obj_master[-1].init_coord(event.x,event.y)
def roi_temp(event):
    obj_master[-1].end_coord(event.x,event.y)
    obj_master[-1].draw(True)
def roi_end(event):
    if obj_master[-1].name[0] == "s":
        if obj_master[-1].xi == event.x or obj_master[-1].yi == event.y:
            print("NO SUELTE EL MOUSE")
            obj_master.pop()
            return
    elif obj_master[-1].name[0] == "c" or obj_master[-1].name[0] == "r":
        if obj_master[-1].xi == event.x and obj_master[-1].yi == event.y:
            print("NO SUELTE EL MOUSE")
            obj_master.pop()
            return
    obj_master[-1].end_coord(event.x,event.y)
    obj_master[-1].draw(False)
    roi_gen(obj_master[-1].name[0])
def roi_escape(event,flag: bool):
    root.config(cursor="arrow")
    root.unbind('<Button-1>')
    root.unbind('<B1-Motion>')
    root.unbind('<ButtonRelease-1>')
    if flag:
        obj_master[-1].insec.incv.delete(obj_master[-1].name)
        obj_master.pop()
        


#-------------- MAIN LOOP ---------------------------------------------------------
      
        
root = Tk()
root.title("S A U R U S")
root.config(bg="#F00") #para debug 
#root.iconbitmap("unsam.ico")

# GLOBAL VARIABLES
MF_W = IntVar(value=1920)
MF_H = IntVar(value=980)
CV_W = IntVar(value=0)
CV_H = IntVar(value=0)
info_text = StringVar(value="SAURUS V1.4")
info_cv = BooleanVar(value=0)
axis_cv = BooleanVar(value=0)
#MAIN WINDOW DISPLAY
windows_creator()
menu_creator()

root.mainloop()

#------------------------------------------------------------------------------