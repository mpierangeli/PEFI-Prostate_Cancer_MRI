from tkinter import *
from PIL import Image, ImageTk, ImageGrab
from tkinter import filedialog,ttk,messagebox
import pydicom
import numpy as np
import math
import imutils
import os
import shutil
import cv2

from pylatex import Document, PageStyle,Foot,MiniPage,VerticalSpace,SmallText,Package,StandAloneGraphic,MediumText,NewPage#,Command, Figure, Itemize, Head,simple_page_number,LineBreak, NewLine,SubFigure, HorizontalSpace,LargeText,FlushLeft
from pylatex.utils import  NoEscape,bold,italic

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

class observacion:
    def __init__(self,id):
        self.id = id        #numero de observacion para identificacion
        self.imagenes = []  #donde guardo los strings de direccion de imagenes para el html
        self.location = "?"   #nombre de la zona afectada
        self.eep = "?"       #checkbox de eep
        self.lesionT2 = [0,0] # [visible en secuencia,clasificacion pirads(1-5)]
        self.lesionDWI = [0,0]
        self.lesionDCE = 0 # [visible en secuencia]
        self.info = "?"      #texto informativo escrito a mano
        self.volumen = 0    #volumen de lesion
        self.medidas = [0,0,0]  #largo ejes de lesion VER SI SOLO NECESITO 1 MEDIDA
        self.categoria = 0  #SEGUN PIRADS FINAL

class prostata:
    def __init__(self):
        self.volumen = 0
        self.medidas = [0,0,0]
        self.categoria = 0   
        self.psa = [0,0,0,0]
        self.calima = "?"
        self.zonap = "?"
        self.zonat = "?"
        self.conclu = "?"
        self.motivo = "?"
        self.hemo = "?"
        self.neuro = "?"
        self.vesi = "?"
        self.linfa = "?"
        self.huesos = "?"
        self.organos = "?"
        self.indicado = "?"
        
## FUNCIONES
def on_closing():
    if messagebox.askokcancel("Salir", "Todas las observaciones se perderán al salir."):
        shutil.rmtree("temp_img")
        
        with open('startup_cfg.txt','w') as f:
            f.write("axis_cv:"+str(axis_cv.get())+"\ninfo_cv:"+str(info_cv.get())+"\nlayout_cv:"+str(layout_cv.get()))
            
        root.destroy()


def windows_creator():

    global main_frame, bot_frame, info_label

    main_frame = Frame(root, width=MF_W.get(), height=MF_H.get(), background="#222") # 20 de botframe 20 menu 20 windows tab 40 windows taskbar
    main_frame.grid(row=1, column=0)
    main_frame.grid_propagate(0)

    bot_frame = Frame(root, width=MF_W.get(), height=20, background="#2CC")
    bot_frame.grid(row=2, column=0)
    bot_frame.grid_propagate(0)

    info_label = Label(bot_frame, textvariable=info_text,bg="#2CC",font=("Roboto",9),fg="#000").grid(row=0,column=0,padx=10)
    global observaciones, obs_id
    # MASTER DE OBSERVACIONES PARA REPORTE
    observaciones = []
    obs_id = 0 # para identificar las observaciones si se borran/modifican

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
    menubar.add_command(label="Reportes", command=report_main)
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

def report_main():
    """
        si es la primera vez creo todas las variables
        si no es la primera vez solo cargo los datos temporales -> objetos de reporte (reporte general es una serie de observaciones)
            los minireports son checkboxes, texto, opciones, e imagenes varias, y metadata util?)
            el reporte general pueda que agarre metadata general tambien (automatica o pedirla antes de generar para no andar guardando)
        muestro la pantalla completa dentro de la misma window o ventana aparte?
        si quiero agregar algo pongo +
        si quiero sacar algo pongo -
        si quiero modificar le doy a "modificar"-> crea uno nuevo y llena con lo q tenia el anterior sin darle a ok?)
        si quiero terminar el reporte le doy a "generar"
        el reporte generado lo guarda en la carpeta de las imagenes dicom como .pdf(ver)
        las imagenes temporales capaz q las cree en una carpeta temporal dentro del folder de esas imagenes y depsues lo borre (ver permisos de windows)
                
    """
    if report_flag.get():
        report_window.destroy()
        report_flag.set(False)
    else:
        report_flag.set(True)
        refresh_report()
        
