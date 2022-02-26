from pylatex import Document, Command, Figure, Itemize, PageStyle,Head,simple_page_number,LineBreak,Foot,NewLine,MiniPage,SubFigure,VerticalSpace,HorizontalSpace,SmallText,LargeText
from pylatex.utils import  NoEscape

#------------------LATEX TO PDF------------------------------
# Diseño la estructura en "latex" y creo un .pdf
def generator (img):
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
    doc.append(LargeText('Primer prueba de reporte'))
    doc.append(VerticalSpace("0.3cm"))
    doc.append(NewLine())
    doc.append(SmallText("""PI-RADS v2.1 is not a comprehensive prostate cancer diagnosis document and should be used in
    conjunction with other current resources. For example, it does not address the use of MRI for
    detection of suspected recurrent prostate cancer following therapy, progression during surveillance,
    or the use of MRI for evaluation of other parts of the body (e.g. skeletal system) that may be involved
    with prostate cancer. Furthermore, it does not elucidate or prescribe optimal technical parameters;
    only those that should result in an acceptable mpMRI examination."""))
    with doc.create(Figure(position='htp')) as fig1:
        doc.append(Command('centering'))
        with doc.create(SubFigure(position='b',width=NoEscape(r'0.3\linewidth'))) as fig1_L:
            fig1_L.add_image("images\original.png",width=NoEscape(r'\linewidth'))
            fig1_L.add_caption('Original')
        doc.append(HorizontalSpace("1cm"))
        with doc.create(SubFigure(position='b',width=NoEscape(r'0.3\linewidth'))) as fig1_R:
            fig1_R.add_image("images\\bordes.png",width=NoEscape(r'\linewidth'))
            fig1_R.add_caption('Gradiente')
        fig1.add_caption("Prueba de imágenes")

    with doc.create(Figure(position='htbp')) as plot:
        plot.add_image("images\histograma.png",width=NoEscape(r'0.5\linewidth'))
        plot.add_caption('Histograma')

    doc.append(VerticalSpace("0.3cm"))
    with doc.create(MiniPage(width=NoEscape(r"0.5\linewidth"))) as dc:
        doc.append('Información General')
        with doc.create(Itemize()) as itemize:
            itemize.add_item(str(img[0x0018,0x0087].keyword)+":  "+str(img[0x0018,0x0087].value))
            itemize.add_item(img[0x0008, 0x0020])
            itemize.add_item(img[0x0010, 0x0010])
            itemize.add_item(img[0x0010, 0x0040])
            itemize.add_item(img[0x0018, 0x0050])
    with doc.create(MiniPage(width=NoEscape(r"0.5\linewidth"))) as dc:
        dc.append('Información de la Imágen')
        with doc.create(Itemize()) as itemize:
            itemize.add_item(f"Size: {img.pixel_array.shape[0]}x{img.pixel_array.shape[1]}")
            itemize.add_item("max: "+str(img.pixel_array.max())+"\nmin: "+str(img.pixel_array.min()))
            itemize.add_item("mean: "+str(img.pixel_array.mean()))

    doc.generate_pdf("TEST-DOC__"+str(img[0x0010, 0x0010].value),clean=True)
#-------------------------------------------------------

