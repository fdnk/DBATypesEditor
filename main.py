#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
#from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import addsignals
import logging
import os.path
import sys, traceback

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Console(tk.Text):
    """Consola"""
    # Métodos de Stream
    def write(self, str):
        #txt = " ".join(args) + '\n'
        
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.configure(state='normal')
        self.insert(tk.END, f"{current_time} > {str}")
        self.see(tk.END)
        self.configure(state='disabled')
    
    def flush(self):
        pass

    def __str__(self):
        return self.get("1.0",tk.END)

class FilePicker:
    """Grupo de texto, cuadro y boton examinar archivo"""
    sv_path = None

    def browse(self):        
        filename = filedialog.askopenfilename(initialdir = ".", title = self.description_text, filetypes = self.filetypes)
        if len(filename) > 0:
            self.sv_path.set(os.path.abspath(filename))

    def __init__(self, window, row, label_text, description_text, default_path, filetypes):
        self.description_text = description_text
        self.default_path = default_path
        self.filetypes = filetypes

        self.sv_path = tk.StringVar()
        self.sv_path.set("")

        self.lbl = ttk.Label(window, text=label_text)
        self.lbl.grid(column=0, row=row)
        self.txt = ttk.Entry(window,width=60,textvariable=self.sv_path)
        self.txt.grid(column=1, row=row)
        self.btn = ttk.Button(window, text="Examinar", command=self.browse)
        self.btn.grid(column=2, row=row, sticky=tk.W+tk.E)

    def getpath(self):
        return self.sv_path.get()
    
    def setpath(self, txt):
        self.sv_path.set(txt)

    def updateState(self,active):
        newstate = 'enabled' if active else 'disabled'
        self.txt.config(state=newstate)
        self.btn.config(state=newstate)

class FileChooser(FilePicker):
    def browse(self):
        filename = filedialog.asksaveasfilename(initialdir = ".", title = self.description_text, filetypes = self.filetypes)
        if len(filename) > 0:
            self.sv_path.set(os.path.abspath(filename))

class Checkbox(ttk.Checkbutton):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = tk.BooleanVar(self)
        self.configure(variable=self.variable)
    
    def checked(self):
        return self.variable.get()
    
    def check(self):
        self.variable.set(True)
    
    def uncheck(self):
        self.variable.set(False)


class Application(ttk.Frame):
    
    def __init__(self, main_window):
        super().__init__(main_window)
        main_window.title("DBA Types Editor")
        main_window.geometry('680x300')
        main_window.iconbitmap(resource_path('lctech.ico'))
        

        typesxml = (("XML files","*.xml"),("All files","*.*"))
        typescsv = (("CSV files","*.csv"),("Text files","*.txt"),("All files","*.*"))

        self.mainXMLPicker = FilePicker(self, row=0, label_text="XML con el tipo a editar", description_text="Seleccione el XML exportado de DBA", default_path="/", filetypes=typesxml)
        self.templatesXMLPicker = FilePicker(self, row=1, label_text="XML de Templates", description_text="Seleccione el XML con los templates", default_path="/", filetypes=typesxml)
        self.csvPicker = FilePicker(self, row=2, label_text="Datos a cargar (CSV)", description_text="Seleccione el CSV con los datos a cargar", default_path="/", filetypes=typescsv)
        self.outFile = FileChooser(self, row=4, label_text="Archivo de salida", description_text="Guardar como", default_path="/", filetypes=typesxml)

        self.ck_overwrite = Checkbox(self, text="Sobreescribir", command=self.check_clicked)
        self.ck_overwrite.grid(column=1,row=5, sticky=tk.W)
        
        self.btn = ttk.Button(self, text="Ejecutar", command=self.run)
        self.btn.grid(column=2, row=6)

        self.console = Console(self, height=3, width=80)
        self.console.configure(state='disabled')
        self.console.grid(column=0,row=7,
            columnspan=3,rowspan=3,sticky=tk.W+tk.E+tk.N+tk.S,  ipady=30)

        self.place(width=680, height=300)
    
    def check_clicked(self):
        active = not self.ck_overwrite.checked()
        self.outFile.updateState(active=active)

    def run(self):
        mainXML = self.mainXMLPicker.getpath()
        templateXML = self.templatesXMLPicker.getpath()
        csv = self.csvPicker.getpath()

        outXML = mainXML if self.ck_overwrite.checked() else self.outFile.getpath()

        try:
            addsignals.processFiles(xmltypes_path=mainXML, xmltemplates_path=templateXML, csvdata_path=csv, outfile_path=outXML)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            logging.error(str(e))
        
        logging.info("Terminado exitosamente")


if __name__ == '__main__':
    main_window = tk.Tk()
    app = Application(main_window)
    logging.basicConfig(stream=app.console, level=logging.INFO, format='%(levelname)s :: %(message)s')

    default_template = resource_path('templates.xml')

    if os.path.exists(default_template):
        app.templatesXMLPicker.setpath(os.path.abspath(default_template))

    app.mainloop()
