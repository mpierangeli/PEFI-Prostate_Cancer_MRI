from tkinter import *
from PIL import Image, ImageTk#, ImageGrab
from tkinter import filedialog
import pydicom
import numpy as np
import math
import imutils
import os

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
    filemenu.add_command(label="Selección Paciente", command=patient_loader)
    filemenu.add_separator()
    filemenu.add_command(label="Panel de Secuencias", command=sec_selector)
    
    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="ROI Rectangular",command=lambda tipo="s": roi_gen(tipo))
    editmenu.add_command(label="ROI Circular",command=lambda tipo="c": roi_gen(tipo))
    editmenu.add_command(label="Medición",command=lambda tipo="r": roi_gen(tipo))

    reportmenu = Menu(menubar, tearoff=0)
    reportmenu.add_command(label="Nuevo Reporte")

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Keybinds")
    helpmenu.add_command(label="Acerca de...")
    helpmenu.add_separator()
    helpmenu.add_command(label="Salir", command=root.quit)

    displaymenu = Menu(menubar, tearoff=0)
    displaymenu.add_command(label="1x1",command=lambda layout=1: canvas_creator(layout))
    displaymenu.add_command(label="1x2",command=lambda layout=2: canvas_creator(layout))
    displaymenu.add_command(label="2x2",command=lambda layout=4: canvas_creator(layout))
    
    menubar.add_cascade(label="Abrir", menu=filemenu)
    menubar.add_cascade(label="Pantalla", menu=displaymenu)
    menubar.add_cascade(label="Herramientas", menu=editmenu)
    menubar.add_cascade(label="Reportar", menu=reportmenu)
    menubar.add_cascade(label="Ayuda", menu=helpmenu)

def canvas_creator(layout: int):
    global cv_master, cv_layout
    cv_layout = layout
    try:
        for temp_cv in cv_master:
            temp_cv.destroy()
    except:
        pass
    for sec in secuencias:
        sec.incv = 0 # VER ESTO
    cv_master = []

    match cv_layout:
        case 1:
            CV_W.set(MF_W.get()-40)
            CV_H.set(MF_H.get()-40)
            cv_master.append(Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0))
            cv_master[0].grid(row=0,column=0,padx=20,pady=20)
        case 2:
            CV_W.set(int(MF_W.get()/2)-10)
            CV_H.set(MF_H.get()-40)
            for n in range(cv_layout):
                cv_master.append(Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0))
            cv_master[0].grid(row=0,column=0,padx=(0,10),pady=20)
            cv_master[1].grid(row=0,column=1,padx=(10,0),pady=20)        
        case 4:
            CV_W.set(int(MF_W.get()/2)-5)
            CV_H.set(int(MF_H.get()/2)-5)
            for n in range(cv_layout):
                cv_master.append(Canvas(main_frame, width=CV_W.get(),height=CV_H.get(),bg="#000",highlightthickness=0))
            cv_master[0].grid(row=0,column=0,padx=(0,5),pady=(0,5))
            cv_master[1].grid(row=0,column=1,padx=(5,0),pady=(0,5))
            cv_master[2].grid(row=1,column=0,padx=(0,5),pady=(5,0))
            cv_master[3].grid(row=1,column=1,padx=(5,0),pady=(5,0))

    for temp_cv in cv_master:
        temp_cv.bind("<Enter>",lambda event, arg=temp_cv: focus_cv(event,arg))
        temp_cv.bind("<Leave>", unfocus_cv)   

    root.bind("<F3>",clear_cv)
    #root.bind("<F4>",reset_cv)
    root.bind("<Control-MouseWheel>", slice_selector)
    root.bind("<Control-z>",go_back_1)
    
def clear_cv (event):
    global obj_master
    for obj in obj_master:                                      # CON ESTO BORRO EL CANVAS PERO NO EL OBJETO
        if obj.insec.incv == cv:
            cv.delete(obj.name)
    obj_master = [obj for obj in obj_master if obj.insec.incv != cv]  # CON ESTO BORRO EL OBJETO PERO NO EL CANVAS
