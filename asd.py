from tkinter import *

def colorOnFocus(b: Button, n=bool):
    if n:   b.widget.config(background="#F80")
    else:   b.widget.config(background="#2CC")

def test():
    steps_window = Frame(root,background="#444")
    steps_window.place(relx=0.5,rely=0.5, width=500,height=1000,anchor=CENTER)
    Label(steps_window, text="Sobre el paciente...",bg="#2CC",font=("Roboto",12),fg="#000").pack(fill=X,ipady=5,ipadx=20,pady=(0,20))

    info_general = Frame(steps_window,background="#555")
    info_general.pack(fill=X,pady=(0,20),ipadx=2, ipady=2)
    Label(info_general, text="Paciente:     JUAN CARLOS PELOTUDO",bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=5,ipadx=20,anchor=W)
    Label(info_general, text="Edad: 65 años         Sexo: Masculino",bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
    Label(info_general, text="Peso: 90 kg       Altura: 180 cm      IMC: 23",bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
    Label(info_general, text="-"*100,bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
    Label(info_general, text="Volúmen Prostático: 35 ml(*)",bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
    Label(info_general, text="Dimensiones Próstata: 10x10x20 mm3",bg="#555",font=("Roboto",10),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
    
    Label(steps_window, text="Historial Clínico",bg="#444",font=("Roboto",12),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
    historial = Frame(steps_window,background="#555")
    historial.pack(fill=X,ipadx=2, ipady=2, pady=(0,20))
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
    #psa = [psa_value.get(),psa_date1.get(),psa_date2.get(),psa_date3.get()]
    auxframe5 = Frame(historial,background="#555")
    auxframe5.pack(fill=X,pady=5)
    Label(auxframe5, text="Motivo\nEstudio:",bg="#555",font=("Roboto",10),fg="#FFF",width=10).pack(side=LEFT,padx=5)
    t1 = Text(auxframe5,width=55,height=4,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
    t1.pack(side=LEFT)
    
    Label(steps_window, text="Sobre la próstata...",bg="#444",font=("Roboto",12),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
    
    estudio_info = Frame(steps_window,background="#555")
    estudio_info.pack(fill=X,ipadx=2, ipady=2, pady=(0,20))
    hemo = StringVar()
    auxframe = Frame(estudio_info,bg="#555")
    auxframe.pack(anchor=W,pady=5)
    Label(auxframe, text="Hemorragia:",bg="#555",font=("Roboto",10),fg="#FFF",width=10).pack(side=LEFT,padx=10)
    Radiobutton(auxframe, text="Si", variable=hemo, value="Si", bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    Radiobutton(auxframe, text="No", variable=hemo, value="No", bg="#555",anchor=W,foreground="#FFF",selectcolor="#444",activebackground="#2CC").pack(side=LEFT)
    auxframe2 = Frame(estudio_info,bg="#555")
    auxframe2.pack(anchor=W,pady=5)
    Label(auxframe2, text="Calidad\nImágenes: ",bg="#555",font=("Roboto",10),fg="#FFF",width=9).pack(side=LEFT,padx=10)
    t2 = Text(auxframe2,width=55,height=4,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
    t2.pack(side=LEFT)
    auxframe3 = Frame(estudio_info,bg="#555")
    auxframe3.pack(anchor=W,pady=5)
    Label(auxframe3, text="Zona\nPeriférica: ",bg="#555",font=("Roboto",10),fg="#FFF",width=9).pack(side=LEFT,padx=10)
    t3 = Text(auxframe3,width=55,height=4,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
    t3.pack(side=LEFT)
    auxframe4 = Frame(estudio_info,bg="#555")
    auxframe4.pack(anchor=W,pady=5)
    Label(auxframe4, text="Zona\nTransicional: ",bg="#555",font=("Roboto",10),fg="#FFF",width=9).pack(side=LEFT,padx=10)
    t4 = Text(auxframe4,width=55,height=4,font=("Roboto",10),fg="#FFF",bd=0,bg="#666",insertbackground="#2CC")
    t4.pack(side=LEFT)
    
    Label(steps_window, text="Sobre las lesiones...",bg="#444",font=("Roboto",12),fg="#FFF").pack(ipady=1,ipadx=20,anchor=W)
    
    lesiones_info = Frame(steps_window,background="#555")
    lesiones_info.pack(fill=X,ipadx=2, ipady=2)
    
    for obs in observaciones:
        mini_report = Frame(lesiones_info,background="#444")
        mini_report.pack(fill=X,pady=(0,5),ipadx=2, ipady=2)
        Label(mini_report, text="ID: "+str(obs.id),bg="#444",font=("Roboto",9),fg="#FFF").pack(side=LEFT)
        Label(mini_report, text="PI-RADS: "+str(obs.categoria),bg="#444",font=("Roboto",9),fg="#FFF").pack(side=LEFT)
        
    b4 = Button(steps_window, text="Finalizar y Generar PDF", font=("Roboto",12), bg="#2CC", bd=0, cursor="hand2",height=3)
    b4.pack(fill=X,side=BOTTOM)
    b4.bind("<Enter>",lambda b=b4:colorOnFocus(b,True))
    b4.bind("<Leave>",lambda b=b4:colorOnFocus(b,False))
    
root = Tk()
root.title("S A U R U S")
root.config(bg="#F00") #para debug
root.minsize(width=800, height=1000)
test()

root.mainloop()