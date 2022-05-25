
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
    aux.pack(fill=X,ipady=5,pady=(20,30))
    Label(aux, text="Zona afectada",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    zonasprostata = ["1a","2a","3a","4a","5a","6a","7a","8a","9a","10a","11a","12a","13a","14a","15a",
                     "1p","2p","3p","4p","5p","6p","7p","8p","9p","10p","11p","12p"]
    zonas = ttk.Combobox(aux, state="readonly", values=zonasprostata,width=45)
    zonas.pack(side=LEFT,padx=5)
    b1 = Button(aux, text="Mapa >>", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2",height=1,command=img_setup)
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
    
    aux3 = Frame(steps_window,background="#555")
    aux3.pack(fill=X,ipady=2,pady=(20,0))
    Label(aux3, text="Lesión en ADC",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    adc_check = IntVar()
    Checkbutton(aux3,text="Visible",variable=adc_check,onvalue=1,offvalue=0,bg="#555",foreground="#FFF",selectcolor="#444",bd=0).pack(side=LEFT)
    aux5 = Frame(steps_window,background="#555")
    aux5.pack(fill=X,ipady=2,pady=(0,20))
    Label(aux5, text="Categoría PI-RADS:",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    catADC = IntVar()
    for n in range(5):
        Radiobutton(aux5, text=str(pirads_opt[n]), variable=catADC, value=pirads_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
        
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

    aux8 = Frame(steps_window,background="#555")
    aux8.pack(fill=X,ipady=2,pady=(30,10))  
    Label(aux8, text="Extensión Extraprostática",bg="#555",font=("Roboto",11),fg="#FFF").pack(fill=X,padx=20,ipady=5)
    eep = StringVar()
    auxframe = Frame(aux8)
    auxframe.pack(padx=(20,0))
    eep_opt = ["Bajo","Medio","Alto","Muy Alto"]
    for n in range(4):
        Radiobutton(auxframe, text=eep_opt[n], variable=eep, value=eep_opt[n], bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
   

    Label(steps_window, text="Información Adicional",bg="#444",font=("Roboto",11),fg="#FFF",anchor=W).pack(fill=X,pady=(20,10),padx=30)
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