def focus_cv(event, arg: Canvas):
    global cv
    cv = arg
    cv.create_text(50,CV_H.get()-20,text="FOCUSED",font=("Roboto",5),fill="#FFF",tag="focus_check")
def unfocus_cv(event):
    cv.delete("focus_check","cv_info")
""" def reset_cv(event):
    global zoomed
    zoomed = False
    cv.delete(ALL) """

def go_back_1(event):
    obj_master[-1].insec.incv.delete(obj_master[-1].name)
    obj_master.pop()

def patient_loader():
    global secuencias, obj_master
    
    # MASTER DE SECUENCIAS CARGADAS
    secuencias = []
    # auxiliar de secuencias
    sec_uids = []
    
    # MASTER DE DIBUJOS
    obj_master = []
    # MASTER DE OBSERVACIONES PARA REPORTE
    #observations = []
    
    filepath = filedialog.askdirectory()
    
    for file in os.listdir(filepath):
        name, ext = os.path.splitext(file)
        if ext == ".IMA":
            temp_dcm = pydicom.dcmread(filepath+"/"+file)
            temp_uid = temp_dcm.SeriesInstanceUID
            if  temp_uid not in sec_uids:
                secuencias.append(secuencia(temp_dcm.SequenceName+"-> TE: "+str(temp_dcm.EchoTime)+", TR: "+str(temp_dcm.RepetitionTime)+", "+str(temp_dcm.ScanOptions)+", UID: "+temp_uid[-5:-1] ,temp_uid))
                secuencias[-1].add_dcm(temp_dcm)
                sec_uids.append(temp_uid)
            else:
                for sec in secuencias:
                    if temp_uid == sec.UID:
                        sec.add_dcm(temp_dcm)
                        break
    for sec in secuencias:
        sec.load_img_serie()
        
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
        sec_list.insert(END,sec.name)
    seq_tab.bind('<Leave>', sec_move)
def sec_move(event):
    seq = sec_list.get(ANCHOR)
    seq_tab.destroy()
    root.config(cursor="plus")
    root.bind('<Button-1>', lambda event, seq=seq: sec_setup(event, seq))  
def sec_setup(event, seq: str):
    for sec in secuencias:
        if sec.incv == cv:
            sec.incv = 0
        if sec.name == seq:
            sec.incv = cv
    root.config(cursor="arrow")
    root.unbind('<Button-1>')
    refresh_canvas()

def refresh_canvas():
    global img2cv
    img2cv = []
    for sec in secuencias:
        if sec.incv != 0:
            if cv_layout == 2:
                temp_img = imutils.resize(sec.img_serie[sec.slice], width=CV_W.get())
            else:
                temp_img = imutils.resize(sec.img_serie[sec.slice], height=CV_H.get())
                
            sec.realx = sec.dcm_serie[0].PixelSpacing[0]*sec.width/temp_img.shape[1]
            sec.realy = sec.dcm_serie[0].PixelSpacing[1]*sec.height/temp_img.shape[0]
            img2cv.append(ImageTk.PhotoImage(Image.fromarray(temp_img)))
            sec.incv.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=img2cv[-1])
        
        # REDIBUJO LOS OBJETOS GUARDADOS EN LOS CANVAS
            for obj in obj_master:
                if obj.insec == sec and obj.inslice == sec.slice:
                    obj.draw(False)
    print(obj_master)
          
def slice_selector(event):
    for sec in secuencias:
        if sec.incv == cv:
            if event.delta > 0 and sec.slice < sec.depth-1: sec.slice += 1
            elif event.delta < 0 and sec.slice > 0: sec.slice -= 1
            break
    refresh_canvas() 

