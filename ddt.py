#open text file
text_file = open("data.tex", "w")
word = "\\documentclass[]{book}\n\\usepackage[spanish]{babel}\n\\title{\\bf A LA GRANDE LE PUSE CUCA}\n\\author{PIERANGELI}\n\\date{\\today}\n\\begin{document}\n\\frontmatter\n\\maketitle\n\\tableofcontents\n\\mainmatter\n\\chapter{Introduccin}\n\\begin{center}\n\\textit{En esta parte se describe el resumen o sntesisdel captulo.}\n\\end{center}\n\\section{Seccin 1}Algo de texto para la seccin\n\\end{document}"
#write string to file
text_file.write(word)

 
#close file
text_file.close()


     
                    
                      










