from pylatex import Document, Command, Figure, Itemize, PageStyle,Head,simple_page_number,LineBreak,Foot,NewLine,MiniPage,SubFigure,VerticalSpace,HorizontalSpace,SmallText,LargeText,FlushLeft,Package,StandAloneGraphic,MediumText,Subsection
from pylatex.utils import  NoEscape,bold,italic
#------------------LATEX TO PDF------------------------------
# Diseño la estructura en "latex" y creo un .pdf
def generator ():
    geometry_options = {
            "head": "40pt",
            "margin": "1.5cm",
            "top": "1cm",
            #"bottom": "2cm"
        }
    doc = Document(geometry_options=geometry_options,lmodern=False)
    doc.packages.append(Package('booktabs'))
    doc.preamble.append(Package('babel', options='spanish'))
    doc.packages.append(Package('montserrat',"defaultfam"))
    footer = PageStyle("footer")
    with footer.create(Foot("C")):
        #footer.append(NoEscape(r"\centering"))
        footer.append("Corporación Médica de Gral. San Martín SA - Matheu 4071, (1650) San Martín - Tel. 47547500")
    doc.preamble.append(footer)
    doc.change_document_style("footer")

    doc.append(NoEscape(r"\noindent"))
    with doc.create(MiniPage(width=NoEscape(r"0.2\linewidth"))) as logo:
        logo.append(StandAloneGraphic(image_options="width=150px",filename="logo_unsam_big.png"))

    with doc.create(MiniPage(width=NoEscape(r"0.6\linewidth"),align="c")) as titulo:
        titulo.append("REPORTE PI-RADS")
    with doc.create(MiniPage(width=NoEscape(r"0.2\linewidth"),align="r")) as datos:
        datos.append("Pág. 1 de 1")
        datos.append("\n")
        datos.append(NoEscape(r'\today'))
    doc.append(VerticalSpace("0.5cm"))

    doc.append("\n")
    doc.append(SmallText("Report ID:asdasd"))
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

    doc.append("\n\n")
    doc.append(SmallText("HISTORIA CLÍNICA"))
    doc.append("\n\n")
    doc.append(SmallText("Motivo Estudio: aca iria lo escrito"))
    doc.append("\n")
    doc.append(SmallText("PSA: VALOR del soft  PSAD: VALOR del soft   FECHA: VALOR del soft"))
    doc.append("\n")
    
    doc.append("\n\n")
    doc.append(SmallText("RESULTADOS"))
    doc.append("\n\n")
    doc.append(SmallText("Vol. Prostático: VALOR del soft  Dim: NNxNNxNN del soft"))
    doc.append("\n")
    doc.append(SmallText("Hemorragia: SI/NO del soft"))
    doc.append("\n")
    doc.append(SmallText("Lesión Neurovascular: SI/NO del soft"))
    doc.append("\n")
    doc.append(SmallText("Lesión Vesicula Seminal: SI/NO del soft"))
    doc.append("\n")
    doc.append(SmallText("Lesión Nodos Linfáticos: SI/NO del soft"))
    doc.append("\n")
    doc.append(SmallText("Lesión Huesos: SI/NO del soft"))
    doc.append("\n")
    doc.append(SmallText("Lesión Órganos: SI/NO del soft"))
    doc.append("\n\n")
    
    doc.append(SmallText("Calidad de Imágenes: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."))
    doc.append("\n")
    doc.append(SmallText("Zona Periférica: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."))
    doc.append("\n")
    doc.append(SmallText("Zona Transicional: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."))
    doc.append("\n\n")
    
    doc.append(SmallText("LESIONES"))
    doc.append("\n\n")
    
    #for obs in observaciones:
    doc.append(SmallText("Observacion ID: 123" ))
    doc.append("\n")
    doc.append(SmallText("Zona Afectada: 123 + AGREGAR MAPA AL LADO" ))
    doc.append("\n")
    doc.append(SmallText("Dimensiones y volumen?: 123 NNxNNxNN" ))
    doc.append("\n")
    doc.append(SmallText("CLASIFICACIÓN PIRADs: 1" ))
    doc.append("\n")
    doc.append(SmallText("Extensión Extraprostática: CUANTO" ))
    doc.append("\n")
    doc.append(SmallText("Información adicional: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum." ))
    doc.append("\n\n")
    doc.append(SmallText("IMAGENES DE LA OBSERVACION" ))
    
    
    
    doc.append("\n\n")
    doc.append(SmallText("CONCLUSION"))
    doc.append("\n\n")
    doc.append(SmallText("Conclusiones: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."))
    doc.append("\n")
    doc.append(SmallText("PIRADS GENERAL: VALOR POR SOFTWARE"))
    doc.append("\n")
    doc.append(SmallText("IMAGEN PIRADS LOCALIZADA"))
    doc.append("\n\n")
    
    doc.append(SmallText("Sobre los resultados"))
    doc.append("\n")
    doc.append(SmallText("PIRADS 1 - Very low. Clinically significant cancer is highly unlikely to be present.\nPIRADS 2 - Low clinically significant cancer is unlikely to be present.\nPIRADS 3 - Intermediate the presence of clinically significant cancer is equivocal.\nPIRADS 4 - High clinically significant cancer is likely to be present.\nPIRADS 5 - Very high clinically significant cancer is highly likely to be present "))

    
    
    


    doc.generate_pdf("TEST-DOC__",clean=True)
#-------------------------------------------------------
# FUNCION QUE ANEXA LOS RESULTADOS DE CADA OBSERVACION
def obstodoc():
    pass

#-------------------------------------------------------
generator()
