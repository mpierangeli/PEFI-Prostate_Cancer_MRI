from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
from pydicom import dcmread
from numpy import asarray, zeros, ogrid, sqrt, ceil
import math
from imutils import resize
import os
from shutil import rmtree
from cv2 import convertScaleAbs
from pylatex import Document, PageStyle, Foot, MiniPage, VerticalSpace, SmallText, Package, StandAloneGraphic, MediumText, NewPage
from pylatex.utils import NoEscape, bold, italic
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)  #FIX DE DPI-WINDOWS -> 100% resolución

## OBJETOS

class roi_square:
    def __init__(self, name, sec):
        self.name = name
        self.insec = sec
        self.inslice = sec.slice
    def init_coord(self,xi,yi):
        self.xi = (xi-(CV_W.get()-self.insec.incv_width)/2)/self.insec.incv_width # posicion de x en porcentaje dentro de la imagen
        self.yi = (yi-(CV_H.get()-self.insec.incv_height)/2)/self.insec.incv_height # posicion de y en porcentaje dentro de la imagen
    def end_coord(self,xf,yf):
        self.xf = (xf-(CV_W.get()-self.insec.incv_width)/2)/self.insec.incv_width
        self.yf = (yf-(CV_H.get()-self.insec.incv_height)/2)/self.insec.incv_height
        self.update_coord()
    def update_coord(self):
        self.xi_ = (self.xi*self.insec.incv_width+(CV_W.get()-self.insec.incv_width)/2)
        self.yi_ = (self.yi*self.insec.incv_height+(CV_H.get()-self.insec.incv_height)/2)
        self.xf_ = (self.xf*self.insec.incv_width+(CV_W.get()-self.insec.incv_width)/2)
        self.yf_ = (self.yf*self.insec.incv_height+(CV_H.get()-self.insec.incv_height)/2)
        self.dx = self.xf_-self.xi_
        self.dy = self.yf_-self.yi_
    def draw(self,temporal):
        self.insec.incv.delete(self.name)
        if temporal:
            self.insec.incv.create_rectangle(self.xi_,self.yi_,self.xf_,self.yf_,outline="#A00",tags=self.name,dash=(7,))
        else:
            self.name = self.name + "_"
            self.insec.incv.create_rectangle(self.xi_,self.yi_,self.xf_,self.yf_,outline="#F00",tags=self.name)
        a = -10 if self.dx>0 else 10
        b = -10 if self.dy>0 else 10
        self.xdis = abs(round(self.insec.realx*self.dx,2))
        self.ydis = abs(round(self.insec.realy*self.dy,2))
        self.insec.incv.create_text((self.xf_+self.xi_)/2,self.yi_+b,text=str(self.xdis)+"mm",fill="#F00",font=("Roboto", 9),tags=self.name)
        self.insec.incv.create_text(self.xi_+a,(self.yf_+self.yi_)/2,text=str(self.ydis)+"mm",fill="#F00",font=("Roboto", 9),tags=self.name,angle=90)
class roi_circle:
    def __init__(self,name,sec):
        self.name = name
        self.insec = sec
        self.inslice = sec.slice
    def init_coord(self,xi,yi):
        self.xi = (xi-(CV_W.get()-self.insec.incv_width)/2)/self.insec.incv_width # posicion de x en porcentaje dentro de la imagen
        self.yi = (yi-(CV_H.get()-self.insec.incv_height)/2)/self.insec.incv_height # posicion de y en porcentaje dentro de la imagen
    def end_coord(self,xf,yf):
        self.xf = (xf-(CV_W.get()-self.insec.incv_width)/2)/self.insec.incv_width
        self.yf = (yf-(CV_H.get()-self.insec.incv_height)/2)/self.insec.incv_height
        self.update_coord()
    def update_coord(self):
        self.xi_ = (self.xi*self.insec.incv_width+(CV_W.get()-self.insec.incv_width)/2)
        self.yi_ = (self.yi*self.insec.incv_height+(CV_H.get()-self.insec.incv_height)/2)
        self.xf_ = (self.xf*self.insec.incv_width+(CV_W.get()-self.insec.incv_width)/2)
        self.yf_ = (self.yf*self.insec.incv_height+(CV_H.get()-self.insec.incv_height)/2)
        self.dx = abs(self.xf_-self.xi_)
        self.dy = abs(self.yf_-self.yi_)
        self.r = math.sqrt(self.dx**2+self.dy**2)
    def draw(self,temporal):
        self.insec.incv.delete(self.name)
        if temporal:
            self.insec.incv.create_oval(self.xi_-self.r,self.yi_-self.r,self.xi_+self.r,self.yi_+self.r,outline="#A00",dash=(7,),tags=self.name)
        else:
            self.name = self.name + "_"
            self.insec.incv.create_oval(self.xi_-self.r,self.yi_-self.r,self.xi_+self.r,self.yi_+self.r,outline="#F00",tags=self.name)
        self.rdis = math.sqrt((self.dx*self.insec.realx)**2+(self.dy*self.insec.realy)**2) # Porq distancia real depende del ancho de pixel en cada dirección.
        self.insec.incv.create_text(self.xi_,self.yi_+self.r+10,text="r: "+str(round(self.rdis,2))+"mm",fill="#F00",font=("Roboto", 9),tags=self.name)
class roi_ruler:
    def __init__(self,name,sec):
        self.name = name
        self.insec = sec
        self.inslice = sec.slice
    def init_coord(self,xi,yi):
        self.xi = (xi-(CV_W.get()-self.insec.incv_width)/2)/self.insec.incv_width # posicion de x en porcentaje dentro de la imagen
        self.yi = (yi-(CV_H.get()-self.insec.incv_height)/2)/self.insec.incv_height # posicion de y en porcentaje dentro de la imagen
    def end_coord(self,xf,yf):
        self.xf = (xf-(CV_W.get()-self.insec.incv_width)/2)/self.insec.incv_width
        self.yf = (yf-(CV_H.get()-self.insec.incv_height)/2)/self.insec.incv_height
        self.update_coord()
    def update_coord(self):
        self.xi_ = (self.xi*self.insec.incv_width+(CV_W.get()-self.insec.incv_width)/2)
        self.yi_ = (self.yi*self.insec.incv_height+(CV_H.get()-self.insec.incv_height)/2)
        self.xf_ = (self.xf*self.insec.incv_width+(CV_W.get()-self.insec.incv_width)/2)
        self.yf_ = (self.yf*self.insec.incv_height+(CV_H.get()-self.insec.incv_height)/2)
        self.dx = self.xf_-self.xi_
        self.dy = self.yf_-self.yi_
    def draw(self,temporal):
        self.insec.incv.delete(self.name)
        if temporal:
            self.insec.incv.create_line(self.xi_,self.yi_,self.xf_,self.yf_,fill="#1BB",dash=(3,),arrow=BOTH,tags=self.name)
        else:
            self.name = self.name + "_"
            self.insec.incv.create_line(self.xi_,self.yi_,self.xf_,self.yf_,fill="#2CC",arrow=BOTH,tags=self.name)
        self.ang = abs(math.degrees(math.atan((-self.dy)/(-self.dx+1e-6))))
        self.rdis = math.sqrt((self.dx*self.insec.realx)**2+(self.dy*self.insec.realy)**2) # Porq distancia real depende del ancho de pixel en cada dirección.
        a = 10
        b = 10
        if int(self.dx) == 0: b -= 10
        elif int(self.dy) == 0: a -= 10
        elif self.dx*self.dy > 0: 
            self.ang = -self.ang
            a -= 20
        self.insec.incv.create_text((self.xf_+self.xi_)/2+a,(self.yf_+self.yi_)/2+b,text=str(round(self.rdis,2))+"mm",fill="#2CC",font=("Roboto", 9),tags=self.name,angle=self.ang)
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
        self.zoom = 1       # multiplicador del tamaño de canvas "incv"
    def add_dcm(self,dcm):
        self.dcm_serie.append(dcm)  # serie de dicoms
        if dcm.pixel_array.shape[0] > self.height: self.height = dcm.pixel_array.shape[0] 
        if dcm.pixel_array.shape[1] > self.width: self.width = dcm.pixel_array.shape[1]
    def load_img_serie(self,*kwargs):
        self.isloaded = True
        if not self.aux_view:
            self.depth = len(self.dcm_serie)    # cantidad de slices de la secuencia
            self.img_serie = zeros((self.depth,self.height,self.width))  # serie de imagenes
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
                self.img_serie = zeros((self.depth,self.height,self.width))
                for i in range(self.depth): # por cada columna de las axiales -> profundidad de la sagital
                    for j in range(self.parent.img_serie.shape[0]): # por cada imagen axial -> altura de la sagital
                        for k in range(self.factor): # por ancho de tomo axial, repito misma muestra
                            self.img_serie[i,j*self.factor+k] = self.parent.img_serie[j,:,i]
                self.realx = self.parent.realy
            elif tipo == "atoc":
                self.depth = self.parent.img_serie.shape[1]
                self.width = self.parent.img_serie.shape[2]
                self.height = self.factor*self.parent.img_serie.shape[0]
                self.img_serie = zeros((self.depth,self.height,self.width))
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
        self.img_serie_cte = zeros((self.depth,self.img_serie.shape[1],self.img_serie.shape[2]))  # serie de imagenes
        
        if self.aux_view:   self.alpha = 1    # parametro de contraste
        else:               self.alpha = 0.2 
        self.beta = 0       # parametro de brillo
            
        for n in range(self.depth):
            self.img_serie_cte[n] = self.img_serie[n]
            if not self.aux_view:
                self.img_serie[n] = convertScaleAbs(self.img_serie_cte[n], alpha=self.alpha, beta=self.beta)
        
    def adjust_img_serie(self,a,b):
        self.alpha += a
        self.beta += b
        for n in range(self.depth):
            self.img_serie[n] = convertScaleAbs(self.img_serie_cte[n], alpha=self.alpha, beta=self.beta)
