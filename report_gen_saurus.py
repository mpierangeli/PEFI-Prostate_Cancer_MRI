from matplotlib import docstring
from pylatex import Document, Command, Figure, Itemize, PageStyle,Head,simple_page_number,LineBreak,Foot,NewLine,MiniPage,SubFigure,VerticalSpace,HorizontalSpace,SmallText,LargeText,HFill
from pylatex.utils import  NoEscape

#------------------LATEX TO PDF------------------------------
# Diseño la estructura en "latex" y creo un .pdf
def generator ():
    geometry_options = {
            "head": "40pt",
            "margin": "1.5cm",
            "top": "2cm"
        }
    doc = Document(geometry_options=geometry_options)

    header = PageStyle("header")
    with header.create(Head("L")):
        header.append(NoEscape(r'\today'))
    with header.create(Head("C")):
        header.append('Reporte PI-RADS')
        header.append(LineBreak())
        header.append('PEFI 2022')
    with header.create(Head("R")):
        header.append(simple_page_number())
    with header.create(Foot("C")):
        header.append("-----Reporte generado automaticamente por software-----")
    doc.preamble.append(header)
    doc.change_document_style("header")
    
    
    doc.append(SmallText("PACIENTE: "))
    doc.append(LineBreak())
    doc.append(SmallText("PACIENTE: "))
    doc.append(LineBreak())
    doc.append(SmallText("PACIENTE: "))
    doc.append(NewLine())
    doc.append(NoEscape(r"\noindent\rule{\textwidth}{1pt}"))
    doc.append(NewLine())

    doc.generate_pdf("TEST-DOC__",clean=True)
#-------------------------------------------------------

generator()
