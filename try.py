from pylatex import Document, Section, Command, Figure, Itemize
from pylatex.utils import italic, NoEscape
import pydicom
import matplotlib.pyplot as plt

filePath = 'PROSTATA_1.MR.0001.0015.2021.12.22.13.14.21.169473.39474333.ima'
img = pydicom.dcmread(filePath) #leo la .ima como si fuera .dcm -> Invento de Siemens
plt.imshow(img.pixel_array,cmap=plt.cm.bone) #inserto la imagen en un plot para que lo entienda latex
print(img) # para ver por consola toda la info que brinda la imagen 

#------------------LATEX TO PDF------------------------------
# Diseño la estructura en "latex" y creo un .pdf
doc = Document()

doc.preamble.append(Command('title', 'Reporte de Prueba'))
doc.preamble.append(Command('author', 'PEFI 2022'))
doc.preamble.append(Command('date', NoEscape(r'\today')))
doc.append(NoEscape(r'\maketitle'))

with doc.create(Section('Primera Parte')):
    doc.append(italic('Primer prueba de reporte, a continuación 1 imagen .IMA y algunos datos:'))
    with doc.create(Figure(position='htbp')) as plot:
        plot.add_plot(width=NoEscape(r'1\textwidth'))
        plot.add_caption(filePath)
    with doc.create(Itemize()) as itemize:
        itemize.add_item(str(img[0x0018,0x0087].keyword)+":  "+str(img[0x0018,0x0087].value))
        itemize.add_item(img[0x0008, 0x0020])
        itemize.add_item(img[0x0010, 0x0010])
        itemize.add_item(img[0x0010, 0x0040])
        itemize.add_item(img[0x0018, 0x0050])

doc.generate_pdf("TEST-DOC",clean=True)
#-------------------------------------------------------