class observacion:
    def __init__(self,id):
        self.id = id        #numero de observacion para identificacion
        self.imagenes = []  #donde guardo los strings de direccion de imagenes para el html
        self.location = "?"   #nombre de la zona afectada
        self.eep = "?"       #checkbox de eep
        self.lesionT2 = 0 # clasificacion pirads(1-5)
        self.lesionDWI = 0
        self.lesionDCE = 0 # [visible en secuencia]
        self.info = "?"      #texto informativo escrito a mano
        self.medidas = 0  #largo eje mayor de lesion 
        self.categoria = 0  #SEGUN PIRADS FINAL
class prostata:
    def __init__(self):
        self.volumen = 0
        self.medidas = [0,0,0]
        self.categoria = 0   
        self.psa = [0,0,0,0,0] # PSA, fPSA, DD/MM/AA
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
        self.uretra = "?"
        self.indicado = "?"
        self.institu = "?"
        
## FUNCIONES
def on_closing():
    if messagebox.askokcancel("Salir", "Todas las observaciones se perderán al salir."):
        rmtree("temp_img")
        
        with open('startup_cfg.txt','w') as f:
            f.write("axis_cv:"+str(axis_cv.get())+"\ninfo_cv:"+str(info_cv.get())+"\nlayout_cv:"+str(layout_cv.get()))
            
        root.destroy()

def windows_creator():
    
    global main_frame, bot_frame, info_label, startupCVs, pb

    main_frame = Frame(root, width=MF_W.get(), height=MF_H.get(), background="#222") 
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
    startupCVs = True
    
    s = ttk.Style()
    s.theme_use('clam')
    s.configure("bar.Horizontal.TProgressbar", troughcolor="#333", bordercolor="#222", background="#2CC", lightcolor="#2CC",darkcolor="#2CC")
    t = ttk.Style()
    t.theme_use('clam')
    t.configure("custom.TCombobox", bordercolor="#444", background="#2CC", lightcolor="#555", darkcolor="#555")

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
    helpmenu.add_command(label="Keybinds",command=keybinds_main)
    helpmenu.add_command(label="Acerca de...")
    helpmenu.add_separator()
    helpmenu.add_command(label="Salir", command=on_closing)

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
    portablemenu.add_cascade(label = "Proyecciones", menu = portableviewmenu)
    portablemenu.add_separator()
    portablemenu.add_command(label="Curva DCE",command = dce_curve)
    portablemenu.add_separator()
    portablemenu.add_command(label = "Metadata", command = info_tab_gen)
    portablemenu.add_command(label = "Limpiar", command = clear_cv)
    portablemenu.add_separator()
    portablemenu.add_command(label = "Nueva Secuencia", command = sec_selector)

def report_main():
    if report_flag.get():
        report_window.destroy()
        report_flag.set(False)
    else:
        report_flag.set(True)
        refresh_report()

def change_report_page(num_page: int):
    global selected_tab
    selected_tab = num_page
    refresh_report()

