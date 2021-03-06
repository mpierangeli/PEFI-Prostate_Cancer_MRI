from tkinter import *
from PIL import Image,ImageTk
from tkinter import filedialog
import pydicom
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
    editmenu.add_command(label="ROI Rectangular",command=lambda tipo="s": roi_gen(tipo))
    editmenu.add_command(label="ROI Circular",command=lambda tipo="c": roi_gen(tipo))
    editmenu.add_command(label="Medición",command=lambda tipo="r": roi_gen(tipo))

    reportmenu = Menu(menubar, tearoff=0)
    reportmenu.add_command(label="Nuevo Reporte",command=report_window_gen)

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Keybinds", command=key_tab_gen)
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

    root.bind("<Control-MouseWheel>", slice_and_depth_selector)

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
    set_img(slice_num,coronal_depth_num,sagital_depth_num)
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
    if axis_switch:
        cv.create_text(80,20,text="Axial/height: "+str(slice_num+1),fill="#2CC",font=("Roboto", 12),tags="cv_info")
        cv.create_text(80,40,text="Coronal/depth: "+str(coronal_depth_num+1),fill="#F80",font=("Roboto", 12),tags="cv_info")
        cv.create_text(80,60,text="Sagital/depth: "+str(sagital_depth_num+1),fill="#5D0",font=("Roboto", 12),tags="cv_info")
def unfocus_cv(event):
    cv.delete("focus_check","cv_info")
def reset_cv(event):
    global zoomed
    zoomed = False
    cv.delete(ALL)
    set_img(slice_num,coronal_depth_num,sagital_depth_num)

def slice_and_depth_selector(event):
    global slice_num,coronal_depth_num,sagital_depth_num
    if cv == cv1:
        if event.delta > 0 and slice_num < len(axiales)-1: slice_num+=1
        elif event.delta < 0 and slice_num > 0: slice_num-=1
    if cv == cv2:
        if event.delta > 0 and coronal_depth_num < len(coronales)-1: coronal_depth_num+=1
        elif event.delta < 0 and coronal_depth_num > 0: coronal_depth_num-=1
    if cv == cv4:
        if event.delta > 0 and sagital_depth_num < len(sagitales)-1: sagital_depth_num+=1
        elif event.delta < 0 and sagital_depth_num > 0: sagital_depth_num-=1
    
    set_img(slice_num,coronal_depth_num,sagital_depth_num)

def patient_loader():
    global filepaths, axiales, coronales, sagitales, slice_num, coronal_depth_num, sagital_depth_num, factor, init_dcm, init_img, px_info_var, px_info_static, zoomed, axis_switch, obj_master
    
    filepaths_raw = filedialog.askopenfilenames()
    if not filepaths_raw: 
        set_img(slice_num,coronal_depth_num,sagital_depth_num)
        return
    filepaths = list(filepaths_raw)
    
    #GENERO CONTAINER DE OBJETOS VERVERVER
    obj_master = []
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

def axis_onoff (event):
    global axis_switch
    axis_switch = False if axis_switch else True
    set_img(slice_num,coronal_depth_num,sagital_depth_num)
        
def key_tab_gen():
    global key_tab
    key_tab = Frame(root,background="#2CC")
    key_tab.place(relx=0,rely=0, width=400, height=MF_H.get())
    l2 = Label(key_tab, text="KEYBINDS",bg="#2CC",font=("Roboto",10),fg="#000").grid(row=0,column=0,pady=(10,20))

    i1 = Label(key_tab, text="F1 -> INFORMACIÓN PACIENTE",bg="#2CC",font=("Roboto",9),fg="#000").grid(row=2,column=0,pady=(0,10))
    i8 = Label(key_tab, text="F2 -> AXIS ON/OFF",bg="#2CC",font=("Roboto",9),fg="#000").grid(row=2,column=0,pady=(0,10))
    i2 = Label(key_tab, text="F3 -> LIMPIAR CANVAS (seleccionado por puntero)",bg="#2CC",font=("Roboto",9),fg="#000").grid(row=4,column=0,pady=(0,10))
    i3 = Label(key_tab, text="F4 -> RESETEAR ZOOM/CANVAS (seleccionado por puntero)",bg="#2CC",font=("Roboto",9),fg="#000").grid(row=5,column=0,pady=(0,10))
    i4 = Label(key_tab, text="Ctrl+Z -> BORRAR ÚLTIMA HERRAMIENTA",bg="#2CC",font=("Roboto",9),fg="#000").grid(row=6,column=0,pady=(0,10))
    i5 = Label(key_tab, text="Right Click -> ZOOM",bg="#2CC",font=("Roboto",9),fg="#000").grid(row=7,column=0,pady=(0,10))
    i6 = Label(key_tab, text="Ctrl+Ruedita -> CAMBIO SLICE/DEPTH (seleccionado por puntero)",bg="#2CC",font=("Roboto",9),fg="#000").grid(row=8,column=0,pady=(0,10))
    i7 = Label(key_tab, text="Escape para cerrar esta ventana",bg="#2CC",font=("Roboto",9),fg="#000").grid(row=9,column=0,pady=(50,10))

    root.bind("<Escape>",key_tab_destroy)
def key_tab_destroy(event):
    key_tab.destroy()

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

