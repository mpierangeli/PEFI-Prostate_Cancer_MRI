from easygui import *
from skimage import io,exposure
from skimage.filters.rank import gradient
from skimage.morphology import disk
import pydicom
import matplotlib.pyplot as plt

#import random.report_gen as report_gen

while 1:
    msgbox("Bienvenido a la prueba de GUI - PEFI2022")

    filepath = fileopenbox("Seleccione la imagen a reportar","MENU")
    full_dicom = pydicom.dcmread(filepath)
    img = full_dicom.pixel_array
    img = exposure.rescale_intensity(img,in_range="image",out_range=(0,1))
    gradient_img = gradient(img, disk(1))
    
    io.imsave("images\original.png",img)
    io.imsave("images\\bordes.png",gradient_img)

    plt.hist(img.flatten(),bins=100,log=True,histtype="stepfilled")
    plt.savefig("images\histograma.png")

    reply = buttonbox("Es la imagen correcta??", image="images\original.png", choices=["Si","No"])
    if reply=="Si":
        if ccbox("Quiere generar el reporte automático?"):
            report_gen.generator(full_dicom)
            if ccbox("Desea ingresar una nueva imágen?","Reporte generado exitosamente"):
                pass
            else:
                exit(0)
        else:
            pass
    else:
        pass