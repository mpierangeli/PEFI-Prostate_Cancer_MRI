
from msilib.schema import CheckBox
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

def img_setup():
    global mapa_setup
    try: mapa_setup.destroy()
    except:
        mapa_setup = Frame(root,background="#444")
        mapa_setup.place(relx=0.78,rely=0.5, width=570,height=700,anchor=CENTER)
        img = ImageTk.PhotoImage(Image.open("sector_map.jpg"))
        l1 = Label(mapa_setup, image = img)
        l1.image = img
        l1.pack(pady=20,padx=5)
    

def test():
    
    steps_window = Frame(root,background="#444")
    steps_window.place(relx=0.5,rely=0.5, width=500,height=1000,anchor=CENTER)
    Label(steps_window, text="Sobre la lesión...",bg="#2CC",font=("Roboto",12),fg="#000").pack(fill=X,ipady=5,ipadx=20)
    aux = Frame(steps_window,background="#555")
    aux.pack(fill=X,ipady=5,pady=10)
    Label(aux, text="Zona afectada",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    zonasprostata = ["1a","2a","3a","4a","5a","6a","7a","8a","9a","10a","11a","12a","13a","14a","15a",
                     "1p","2p","3p","4p","5p","6p","7p","8p","9p","10p","11p","12p"]
    zonas = ttk.Combobox(aux, state="readonly", values=zonasprostata,width=45)
    zonas.pack(side=LEFT,padx=5)
    b1 = Button(aux, text="Mapa >>", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2",height=1,command=img_setup)
    b1.pack(side=RIGHT,ipadx=5)
    
    
    aux = Frame(steps_window,background="#555")
    aux.pack(fill=X,pady=1)
    t2_info = [StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()]
    Label(aux, text="Lesión en T2",bg="#555",font=("Roboto",10),fg="#FFF",anchor=W).pack(side=LEFT,padx=30)
    Checkbutton(aux,text="Visible",variable=t2_info[0],onvalue="si",offvalue="no",bg="#555",foreground="#FFF",selectcolor="#444",bd=0).pack(side=LEFT)
    aux2 = Frame(steps_window,background="#555")
    aux2.pack(fill=X)
    Label(aux2, text="Tipo:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
    info1 = ["Hipotenso","Hipertenso"]
    for n in range(len(info1)):
        Radiobutton(aux2, text=info1[n], variable=t2_info[1], value=info1[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    aux3 = Frame(steps_window,background="#555")
    aux3.pack(fill=X)
    Label(aux3, text="Intensidad:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
    info2 = ["Leve","Moderada","Significante"]
    for n in range(len(info2)):
        Radiobutton(aux3, text=info2[n], variable=t2_info[2], value=info2[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    aux4 = Frame(steps_window,background="#555")
    aux4.pack(fill=X)
    Label(aux4, text="Bordes:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
    info3 = ["Circunscrita","No circunscrita"]
    for n in range(len(info3)):
        Radiobutton(aux4, text=info3[n], variable=t2_info[3], value=info3[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    aux5 = Frame(steps_window,background="#555")
    aux5.pack(fill=X)
    Label(aux5, text="Homogeneidad:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
    info4 = ["Homogenea","Heterogenea"]
    for n in range(len(info4)):
        Radiobutton(aux5, text=info4[n], variable=t2_info[4], value=info4[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    aux6 = Frame(steps_window,background="#555")
    aux6.pack(fill=X)
    Label(aux6, text="Focalidad:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
    info5 = ["Focalizada","No focalizada"]
    for n in range(len(info5)):
        Radiobutton(aux6, text=info5[n], variable=t2_info[5], value=info5[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    aux7 = Frame(steps_window,background="#555")
    aux7.pack(fill=X)
    Label(aux7, text="Forma:",bg="#555",font=("Roboto",10),fg="#FFF",width=18).pack(side=LEFT,padx=5)
    info6 = ["Lineal","Lenticular","Irregular"]
    for n in range(len(info6)):
        Radiobutton(aux7, text=info6[n], variable=t2_info[6], value=info6[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT) 

        





    Label(steps_window, text="Lesión en ADC",bg="#444",font=("Roboto",10),fg="#FFF",anchor=W).pack(fill=X,pady=10,padx=30)
    lesionADC = ttk.Combobox(steps_window, state="readonly", values=["Zona A","Zona B","Zona C"],width=70)
    lesionADC.pack()

    Label(steps_window, text="Lesión en DWI",bg="#444",font=("Roboto",10),fg="#FFF",anchor=W).pack(fill=X,pady=10,padx=30)
    lesionDWI = ttk.Combobox(steps_window, state="readonly", values=["Zona A","Zona B","Zona C"],width=70)
    lesionDWI.pack()

    Label(steps_window, text="Extensión Extraprostática",bg="#444",font=("Roboto",10),fg="#FFF",anchor=W).pack(fill=X,pady=10,padx=30)
    eep = StringVar()
    auxframe = Frame(steps_window)
    auxframe.pack(padx=(30,0),anchor=W)
    Radiobutton(auxframe, text="Bajo", variable=eep, value="Bajo", bg="#444",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    Radiobutton(auxframe, text="Medio", variable=eep, value="Medio", bg="#444",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    Radiobutton(auxframe, text="Alto", variable=eep, value="Alto", bg="#444",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    Radiobutton(auxframe, text="Muy Alto", variable=eep, value="Muy Alto", bg="#444",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)

    Label(steps_window, text="Información Adicional",bg="#444",font=("Roboto",10),fg="#FFF",anchor=W).pack(fill=X,pady=(20,10),padx=30)
    info = Text(steps_window,width=62,font=("Roboto",10),height=10,bg="#555",fg="#FFF",bd=0,insertbackground="#2CC")
    info.pack()
    auxframe2 = Frame(steps_window)
    auxframe2.pack(padx=30,pady=30,anchor=W)
    b3 = Button(auxframe2, text="Agregar Imágenes", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2")
    b3.pack(ipadx=2,ipady=2)
    b4 = Button(steps_window, text="Guardar Observación", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2",height=3,command=lambda step=3:steps_main(step))
    b4.pack(fill=X,side=BOTTOM)

root = Tk()
root.minsize(width=1900,height=1000)
test()
root.mainloop()