def refresh_report():
    global report_window,b1,b2
    try: report_window.destroy()
    except: pass
    report_window = Frame(root,background="#333")
    report_window.place(relx=0,rely=0, height=MF_H.get(), width=MF_W.get()/2)
    Label(report_window, text="REPORTE PI-RADS",bg="#2CC",font=("Roboto",15),fg="#000").pack(fill=X,ipady=10)
    Label(report_window, text="PANEL DE OBSERVACIONES",bg="#2CC",font=("Roboto",13),fg="#000").pack(fill=X,pady=(0,20))
    b1 = Button(report_window, text="NUEVA OBSERVACION", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2", command=lambda tipo="new":obs_setup(tipo))
    b1.pack(fill=X,pady=(0,20), ipady=10)
    b1.bind("<Enter>",lambda b=b1:colorOnFocus(b,True))
    b1.bind("<Leave>",lambda b=b1:colorOnFocus(b,False))
    for n, obs in enumerate(observaciones):
        mini_report = Frame(report_window,background="#444")
        mini_report.pack(fill=X,pady=(0,30),ipadx=2, ipady=2)
        Button(mini_report, text="Del.", font=("Roboto",12,"bold"), bg="#A55", cursor="hand2", bd=0, command=lambda to_destroy=n:del_obs(to_destroy)).pack(side=LEFT,ipadx=1,fill=Y,padx=5)
        Button(mini_report, text="Edit", font=("Roboto",12,"bold"), bg="#AA5", cursor="hand2", bd=0, command=lambda to_edit=n:edit_obs(to_edit)).pack(side=LEFT,ipadx=1,fill=Y)
        temp_bg = "#555"
        if obs.categoria == 1: temp_bg = "#0F0"
        elif obs.categoria == 2: temp_bg = "#AF0"
        elif obs.categoria == 3: temp_bg = "#FF0"
        elif obs.categoria == 4: temp_bg = "#F90"
        elif obs.categoria == 5: temp_bg = "#F00"
        Label(mini_report, text="PI-RADS "+str(obs.categoria),bg=temp_bg,font=("Roboto",12,"bold"),fg="#000").pack(side=RIGHT,padx=(0,30),fill=Y,ipadx=1)
        Label(mini_report, text="ID:"+str(obs.id),bg="#444",font=("Roboto",9),fg="#FFF").pack(anchor=W,padx=(15,0))
        Label(mini_report, text="Ubicación: "+obs.location,bg="#444",font=("Roboto",10),fg="#FFF").pack(anchor=W,padx=(15,0))
        Label(mini_report, text="Tamaño: "+str(obs.medidas[0])+"x"+str(obs.medidas[1])+"x"+str(obs.medidas[2])+"mm --> Vol: "+str(obs.volumen)+"ml",bg="#444",font=("Roboto",10),fg="#FFF").pack(anchor=W,padx=(15,0))
        Label(mini_report, text="Descripción:",bg="#444",font=("Roboto",10),fg="#FFF").pack(anchor=W,padx=(15,0))
        des = Text(mini_report,bg="#444",font=("Roboto",9),fg="#FFF",height=4,width=100,bd=0)
        des.pack(anchor=W,padx=(15,0))
        T =  obs.info
        des.insert(END,T)
    if len(observaciones) == 0: 
        b2 = Button(report_window, text="INICIAR REPORTE", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2", state="disabled")
        b2.pack(side=BOTTOM,fill=X,ipady=10,pady=10)
    else:
        b2 = Button(report_window, text="INICIAR REPORTE", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2",command=lambda tipo="create":obs_setup(tipo))
        b2.pack(side=BOTTOM,fill=X,ipady=10,pady=10)
    b2.bind("<Enter>",lambda b=b2:colorOnFocus(b,True))
    b2.bind("<Leave>",lambda b=b2:colorOnFocus(b,False))
   
def colorOnFocus(b: Button, n=bool):
    if n:   b.widget.config(background="#F80")
    else:   b.widget.config(background="#2CC")
           
def obs_setup(tipo: str):
    global obs_id,prostata_flag,prosta,medidas
    prostata_flag = False
    if tipo == "new":
        observaciones.append(observacion(obs_id))
        obs_id += 1
        report_window.destroy()
        steps_main(1)
    elif tipo == "edit":
        report_window.destroy()
        steps_main(1)
    elif tipo == "bypassed":
        observaciones[-1].volumen = vol
        observaciones[-1].medidas = medidas
        medidas = []
        steps_window.destroy()
        steps_main(2)
    elif tipo == "create":
        report_window.destroy()
        prostata_flag = True
        prosta = prostata()
        steps_main(1)
    elif tipo == "end":
        prosta.volumen = vol
        prosta.medidas = medidas
        medidas = []
        steps_window.destroy()
        steps_main(4)
        
def steps_main(step: int):
    global steps_window,steps_levels, zona_label, t2_check,dce_check,dwi_check,catT2,catDWI, eep, info, mapa_flag, psa_value, psa_date1, psa_date2, psa_date3, t1,t2,t3,t4,t5,t6,hemo,neuro,vesi,huesos,organos,linfa,auxframe2, zona
    mapa_flag = False
    if step == 1:
        steps_window = Frame(root,background="#2CC")
        steps_window.place(relx=0.5,rely=0.05, height=40,anchor=CENTER)
        to_vol = "próstata" if prostata_flag else "lesión"
        Label(steps_window, text="Seleccione 3 ejes de la "+to_vol,bg="#2CC",font=("Roboto",12),fg="#000").pack(ipady=5,ipadx=20)
        vol_calculator()
    elif step == 2:
        steps_levels = Toplevel(root,background="#444")
        steps_levels.geometry("435x1000")
        steps_window = Frame(steps_levels,background="#444")
        steps_window.pack(side=LEFT,fill=Y)
        Label(steps_window, text="Sobre la lesión...",bg="#2CC",font=("Roboto",12),fg="#000").pack(fill=X,ipady=5,ipadx=20)
        
        aux = Frame(steps_window,background="#555")
        aux.pack(fill=X,ipady=5,pady=(20,30))
        zona = StringVar(value="Seleccione Zona Afectada")
        zona_label = Label(aux, textvariable=zona,bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        b1 = Button(aux, text="Mapa >>", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2",height=1,command=mapa_show)
        b1.pack(side=RIGHT,ipadx=5)
        
        aux = Frame(steps_window,background="#555")
        aux.pack(fill=X,ipady=2)
        Label(aux, text="Lesión en T2",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        t2_check = IntVar()
        Checkbutton(aux,text="Visible",variable=t2_check,onvalue=1,offvalue=0,bg="#555",foreground="#FFF",selectcolor="#444",bd=0).pack(side=LEFT)
        pirads_opt = [1,2,3,4,5]
        aux2 = Frame(steps_window,background="#555")
        aux2.pack(fill=X,ipady=2)
        Label(aux2, text="Categoría PI-RADS:",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        catT2 = IntVar()
        for n in range(5):
            Radiobutton(aux2, text=str(pirads_opt[n]), variable=catT2, value=pirads_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        
        aux6 = Frame(steps_window,background="#555")
        aux6.pack(fill=X,ipady=2)
        Label(aux6, text="Lesión en DWI",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        dwi_check = IntVar()
        Checkbutton(aux6,text="Visible",variable=dwi_check,onvalue=1,offvalue=0,bg="#555",foreground="#FFF",selectcolor="#444",bd=0).pack(side=LEFT)
        aux7 = Frame(steps_window,background="#555")
        aux7.pack(fill=X,ipady=2)
        Label(aux7, text="Categoría PI-RADS:",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        catDWI = IntVar()
        for n in range(5):
            Radiobutton(aux7, text=str(pirads_opt[n]), variable=catDWI, value=pirads_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        
        aux3 = Frame(steps_window,background="#555")
        aux3.pack(fill=X,ipady=2,pady=(20,0))
        Label(aux3, text="DCE",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        dce_check = IntVar()
        Checkbutton(aux3,text="Visible",variable=dce_check,onvalue=1,offvalue=0,bg="#555",foreground="#FFF",selectcolor="#444",bd=0).pack(side=LEFT)

        aux8 = Frame(steps_window,background="#555")
        aux8.pack(fill=X,ipady=2,pady=(30,10))  
        Label(aux8, text="Extensión Extraprostática",bg="#555",font=("Roboto",11),fg="#FFF").pack(fill=X,padx=20,ipady=5)
        eep = StringVar()
        auxframe = Frame(aux8)
        auxframe.pack(padx=20)
        eep_opt = ["Bajo","Medio","Alto","Muy Alto"]
        for n in range(4):
            Radiobutton(auxframe, text=eep_opt[n], variable=eep, value=eep_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    
        Label(steps_window, text="Información Adicional",bg="#444",font=("Roboto",11),fg="#FFF",anchor=W).pack(fill=X,pady=(20,10),padx=30)
        info = Text(steps_window,width=62,font=("Roboto",10),height=10,bg="#555",fg="#FFF",bd=0,insertbackground="#2CC")
        info.pack()
        auxframe2 = Frame(steps_window,bg="#444")
        auxframe2.pack(padx=30,pady=30,anchor=W)
        b3 = Button(auxframe2, text="Agregar Imágenes", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2",command=save_cv)
        b3.pack(ipadx=2,ipady=2,pady=(0,20))
        b4 = Button(steps_window, text="Guardar Observación", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2",height=3,command=lambda step=3:steps_main(step))
        b4.pack(fill=X,side=BOTTOM)
        b3.bind("<Enter>",lambda b=b3:colorOnFocus(b,True))
        b3.bind("<Leave>",lambda b=b3:colorOnFocus(b,False))
        b4.bind("<Enter>",lambda b=b4:colorOnFocus(b,True))
        b4.bind("<Leave>",lambda b=b4:colorOnFocus(b,False))
        
    elif step == 3:
        observaciones[-1].location = zona.get()
        observaciones[-1].lesionT2 = t2_check.get(),catT2.get()
        observaciones[-1].lesionDWI = dwi_check.get(),catDWI.get()
        observaciones[-1].lesionDCE = dce_check.get()
        observaciones[-1].eep = eep.get()
        observaciones[-1].info = info.get("1.0","end-1c")
        observaciones[-1].categoria = pirads_lesion(observaciones[-1])
        steps_levels.destroy()
        refresh_report()
        
    elif step == 4:
        steps_levels = Toplevel(root,background="#444")
        steps_levels.geometry("500x1000")
        steps_window = Frame(steps_levels,background="#444")
        steps_window.pack(fill=Y)
        Label(steps_window, text="Sobre el paciente...",bg="#2CC",font=("Roboto",12),fg="#000").pack(fill=X,ipady=5,ipadx=20)

        info_general = Frame(steps_window,background="#555")
        info_general.pack(fill=X,ipadx=2, ipady=2,pady=(0,5))
        Label(info_general, text="Paciente:     "+str(secuencias[0].dcm_serie[0].PatientName),bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=5,ipadx=20,anchor=W)
        Label(info_general, text="Edad: XX años | Sexo: "+str(secuencias[0].dcm_serie[0].PatientSex),bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
        #Label(info_general, text="Peso: 90 kg | Altura: 180 cm | IMC: 23",bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
        Label(info_general, text="Volúmen Prostático: "+str(prosta.volumen)+" ml | Dimensiones: "+str(prosta.medidas[0])+"x"+str(prosta.medidas[1])+"x"+str(prosta.medidas[2])+" mm",bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
        
        Label(steps_window, text="Historial Clínico",bg="#444",font=("Roboto",11),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
        historial = Frame(steps_window,background="#555")
        historial.pack(fill=X,ipadx=2, ipady=2, pady=(0,5))
        auxframe1 = Frame(historial,bg="#555")
        auxframe1.pack(anchor=W,pady=5)
        Label(auxframe1, text="PSA:",bg="#555",font=("Roboto",10),fg="#FFF",width=10).pack(side=LEFT,padx=5)
        psa_value = Entry(auxframe1,width=10,font=("Roboto",12),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        psa_value.pack(side=LEFT)
        Label(auxframe1, text="Fecha(DD/MM/AA):",bg="#555",font=("Roboto",10),fg="#FFF",width=15).pack(side=LEFT)
        psa_date1= Entry(auxframe1,width=2,font=("Roboto",12),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        psa_date1.pack(side=LEFT,padx=(0,2))
        Label(auxframe1, text="/",bg="#555",font=("Roboto",10),fg="#FFF",width=1).pack(side=LEFT)
        psa_date2= Entry(auxframe1,width=2,font=("Roboto",12),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        psa_date2.pack(side=LEFT,padx=(0,2))
        Label(auxframe1, text="/",bg="#555",font=("Roboto",10),fg="#FFF",width=1).pack(side=LEFT)
        psa_date3= Entry(auxframe1,width=2,font=("Roboto",12),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        psa_date3.pack(side=LEFT,padx=(0,2))
        
        auxframe5 = Frame(historial,background="#555")
        auxframe5.pack(fill=X,pady=5)
        Label(auxframe5, text="Motivo\nEstudio:",bg="#555",font=("Roboto",10),fg="#FFF",width=10).pack(side=LEFT,padx=5)
        t1 = Text(auxframe5,width=55,height=4,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        t1.pack(side=LEFT)
        
        auxframe6 = Frame(historial,background="#555")
        auxframe6.pack(fill=X,pady=5)
        Label(auxframe6, text="Indicado por:",bg="#555",font=("Roboto",10),fg="#FFF",width=10).pack(side=LEFT,padx=5)
        t6 = Text(auxframe6,width=55,height=1,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        t6.pack(side=LEFT)
        
        Label(steps_window, text="Informe de Resultados",bg="#444",font=("Roboto",11),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
        
        estudio_info = Frame(steps_window,background="#555")
        estudio_info.pack(fill=X,ipadx=2, ipady=2, pady=(0,5))
        hemo = StringVar()
        neuro = StringVar()
        vesi = StringVar()
        linfa = StringVar()
        huesos = StringVar()
        organos = StringVar()
        m0 = Frame(estudio_info,bg="#555")
        m0.pack(side=LEFT)
        a0 = Frame(m0,bg="#555")
        a0.pack(pady=1)
        Label(a0, text="Hemorragia:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
        Radiobutton(a0, text="Si", variable=hemo, value="Si", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        Radiobutton(a0, text="No", variable=hemo, value="No", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        a1 = Frame(m0,bg="#555")
        a1.pack(pady=1)
        Label(a1, text="Lesión Neurovascular:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
        Radiobutton(a1, text="Si", variable=neuro, value="Si", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        Radiobutton(a1, text="No", variable=neuro, value="No", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        a2 = Frame(m0,bg="#555")
        a2.pack(pady=1)
        Label(a2, text="Lesión Vesicula Seminal:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
        Radiobutton(a2, text="Si", variable=vesi, value="Si", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        Radiobutton(a2, text="No", variable=vesi, value="No", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        m1 = Frame(estudio_info,bg="#555")
        m1.pack(side=LEFT)
        a3 = Frame(m1,bg="#555")
        a3.pack(pady=1)
        Label(a3, text="Lesión Nodos Linfáticos:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
        Radiobutton(a3, text="Si", variable=linfa, value="Si", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        Radiobutton(a3, text="No", variable=linfa, value="No", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        a4 = Frame(m1,bg="#555")
        a4.pack(pady=1)
        Label(a4, text="Lesión Huesos:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
        Radiobutton(a4, text="Si", variable=huesos, value="Si", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        Radiobutton(a4, text="No", variable=huesos, value="No", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        a5 = Frame(m1,bg="#555")
        a5.pack(pady=1)
        Label(a5, text="Lesión Órganos:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
        Radiobutton(a5, text="Si", variable=organos, value="Si", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        Radiobutton(a5, text="No", variable=organos, value="No", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        
        estudio_info2 = Frame(steps_window,background="#555")
        estudio_info2.pack(fill=X,ipadx=2, ipady=2)
        auxframe2 = Frame(estudio_info2,bg="#555")
        auxframe2.pack(anchor=W,pady=5)
        Label(auxframe2, text="Calidad\nImágenes: ",bg="#555",font=("Roboto",10),fg="#FFF",width=9).pack(side=LEFT,padx=10)
        t2 = Text(auxframe2,width=55,height=4,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        t2.pack(side=LEFT)
        auxframe3 = Frame(estudio_info2,bg="#555")
        auxframe3.pack(anchor=W,pady=5)
        Label(auxframe3, text="Zona\nPeriférica: ",bg="#555",font=("Roboto",10),fg="#FFF",width=9).pack(side=LEFT,padx=10)
        t3 = Text(auxframe3,width=55,height=4,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        t3.pack(side=LEFT)
        auxframe4 = Frame(estudio_info2,bg="#555")
        auxframe4.pack(anchor=W,pady=5)
        Label(auxframe4, text="Zona\nTransicional: ",bg="#555",font=("Roboto",10),fg="#FFF",width=9).pack(side=LEFT,padx=10)
        t4 = Text(auxframe4,width=55,height=4,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        t4.pack(side=LEFT)
        
        Label(steps_window, text="Observaciones Realizadas",bg="#444",font=("Roboto",11),fg="#FFF").pack(ipady=2,ipadx=20,anchor=W)
        
        lesiones_info = Frame(steps_window,background="#555")
        lesiones_info.pack(fill=X,ipadx=2, ipady=2, pady=(0,5))
        l1 = Frame(lesiones_info,background="#555")
        l1.pack(side=LEFT)
        for obs in observaciones:
            mini_report = Frame(l1,background="#555")
            mini_report.pack(padx=20)
            Label(mini_report, text="ID: "+str(obs.id),bg="#555",font=("Roboto",10),fg="#FFF").pack(side=LEFT)
            Label(mini_report, text=" | PI-RADS: "+str(obs.categoria),bg="#555",font=("Roboto",10),fg="#FFF").pack(side=LEFT)
        l2 = Frame(lesiones_info,background="#555")
        l2.pack(side=RIGHT)
        prosta.categoria = pirads_prostata()
        temp_bg = "#555"
        if prosta.categoria == 1: temp_bg = "#0F0"
        elif prosta.categoria == 2: temp_bg = "#AF0"
        elif prosta.categoria == 3: temp_bg = "#FF0"
        elif prosta.categoria == 4: temp_bg = "#F90"
        elif prosta.categoria == 5: temp_bg = "#F00"
        Label(l2, text="PI-RADS\nGeneral\n"+str(prosta.categoria),bg=temp_bg,font=("Roboto",12,"bold"),fg="#000").pack(fill=Y,ipadx=20,ipady=5) 
        
        Label(steps_window, text="Conclusiones",bg="#444",font=("Roboto",12),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W) 
        t5 = Text(steps_window,width=65,height=7,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        t5.pack(pady=(0,20))
        
        b4 = Button(steps_window, text="Finalizar y Generar PDF", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2",height=3,command=lambda step=5:steps_main(step))
        b4.pack(fill=X,side=BOTTOM)
        b4.bind("<Enter>",lambda b=b4:colorOnFocus(b,True))
        b4.bind("<Leave>",lambda b=b4:colorOnFocus(b,False))
    
    elif step == 5:
        
        try: prosta.psa = [psa_value.get(),psa_date1.get(),psa_date2.get(),psa_date3.get()]
        except: pass
        prosta.motivo = t1.get("1.0","end-1c")
        prosta.indicado = t6.get("1.0","end-1c")
        prosta.calima = t2.get("1.0","end-1c")
        prosta.zonap = t3.get("1.0","end-1c")
        prosta.zonat = t4.get("1.0","end-1c")
        prosta.conclu = t5.get("1.0","end-1c")
        prosta.hemo = hemo.get()
        prosta.neuro = neuro.get()
        prosta.vesi = vesi.get()
        prosta.linfa = linfa.get()
        prosta.huesos = huesos.get()
        prosta.organos = organos.get()
        #quiza ventana de prevista y confirmacion?
        steps_levels.destroy()
        mapa_pirads_gen()
        generator()
        #generator(filedialog.askdirectory(title="Guardar Reporte"))
def edit_obs(n: int):
    global steps_window,steps_levels, zona_label, t2_check,dce_check,dwi_check,catT2,catDWI, eep, info, mapa_flag, auxframe2, zona

    report_window.destroy()
    obs = observaciones[n]
    steps_levels = Toplevel(root,background="#444")
    steps_levels.geometry("435x1000")
    steps_window = Frame(steps_levels,background="#444")
    steps_window.pack(side=LEFT,fill=Y)
    Label(steps_window, text="Sobre la lesión...",bg="#2CC",font=("Roboto",12),fg="#000").pack(fill=X,ipady=5,ipadx=20)
    
    aux = Frame(steps_window,background="#555")
    aux.pack(fill=X,ipady=5,pady=(20,30))
    zona = StringVar(value=obs.location)
    zona_label = Label(aux, textvariable=zona,bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    b1 = Button(aux, text="Mapa >>", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2",height=1,command=mapa_show)
    b1.pack(side=RIGHT,ipadx=5)
    
    aux = Frame(steps_window,background="#555")
    aux.pack(fill=X,ipady=2)
    Label(aux, text="Lesión en T2",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    t2_check = IntVar(value=obs.lesionT2[0])
    Checkbutton(aux,text="Visible",variable=t2_check,onvalue=1,offvalue=0,bg="#555",foreground="#FFF",selectcolor="#444",bd=0).pack(side=LEFT)
    pirads_opt = [1,2,3,4,5]
    aux2 = Frame(steps_window,background="#555")
    aux2.pack(fill=X,ipady=2)
    Label(aux2, text="Categoría PI-RADS:",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    catT2 = IntVar(value=obs.lesionT2[1])
    for n in range(5):
        Radiobutton(aux2, text=str(pirads_opt[n]), variable=catT2, value=pirads_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    
    aux6 = Frame(steps_window,background="#555")
    aux6.pack(fill=X,ipady=2)
    Label(aux6, text="Lesión en DWI",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    dwi_check = IntVar(value=obs.lesionDWI[0])
    Checkbutton(aux6,text="Visible",variable=dwi_check,onvalue=1,offvalue=0,bg="#555",foreground="#FFF",selectcolor="#444",bd=0).pack(side=LEFT)
    aux7 = Frame(steps_window,background="#555")
    aux7.pack(fill=X,ipady=2)
    Label(aux7, text="Categoría PI-RADS:",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    catDWI = IntVar(value=obs.lesionDWI[1])
    for n in range(5):
        Radiobutton(aux7, text=str(pirads_opt[n]), variable=catDWI, value=pirads_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    
    aux3 = Frame(steps_window,background="#555")
    aux3.pack(fill=X,ipady=2,pady=(20,0))
    Label(aux3, text="DCE",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    dce_check = IntVar(value=obs.lesionDCE)
    Checkbutton(aux3,text="Visible",variable=dce_check,onvalue=1,offvalue=0,bg="#555",foreground="#FFF",selectcolor="#444",bd=0).pack(side=LEFT)

    aux8 = Frame(steps_window,background="#555")
    aux8.pack(fill=X,ipady=2,pady=(30,10))  
    Label(aux8, text="Extensión Extraprostática",bg="#555",font=("Roboto",11),fg="#FFF").pack(fill=X,padx=20,ipady=5)
    eep = StringVar(value=obs.eep)
    auxframe = Frame(aux8)
    auxframe.pack(padx=20)
    eep_opt = ["Bajo","Medio","Alto","Muy Alto"]
    for n in range(4):
        Radiobutton(auxframe, text=eep_opt[n], variable=eep, value=eep_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)

    Label(steps_window, text="Información Adicional",bg="#444",font=("Roboto",11),fg="#FFF",anchor=W).pack(fill=X,pady=(20,10),padx=30)
    info = Text(steps_window,width=62,font=("Roboto",10),height=10,bg="#555",fg="#FFF",bd=0,insertbackground="#2CC")
    info.pack()
    info.insert(END, obs.info)
    auxframe2 = Frame(steps_window,bg="#444")
    auxframe2.pack(padx=30,pady=30,anchor=W)
    b3 = Button(auxframe2, text="Agregar Imágenes", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2",command=save_cv)
    b3.pack(ipadx=2,ipady=2,pady=(0,20))
    for n,img in enumerate(obs.imagenes):
        Label(auxframe2, text="added obs_"+str(obs.id)+"_"+str(n+1)+".png",bg="#444",font=("Roboto",11),fg="#FFF",anchor=W).pack(fill=X,ipady=1,ipadx=1)
    b4 = Button(steps_window, text="Guardar Cambios", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2",height=3,command=lambda obs=obs: confirm_edit(obs))
    b4.pack(fill=X,side=BOTTOM)
    b3.bind("<Enter>",lambda b=b3:colorOnFocus(b,True))
    b3.bind("<Leave>",lambda b=b3:colorOnFocus(b,False))
    b4.bind("<Enter>",lambda b=b4:colorOnFocus(b,True))
    b4.bind("<Leave>",lambda b=b4:colorOnFocus(b,False))

def confirm_edit(obs:observacion):
    obs.location = zona.get()
    obs.lesionT2 = t2_check.get(),catT2.get()
    obs.lesionDWI = dwi_check.get(),catDWI.get()
    obs.lesionDCE = dce_check.get()
    obs.eep = eep.get()
    obs.info = info.get("1.0","end-1c")
    obs.categoria = pirads_lesion(obs)
    steps_levels.destroy()
    refresh_report()
    
def mapa_pirads_gen():
    mapa = np.asarray(Image.open("sector_map_v21_bnw2.png"))
    mapa_colores = np.asarray(Image.open("sector_map_v21_mask.png"))
    pirads_colores = [[0,255,0],[170,255,0],[255,255,0],[255,133,0],[255,0,0]] #color para piradas 1,2,3,4,5 segun reporte
    for obs in observaciones:
        for RGB_code in RGB_codes:
            if obs.location == RGB_code[3]:
                mask = (mapa_colores[:,:,0] == RGB_code[0])*(mapa_colores[:,:,1] == RGB_code[1])*(mapa_colores[:,:,2] == RGB_code[2])
                mapa[mask] = pirads_colores[obs.categoria-1]
    save_img = os.path.join("temp_img","mapa_final.png")
    mapa = Image.fromarray(mapa)
    mapa.save(save_img)
    
def del_obs(to_destroy: int):
    observaciones.pop(to_destroy)
    refresh_report()

def mapa_show():
    global mapa_flag,mapa_window,cv_mapa,mapa_img
    if mapa_flag:   
        mapa_window.destroy()
        mapa_flag = False
        steps_levels.geometry("435x1000")
        steps_levels.config(cursor="arrow")
    else:
        steps_levels.config(cursor="plus")
        mapa_img = ImageTk.PhotoImage(Image.open("sector_map_v21.png"))
        steps_levels.geometry(str(mapa_img.width()+435)+"x1000")
        mapa_window = Frame(steps_levels,background="#444")
        mapa_window.pack(side=RIGHT)
        cv_mapa = Canvas(mapa_window, width=mapa_img.width(),height=mapa_img.height(),bg="#000",highlightthickness=0)
        cv_mapa.pack()
        cv_mapa.create_image(mapa_img.width()/2, mapa_img.height()/2, anchor=CENTER, image=mapa_img)
        cv_mapa.bind("<Button-1>",zone_selector)
        
        mapa_flag = True
        
def zone_selector(event):
    global RGB_codes
    x = event.x
    y = event.y
    mapa_colores  = np.asarray(Image.open("sector_map_v21_mask.png"))
    RGB_codes = [[20,0,0,"Transicional Posterior Izquierda (Base)"],
                 [50,0,0,"Transicional Posterior Derecha (Base)"],
                 [60,0,0,"Central Izquierda (Base)"],
                 [80,0,0,"Central Derecha (Base)"],
                 [100,0,0,"Transicional Anterior Izquierda (Base)"],
                 [120,0,0,"Transicional Anterior Derecha (Base)"],
                 [140,0,0,"Estroma Fibromuscular Anterior (Base)"],
                 [160,0,0,"Periférica Anterior Izquierda (Base)"],
                 [180,0,0,"Periférica Posterior Izquierda (Base)"],
                 [200,0,0,"Periférica Anterior Derecha (Base)"],
                 [220,0,0,"Periférica Posterior Derecha (Base)"],
                 
                 [0,20,0,"Transicional Posterior Izquierda (Medio)"],
                 [0,50,0,"Transicional Posterior Derecha (Medio)"],
                 [0,60,0,"Periférica Medial Izquierda (Medio)"],
                 [0,80,0,"Periférica Medial Derecha (Medio)"],
                 [0,100,0,"Transicional Anterior Izquierda (Medio)"],
                 [0,120,0,"Transicional Anterior Derecha (Medio)"],
                 [0,140,0,"Estroma Fibromuscular Anterior (Medio)"],
                 [0,160,0,"Periférica Anterior Izquierda (Medio)"],
                 [0,180,0,"Periférica Posterior Izquierda (Medio)"],
                 [0,200,0,"Periférica Anterior Derecha (Medio)"],
                 [0,220,0,"Periférica Posterior Derecha (Medio)"],
                 
                 [0,0,20,"Transicional Posterior Izquierda (Apex)"],
                 [0,0,50,"Transicional Posterior Derecha (Apex)"],
                 [0,0,60,"Periférica Medial Izquierda (Apex)"],
                 [0,0,80,"Periférica Medial Derecha (Apex)"],
                 [0,0,100,"Transicional Anterior Izquierda (Apex)"],
                 [0,0,120,"Transicional Anterior Derecha (Apex)"],
                 [0,0,140,"Estroma Fibromuscular Anterior (Apex)"],
                 [0,0,160,"Periférica Anterior Izquierda (Apex)"],
                 [0,0,180,"Periférica Posterior Izquierda (Apex)"],
                 [0,0,200,"Periférica Anterior Derecha (Apex)"],
                 [0,0,220,"Periférica Posterior Derecha (Apex)"]]
    
    for RGB_code in RGB_codes:
        if (mapa_colores[y,x,0] == RGB_code[0])*(mapa_colores[y,x,1] == RGB_code[1])*(mapa_colores[y,x,2] == RGB_code[2]):
            zona.set(RGB_code[3])
            mapa_show() # para cerrar el mapa una vez seleccionada la zona
    
def canvas_creator(layout:int):
    global cv_master, img2cv
    img2cv = [0,0,0,0]
    layout_cv.set(layout)
    try:
        for temp_cv in cv_master:
            temp_cv.destroy()
    except:
        pass
    for sec in secuencias:
        sec.incv = 0 # VER ESTO
    cv_master = []
    if layout == 1:   # VER DE SACAR ESTO SI FUERZA A USAR python 3.10
        CV_W.set(MF_W.get()-40)
        CV_H.set(MF_H.get()-40)
        cv_master.append(Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0))
        cv_master[0].grid(row=0,column=0,padx=20,pady=20)
    elif layout == 2:
        CV_W.set(int(MF_W.get()/2)-10)
        CV_H.set(MF_H.get()-40)
        for n in range(layout):
            cv_master.append(Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0))
        cv_master[0].grid(row=0,column=0,padx=(0,10),pady=20)
        cv_master[1].grid(row=0,column=1,padx=(10,0),pady=20)        
    elif layout == 4:
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
    if len(obj_master) > 0:
        obj_master[-1].insec.incv.delete(obj_master[-1].name)
        obj_master.pop()

def patient_loader():
    global secuencias, obj_master, observaciones, obs_id
    
    filepath = filedialog.askdirectory()
    if not filepath: return 
    
    # MASTER DE SECUENCIAS CARGADAS
    secuencias = []
        # auxiliar de secuencias
    sec_uids = []
    # MASTER DE DIBUJOS
    obj_master = []
    
    
    for file in sorted(os.listdir(filepath)):
        name, ext = os.path.splitext(file)
        if ext == ".IMA":
            temp_dcm = pydicom.dcmread(filepath+"/"+file)
            temp_uid = temp_dcm.SeriesInstanceUID
            if  temp_uid not in sec_uids:
                secuencias.append(secuencia(temp_dcm.SequenceName+"-> TE: "+str(temp_dcm.EchoTime)+", TR: "+str(temp_dcm.RepetitionTime)+", "+str(temp_dcm.ScanOptions)+", UID: "+temp_uid[-4:-1]))
                sec_uids.append(temp_uid)
            secuencias[-1].add_dcm(temp_dcm)
    canvas_creator(layout_cv.get())
    sec_selector()              

def sec_selector():
    global seq_tab,sec_list
    try: seq_tab.destroy()
    except: pass
    seq_tab = Frame(root,background="#333")
    seq_tab.place(relx=0,rely=0, height=MF_H.get())
    Label(seq_tab, text="SECUENCIAS DISPONIBLES",bg="#2CC",font=("Roboto",12),fg="#000").grid(row=0,column=0,ipadx=80,ipady=10,columnspan=2)
    sec_list = Listbox(seq_tab, height=57, width=50, relief=FLAT, bg="#333",font=("Roboto",9), cursor="hand2",selectmode="",activestyle="dotbox",fg="#FFF",selectbackground="#222",highlightthickness=0)
    sec_list.grid(row=1, column=0,padx=5,pady=10)
    for sec in secuencias:
        if not sec.aux_view:
            sec_list.insert(END,sec.name)
    sb = Scrollbar(seq_tab,orient=VERTICAL)
    sb.grid(row=1, column=1, sticky=NS)
    sec_list.config(yscrollcommand=sb.set)
    sb.config(command=sec_list.yview)
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
        sec.realy = sec.parent.dcm_serie[0].PixelSpacing[0]*sec.parent.depth*sec.factor/temp_img.shape[0]
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
    else: 
        for cvs in cv_master:
            cvs.delete("axial_depth_marker","sagital_depth_marker","coronal_depth_marker")
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
    try: info_tab.destroy()
    except: pass
    info = ""
    for sec in secuencias:
        if sec.incv == cv:
            if sec.aux_view: return
            else:
                for item in sec.dcm_serie[sec.slice]:
                    info += (" " + str(item) + "\n")
    info_tab = Frame(root,background="#333")
    info_tab.place(relx=0,rely=0, height=MF_H.get())
    Label(info_tab, text="DICOM METADATA",bg="#2CC",font=("Roboto",12),fg="#000").grid(row=0,column=0,columnspan=2,sticky=NSEW,ipady=10)
    text_box = Text(info_tab,width=100,height=58,font=("Roboto",10),fg="#FFF",bg="#333",bd=0)
    text_box.grid(row=1, column=0,pady=(10,0))
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
       
def save_cv():
    root.config(cursor="target")
    root.bind('<Button-1>', screenshot)
    steps_levels.iconify()
             
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
    
    global vol_cont, vol_flag, vol
    if vol_flag:
        vol_cont += 1
        medidas.append(round(obj_master[-1].rdis,1))
        if vol_cont == 3:
            vol_cont = 0
            vol_flag = False
            vol = round(obj_master[-1].rdis*obj_master[-2].rdis*obj_master[-3].rdis*0.52/1000,2) #volumen de elipsoide en ml
            for n in range(3):
                obj_master[-1].insec.incv.delete(obj_master[-1].name)
                obj_master.pop()
            root.config(cursor="arrow")
            root.unbind('<Button-1>')
            root.unbind('<B1-Motion>')
            root.unbind('<ButtonRelease-1>')
            if prostata_flag: obs_setup("end")
            else:   obs_setup("bypassed")              
def roi_escape(event,flag: bool):
    root.config(cursor="arrow")
    root.unbind('<Button-1>')
    root.unbind('<B1-Motion>')
    root.unbind('<ButtonRelease-1>')
    if flag:
        obj_master[-1].insec.incv.delete(obj_master[-1].name)
        obj_master.pop()
        
def vol_calculator():
    global vol_cont, vol_flag, vol, medidas
    vol_cont = 0    # cantidad de mediciones de axis elipsoide
    vol_flag = True # las rois de mediciones son para volumen
    vol = 0         # el volumen medido
    medidas = []
    roi_gen("r")

def pirads_lesion(obs: observacion):
    #depende las opciones de la lesion determina el pirads particular de la lesion
    #sigue el diagrama del paper (no el de la pagina)
    pirad = 0
    if ("Periférica" or "Central") in obs.location: 
        #si es zona periferica o central lo importante es DWI
        if obs.lesionDWI[0] == 1:
            if obs.lesionDWI[1] == 3 and obs.lesionDCE == 1:
                pirad = 4
            else:
                pirad = obs.lesionDWI[1]
    elif ("Transicional" or "Estroma") in obs.location:
        #si es zona transicional o efma lo importante es T2
        if obs.lesionT2[0] == 1:
            if obs.lesionDWI[0] == 1:
                if obs.lesionT2[1] == 2 and obs.lesionDWI[1] >=4:
                    pirad = 3
                elif obs.lesionT2[1] == 3 and obs.lesionDWI[1] == 5:
                    pirad = 4
                else:
                    pirad = obs.lesionT2[1]
            else:
                pirad = obs.lesionT2[1]
                
    return pirad # SI VUELVE 0 es un ERROR

def pirads_prostata():
    #depende de los resultados de las observaciones determina el pirads general
    #usa el máximo relevado VER
    pirad = 0
    for obs in observaciones:
        if obs.categoria >= pirad:
            pirad = obs.categoria
            
    return pirad # SI VUELVE 0 es un ERROR

def screenshot(event):
    
    observaciones[-1].imagenes.append(ImageGrab.grab((cv.winfo_rootx(), cv.winfo_rooty(), cv.winfo_rootx() + cv.winfo_width(), cv.winfo_rooty() + cv.winfo_height())))
    save_img = os.path.join("temp_img","obs_"+str(observaciones[-1].id)+"_"+str(len(observaciones[-1].imagenes))+".png")
    observaciones[-1].imagenes[-1].save(save_img) # VER DONDE GUARDA ESTO Y SI ES NECESARIO GUARDAR
    root.unbind('<Button-1>')
    root.config(cursor="arrow")
    steps_levels.deiconify()
    Label(auxframe2, text="added obs_"+str(observaciones[-1].id)+"_"+str(len(observaciones[-1].imagenes))+".png",bg="#444",font=("Roboto",11),fg="#FFF",anchor=W).pack(fill=X,ipady=1,ipadx=1)
#------------------LATEX TO PDF------------------------------
# Diseño la estructura en "latex" y creo un .pdf
def generator ():
    geometry_options = {
            "head": "40pt",
            "margin": "1.5cm",
            "top": "1cm",
            "bottom": "2cm"
        }
    doc = Document(geometry_options=geometry_options)
    doc.preamble.append(Package('babel', options='spanish'))
    #doc.packages.append(Package('HindMadurai'))
    doc.packages.append(Package('montserrat',"defaultfam"))
    footer = PageStyle("footer")
    with footer.create(Foot("C")):
        footer.append("Corporación Médica de Gral. San Martín SA - Matheu 4071, (1650) San Martín - Tel. 47547500")
    doc.preamble.append(footer)
    doc.change_document_style("footer")

    doc.append(NoEscape(r"\noindent"))
    with doc.create(MiniPage(width=NoEscape(r"0.2\linewidth"))) as logo:
        logo.append(StandAloneGraphic(image_options="width=150px",filename="logo_unsam_big.png"))
    with doc.create(MiniPage(width=NoEscape(r"0.6\linewidth"),align="c")) as titulo:
        titulo.append(MediumText("REPORTE PI-RADS"))
    with doc.create(MiniPage(width=NoEscape(r"0.2\linewidth"),align="r")) as datos:
        datos.append("Pág. 1 de 2")
        datos.append("\n")
        datos.append(NoEscape(r'\today'))
    doc.append(VerticalSpace("1cm"))

    doc.append("\n")
    doc.append(SmallText("Report ID: "))
    doc.append(SmallText(bold("ID guardado en save.txt?)")))
    doc.append("\n")
    doc.append(SmallText("Paciente: "))
    doc.append(SmallText(bold(str(secuencias[0].dcm_serie[0].PatientName))))
    doc.append("\n")
    doc.append(SmallText("Fecha estudio: "))
    doc.append(SmallText(bold(secuencias[0].dcm_serie[0].InstanceCreationDate[6:]+"/"+secuencias[0].dcm_serie[0].InstanceCreationDate[4:6]+"/"+secuencias[0].dcm_serie[0].InstanceCreationDate[0:4])))
    doc.append("\n")
    doc.append(SmallText("Indicado por: "))
    doc.append(SmallText(bold(prosta.indicado)))
    doc.append("\n")
    doc.append(SmallText("Revisado por: "))
    doc.append(SmallText(bold("NOMBRE FIJO?")))
    doc.append("\n")
    doc.append(NoEscape(r"\rule{\textwidth}{2pt}"))

    doc.append("\n\n")
    doc.append(SmallText(bold("HISTORIA CLÍNICA")))
    doc.append("\n\n")
    doc.append(SmallText("Motivo Estudio: "))
    doc.append(SmallText(italic(prosta.motivo)))
    doc.append("\n")
    doc.append(SmallText("PSA: "))
    doc.append(SmallText(bold(prosta.psa[0]+" ng/ml")))
    doc.append(NoEscape("\quad"))
    doc.append(SmallText("realizado el: "+prosta.psa[1]+"/"+prosta.psa[2]+"/"+prosta.psa[3]))
    doc.append("\n")
    doc.append(SmallText("PSAD: "))
    doc.append(SmallText(bold(str(round(int(prosta.psa[0])/prosta.volumen,2))+" ng/ml/cc")))
    doc.append("\n")
    doc.append(NoEscape(r"\rule{15cm}{1pt}"))
    
    doc.append("\n\n")
    doc.append(SmallText(bold("RESULTADOS")))
    doc.append("\n\n")
    doc.append(SmallText("Vol. Prostático: "))
    doc.append(SmallText(bold(str(prosta.volumen)+" ml")))
    doc.append(NoEscape("\quad"))
    doc.append(SmallText("|  Dim: "))
    doc.append(SmallText(bold(str(prosta.medidas[0]))))
    doc.append(SmallText("x"))
    doc.append(SmallText(bold(str(prosta.medidas[1]))))
    doc.append(SmallText("x"))
    doc.append(SmallText(bold(str(prosta.medidas[2]))))
    doc.append(SmallText(" mm"))
    doc.append("\n\n")
    with doc.create(MiniPage(width=NoEscape(r"0.30\linewidth"))) as resultL:
        resultL.append(SmallText("Hemorragia: "))
        resultL.append(SmallText(bold(prosta.hemo)))
        resultL.append("\n")
        resultL.append(SmallText("Lesión Neurovascular: "))
        resultL.append(SmallText(bold(prosta.neuro)))
        resultL.append("\n")
        resultL.append(SmallText("Lesión Vesícula Seminal: "))
        resultL.append(SmallText(bold(prosta.vesi)))
        resultL.append("\n")
        resultL.append(SmallText("Lesión Nodos Linfáticos: "))
        resultL.append(SmallText(bold(prosta.linfa)))
        resultL.append("\n")
        resultL.append(SmallText("Lesión Huesos: "))
        resultL.append(SmallText(bold(prosta.huesos)))
        resultL.append("\n")
        resultL.append(SmallText("Lesión Órganos: "))
        resultL.append(SmallText(bold(prosta.organos)))
    doc.append(NoEscape(r"\hfill\vline\hfill"))
    with doc.create(MiniPage(width=NoEscape(r"0.66\linewidth"))) as resultR:
        resultR.append(SmallText("Calidad de estudio: "))
        resultR.append(SmallText(italic(prosta.calima)))
        resultR.append("\n\n")
        resultR.append(SmallText("Zona Periférica: "))
        resultR.append(SmallText(italic(prosta.zonap)))
        resultR.append("\n\n")
        resultR.append(SmallText("Zona Transicional: "))
        resultR.append(SmallText(italic(prosta.zonat)))
    
    doc.append("\n\n\n")
    doc.append(SmallText(bold("Lesiones más significantes:")))
    doc.append("\n\n")
    
    all_images = list(os.listdir('temp_img'))
    for obs in observaciones:
        with doc.create(MiniPage(width=NoEscape(r"0.50\linewidth"))) as obsL:
            obsL.append(SmallText("ID : "))
            obsL.append(SmallText(bold(str(obs.id))))
            obsL.append("\n")
            obsL.append(SmallText("Zona Afectada: "))
            obsL.append(SmallText(bold(obs.location)))
            obsL.append("\n")
            obsL.append(SmallText("Vol. Lesión: "))
            obsL.append(SmallText(bold(str(obs.volumen)+" ml")))
            obsL.append(NoEscape("\quad"))
            obsL.append(SmallText("|  Dim: "))
            obsL.append(SmallText(bold(str(obs.medidas[0]))))
            obsL.append(SmallText("x"))
            obsL.append(SmallText(bold(str(obs.medidas[1]))))
            obsL.append(SmallText("x"))
            obsL.append(SmallText(bold(str(obs.medidas[2]))))
            obsL.append(SmallText(" mm"))
            obsL.append("\n")
            obsL.append(SmallText("Extensión Extraprostática: "))
            obsL.append(SmallText(bold(obs.eep)))
            obsL.append("\n")
            obsL.append(SmallText("Clasificación PIRADS: "))
            obsL.append(SmallText(bold(str(obs.categoria))))
            obsL.append("\n")
            obsL.append(SmallText("Observaciones: "))
            obsL.append(SmallText(italic(obs.info)))
        doc.append(NoEscape(r"\hfill\vline\hfill"))
        with doc.create(MiniPage(width=NoEscape(r"0.48\linewidth"))) as obsR:
            for img in all_images:
                if img[4] == str(obs.id):
                    img_to_open = "temp_img/"+img
                    obsR.append(StandAloneGraphic(image_options="width=250px",filename=img_to_open))
                    break
            """    cont = 0
            for img in all_images:
                if img[4] == str(obs.id):
                    img_to_open = "temp_img/"+img
                    if cont % 2 == 0:
                        obsR.append("\n")
                    obsR.append(StandAloneGraphic(image_options="width=150px",filename=img_to_open))
                    #obsR.append(NoEscape("\hspace{0.2cm}"))   
                    cont +=1"""
        doc.append("\n")
    doc.append(NewPage())
    doc.append(NoEscape(r"\noindent"))
    with doc.create(MiniPage(width=NoEscape(r"0.2\linewidth"))) as logo:
        logo.append(StandAloneGraphic(image_options="width=150px",filename="logo_unsam_big.png"))
    with doc.create(MiniPage(width=NoEscape(r"0.6\linewidth"),align="c")) as titulo:
        titulo.append(MediumText("REPORTE PI-RADS"))
    with doc.create(MiniPage(width=NoEscape(r"0.2\linewidth"),align="r")) as datos:
        datos.append("Pág. 2 de 2")
        datos.append("\n")
        datos.append(NoEscape(r'\today'))
    doc.append(VerticalSpace("1cm"))
    
    doc.append("\n")
    
    with doc.create(MiniPage(width=NoEscape(r"0.5\linewidth"))) as concluL:
        concluL.append(SmallText(bold("CONCLUSIÓN")))
        concluL.append("\n\n")
        concluL.append(SmallText(italic(prosta.conclu)))
        concluL.append("\n\n")
        concluL.append(MediumText(bold("PIRADS Final: "+str(prosta.categoria))))
    with doc.create(MiniPage(width=NoEscape(r"0.5\linewidth"))) as concluR:
        all_images = list(os.listdir('temp_img'))
        img_to_open = "temp_img/"+all_images[0]
        concluR.append(StandAloneGraphic(image_options="width=250px",filename=img_to_open))
    
    doc.append("\n")
    doc.append(NoEscape(r"\rule{\textwidth}{0.2pt}"))
    doc.append("\n\n")
    doc.append(SmallText("Sobre los resultados:"))
    doc.append("\n\n")
    doc.append(SmallText("La clasificación PI-RADS es un sistema internacionalmente consensuado, reconocido y recomendado por el American College of Radiology para informar la RMmp de forma uniforme por todos los radiólogos y se debe usar de forma obligatoria en la valoración de esta prueba."))
    doc.append("\n\n")
    doc.append(SmallText("PIRADS 1 - Muy Bajo. Es muy poco probable que la lesión sea un cáncer clínicamente significativo.\nPIRADS 2 - Bajo. Es poco probable que la lesión sea un cáncer clínicamente significativo; lesión probablemente benigna.\nPIRADS 3 - Intermedia. No hay datos que orienten claramente hacia la benignidad o malignidad de la lesión.\nPIRADS 4 - Alta. Es probable que la lesión sea un cáncer significativo; lesión probablemente maligna.\nPIRADS 5 - Muy Alta. Es muy probable que la lesión sea un cáncer significativo; lesión muy probablemente maligna."))
    doc.append("\n")
    #fp = os.path.join(save_directory,"TEST-DOC")
    doc.generate_pdf("TEST-DOC__",clean=True)
#-------------------------------------------------------


#-------------- MAIN LOOP ---------------------------------------------------------
      
        
root = Tk()
root.title("S A U R U S")
root.config(bg="#F00") #para debug 
root.iconbitmap("unsam.ico")
root.state('zoomed')


# GLOBAL VARIABLES
MF_W = IntVar(value=1920)
MF_H = IntVar(value=980)
CV_W = IntVar(value=0)
CV_H = IntVar(value=0)
info_text = StringVar(value="SAURUS V1.9")
info_cv = BooleanVar(value=False)
axis_cv = BooleanVar(value=False)
report_flag = BooleanVar(value=False)
layout_cv = IntVar(value=1)

#MEMORY READ

if os.path.isfile('startup_cfg.txt'):
    with open('startup_cfg.txt','r') as f:
        lines = f.readlines()
        lines = [line.rstrip().split(":") for line in lines]
        
        for var in lines:
            if var[1] == "False": var[1] = False
            if var[0] == "axis_cv": axis_cv.set(var[1])
            elif var[0] == "info_cv": info_cv.set(var[1])
            elif var[0] == "layout_cv": layout_cv.set(int(var[1]))

#TEMP DIRECTORY CREATION

try:
    os.makedirs("temp_img", exist_ok = True)
except OSError as error:
    print("Problema para crear el directorio de temp_img")

#MAIN WINDOW DISPLAY
windows_creator()
menu_creator()



root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

#------------------------------------------------------------------------------


# COSAS Q FALTAN AGREGAR

"""
Report ID automatico
Patient AGE -> habria q calcular con el patient date birth [0:4] (año y restarlo al actual o algo asi)
Estudio realizado por  ? lo pone el médico o lo pongo abajo con el simbolioto para poner firma?
Indicado por? lo pongo arriba en historia clinica o no?
Guardar reporte en direccion destino (ver problema de q si cambio path no lee bien las temp_img creo)
Guardar estado de reporte -> observaciones, imagenes, rois, secuencias (sin cambiar layout porq se complica)
(a verse de hacer) size layout dinamico que rehaga todas las secuencias y fixee los sizes de las secuencias y rois (con mediciones)

"""