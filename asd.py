
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
    aux1 = Frame(steps_window,background="#555")
    aux1.pack(fill=X,ipady=5,pady=10)
    Label(aux1, text="Zona afectada",bg="#555",font=("Roboto",11),fg="#FFF").pack(side=LEFT,padx=20)
    zonasprostata = [""]
    zonas = ttk.Combobox(aux1, state="readonly", values=["Zona A","Zona B","Zona C"],width=45)
    zonas.pack(side=LEFT,padx=5)
    b1 = Button(aux1, text="Mapa >>", font=("Roboto",10), bg="#2CC", bd=0, cursor="hand2",height=1,command=img_setup)
    b1.pack(side=RIGHT,ipadx=5)

    Label(steps_window, text="Lesión en T2",bg="#444",font=("Roboto",10),fg="#FFF",anchor=W).pack(fill=X,pady=10,padx=30)
    lesionT2 = ttk.Combobox(steps_window, state="readonly", values=["Zona A","Zona B","Zona C"],width=70)
    lesionT2.pack()

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