""" def patient_loader():
    global filepaths, axiales, coronales, sagitales, slice_num, coronal_depth_num, sagital_depth_num, factor, init_dcm, init_img, px_info_var, px_info_static, zoomed, axis_switch, obj_master, observations
    
    filepaths_raw = filedialog.askopenfilenames()
    if not filepaths_raw: 
        set_img(slice_num,coronal_depth_num,sagital_depth_num)
        return
    filepaths = list(filepaths_raw)
    
    #GENERO CONTAINER DE OBJETOS VERVERVER
    obj_master = []
    observations = []
    #-------------------------------------------------
    #GENERO PLANO CORONAL CON IMAGENES T2 (VER COMO SELECCIONAR ESAS EN PARTICULAR)
    init_dcm = pydicom.dcmread(filepaths[0])
    init_img = init_dcm.pixel_array

    px_info_static = [float(init_dcm[0x0028,0x0030].value[0]),float(init_dcm[0x0028,0x0030].value[1])]
    px_info_var = [float(init_dcm[0x0028,0x0030].value[0]),float(init_dcm[0x0028,0x0030].value[1])]
    factor = int(init_dcm[0x0018, 0x0050].value/px_info_static[0])

    axiales = np.zeros((len(filepaths),init_img.shape[0],init_img.shape[1]))
    coronales  =  np.zeros((axiales.shape[1],factor*axiales.shape[0],axiales.shape[2]))
    sagitales = np.zeros((axiales.shape[2],factor*axiales.shape[0],axiales.shape[1]))

    slice_num = 0
    coronal_depth_num = int(coronales.shape[0]/2)
    sagital_depth_num = int(sagitales.shape[0]/2)


    for n, dcm in enumerate(filepaths):
        full_dicom = pydicom.dcmread(dcm)
        axiales[n] = full_dicom.pixel_array
    max = axiales.max()
    for n in range(len(axiales)):
        axiales[n] = (axiales[n]/max)*255

    for i in range(axiales.shape[1]): # por cada fila de las axiales -> profundidad de la coronal
        for j in range(axiales.shape[0]): # por cada imagen axial -> altura de la coronal
            for k in range(factor): # por ancho de tomo axial, repito misma muestra
                coronales[i,j*factor+k] = axiales[j,i,:]

    for i in range(axiales.shape[2]): # por cada columna de las axiales -> profundidad de la sagital
        for j in range(axiales.shape[0]): # por cada imagen axial -> altura de la sagital
            for k in range(factor): # por ancho de tomo axial, repito misma muestra
                sagitales[i,j*factor+k] = axiales[j,:,i]
    #------------------------------------------------
    zoomed = False
    axis_switch = False
    set_img(slice_num,coronal_depth_num,sagital_depth_num) # por default inicia mostrando esto

    #-------------------------------------
    root.bind("<F1>",info_tab_gen)
    root.bind("<F2>",axis_onoff)
    root.bind("<F8>",screenshot)
    root.bind("<Control-MouseWheel>", slice_and_depth_selector)
    root.bind("<Control-z>",go_back_1) """