def set_img(slice,coronal_depth,sagital_depth):
    global cv,cv1,cv2,cv3,cv4,axial_t2,coronal_t2,sagital_t2, xcf_axial_t2, ycf_axial_t2, xcf_coronal_t2, ycf_coronal_t2, px_info_var, xi,yi,xf,yf
    
    temp_axial_t2 = imutils.resize(axiales[slice], height=CV_H.get())
    init_width = temp_axial_t2.shape[1]
    init_height = temp_axial_t2.shape[0]
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
        
    temp_coronal_t2 = imutils.resize(coronales[coronal_depth], width=init_width) 
    xcf_coronal_t2 = coronales[coronal_depth].shape[0]/temp_coronal_t2.shape[0] #x factor correction -> por el resize
    ycf_coronal_t2 = coronales[coronal_depth].shape[1]/temp_coronal_t2.shape[1] #y factor correction -> por el resize
    
    temp_sagital_t2 = imutils.resize(sagitales[sagital_depth], width=init_height) 
    xcf_sagital_t2 = sagitales[sagital_depth].shape[0]/temp_sagital_t2.shape[0] #x factor correction -> por el resize
    ycf_sagital_t2 = sagitales[sagital_depth].shape[1]/temp_sagital_t2.shape[1] #y factor correction -> por el resize

    axial_t2 = ImageTk.PhotoImage(Image.fromarray(temp_axial_t2))
    coronal_t2 = ImageTk.PhotoImage(Image.fromarray(temp_coronal_t2))
    sagital_t2 = ImageTk.PhotoImage(Image.fromarray(temp_sagital_t2))
    
    px_info_var = [float(init_dcm[0x0028,0x0030].value[0])*xcf_axial_t2,float(init_dcm[0x0028,0x0030].value[1])*ycf_axial_t2]

    cv1.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=axial_t2, tags="axial_t2")
    cv2.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=coronal_t2, tags="coronal_t2")
    cv4.create_image(CV_W.get()/2, CV_H.get()/2, anchor=CENTER, image=sagital_t2, tags="sagital_t2")

    cv1.delete("coronal_depth_marker","sagital_depth_marker","cv_info")
    cv2.delete("slice_marker","sagital_depth_marker","cv_info")
    cv3.delete("cv_info")
    cv4.delete("slice_marker","coronal_depth_marker","cv_info")
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
            obj.draw(False)

## HERRAMIENTAS

#ROI GENERATORS
def roi_gen(tipo):
    root.config(cursor="tcross")
    root.bind('<Button-1>', lambda event, arg=tipo: roi_start(event,arg))
    root.bind('<B1-Motion>', roi_temp)
    root.bind('<ButtonRelease-1>', roi_end)
def roi_start(event,tipo):
    if tipo == "s":
        obj_master.append(roi_square(tipo+str(len(obj_master)),cv,slice_num))
    elif tipo == "c":
        obj_master.append(roi_circle(tipo+str(len(obj_master)),cv,slice_num))
    elif tipo == "r":
        obj_master.append(roi_ruler(tipo+str(len(obj_master)),cv,slice_num))
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
    root.config(cursor="arrow")
    root.unbind('<Button-1>')
    root.unbind('<B1-Motion>')
    root.unbind('<ButtonRelease-1>')


    if obj_master[-1].xi == event.x and obj_master[-1].yi == event.y:
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
    def __init__(self,name,incv,inslice):
        self.name = name
        self.incv = incv
        self.inslice = inslice
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
        self.xdis = abs(round(px_info_var[0]*self.dx,2))
        self.ydis = abs(round(px_info_var[1]*self.dy,2))
        cv.create_text((self.xf+self.xi)/2,self.yi+b,text=str(self.xdis)+"mm",fill="#F00",font=("Roboto", 9),tags=self.name)
        cv.create_text(self.xi+a,(self.yf+self.yi)/2,text=str(self.ydis)+"mm",fill="#F00",font=("Roboto", 9),tags=self.name,angle=90)
class roi_circle:
    def __init__(self,name,incv,inslice):
        self.name = name
        self.incv = incv
        self.inslice = inslice
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
        self.rdis = math.sqrt((self.dx*px_info_var[0])**2+(self.dy*px_info_var[1])**2) # Porq distancia real depende del ancho de pixel en cada dirección.
        cv.create_text(self.xi,self.yi+self.r+10,text="r: "+str(round(self.rdis,2))+"mm",fill="#F00",font=("Roboto", 9),tags=self.name)
class roi_ruler:
    def __init__(self,name,incv,inslice):
        self.name = name
        self.incv = incv
        self.inslice = inslice
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
        self.rdis = math.sqrt((self.dx*px_info_var[0])**2+(self.dy*px_info_var[1])**2) # Porq distancia real depende del ancho de pixel en cada dirección.
        a = 10
        b = 10
        if int(self.dx) == 0: b -= 10
        elif int(self.dy) == 0: a -= 10
        elif self.dx*self.dy > 0: 
            self.ang = -self.ang
            a -= 20
        cv.create_text((self.xf+self.xi)/2+a,(self.yf+self.yi)/2+b,text=str(round(self.rdis,2))+"mm",fill="#2CC",font=("Roboto", 9),tags=self.name,angle=self.ang)
        

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