def refresh_report():
    global report_window,b1,b2,tabs
    try: report_window.destroy()
    except: pass
    try: steps_levels.destroy()
    except: pass
    report_window = Frame(root,background="#333")
    report_window.place(relx=0,rely=0, height=MF_H.get(), width=MF_W.get()/2)
    Label(report_window, text="REPORTE PI-RADS",bg="#2CC",font=("Roboto",15),fg="#000").pack(fill=X,ipady=10)
    Label(report_window, text="PANEL DE OBSERVACIONES",bg="#2CC",font=("Roboto",13),fg="#000").pack(fill=X,pady=(0,20))
    b1 = Button(report_window, text="NUEVA OBSERVACIÓN", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2", command=lambda tipo="new":obs_setup(tipo))
    b1.pack(fill=X,pady=(0,10), ipady=10)
    b1.bind("<Enter>",lambda b=b1:colorOnFocus(b,True,"#F80","#2CC"))
    b1.bind("<Leave>",lambda b=b1:colorOnFocus(b,False,"#F80","#2CC"))
    tabs_window = Frame(report_window,background="#333")
    tabs_window.pack(anchor="center",pady=(0,10))
    
    if len(observaciones)>0:
        obs_window = Frame(report_window,background="#333")
        obs_window.pack(fill=X)
        if screen_h > 900: tabs = 5
        elif screen_h > 800: tabs = 4
        else: tabs = 3
        for i in range(int(ceil(len(observaciones)/tabs))):
            ff = "#2CC" if selected_tab == i+1 else "#000"
            b_tab = Button(tabs_window, text=str(i+1), font=("Roboto",12),bg="#444", fg=ff, bd=0, cursor="hand2", command=lambda new_sel_tab=i+1:change_report_page(new_sel_tab))
            b_tab.pack(side=LEFT,ipadx=20,ipady=1,padx=(0,5))
            b_tab.bind("<Enter>",lambda b=b_tab:colorOnFocus(b,True,"#666","#444"))
            b_tab.bind("<Leave>",lambda b=b_tab:colorOnFocus(b,False,"#666","#444"))
            
        for n, obs in enumerate(observaciones[(selected_tab-1)*tabs:(selected_tab-1)*tabs+tabs]):
            mini_report = Frame(obs_window,background="#444")
            mini_report.pack(fill=X,pady=(0,5),ipadx=2, ipady=2)
            b6 = Button(mini_report, text="Del.", font=("Roboto",12,"bold"), bg="#A55", cursor="hand2", bd=0, command=lambda to_destroy=n:del_obs(to_destroy))
            b6.pack(side=LEFT,ipadx=1,fill=Y,padx=5)
            b7 = Button(mini_report, text="Edit", font=("Roboto",12,"bold"), bg="#AA5", cursor="hand2", bd=0, command=lambda to_edit=n:edit_obs(to_edit))
            b7.pack(side=LEFT,ipadx=1,fill=Y)
            b6.bind("<Enter>",lambda b=b6:colorOnFocus(b,True,"#B66","#A55"))
            b6.bind("<Leave>",lambda b=b6:colorOnFocus(b,False,"#B66","#A55"))
            b7.bind("<Enter>",lambda b=b7:colorOnFocus(b,True,"#BB6","#AA5"))
            b7.bind("<Leave>",lambda b=b7:colorOnFocus(b,False,"#BB6","#AA5"))
            temp_bg = "#555"
            if obs.categoria == 1: temp_bg = "#0F0"
            elif obs.categoria == 2: temp_bg = "#AF0"
            elif obs.categoria == 3: temp_bg = "#FF0"
            elif obs.categoria == 4: temp_bg = "#F90"
            elif obs.categoria == 5: temp_bg = "#F00"
            Label(mini_report, text="PI-RADS "+str(obs.categoria),bg=temp_bg,font=("Roboto",12,"bold"),fg="#000").pack(side=RIGHT,padx=(0,30),fill=Y,ipadx=1)
            Label(mini_report, text="ID:"+str(obs.id),bg="#444",font=("Roboto",9),fg="#FFF").pack(anchor=W,padx=(15,0))
            Label(mini_report, text="Ubicación: "+obs.location,bg="#444",font=("Roboto",9),fg="#FFF").pack(anchor=W,padx=(15,0))
            Label(mini_report, text="Tamaño: "+str(obs.medidas[0])+" mm",bg="#444",font=("Roboto",9),fg="#FFF").pack(anchor=W,padx=(15,0))
            Label(mini_report, text="Descripción:",bg="#444",font=("Roboto",9),fg="#FFF").pack(anchor=W,padx=(15,0))
            des = Text(mini_report,bg="#444",font=("Roboto",9),fg="#FFF",height=3,width=100,bd=0)
            des.pack(anchor=W,padx=(15,0))
            T =  obs.info
            des.insert(END,T)
        b2 = Button(report_window, text="INICIAR REPORTE", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2",command=lambda tipo="create":obs_setup(tipo))
        b2.pack(side=BOTTOM,fill=X,ipady=10,pady=10)
    else:
        b2 = Button(report_window, text="INICIAR REPORTE", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2", state="disabled")
        b2.pack(side=BOTTOM,fill=X,ipady=10,pady=10)
    b2.bind("<Enter>",lambda b=b2:colorOnFocus(b,True,"#F80","#2CC"))
    b2.bind("<Leave>",lambda b=b2:colorOnFocus(b,False,"#F80","#2CC"))

def keybinds_main():
    if keybinds_flag.get():
        keybinds_window.destroy()
        keybinds_flag.set(False)
    else:
        keybinds_flag.set(True)
        keybinds_window_creator()

def keybinds_window_creator():
    global keybinds_window
    try: keybinds_window.destroy()
    except: pass
    keybinds_window = Frame(root,background="#333")
    keybinds_window.place(relx=0,rely=0, height=MF_H.get(), width=MF_W.get()/4)
    Label(keybinds_window, text="Controles",bg="#2CC",font=("Roboto",18),fg="#000").pack(fill=X,ipady=10,pady=(0,20))
    Label(keybinds_window, text='"Control" + "Ruedita" | Selección de corte/slices',bg="#333",font=("Roboto",13),fg="#FFF").pack(fill=X,ipady=10)
    Label(keybinds_window, text='"Shift" + "Ruedita" | Zoom in/out',bg="#333",font=("Roboto",13),fg="#FFF").pack(fill=X,ipady=10)
    Label(keybinds_window, text='"Flechas UP y DOWN" | Control Brillo',bg="#333",font=("Roboto",13),fg="#FFF").pack(fill=X,ipady=10)
    Label(keybinds_window, text='"Flechas LEFT y RIGHT" | Control Contraste',bg="#333",font=("Roboto",13),fg="#FFF").pack(fill=X,ipady=10)
    
def colorOnFocus(b: Button, n: bool, color_on: str, color_off: str):
    if n:   b.widget.config(background=color_on)
    else:   b.widget.config(background=color_off)

def validate(P):
    if len(P) == 0: 
        return True
    if ((len(P) <= 5) and (float(P) > 0)):
        return True
    else:
        return False
def validate2(P):
    if len(P) == 0: 
        return True
    if ((len(P) <= 2) and (int(P) > 0)):
        return True
    else:
        return False
        
def obs_setup(tipo: str):
    global obs_id,prostata_flag,lesion_flag,prosta,medidas
    prostata_flag = False
    
    if tipo == "new":
        observaciones.append(observacion(obs_id))
        obs_id += 1
        report_window.destroy()
        lesion_flag = True
        steps_main(1)
    elif tipo == "edit":
        report_window.destroy()
        steps_main(1)
    elif tipo == "bypassed":
        observaciones[-1].medidas = medidas
        medidas = []
        steps_levels.destroy()
        steps_main(2)
    elif tipo == "create":
        for obs in observaciones:
            if obs.categoria == 0: 
                messagebox.showwarning(title="Reporte de Observaciones", message="Una o más observaciones están incompletas")
                return
        report_window.destroy()
        prostata_flag = True
        prosta = prostata()
        steps_main(1)
    elif tipo == "end":
        prosta.volumen = vol
        prosta.medidas = medidas
        medidas = []
        steps_levels.destroy()
        steps_main(4)
        
def steps_main(step: int):
    global steps_window,steps_levels, zona_label, dce_check, catT2,catDWI, eep, info, mapa_flag, psa_value, fpsa_value, psa_date1, psa_date2, psa_date3, t1,t2,t3,t4,t5,t6,hemo,neuro,vesi,huesos,organos,linfa,uretra, auxframe2, zona, lesion_flag, institu, selected_tab
    mapa_flag = False
    intra_pad = int(MF_H.get()*0.0185)  # para hacer pad dinámico
    if step == 1:
        steps_levels = Frame(root,background="#2CC")
        steps_levels.place(relx=0.5,rely=0.05, height=40,anchor=CENTER)
        
        if prostata_flag:   
            to_text = "Seleccione los 3 ejes de la próstata"
        else:   
            to_text = "Seleccione el eje mayor de la lesión"
        Label(steps_levels, text=to_text,bg="#2CC",font=("Roboto",12),fg="#000").pack(ipady=5,ipadx=20)
        vol_calculator()
    elif step == 2:
        steps_levels = Toplevel(root,background="#444")
        steps_window = Frame(steps_levels,background="#444")
        steps_window.pack(side=LEFT,fill=Y)
        Label(steps_window, text="Sobre la lesión...",bg="#2CC",font=("Roboto",12),fg="#000").pack(fill=X,ipady=5,ipadx=20)
        
        aux = Frame(steps_window,background="#555")
        aux.pack(fill=X,ipady=5,pady=(intra_pad,intra_pad+10))
        zona = StringVar(value="Seleccione Zona Afectada")
        zona_label = Label(aux, textvariable=zona,bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        b1 = Button(aux, text="Mapa >>", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2",height=1,command=mapa_show)
        b1.pack(side=RIGHT,ipadx=5)
        b1.bind("<Enter>",lambda b=b1:colorOnFocus(b,True,"#F80","#2CC"))
        b1.bind("<Leave>",lambda b=b1:colorOnFocus(b,False,"#F80","#2CC"))
        aux = Frame(steps_window,background="#555")
        aux.pack(fill=X,ipady=2)
        Label(aux, text="Lesión en T2",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        pirads_opt = [1,2,3,4,5]
        aux2 = Frame(steps_window,background="#555")
        aux2.pack(fill=X,ipady=2,pady=(0,5))
        Label(aux2, text="Categoría PI-RADS:",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        catT2 = IntVar()
        for n in range(5):
            Radiobutton(aux2, text=str(pirads_opt[n]), variable=catT2, value=pirads_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        
        aux6 = Frame(steps_window,background="#555")
        aux6.pack(fill=X,ipady=2)
        Label(aux6, text="Lesión en DWI",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        aux7 = Frame(steps_window,background="#555")
        aux7.pack(fill=X,ipady=2)
        Label(aux7, text="Categoría PI-RADS:",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        catDWI = IntVar()
        for n in range(5):
            Radiobutton(aux7, text=str(pirads_opt[n]), variable=catDWI, value=pirads_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        
        aux3 = Frame(steps_window,background="#555")
        aux3.pack(fill=X,ipady=2,pady=(intra_pad,0))
        Label(aux3, text="DCE",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
        dce_check = IntVar()
        Checkbutton(aux3,text="Visible",variable=dce_check,onvalue=1,offvalue=0,bg="#555",foreground="#FFF",selectcolor="#444",bd=0).pack(side=LEFT)

        aux8 = Frame(steps_window,background="#555")
        aux8.pack(fill=X,ipady=2,pady=(intra_pad,10))  
        Label(aux8, text="Extensión Extraprostática",bg="#555",font=("Roboto",11),fg="#FFF").pack(fill=X,padx=20,ipady=5)
        eep = StringVar()
        auxframe = Frame(aux8)
        auxframe.pack(padx=20)
        eep_opt = ["Bajo","Medio","Alto","Muy Alto"]
        for n in range(4):
            Radiobutton(auxframe, text=eep_opt[n], variable=eep, value=eep_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    
        Label(steps_window, text="Información Adicional",bg="#444",font=("Roboto",11),fg="#FFF",anchor=W).pack(fill=X,pady=(intra_pad,10),padx=30)
        info = Text(steps_window,width=62,font=("Roboto",10),height=6,bg="#555",fg="#FFF",bd=0,insertbackground="#2CC")
        info.pack()
        auxframe2 = Frame(steps_window,bg="#444")
        auxframe2.pack(padx=30,pady=intra_pad,anchor=W)
        b3 = Button(auxframe2, text="Agregar Imágenes", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2",command=save_cv)
        b3.pack(ipadx=2,ipady=2,pady=(0,20))
        b4 = Button(steps_window, text="Guardar Observación", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2",height=3,command=lambda step=3:steps_main(step))
        b4.pack(fill=X,side=BOTTOM)
        b3.bind("<Enter>",lambda b=b3:colorOnFocus(b,True,"#F80","#2CC"))
        b3.bind("<Leave>",lambda b=b3:colorOnFocus(b,False,"#F80","#2CC"))
        b4.bind("<Enter>",lambda b=b4:colorOnFocus(b,True,"#F80","#2CC"))
        b4.bind("<Leave>",lambda b=b4:colorOnFocus(b,False,"#F80","#2CC"))
        
    elif step == 3:
        observaciones[-1].location = zona.get()
        observaciones[-1].lesionT2 = catT2.get()
        observaciones[-1].lesionDWI = catDWI.get()
        observaciones[-1].lesionDCE = dce_check.get()
        observaciones[-1].eep = eep.get()
        observaciones[-1].info = info.get("1.0","end-1c")
        observaciones[-1].categoria = pirads_lesion(observaciones[-1])
        steps_levels.destroy()
        if len(observaciones) == 1: 
            selected_tab = 1
            refresh_report()
        else:
            change_report_page(int(ceil(len(observaciones)/tabs)))
        
    elif step == 4:
        steps_levels = Toplevel(root,background="#444")
        steps_title = Frame(steps_levels,background="#444")
        steps_title.pack(side=TOP,fill=X)
        Label(steps_title, text="Redacción de Informe",bg="#2CC",font=("Roboto",12),fg="#000").pack(fill=X,ipady=5,ipadx=20,pady=(0,10))
        steps_window = Frame(steps_levels,background="#444")
        steps_window.pack(side=LEFT,fill=Y)
        
        info_general = Frame(steps_window,background="#555")
        info_general.pack(fill=X,ipadx=2, ipady=2,pady=(0,5))
        
        Label(info_general, text="Paciente: "+str(secuencias[0].dcm_serie[0].PatientName),bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
        Label(info_general, text="Edad: "+str(int(secuencias[0].dcm_serie[0].PatientAge[:3]))+" años | Sexo: "+str(secuencias[0].dcm_serie[0].PatientSex),bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
        Label(info_general, text="Volúmen Prostático: "+str(prosta.volumen)+" ml | Dimensiones: "+str(prosta.medidas[0])+"x"+str(prosta.medidas[1])+"x"+str(prosta.medidas[2])+" mm",bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
        
        Label(steps_window, text="Historial Clínico",bg="#444",font=("Roboto",11),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
        
        historial = Frame(steps_window,background="#555")
        historial.pack(fill=X,ipadx=2, ipady=2, pady=(0,5))
        
        auxframe1 = Frame(historial,bg="#555")
        auxframe1.pack(anchor=W,pady=5)
        
        Label(auxframe1, text="PSA:",bg="#555",font=("Roboto",10),fg="#FFF",width=10).pack(side=LEFT,padx=5)
        psa_value = Entry(auxframe1,width=5,font=("Roboto",12),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC", validate="key", validatecommand=(root.register(validate), '%P'))
        psa_value.pack(side=LEFT)
        Label(auxframe1, text="f PSA:",bg="#555",font=("Roboto",10),fg="#FFF",width=7).pack(side=LEFT)
        fpsa_value = Entry(auxframe1,width=5,font=("Roboto",12),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC", validate="key", validatecommand=(root.register(validate), '%P'))
        fpsa_value.pack(side=LEFT)
        Label(auxframe1, text="Fecha(DD/MM/AA):",bg="#555",font=("Roboto",10),fg="#FFF",width=15).pack(side=LEFT)
        psa_date1= Entry(auxframe1,width=2,font=("Roboto",12),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC", validate="key", validatecommand=(root.register(validate2), '%P'))
        psa_date1.pack(side=LEFT,padx=(0,2))
        Label(auxframe1, text="/",bg="#555",font=("Roboto",10),fg="#FFF",width=1).pack(side=LEFT)
        psa_date2= Entry(auxframe1,width=2,font=("Roboto",12),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC", validate="key", validatecommand=(root.register(validate2), '%P'))
        psa_date2.pack(side=LEFT,padx=(0,2))
        Label(auxframe1, text="/",bg="#555",font=("Roboto",10),fg="#FFF",width=1).pack(side=LEFT)
        psa_date3= Entry(auxframe1,width=2,font=("Roboto",12),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC", validate="key", validatecommand=(root.register(validate2), '%P'))
        psa_date3.pack(side=LEFT,padx=(0,2))
        
        auxframe5 = Frame(historial,background="#555")
        auxframe5.pack(fill=X,pady=5)
        Label(auxframe5, text="Motivo\nEstudio:",bg="#555",font=("Roboto",10),fg="#FFF",width=10).pack(side=LEFT,padx=5)
        t1 = Text(auxframe5,width=55,height=4,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        t1.pack(side=LEFT)
        
        auxframe6 = Frame(historial,background="#555")
        auxframe6.pack(fill=X)
        Label(auxframe6, text="Indicado por:",bg="#555",font=("Roboto",10),fg="#FFF",width=10).pack(side=LEFT,padx=5)
        t6 = Text(auxframe6,width=55,height=1,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        t6.pack(side=LEFT)
        
        Label(steps_window, text="Informe de Resultados",bg="#444",font=("Roboto",11),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
        
        estudio_info2 = Frame(steps_window,background="#555")
        estudio_info2.pack(fill=X,ipadx=2, ipady=2, pady=(0,5))
        
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
        
        separator = Frame(steps_levels,background="#444")
        separator.pack(side=LEFT,fill=Y,ipadx=2)
        
        steps_window2 = Frame(steps_levels,background="#444")
        steps_window2.pack(side=RIGHT,fill=Y)
        
        estudio_info = Frame(steps_window2,background="#555")
        estudio_info.pack(fill=X,ipadx=2, ipady=2, pady=(0,5))
        
        hemo = StringVar()
        neuro = StringVar()
        vesi = StringVar()
        linfa = StringVar()
        huesos = StringVar()
        organos = StringVar()
        uretra = StringVar()
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
        a6 = Frame(m0,bg="#555")
        a6.pack(pady=1)
        Label(a6, text="Lesión Uretra:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
        Radiobutton(a6, text="Si", variable=uretra, value="Si", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        Radiobutton(a6, text="No", variable=uretra, value="No", bg="#555",foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
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
        
        Label(steps_window2, text="Observaciones Realizadas",bg="#444",font=("Roboto",11),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
        
        lesiones_info = Frame(steps_window2,background="#555")
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
        
        Label(steps_window2, text="Conclusiones",bg="#444",font=("Roboto",11),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W) 
        t5 = Text(steps_window2,width=65,height=7,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
        t5.pack(pady=(0,5))
        
        estudio_info10 = Frame(steps_window2,background="#444")
        estudio_info10.pack(fill=X,ipadx=2, ipady=2, pady=(0,5))
        auxframe10 = Frame(estudio_info10,bg="#444")
        auxframe10.pack(anchor=W,pady=5)
        Label(auxframe10, text="Estudio realizado en: ",bg="#444",font=("Roboto",11),fg="#FFF",width=15).pack(side=LEFT,padx=10)
        instituciones = ["CEUNIM - UNSAM","Corporación Médica","Diagnóstico Tesla"]
        institu = ttk.Combobox(auxframe10, state="readonly", values = instituciones,width=40,style='custom.TCombobox')
        institu.pack(side=LEFT)
        
        b4 = Button(steps_window2, text="Finalizar y Generar PDF", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2",height=3,command=lambda step=5:steps_main(step))
        b4.pack(fill=X,side=BOTTOM)
        b4.bind("<Enter>",lambda b=b4:colorOnFocus(b,True,"#F80","#2CC"))
        b4.bind("<Leave>",lambda b=b4:colorOnFocus(b,False,"#F80","#2CC"))
    
    elif step == 5:
        prosta.psa = [psa_value.get(),fpsa_value.get(),psa_date1.get(),psa_date2.get(),psa_date3.get()]
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
        prosta.uretra = uretra.get()
        prosta.institu = institu.get()
        
        steps_levels.destroy()
        mapa_pirads_gen()
        fp = filedialog.askdirectory(title="Guardar Reporte")
        fp.replace("\\","/")
        generator(fp)
        
def edit_obs(n: int):
    global steps_window,steps_levels, zona_label, t2_check,dce_check,dwi_check,catT2,catDWI, eep, info, mapa_flag, auxframe2, zona
    intra_pad = int(MF_H.get()*0.0185)
    report_window.destroy()
    obs = observaciones[n]
    steps_levels = Toplevel(root,background="#444")
    steps_window = Frame(steps_levels,background="#444")
    steps_window.pack(side=LEFT,fill=Y)
    Label(steps_window, text="Sobre la lesión...",bg="#2CC",font=("Roboto",12),fg="#000").pack(fill=X,ipady=5,ipadx=20)
    
    aux = Frame(steps_window,background="#555")
    aux.pack(fill=X,ipady=5,pady=(intra_pad,intra_pad+10))
    zona = StringVar(value=obs.location)
    zona_label = Label(aux, textvariable=zona,bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    b1 = Button(aux, text="Mapa >>", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2",height=1,command=mapa_show)
    b1.pack(side=RIGHT,ipadx=5)
    
    aux = Frame(steps_window,background="#555")
    aux.pack(fill=X,ipady=2)
    Label(aux, text="Lesión en T2",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    pirads_opt = [1,2,3,4,5]
    aux2 = Frame(steps_window,background="#555")
    aux2.pack(fill=X,ipady=2,pady=(0,5))
    Label(aux2, text="Categoría PI-RADS:",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    catT2 = IntVar(value=obs.lesionT2)
    for n in range(5):
        Radiobutton(aux2, text=str(pirads_opt[n]), variable=catT2, value=pirads_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    
    aux6 = Frame(steps_window,background="#555")
    aux6.pack(fill=X,ipady=2)
    Label(aux6, text="Lesión en DWI",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    aux7 = Frame(steps_window,background="#555")
    aux7.pack(fill=X,ipady=2)
    Label(aux7, text="Categoría PI-RADS:",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    catDWI = IntVar(value=obs.lesionDWI)
    for n in range(5):
        Radiobutton(aux7, text=str(pirads_opt[n]), variable=catDWI, value=pirads_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    
    aux3 = Frame(steps_window,background="#555")
    aux3.pack(fill=X,ipady=2,pady=(intra_pad,0))
    Label(aux3, text="DCE",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    dce_check = IntVar(value=obs.lesionDCE)
    Checkbutton(aux3,text="Visible",variable=dce_check,onvalue=1,offvalue=0,bg="#555",foreground="#FFF",selectcolor="#444",bd=0).pack(side=LEFT)

    aux8 = Frame(steps_window,background="#555")
    aux8.pack(fill=X,ipady=2,pady=(intra_pad,10))  
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
    auxframe2.pack(padx=30,pady=intra_pad,anchor=W)
    b3 = Button(auxframe2, text="Agregar Imágenes", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2",command=save_cv)
    b3.pack(ipadx=2,ipady=2,pady=(0,intra_pad))
    for n,img in enumerate(obs.imagenes):
        Label(auxframe2, text="added obs_"+str(obs.id)+"_"+str(n+1)+".png",bg="#444",font=("Roboto",11),fg="#FFF",anchor=W).pack(fill=X,ipady=1,ipadx=1)
    b4 = Button(steps_window, text="Guardar Cambios", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2",height=3,command=lambda obs=obs: confirm_edit(obs))
    b4.pack(fill=X,side=BOTTOM)
    b3.bind("<Enter>",lambda b=b3:colorOnFocus(b,True,"#F80","#2CC"))
    b3.bind("<Leave>",lambda b=b3:colorOnFocus(b,False,"#F80","#2CC"))
    b4.bind("<Enter>",lambda b=b4:colorOnFocus(b,True,"#F80","#2CC"))
    b4.bind("<Leave>",lambda b=b4:colorOnFocus(b,False,"#F80","#2CC"))

def confirm_edit(obs: observacion):
    obs.location = zona.get()
    obs.lesionT2 = catT2.get()
    obs.lesionDWI = catDWI.get()
    obs.lesionDCE = dce_check.get()
    obs.eep = eep.get()
    obs.info = info.get("1.0","end-1c")
    obs.categoria = pirads_lesion(obs)
    steps_levels.destroy()
    refresh_report()
    
def mapa_pirads_gen():
    mapa = asarray(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"saurus_img","sector_map_v21_bnw2.png")))
    mapa_colores = asarray(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"saurus_img","sector_map_v21_mask.png")))
    pirads_colores = [[0,255,0],[170,255,0],[255,255,0],[255,133,0],[255,0,0]] #color para piradas 1,2,3,4,5 segun reporte
    for obs in observaciones:
        for RGB_code in RGB_codes:
            if obs.location == RGB_code[3]:
                mask = (mapa_colores[:,:,0] == RGB_code[0])*(mapa_colores[:,:,1] == RGB_code[1])*(mapa_colores[:,:,2] == RGB_code[2])
                mapa[mask] = pirads_colores[obs.categoria-1]
    save_img = os.path.join(os.path.dirname(os.path.realpath(__file__)),"temp_img","mapa_final.png")
    mapa = Image.fromarray(mapa)
    mapa.save(save_img)
    
def del_obs(to_destroy: int):
    observaciones.pop(to_destroy)
    refresh_report()

def mapa_show():
    global mapa_flag,mapa_window,cv_mapa,mapa_img,steps_h
    if mapa_flag:   
        mapa_window.destroy()
        mapa_flag = False
        steps_levels.config(cursor="arrow")
    else:
        steps_levels.config(cursor="plus")
        mapa_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"saurus_img","sector_map_v21.png")))
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
    mapa_colores  = asarray(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"saurus_img","sector_map_v21_mask.png")))
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

def bnc_start(event):
    global bnc_x, bnc_y
    if (type(event.widget) == Canvas):
        bnc_x = event.x
        bnc_y = event.y
        root.bind("<Motion>",bnc_control)
        root.bind("<ButtonRelease-2>",bnc_stop)
        root.unbind("<MouseWheel>")
def bnc_control(event):
    global bnc_x, bnc_y
    tipo = ""
    if event.x > 1.02*bnc_x: 
        tipo = "c+"
        bnc_x = event.x
    elif event.x < 0.98*bnc_x: 
        tipo = "c-"
        bnc_x = event.x
    if event.y > 1.05*bnc_y: 
        tipo = "b-"
        bnc_y = event.y
    elif event.y < 0.95*bnc_y: 
        tipo = "b+"
        bnc_y = event.y
    for sec in secuencias:
        if sec.incv == cv:
            if sec in dce_secs:
                for dcesec in dce_secs:
                    if tipo == "c+" and dcesec.alpha < 1:
                        dcesec.adjust_img_serie(0.01,0)
                    elif tipo == "c-" and dcesec.alpha >= 0.01:
                        dcesec.adjust_img_serie(-0.01,0)
                    elif tipo == "b+" and dcesec.beta < 100:
                        dcesec.adjust_img_serie(0,5)
                    elif tipo == "b-" and dcesec.beta >= 5:
                        dcesec.adjust_img_serie(0,-5)
            else:
                if tipo == "c+" and sec.alpha < 1:
                    sec.adjust_img_serie(0.01,0)
                elif tipo == "c-" and sec.alpha >= 0.01:
                    sec.adjust_img_serie(-0.01,0)
                elif tipo == "b+" and sec.beta < 100:
                    sec.adjust_img_serie(0,5)
                elif tipo == "b-" and sec.beta >= 5:
                    sec.adjust_img_serie(0,-5)
            refresh_canvas(sec)
            return        
def bnc_stop(event):
    root.unbind("<Motion>")
    root.unbind("<ButtonRelease-2>")
    root.bind("<MouseWheel>", slice_selector)
    
def canvas_creator(layout: int):
    global cv_master, img2cv, startupCVs, axis_cv, prostata_flag, lesion_flag, dce_flag
    prostata_flag = False
    lesion_flag = False
    dce_flag = False    
    
    if startupCVs:   # asigno CONTROLES DE USUARIO
        
        root.bind("<MouseWheel>", slice_selector)
        root.bind("<Shift-MouseWheel>", zoom_selector)
        root.bind("<Control-z>",go_back_1)
        root.bind("<Button-2>",bnc_start)
        
    if ((not startupCVs) and (layout == layout_cv.get())): return    # si intento cambiar la cantidad, pero es la ya seleccionada no hago nada
     
    img2cv = [0,0,0,0]
    if not startupCVs:
        old_master = cv_master
        for temp_cv in cv_master:   temp_cv.destroy() # borro los cv de la ventana antes de volver a crear nuevos.
    
    cv_master = []
    
    # creo los canvas segun la opcion q elegí
    if layout == 1:  
        CV_W.set(MF_W.get()-40)
        CV_H.set(MF_H.get()-40)
        cv_master.append(Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0))
        cv_master[0].grid(row=0,column=0,padx=(20,0),pady=(20,0))
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
    
    for temp_cv in cv_master:   # asigno propiedades a los cv creados
        temp_cv.bind("<Enter>",lambda event, arg=temp_cv: focus_cv(event,arg))
        temp_cv.bind("<Leave>", unfocus_cv)
        temp_cv.bind("<Button-3>", popupmenu)
        
    if ((not startupCVs) and (layout != layout_cv.get())): # si no es la primera vez y tengo un cambio de layout reacomodo las secuencias:
        
        if layout_cv.get() == 1:    # si tengo 1 y voy a 2 o 4 la pongo en la primera
            for sec in secuencias:
                if sec.incv != 0:
                    sec.incv = cv_master[0]
                    refresh_canvas(sec)
                    break
        elif layout == 1:   # si tengo 2 o 4 y voy a 1, dejo la primera
            found = False
            for temp_cv in old_master:
                if ((temp_cv != 0) and (not found)):
                    for sec in secuencias:
                        if sec.incv == temp_cv:
                            sec.incv = cv_master[0]
                            refresh_canvas(sec)
                            found = True
            for sec in secuencias:
                if sec.incv != cv_master[0]: sec.incv = 0
        else:  # si tengo 2 y voy a 4 o si tenog 4 y voy a 2
            found = 0
            for temp_cv in old_master:
                if ((temp_cv != 0) and (found != 2)):
                    for sec in secuencias:
                        if sec.incv == temp_cv:
                            sec.incv = cv_master[found]
                            if axis_cv.get():
                                axis_cv.set(False)  # CORRECION PROVISORIA POSIBLEMENTE UN BUG PERO NO SE
                                refresh_canvas(sec)
                                axis_cv.set(True)
                            else:
                                refresh_canvas(sec)
                            found += 1
            for sec in secuencias:
                if ((sec.incv != cv_master[0]) and (sec.incv != cv_master[1])): sec.incv = 0
        for obj in obj_master:  obj.update_coord()  # actualizo los dibujos para que tomen un nuevo tamaño proporcional 
        for sec in secuencias:  # actualizo el canvas para que se me muestren los dibujos actualizados
            if sec.incv != 0:
                refresh_canvas(sec)
                break                    
    layout_cv.set(layout)   # asigno el nuevo layout de forma permanente.
    startupCVs = False 
    
def clear_cv ():
    global obj_master
    for obj in obj_master:                                      # CON ESTO BORRO EL CANVAS PERO NO EL OBJETO
        if obj.insec.incv == cv:
            obj.insec.incv.delete(obj.name)
    obj_master = [obj for obj in obj_master if obj.insec.incv != cv]  # CON ESTO BORRO EL OBJETO PERO NO EL CANVAS
    for sec in secuencias:
        if sec.incv == cv:
            sec.load_img_serie()
            refresh_canvas(sec)
            return
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
    global cv
    if cv != 0: cv.delete("focus_check","cv_info")
    cv = 0

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
        sec.incv.create_text(10,180,text="Brillo: "+str(round(sec.beta,3)),font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
        sec.incv.create_text(10,200,text="Contraste: "+str(round(sec.alpha,3)),font=("Roboto",10),fill="#FFF",tag="cv_info",anchor=W)
                
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
    global secuencias, dce_secs, obj_master, observaciones, obs_id,pb
    
    filepath = filedialog.askdirectory()
    if not filepath: return 
    
    sec_uids = []   # uids de secuencias (auxiliar)
    
    pb = ttk.Progressbar(root,orient='horizontal',mode='determinate',length=300,style="bar.Horizontal.TProgressbar")
    pb.place(relx=0.5, rely=0.5, height=25, anchor=CENTER)
    
    paciente = sorted(os.listdir(filepath))
    for seq in paciente:
        pb.step(100/len(paciente))
        root.update_idletasks()
        if(os.path.isdir(os.path.join(filepath,seq))):
            seq_path = os.listdir(os.path.join(filepath,seq))
            for file in seq_path:
                name, ext = os.path.splitext(file)
                if (ext == ".IMA") or (ext == ".dcm"):
                    temp_dcm = dcmread(os.path.join(filepath,seq,file))
                    temp_uid = temp_dcm.SeriesInstanceUID
                    if  temp_uid not in sec_uids:
                        try: 
                            if temp_dcm.ContrastBolusAgent: dce_secs.append(secuencia(seq))
                        except:
                            secuencias.append(secuencia(seq))
                        sec_uids.append(temp_uid)
                    try: 
                        if temp_dcm.ContrastBolusAgent: dce_secs[-1].add_dcm(temp_dcm)
                    except:
                        secuencias[-1].add_dcm(temp_dcm)
                    
    if len(dce_secs):   secuencias.append(dce_secs[0])    # si hay dce muestro solo 1    
    
    pb.destroy()
    canvas_creator(layout_cv.get())
    sec_selector()
             

def sec_selector():
    global seq_tab,sec_list, ss_indicator
    
    try: seq_tab.destroy()
    except: pass
    try: ss_indicator.destroy()
    except: pass
    
    seq_tab = Frame(root,background="#333")
    seq_tab.place(relx=0,rely=0, height=MF_H.get())
    Label(seq_tab, text="SECUENCIAS DISPONIBLES",bg="#2CC",font=("Roboto",12),fg="#000").grid(row=0,column=0,ipadx=80,ipady=10,columnspan=2)
    sec_list = Listbox(seq_tab, height=57, width=50, relief=FLAT, bg="#333",font=("Roboto",9), cursor="hand2",activestyle="dotbox",fg="#FFF",selectbackground="#266",highlightthickness=0)
    sec_list.grid(row=1, column=0,padx=5,pady=10)
    if len (secuencias) > 0:
        for sec in secuencias:
            if not sec.aux_view:
                sec_list.insert(END,sec.name)
        sb = Scrollbar(seq_tab,orient=VERTICAL)
        sb.grid(row=1, column=1, sticky=NS)
        sec_list.config(yscrollcommand=sb.set)
        sb.config(command=sec_list.yview)
        ss_indicator = Frame(root,background="#2CC")
        ss_indicator.place(relx=0.5,rely=0.05, height=40,anchor=CENTER)  
        Label(ss_indicator, text="Seleccione secuencia y haga clic en el canvas",bg="#2CC",font=("Roboto",12),fg="#000").pack(ipady=5,ipadx=20)
    seq_tab.bind('<Leave>', sec_move)
    root.bind("<Escape>",seq_tab_destroy)
    
def sec_move(event):
    seq = sec_list.get(ANCHOR)
    
    root.config(cursor="plus")
    root.bind('<Button-1>', lambda event, seq=seq: sec_setup(event, seq))
def sec_setup(event, sec_name: str):
    if(type(event.widget)==Canvas):
        ss_indicator.destroy()
        #seq_tab.destroy()
        for sec in secuencias:
            if sec.incv == cv: 
                if sec.name == sec_name: return
                else: sec.incv = 0
            elif sec.name == sec_name:
                if sec.incv != 0: sec.incv.delete(ALL)
                sec.incv = cv
                sec.incv.delete(ALL)
                if not sec.isloaded:
                    if sec in dce_secs:
                        for s in dce_secs: s.load_img_serie()
                    sec.load_img_serie()
                refresh_canvas(sec)

        root.config(cursor="arrow")
        root.unbind('<Button-1>')

def refresh_canvas(sec: secuencia):
    
    if not sec.aux_view:
        if len(cv_master) == 2:
            temp_img = resize(sec.img_serie[sec.slice], width=int(CV_W.get()*sec.zoom)) #TRABAJANDO ACA VER
        else:
            temp_img = resize(sec.img_serie[sec.slice], height=int(CV_H.get()*sec.zoom))
        sec.realx = sec.dcm_serie[0].PixelSpacing[0]*sec.width/temp_img.shape[1]
        sec.realy = sec.dcm_serie[0].PixelSpacing[1]*sec.height/temp_img.shape[0]  
    else:
        if sec.parent.plano == "axial" and sec.plano == "sagital": 
            temp_width = sec.parent.incv_height
        if sec.parent.plano == "axial" and sec.plano == "coronal": 
            temp_width = sec.parent.incv_width
        temp_img = resize(sec.img_serie[sec.slice], width=temp_width)
        sec.realy = sec.parent.dcm_serie[0].PixelSpacing[0]*sec.parent.depth*sec.factor/temp_img.shape[0]
    sec.incv_height = temp_img.shape[0]
    sec.incv_width =  temp_img.shape[1]
    img2cv_master(sec,temp_img)
    
    # REDIBUJO LOS OBJETOS GUARDADOS EN LOS CANVAS
    for obj in obj_master:
        if obj.insec == sec and obj.inslice == sec.slice:
            obj.update_coord()
            obj.draw(False)
            
    if info_cv.get(): info_cv_gen(sec)
    if axis_cv.get(): axis_gen()
    else: 
        for cvs in cv_master:
            cvs.delete("axial_depth_marker","sagital_depth_marker","coronal_depth_marker")
    pos_info(sec)

def img2cv_master(sec: secuencia, temp_img):
    global img2cv
    for n,cvs in enumerate(cv_master):
        if sec.incv == cvs:
            img2cv[n] = ImageTk.PhotoImage(Image.fromarray(temp_img))
            cvs.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=img2cv[n])

def axis_gen():
    #for sec in secuencias: print(sec.incv, cv_master)
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
    if sec.plano == "axial":        temp_pos = ["A","P","R","L"] # UP, DOWN , RIGHT, LEFT
    elif sec.plano == "sagital":    temp_pos = ["S","I","A","P"]
    elif sec.plano == "coronal":    temp_pos = ["S","I","R","L"]
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
            refresh_canvas(sec) 
            break

def zoom_selector(event):
    if (type(event.widget) == Canvas):
        for sec in secuencias:
            if sec.incv == cv:
                if event.delta > 0 and sec.zoom < 3: sec.zoom += 0.1
                elif event.delta < 0 and sec.zoom > 1: sec.zoom -= 0.1
                refresh_canvas(sec) 
                return
    
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
    root.unbind("<Escape>")
    info_tab.destroy()
def seq_tab_destroy(event):
    try: ss_indicator.destroy()
    except: pass
    seq_tab.destroy()

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
    global ss_indicator
    
    ss_indicator = Frame(root,background="#2CC")
    ss_indicator.place(relx=0.5,rely=0.05, height=40,anchor=CENTER)  
    Label(ss_indicator, text="Haga clic en la imágen que desea registrar",bg="#2CC",font=("Roboto",12),fg="#000").pack(ipady=5,ipadx=20)
    root.config(cursor="target")
    root.bind('<Button-1>', screenshot)
    steps_levels.iconify()
             
## HERRAMIENTAS

#ROI GENERATORS
def roi_gen(tipo: str):
    root.config(cursor="tcross")
    root.bind('<Button-1>', lambda event, arg=tipo: roi_start(event,arg))
    root.bind("<Escape>", lambda event, arg=False: roi_escape(event,arg))
def roi_start(event,tipo: str):
    if(type(event.widget)==Canvas):
        root.bind("<Escape>", lambda event, arg=True: roi_escape(event,arg))
        cont = 0
        for sec in secuencias:
            if sec.incv == cv:  break
            else: cont += 1
        if cont == len(secuencias): return
        else:
            root.bind('<B1-Motion>', lambda event: roi_temp(event))
            root.bind('<ButtonRelease-1>', lambda event: roi_end(event))
        if tipo == "s":
            obj_master.append(roi_square(tipo+str(len(obj_master)),sec))
        elif tipo == "c":
            obj_master.append(roi_circle(tipo+str(len(obj_master)),sec))
        elif tipo == "r":
            obj_master.append(roi_ruler(tipo+str(len(obj_master)),sec))
        obj_master[-1].init_coord(event.x,event.y)
def roi_temp(event):
    if cv == 0: 
        obj_master[-1].insec.incv.delete(obj_master[-1].name)
        return
    obj_master[-1].end_coord(event.x,event.y)
    obj_master[-1].draw(True) 
def roi_end(event):
    if cv == 0: 
        obj_master[-1].insec.incv.delete(obj_master[-1].name)
        obj_master.pop()
        return
    if obj_master[-1].name[0] == "s":
        if obj_master[-1].xi == event.x or obj_master[-1].yi == event.y:
            print("NO SUELTE EL MOUSE")
            obj_master.pop()
            roi_unbind()
            return
    elif obj_master[-1].name[0] == "c" or obj_master[-1].name[0] == "r":
        if obj_master[-1].xi == event.x and obj_master[-1].yi == event.y:
            print("NO SUELTE EL MOUSE")
            obj_master.pop()
            roi_unbind()
            return
    obj_master[-1].end_coord(event.x,event.y)
    obj_master[-1].draw(False)
    roi_unbind()
    
    global vol_cont, lesion_flag, vol, dce_flag
    if dce_flag:
        obj_master[-1].update_coord()
        dce_coord.append(obj_master[-1].xi)
        dce_coord.append(obj_master[-1].yi)
        dce_coord.append(obj_master[-1].r)
        obj_master[-1].insec.incv.delete(obj_master[-1].name)
        obj_master.pop()
        dce_flag = False
        dce_curve_calculator()
    elif prostata_flag:
        roi_gen(obj_master[-1].name[0])
        vol_cont += 1
        medidas.append(round(obj_master[-1].rdis,1))
        if vol_cont == 3:
            vol_cont = 0
            vol = round(obj_master[-1].rdis*obj_master[-2].rdis*obj_master[-3].rdis*0.52/1000,2) #volumen de elipsoide en ml
            for n in range(3):
                obj_master[-1].insec.incv.delete(obj_master[-1].name)
                obj_master.pop()
            roi_unbind()
            obs_setup("end")
    elif lesion_flag:
        roi_gen(obj_master[-1].name[0])
        medidas.append(round(obj_master[-1].rdis,1))
        obj_master[-1].insec.incv.delete(obj_master[-1].name)
        obj_master.pop()
        lesion_flag = False
        roi_unbind()
        obs_setup("bypassed")
    else: pass   # si estoy creando un objeto solo de indicación
    
         
def roi_escape(event,flag: bool):
    try:
        steps_levels.destroy()
    except:
        pass
    roi_unbind()
    if flag:
        obj_master[-1].insec.incv.delete(obj_master[-1].name)
        obj_master.pop()
def roi_unbind():
    root.config(cursor="arrow")
    root.unbind('<Button-1>')
    root.unbind('<B1-Motion>')
    root.unbind('<ButtonRelease-1>')
    root.unbind('<Escape>')
          
def vol_calculator():
    global vol_cont, vol, medidas
    vol_cont = 0    # cantidad de mediciones de axis elipsoide
    vol = 0         # el volumen medido
    medidas = []
    roi_gen("r")

def pirads_lesion(obs: observacion):
    #depende las opciones de la lesion determina el pirads particular de la lesion
    #sigue el diagrama del paper (no el de la pagina)
    pirad = 0
    if (("Periférica" in obs.location) or ("Central" in obs.location)): 
        #si es zona periferica o central lo importante es DWI
        if ((obs.lesionDWI == 3) and (obs.lesionDCE == 1)):
            pirad = 4
        else:
            pirad = obs.lesionDWI
    elif (("Transicional" in obs.location) or ("Estroma" in obs.location)):
        #si es zona transicional o efma lo importante es T2
        if ((obs.lesionT2 == 2) and (obs.lesionDWI >=4)):
            pirad = 3
        elif ((obs.lesionT2 == 3) and (obs.lesionDWI == 5)):
            pirad = 4
        else:
            pirad = obs.lesionT2
    elif obs.location != "Seleccione Zona Afectada":
        pirad = obs.lesionT2
    else:
        pirad = 0
        messagebox.showwarning(title="Observación Incompleta", message="Por favor edite su observación y seleccione la zona afectada")
        #ACA LLAMAR A FUNCION Q POPEE UN MSJ DE ERROR          
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
    
    if(type(event.widget)==Canvas):
        ss_indicator.destroy()
        root.update()
        observaciones[-1].imagenes.append(ImageGrab.grab((cv.winfo_rootx(), cv.winfo_rooty(), cv.winfo_rootx() + cv.winfo_width(), cv.winfo_rooty() + cv.winfo_height())))
        save_img = os.path.join(os.path.dirname(os.path.realpath(__file__)),"temp_img","obs_"+str(observaciones[-1].id)+"_"+str(len(observaciones[-1].imagenes))+".png")
        observaciones[-1].imagenes[-1].save(save_img) # VER DONDE GUARDA ESTO Y SI ES NECESARIO GUARDAR
        root.unbind('<Button-1>')
        root.config(cursor="arrow")
        steps_levels.deiconify()
        Label(auxframe2, text="added obs_"+str(observaciones[-1].id)+"_"+str(len(observaciones[-1].imagenes))+".png",bg="#444",font=("Roboto",11),fg="#FFF",anchor=W).pack(fill=X,ipady=1,ipadx=1)
    

def dce_curve():
    global dceroi, dce_flag, dce_coord 
    dce_flag = True
    dce_coord = []
    for sec in secuencias:
        if sec.incv == cv:
            if sec in dce_secs:
                dceroi = Frame(root,background="#2CC")
                dceroi.place(relx=0.5,rely=0.05, height=40,anchor=CENTER)
                Label(dceroi, text="Seleccione ROI",bg="#2CC",font=("Roboto",12),fg="#000").pack(ipady=5,ipadx=20)
                roi_gen("c")
                #genero una mascara mismo size q la imagen con 1 dentro de la ROI
                #por cada secuencia de dce_secs calculo la media de pixeles dentro de la ROI de cada corte? y con n puntos de brillo (n = len(dce_secs)) dibujo la curva en una nueva ventana
                break
            else:
                return
            
def dce_curve_calculator():
    global dce_coord
    
    dceroi.destroy()
    for sec in secuencias:
        if sec.incv == cv:
            if sec in dce_secs:
                ww, hh = sec.incv_width, sec.incv_height
                temp_slice = sec.slice
    Y, X = ogrid[:hh, :ww]
    dist_from_center = sqrt((X - int(dce_coord[0]*ww))**2 + (Y-int(dce_coord[1]*hh))**2)
    dce_mask = (dist_from_center <= int(dce_coord[2]))
    curva = []
    first = True
    for sec in dce_secs:
        if len(cv_master) == 2:
            temp_img = resize(sec.img_serie[temp_slice], width=ww)
        else:
            temp_img = resize(sec.img_serie[temp_slice], height=hh)
        try:    # el try por el error en decir q tiene contraste con mismo uid la secuencia VER
            temp_img*=dce_mask
            if first:
                brillo_inicial = sum(sum(temp_img))
                first = False
            curva.append((((sum(sum(temp_img)))-brillo_inicial)/brillo_inicial)*100)   # porcentaje de "enhancement"
        except:
            pass
    #curva = savgol_filter(curva, 5, 3) # window size 11, polynomial order 2
    xtime = [100/len(curva)*t for t in range(len(curva))] 
    
    DCEGraph = Toplevel(root,background="#444")
    DCEGraph.geometry("800x600")
    fig = Figure(figsize=(8,6),dpi=100)
    fig.patch.set_facecolor("#222")
    plot1 = fig.add_subplot(111)
    plot1.set_ylabel(r"Enhancement (%)",color="#FFF")
    plot1.set_xlabel(r"Tiempo estudio (%)",color="#FFF")
    plot1.set_title("Curva DCE",color="#FFF")
    plot1.set_facecolor("#111")
    plot1.tick_params(axis='x', colors="#FFF")
    plot1.tick_params(axis='y', colors="#FFF")
    plot1.set_xticks(range(0,101,10))
    plot1.grid(axis='x',color="#444")
    plot1.plot(xtime,curva)
    
    canvas = FigureCanvasTkAgg(fig,master=DCEGraph)  
    canvas.draw()
    canvas.get_tk_widget().pack()
  
    dce_coord = [] # limpio dce por si quiero repetir prueba
             


#------------------LATEX TO PDF------------------------------
# Diseño la estructura en "latex" y creo un .pdf
def generator (save_directory: str):
    global ss_indicator
    ss_indicator = Frame(root,background="#F80")
    ss_indicator.place(relx=0.5,rely=0.5, height=60,anchor=CENTER)  
    Label(ss_indicator, text="GENERANDO REPORTE",bg="#F80",font=("Roboto",14,"bold"),fg="#000").pack(ipady=20,ipadx=20)
    root.update_idletasks()
    
    geometry_options = {
            "head": "40pt",
            "margin": "1.5cm",
            "top": "1cm",
            "bottom": "2cm"
        }
    doc = Document(geometry_options=geometry_options) 
    doc.preamble.append(Package('babel', options='spanish'))
    doc.packages.append(Package('montserrat',"defaultfam"))
    footer = PageStyle("footer")
    with footer.create(Foot("C")):
        if prosta.institu == "Corporación Médica":
            footer.append("Corporación Médica de Gral. San Martín SA - Matheu 4071, (1650) San Martín - Tel. 4754-7500")
        elif prosta.institu == "CEUNIM - UNSAM":
            footer.append("Centro Universitario de Imágenes Médicas - UNSAM - Av.25 de Mayo 901, (1650) San Martín - Tel. 2033-1458")
        elif prosta.institu == "Diagnóstico Tesla":
            footer.append("Diagnóstico Tesla - Sede Morón - Buen Viaje 548, (1708) Morón - Tel. 4489-9999")
        else:
            footer.append("Reporte generado automáticamente por software SAURUS")
    doc.preamble.append(footer)
    doc.change_document_style("footer")

    doc.append(NoEscape(r"\noindent"))
    with doc.create(MiniPage(width=NoEscape(r"0.3\linewidth"))) as logo:
        logo_unsam = os.path.dirname(os.path.realpath(__file__)).replace("\\","/")+"/saurus_img/logo_unsam_big.png"
        logo.append(StandAloneGraphic(image_options="width=150px",filename=logo_unsam))
    with doc.create(MiniPage(width=NoEscape(r"0.4\linewidth"),align="c")) as titulo:
        titulo.append(MediumText("REPORTE PI-RADS"))
    with doc.create(MiniPage(width=NoEscape(r"0.3\linewidth"),align="r")) as datos:
        datos.append("Pág. 1 de 2")
        datos.append("\n")
        datos.append(NoEscape(r'\today'))
    
    doc.append(VerticalSpace("1cm"))
    doc.append("\n")
    doc.append(SmallText("Report ID: "))
    doc.append(SmallText(bold(str(secuencias[0].dcm_serie[0].PatientID))))
    doc.append("\n")
    doc.append(SmallText("Paciente: "))
    doc.append(SmallText(bold(str(secuencias[0].dcm_serie[0].PatientName))))
    doc.append("\n")
    doc.append(SmallText("Edad: "))
    doc.append(SmallText(bold(str(int(secuencias[0].dcm_serie[0].PatientAge[:3]))+" años")))
    doc.append("\n")
    doc.append(SmallText("Fecha estudio: "))
    doc.append(SmallText(bold(secuencias[0].dcm_serie[0].InstanceCreationDate[6:]+"/"+secuencias[0].dcm_serie[0].InstanceCreationDate[4:6]+"/"+secuencias[0].dcm_serie[0].InstanceCreationDate[0:4])))
    doc.append("\n")
    doc.append(SmallText("Indicado por: "))
    doc.append(SmallText(bold(prosta.indicado)))
    doc.append("\n")
    doc.append(SmallText("Revisado por: "))
    doc.append(SmallText(bold("Dr. Diego Santoro")))
    doc.append("\n")
    doc.append(NoEscape(r"\rule{\textwidth}{2pt}"))
    doc.append("\n\n")
    doc.append(SmallText(bold("HISTORIA CLÍNICA")))
    doc.append("\n\n")
    doc.append(SmallText("Motivo Estudio: "))
    doc.append(SmallText(italic(prosta.motivo)))
    doc.append("\n")
    doc.append(SmallText("PSA: "))
    try:
        doc.append(SmallText(bold(prosta.psa[0]+" ng/ml")))
    except: pass
    doc.append(NoEscape("\quad"))
    doc.append(SmallText("realizado el: "+prosta.psa[2]+"/"+prosta.psa[3]+"/"+prosta.psa[4]))
    doc.append("\n")
    doc.append(SmallText("fPSA: "))
    try:
        doc.append(SmallText(bold(prosta.psa[1]+"ng/ml")))
    except: pass
    doc.append("\n")
    doc.append(SmallText("PSAD: "))
    try:
        doc.append(SmallText(bold(str(round(float(prosta.psa[0])/prosta.volumen,2))+" ng/ml/cc")))
    except: pass
    doc.append("\n")
    doc.append(SmallText("fPSA ratio: "))
    try:
        doc.append(SmallText(bold(str(round(float(prosta.psa[1])*100/float(prosta.psa[0]),2))+"%")))
    except: pass
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
        resultL.append("\n")
        resultL.append(SmallText("Lesión Uretra: "))
        resultL.append(SmallText(bold(prosta.uretra)))
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
    doc.append(SmallText(bold("Lesiones más significativas:")))
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
            obsL.append(SmallText("Dim. Lesión: "))
            obsL.append(SmallText(bold(str(obs.medidas[0]))))
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
                    img_to_open = os.path.dirname(os.path.realpath(__file__)).replace("\\","/")+"/temp_img/"+img 
                    #hago esto porq con el path.join sale como \ y no funca con el standalone
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
    with doc.create(MiniPage(width=NoEscape(r"0.3\linewidth"))) as logo:
        logo_unsam = os.path.dirname(os.path.realpath(__file__)).replace("\\","/")+"/saurus_img/logo_unsam_big.png"
        logo.append(StandAloneGraphic(image_options="width=150px",filename=logo_unsam))
    with doc.create(MiniPage(width=NoEscape(r"0.4\linewidth"),align="c")) as titulo:
        titulo.append(MediumText("REPORTE PI-RADS"))
    with doc.create(MiniPage(width=NoEscape(r"0.3\linewidth"),align="r")) as datos:
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
        img_to_open = os.path.dirname(os.path.realpath(__file__)).replace("\\","/")+"/temp_img/mapa_final.png"
        concluR.append(StandAloneGraphic(image_options="width=250px",filename=img_to_open))
    
    doc.append("\n")
    doc.append(NoEscape(r"\rule{\textwidth}{0.2pt}"))
    doc.append("\n\n")
    doc.append(SmallText("Sobre los resultados:"))
    doc.append("\n\n")
    doc.append(SmallText("La clasificación PI-RADS es un sistema internacionalmente consensuado, reconocido y recomendado por el American College of Radiology para informar la RMmp de forma uniforme por todos los radiólogos y se debe usar de forma obligatoria en la valoración de esta prueba."))
    doc.append("\n\n")
    doc.append(SmallText("PIRADS 1 - Muy Bajo. Es muy poco probable que la lesión sea un cáncer significativo.\nPIRADS 2 - Bajo. Es poco probable que la lesión sea un cáncer significativo; lesión probablemente benigna.\nPIRADS 3 - Intermedia. No hay datos que orienten claramente hacia la benignidad o malignidad de la lesión.\nPIRADS 4 - Alta. Es probable que la lesión sea un cáncer significativo; lesión probablemente maligna.\nPIRADS 5 - Muy Alta. Es muy probable que la lesión sea un cáncer significativo; lesión muy probablemente maligna."))
    doc.append("\n")
    rp_name = str(secuencias[0].dcm_serie[0].PatientID)+"_"+str(secuencias[0].dcm_serie[0].PatientName)+"_Reporte_PI-RADS"
    fp = save_directory+"/"+rp_name
    doc.generate_pdf(fp,clean=True)
    ss_indicator.destroy()

    #CHECKEO SI EL REPORTE SE GENERO Y GUARDO EN EL DIRECTORIO INDICADO
    if (rp_name+".pdf") in os.listdir(save_directory):
        messagebox.showinfo(title="Estado de Reporte", message="Reporte generado exitosamente")
    else:
        messagebox.showerror(title="Estado de Reporte", message="Hubo un error al generar el reporte")
#-------------------------------------------------------


#-------------- MAIN LOOP ---------------------------------------------------------
      
        
root = Tk()
root.title("S A U R U S")
root.config(bg="#F00") #para debug 
root.iconbitmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),"saurus_img","unsam2.ico"))
root.state('zoomed')
#root.resizable(True, True)
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

# GLOBAL VARIABLES
MF_W = IntVar(value=screen_w)
MF_H = IntVar(value=screen_h-100) # -100 por que 20 de botframe 20 menu 20 windows tab 40 windows taskbar
CV_W = IntVar(value=0)
CV_H = IntVar(value=0)
info_text = StringVar(value="SAURUS V2.0")
info_cv = BooleanVar(value=False)
axis_cv = BooleanVar(value=False)
report_flag = BooleanVar(value=False)
keybinds_flag = BooleanVar(value=False)
layout_cv = IntVar(value=1)

# MASTER DE SECUENCIAS CARGADAS
secuencias = [] # secuencias normales
dce_secs = []   # secuencias del DCE -> solo muestro 1
# MASTER DE DIBUJOS
obj_master = [] # vector de ROIs y mediciones

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
Guardar estado de reporte -> observaciones, imagenes, rois, secuencias (sin cambiar layout porq se complica)

"""