""" def set_img(slice: int, coronal_depth: int, sagital_depth: int):
    global cv,cv1,cv2,cv3,cv4,axial_t2,coronal_t2,sagital_t2, xcf_axial_t2, ycf_axial_t2, xcf_coronal_t2, ycf_coronal_t2, px_info_var, xi,yi,xf,yf
    
    temp_axial_t2 = imutils.resize(axiales[slice], height=CV_H.get())
    init_width = temp_axial_t2.shape[1]
    init_height = temp_axial_t2.shape[0]
    xcf_axial_t2 = axiales[slice].shape[0]/temp_axial_t2.shape[0] #x factor correction -> por el resize inicial
    ycf_axial_t2 = axiales[slice].shape[1]/temp_axial_t2.shape[1] #y factor correction -> por el resize inicial

    if zoomed:
        crop = temp_axial_t2[yi:yf,xi:xf]
        if (abs(yf-yi) >= abs(xf-xi)):
            temp_axial_t2 = imutils.resize(crop, height=CV_H.get())     #CORREGIR ZOOM PARA CORTES SEMI-CUADRADOS !!!!!!!!!!!!!!!!!!!!!!
        else:
            temp_axial_t2 = imutils.resize(crop, width=CV_W.get())
        xcf_axial_t2 *= crop.shape[0]/temp_axial_t2.shape[0] #x factor correction -> por el resize inicial
        ycf_axial_t2 *= crop.shape[1]/temp_axial_t2.shape[1] #y factor correction -> por el resize inicial
        
    temp_coronal_t2 = imutils.resize(coronales[coronal_depth], width=init_width) 
    xcf_coronal_t2 = coronales[coronal_depth].shape[0]/temp_coronal_t2.shape[0] #x factor correction -> por el resize
    ycf_coronal_t2 = coronales[coronal_depth].shape[1]/temp_coronal_t2.shape[1] #y factor correction -> por el resize
    
    temp_sagital_t2 = imutils.resize(sagitales[sagital_depth], width=init_height) 
    xcf_sagital_t2 = sagitales[sagital_depth].shape[0]/temp_sagital_t2.shape[0] #x factor correction -> por el resize
    ycf_sagital_t2 = sagitales[sagital_depth].shape[1]/temp_sagital_t2.shape[1] #y factor correction -> por el resize

    # GENERO LAS IMAGENES A MOSTRAR
    axial_t2 = ImageTk.PhotoImage(Image.fromarray(temp_axial_t2))
    coronal_t2 = ImageTk.PhotoImage(Image.fromarray(temp_coronal_t2))
    sagital_t2 = ImageTk.PhotoImage(Image.fromarray(temp_sagital_t2))
    
    # CORRIJO EL ANCHO DE PIXEL PARA LA AXIAL
    px_info_var = [float(init_dcm[0x0028,0x0030].value[0])*xcf_axial_t2,float(init_dcm[0x0028,0x0030].value[1])*ycf_axial_t2]

    # LIMPIO EL FRAME ANTES DE DIBUJAR
    cv1.delete("coronal_depth_marker","sagital_depth_marker","cv_info","pos_info")
    cv2.delete("slice_marker","sagital_depth_marker","cv_info","pos_info")
    cv3.delete("cv_info")
    cv4.delete("slice_marker","coronal_depth_marker","cv_info","pos_info")

    # VISTA T2 AXIAL
    cv1.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=axial_t2, tags="axial_t2")
    # POSICION EN ESPACIO -> VER SI DICOM DICE ALGO PARA AUTOMATIZAR
    cv1.create_text(CV_W.get()/2,10,text="A",fill="#FFF",font=("Roboto", 9),tags="pos_info")
    cv1.create_text(CV_W.get()/2,CV_H.get()-10,text="P",fill="#FFF",font=("Roboto", 9),tags="pos_info")
    cv1.create_text(CV_W.get()/2-axial_t2.width()/2-10,CV_H.get()/2,text="L",fill="#FFF",font=("Roboto", 9),tags="pos_info")
    cv1.create_text(CV_W.get()/2+axial_t2.width()/2+10,CV_H.get()/2,text="R",fill="#FFF",font=("Roboto", 9),tags="pos_info")
    # VISTA T2 CORONAL
    cv2.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=coronal_t2, tags="coronal_t2")
    # POSICION EN ESPACIO -> VER SI DICOM DICE ALGO PARA AUTOMATIZAR
    cv2.create_text(CV_W.get()/2,10,text="S",fill="#FFF",font=("Roboto", 9),tags="pos_info")
    cv2.create_text(CV_W.get()/2,CV_H.get()-10,text="I",fill="#FFF",font=("Roboto", 9),tags="pos_info")
    cv2.create_text(CV_W.get()/2-coronal_t2.width()/2-10,CV_H.get()/2,text="L",fill="#FFF",font=("Roboto", 9),tags="pos_info")
    cv2.create_text(CV_W.get()/2+coronal_t2.width()/2+10,CV_H.get()/2,text="R",fill="#FFF",font=("Roboto", 9),tags="pos_info")
    # VISTA T2 SAGITAL
    cv4.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=sagital_t2, tags="sagital_t2")
    # POSICION EN ESPACIO -> VER SI DICOM DICE ALGO PARA AUTOMATIZAR
    cv4.create_text(CV_W.get()/2,10,text="S",fill="#FFF",font=("Roboto", 9),tags="pos_info")
    cv4.create_text(CV_W.get()/2,CV_H.get()-10,text="I",fill="#FFF",font=("Roboto", 9),tags="pos_info")
    cv4.create_text(CV_W.get()/2-sagital_t2.width()/2-10,CV_H.get()/2,text="A",fill="#FFF",font=("Roboto", 9),tags="pos_info")
    cv4.create_text(CV_W.get()/2+sagital_t2.width()/2+10,CV_H.get()/2,text="P",fill="#FFF",font=("Roboto", 9),tags="pos_info")

    
    if axis_switch:

        # AXIS EN T2
        cv1.create_line(CV_W.get()/2-axial_t2.width()/2+2, coronal_depth/ycf_axial_t2, axial_t2.width()/2+CV_W.get()/2, coronal_depth/ycf_axial_t2, fill="#F80", tags="coronal_depth_marker")
        cv1.create_line(CV_W.get()/2-axial_t2.width()/2+2, (coronal_depth+1)/ycf_axial_t2, axial_t2.width()/2+CV_W.get()/2, (coronal_depth+1)/ycf_axial_t2, fill="#F80", tags="coronal_depth_marker")
        cv1.create_line(sagital_depth/xcf_axial_t2+CV_W.get()/2-axial_t2.width()/2+2,0,sagital_depth/xcf_axial_t2+CV_W.get()/2-axial_t2.width()/2+2,CV_H.get(), fill="#5D0", tags="sagital_depth_marker")
        cv1.create_line((sagital_depth+1)/xcf_axial_t2+CV_W.get()/2-axial_t2.width()/2+2,0,(sagital_depth+1)/xcf_axial_t2+CV_W.get()/2-axial_t2.width()/2+2,CV_H.get(), fill="#5D0", tags="sagital_depth_marker")

        # AXIS EN VISTA CORONAL
        cv2.create_line(CV_W.get()/2-coronal_t2.width()/2+2, slice*factor/ycf_coronal_t2+CV_H.get()/2-coronal_t2.height()/2, coronal_t2.width()/2+CV_W.get()/2, slice*factor/ycf_coronal_t2+CV_H.get()/2-coronal_t2.height()/2, fill="#2DD", tags="slice_marker")
        cv2.create_line(CV_W.get()/2-coronal_t2.width()/2+2, (slice+1)*factor/ycf_coronal_t2+CV_H.get()/2-coronal_t2.height()/2, coronal_t2.width()/2+CV_W.get()/2, (slice+1)*factor/ycf_coronal_t2+CV_H.get()/2-coronal_t2.height()/2, fill="#2DD", tags="slice_marker")
        cv2.create_line(sagital_depth/xcf_coronal_t2+CV_W.get()/2-coronal_t2.width()/2+2,0,sagital_depth/xcf_coronal_t2+CV_W.get()/2-coronal_t2.width()/2+2,CV_H.get(), fill="#5D0", tags="sagital_depth_marker")
        cv2.create_line((sagital_depth+1)/xcf_coronal_t2+CV_W.get()/2-coronal_t2.width()/2+2,0,(sagital_depth+1)/xcf_coronal_t2+CV_W.get()/2-coronal_t2.width()/2+2,CV_H.get(), fill="#5D0", tags="sagital_depth_marker")

        # AXIS EN VISTA SAGITAL
        cv4.create_line(CV_W.get()/2-sagital_t2.width()/2+2, slice*factor/ycf_sagital_t2+CV_H.get()/2-sagital_t2.height()/2, sagital_t2.width()/2+CV_W.get()/2, slice*factor/ycf_sagital_t2+CV_H.get()/2-sagital_t2.height()/2, fill="#2DD", tags="slice_marker")
        cv4.create_line(CV_W.get()/2-sagital_t2.width()/2+2, (slice+1)*factor/ycf_sagital_t2+CV_H.get()/2-sagital_t2.height()/2, sagital_t2.width()/2+CV_W.get()/2, (slice+1)*factor/ycf_sagital_t2+CV_H.get()/2-sagital_t2.height()/2, fill="#2DD", tags="slice_marker")
        cv4.create_line(coronal_depth/xcf_sagital_t2+CV_W.get()/2-sagital_t2.width()/2+2,0,coronal_depth/xcf_sagital_t2+CV_W.get()/2-sagital_t2.width()/2+2,CV_H.get(), fill="#F80", tags="coronal_depth_marker")
        cv4.create_line((coronal_depth+1)/xcf_sagital_t2+CV_W.get()/2-sagital_t2.width()/2+2,0,(coronal_depth+1)/xcf_sagital_t2+CV_W.get()/2-sagital_t2.width()/2+2,CV_H.get(), fill="#F80", tags="coronal_depth_marker")

        # AXIS INFO EN FOCUS CV
        cv.create_text(80,20,text="Axial/height: "+str(slice_num+1),fill="#2CC",font=("Roboto", 12),tags="cv_info")
        cv.create_text(80,40,text="Coronal/depth: "+str(coronal_depth_num+1),fill="#F80",font=("Roboto", 12),tags="cv_info")
        cv.create_text(80,60,text="Sagital/depth: "+str(sagital_depth_num+1),fill="#5D0",font=("Roboto", 12),tags="cv_info")

    # REDIBUJO EL CANVAS CON LO QUE TENIA
    for obj in obj_master:
        if obj.inslice == slice_num:
            obj.draw(False) """


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
        if sec.incv == cv:
            temp_sec = sec
            break
    if tipo == "s":
        obj_master.append(roi_square(tipo+str(len(obj_master)),temp_sec))
    elif tipo == "c":
        obj_master.append(roi_circle(tipo+str(len(obj_master)),temp_sec))
    elif tipo == "r":
        obj_master.append(roi_ruler(tipo+str(len(obj_master)),temp_sec))
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
    def __init__(self,name,UID):
        self.name = name    # nombre de secuencia -> name+TE+TR+Modes
        self.UID = UID      # UID único (lo que realmente las identifica)
        self.dcm_serie = [] # serie de dicoms pertenecientes al mismo UID
        self.incv = 0       # en que cv la quiero mostrar
        self.width = 0      # w del pixel_array de las dicom
        self.height = 0     # h del pixel_array de las dicom
        self.realx = 0      # tamaño en mm del pixel en x
        self.realy = 0      # tamaño en mm del pixel en y
    def add_dcm(self,dcm):
        self.dcm_serie.append(dcm)
        if dcm.pixel_array.shape[0] > self.height: self.height = dcm.pixel_array.shape[0] # ESTO NO HACE FALTA VER
        if dcm.pixel_array.shape[1] > self.width: self.width = dcm.pixel_array.shape[1]
    def load_img_serie(self):
        self.depth = len(self.dcm_serie)
        self.img_serie = np.zeros((self.depth,self.height,self.width))
        self.slice = int(self.depth/2)    # en que slice tengo posicionada la secuencia para mostrarla
        for n, dcm in enumerate(self.dcm_serie):
            try:
                self.img_serie[n] = dcm.pixel_array
            except:
                print("ALGUNAS IMAGENES NO SE CARGARON POR TAMAÑO")
        max = self.img_serie.max()
        for n in range(self.depth):
            self.img_serie[n] = (self.img_serie[n]/max)*255     # normalizo las imagenes
        
#-------------- MAIN LOOP ---------------------------------------------------------
      
        
root = Tk()
root.title("S A U R U S")
root.config(bg="#F00") #para debug
root.iconbitmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),"saurus_img","unsam.ico"))

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