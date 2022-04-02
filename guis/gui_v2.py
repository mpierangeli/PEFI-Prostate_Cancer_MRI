from tkinter import *
from PIL import Image,ImageTk
from tkinter import filedialog
import pydicom


def img_selector():
    global ima
    global filepath
    filepath = filedialog.askopenfilename()
    ima = ImageTk.PhotoImage(Image.open(filepath))
    venta = Label(image=ima)
    venta.grid(row=1,column=0)
def efecter():
    global ima_2
    ima_2 = ImageTk.PhotoImage(Image.open("images\\bordes.png"))
    venta_2 = Label(image=ima_2)
    venta_2.grid(row=2,column=0)


root = Tk()
root.title("Software de Prueba PEFI 2022")
root.geometry("640x640")
filepath = "images\original.png"
ima = ImageTk.PhotoImage(Image.open(filepath))

frame1 = Frame(root)
frame1.grid(column=0)

btn_1 = Button(root, text="Selección Imágen",command=img_selector)
btn_1.grid(row=0,column=1)

venta = Label(frame1,image=ima)
venta.grid(row=1,column=0)

btn_2 = Button(root, text="Aplicar efecto",command=efecter)
btn_2.grid(row=1,column=1)

root.mainloop()