from pylatex import Document, Section, Command, Figure, Itemize, PageStyle,Head,simple_page_number,LineBreak,Foot,NewLine,MiniPage,SubFigure
from pylatex.utils import italic, NoEscape
import pydicom
import matplotlib.pyplot as plt

filePath = 'PROSTATA_1.MR.0001.0015.2021.12.22.13.14.21.169473.39474333.ima'
img = pydicom.dcmread(filePath) #leo la .ima como si fuera .dcm -> Invento de Siemens
plt.imshow(img.pixel_array,cmap=plt.cm.bone) #inserto la imagen en un plot para que lo entienda latex
print(img) # para ver por consola toda la info que brinda la imagen 

#------------------LATEX TO PDF------------------------------
# Diseño la estructura en "latex" y creo un .pdf

geometry_options = {
        "head": "40pt",
        "margin": "2cm",
        "top": "2cm"
    }
doc = Document(geometry_options=geometry_options)

header = PageStyle("header")
with header.create(Head("L")):
    header.append(NoEscape(r'\today'))
with header.create(Head("C")):
    header.append('Reporte de Prueba')
    header.append(LineBreak())
    header.append('PEFI 2022')
with header.create(Head("R")):
    header.append(simple_page_number())
with header.create(Foot("C")):
    header.append("-----Reporte generado automaticamente por software-----")

doc.preamble.append(header)
doc.change_document_style("header")

doc.append(italic('Primer prueba de reporte, a continuación 1 imagen .IMA y algunos datos:'))

with doc.create(Figure(position='htp')) as fig1:
    with doc.create(SubFigure(position='b',width=NoEscape(r'0.4\linewidth'))) as fig1_L:
        fig1_L.add_image("original.png",width=NoEscape(r'\linewidth'))
        fig1_L.add_caption('Original')
    with doc.create(SubFigure(position='b',width=NoEscape(r'0.4\linewidth'))) as fig1_R:
        fig1_R.add_image("bordes.png",width=NoEscape(r'\linewidth'))
        fig1_R.add_caption('Gradiente')
    fig1.add_caption("Prueba de imagenes")

# with doc.create(Figure(position='htb')) as plot:
#     plot.add_plot(width=NoEscape(r'0.5\textwidth'))
#     plot.add_caption(filePath)
doc.append('Información General')
doc.append(NewLine())
with doc.create(Itemize()) as itemize:
    itemize.add_item(str(img[0x0018,0x0087].keyword)+":  "+str(img[0x0018,0x0087].value))
    itemize.add_item(img[0x0008, 0x0020])
    itemize.add_item(img[0x0010, 0x0010])
    itemize.add_item(img[0x0010, 0x0040])
    itemize.add_item(img[0x0018, 0x0050])

doc.generate_pdf("TEST-DOC",clean=True)
#-------------------------------------------------------

