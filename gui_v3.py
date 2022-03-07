from tkinter import *
from PIL import Image,ImageTk
from tkinter import filedialog

#DICOM SETUP ?? ABRIR EL DICOM COMO SI FUERA UNA IMAGEN DE 1 VER VER VER VER
#filepath = filedialog.askopenfilename()
#ima = ImageTk.PhotoImage(Image.open(filepath))

def draw_line(event):

    x, y = event.x, event.y
    if cv.old_coords:
        x1, y1 = cv.old_coords
        cv.create_line(x, y, x1, y1)
    cv.old_coords = x,y
def clear_app(event):
    cv.old_coords = None

#MAIN WINDOW SETUP
root = Tk()
root.title("Software de Prueba PEFI 2022")
root.maxsize(800, 600)
#root.geometry("800x600")
root.config(bg="skyblue")
root.iconbitmap("unsam.ico")

#MAIN WINDOW DISPLAY
l_frame = Frame(root, width=200, height=580)
l_frame.grid(row=0, column=0, padx=10, pady=10)
r_frame = Frame(root, width=560, height=580)
r_frame.grid(row=0, column=1, padx=10, pady=10)


Label(l_frame, text="Imágen Original").grid(row=0, column=0, padx=5, pady=5)
image = PhotoImage(file="images\original.png").subsample(2,2)
Label(l_frame, image=image).grid(row=1, column=0, padx=5, pady=5)


# DIBUJAR EN CANVAS





cv = Canvas(r_frame, width=550,height=560)
cv.grid(row=0,column=0, padx=5, pady=5)
cv.old_coords = None

cv.bind('<B1-Motion>', draw_line)
cv.bind('<ButtonRelease-1>', clear_app)



tool_bar = Frame(l_frame, width=180, height=340)
tool_bar.grid(row=2, column=0, padx=5, pady=5)
Label(tool_bar, text="Tools").grid(row=0, column=0, padx=5, pady=10) 
Label(tool_bar, text="Filters").grid(row=0, column=1, padx=5, pady=10)
Label(tool_bar, text="Select").grid(row=1, column=0, padx=5, pady=5)
Button(tool_bar, text="Crop").grid(row=2, column=0, padx=5, pady=5)
Label(tool_bar, text="Rotate & Flip").grid(row=3, column=0, padx=5, pady=5)
Label(tool_bar, text="Resize").grid(row=4, column=0, padx=5, pady=5)
Label(tool_bar, text="Exposure").grid(row=5, column=0, padx=5, pady=5)

root.mainloop()