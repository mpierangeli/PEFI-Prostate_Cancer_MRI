from matplotlib import docstring
from pylatex import Document, Command, Figure, Itemize, PageStyle,Head,simple_page_number,LineBreak,Foot,NewLine,MiniPage,SubFigure,VerticalSpace,HorizontalSpace,SmallText,LargeText,FlushLeft,Package,StandAloneGraphic,MediumText
from pylatex.utils import  NoEscape
import os
#------------------LATEX TO PDF------------------------------
# Diseño la estructura en "latex" y creo un .pdf
def generator ():
    geometry_options = {
            "head": "40pt",
            "margin": "1.5cm",
            "top": "1cm"
        }
    doc = Document(geometry_options=geometry_options)
    doc.packages.append(Package('booktabs'))
    doc.preamble.append(Package('babel', options='spanish'))

    footer = PageStyle("footer")
    with footer.create(Foot("C")):
        footer.append("-----Reporte generado automaticamente por software-----")
    doc.preamble.append(footer)
    doc.change_document_style("footer")

    doc.append(NoEscape(r"\noindent"))
    with doc.create(MiniPage(width=NoEscape(r"0.2\linewidth"))) as logo:
        logo.append("LOGO")
    with doc.create(MiniPage(width=NoEscape(r"0.6\linewidth"),align="c")) as titulo:
        titulo.append("REPORTE PI-RADS")
    with doc.create(MiniPage(width=NoEscape(r"0.2\linewidth"),align="r")) as datos:
        datos.append("Pág. 1 de 1")
        datos.append("\n")
        datos.append(NoEscape(r'\today'))
    doc.append(VerticalSpace("1cm"))

    doc.append("\n")
    doc.append(SmallText("Report ID:"))
    doc.append(NoEscape("\quad\quad\quad\quad"))
    doc.append(SmallText("12345678"))
    doc.append("\n")
    doc.append(SmallText("Paciente:"))
    doc.append(NoEscape("\quad\quad\quad\quad\quad"))
    doc.append(SmallText("JORGE CARRASCO"))
    doc.append("\n")
    doc.append(SmallText("Fecha estudio:"))
    doc.append(NoEscape("\hspace{1cm}"))
    doc.append(SmallText("11/5/2022"))
    doc.append("\n")
    doc.append(SmallText("Revisado por:"))
    doc.append(NoEscape("\hspace{1cm}"))
    doc.append(SmallText("JUAN PEREZ"))
    doc.append("\n")
    doc.append(NoEscape(r"\rule{\textwidth}{1pt}"))


    doc.generate_pdf("TEST-DOC__",clean=True)
#-------------------------------------------------------

generator()
