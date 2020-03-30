from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog

class FilePicker:
    """Grupo de texto, cuadro y boton examinar archivo"""
    sv_path = None

    def browse(self):
        filename = filedialog.askopenfilename(initialdir = "/", title = self.description_text, filetypes = self.filetypes)
        if len(filename) > 0:
            self.sv_path.set(filename)

    def __init__(self, window, row, label_text, description_text, default_path, filetypes):
        self.description_text = description_text
        self.default_path = default_path
        self.filetypes = filetypes

        self.sv_path = StringVar()
        self.sv_path.set("")

        lbl = Label(window, text=label_text)
        lbl.grid(column=0, row=row)
        txt = Entry(window,width=40,textvariable=self.sv_path)
        txt.grid(column=1, row=row)
        btn = Button(window, text="Examinar", command=self.browse)
        btn.grid(column=2, row=row)

    def getpath(self):
        return self.sv_path.get()



window = Tk()

window.title("DBA Types Editor")
window.geometry('500x200')


typesxml = (("XML files","*.xml"),("All files","*.*"))
typescsv = (("CSV files","*.csv"),("Text files","*.txt"),("All files","*.*"))
MainXMLPicker = FilePicker(window, row=0, label_text="XML con el tipo a editar", description_text="Seleccione el XML exportado de DBA", default_path="/", filetypes=typesxml)
TemplatesXMLPicker = FilePicker(window, row=1, label_text="XML de Templates", description_text="Seleccione el XML con los templates", default_path="/", filetypes=typesxml)
CSVPicker = FilePicker(window, row=2, label_text="Datos a cargar (CSV)", description_text="Seleccione el CSV con los datos a cargar", default_path="/", filetypes=typescsv)

window.mainloop()