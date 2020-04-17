#!/usr/bin/python3
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import sys
import csv
from datetime import datetime
import logging
import re

######## SUPER TO-DO: Romper esta funcion espagueti en pedacitos
def addsignals(xmltypes_tree, xmltemplates_tree, csvdata):
    ## Proceso el XML con los tipicos
    xmltypes_root = xmltypes_tree.getroot()
    logging.info("Fecha de creación del XML: "+ xmltypes_root.attrib['Date'])

    # Obtengo los nombres de cada elemento del documento
    #childs = list(map(lambda x: x.attrib['Na'], root))
    if len(xmltypes_root) > 1:
        raise NotImplementedError('Se encontró más de un tipo en el archivo xml. Exporte solo uno.')
    
    mytypical = xmltypes_root[0]
    logging.info("Editando el típico: " + mytypical.attrib['Na'])

    ## Procesamiento templates XML
    xmltemplates_root = xmltemplates_tree.getroot()

    # Armo un diccionario con el tempate para cada tipo
    try:
        templates = {x.attrib['type']: {
        'placeholds': x.attrib['placeholds'].split(' '),
        'tree': x
        } for x in xmltemplates_root.find("signals")
        }
    except KeyError as e:
        raise KeyError("XML de templates malformado") from e
    
    # Armo un diccionario con las expresiones regulares
    rules_placeholds = {x.attrib['name']: {
    'regex': re.compile(x.text.strip()),
    'description': x.attrib['description'] if 'description' in x.attrib else ''
    } for x in xmltemplates_root.find("rules")}

    ## Procesamiento de los datos del CSV, linea por linea
    for i, reg in enumerate(csvdata):
        # Busco el tipo que dice el CSV dentro del xml con templates
        tipo = reg['type']

        if len(tipo)<1:
            print(f"Se omite tipo vacío en linea {i} del CSV.")
            continue
        
        if len(tipo)<1:
            print(f"Se omite tipo vacío en linea {i} del CSV.")
            continue
        
        # Chequeo que el tipico exista
        if not tipo in templates:
            raise ValueError(f"No se encuentra el tipo '{tipo}' en el template xml. Linea {i} del CSV.")
        

        # Obtengo los placeholds correspondientes a este tipo
        template = templates[tipo]
        placeholds = template['placeholds']

        template_str = ET.tostring(template['tree'], encoding='unicode')
        
        ## Reemplazo de placeholds
        # Es importante realizar los remplazos comenzando con los placeholds
        # más largos y seguir por los más cortos
        for phold in sorted(placeholds, key=len, reverse=True):
            try:
                new_text = reg[phold].strip()
            except ValueError as e:
                raise ValueError(f"Linea {i} del CSV: No se encuentra el campo '{phold}' para reemplazar en el template {tipo}.") from e

            if len(new_text)==0:
                logging.warning(f"Linea {i} del CSV: El campo '{phold}' se encuentra vacío pero es requerido por el template {tipo}.")

            if phold in rules_placeholds:
                regex = rules_placeholds[phold]['regex']
                regex_description = rules_placeholds[phold]['description']
                # Realizo la busqueda
                if not regex.search(new_text):
                    raise KeyError(f"Linea {i} del CSV: El placehold {phold}='{new_text}' no cumple la regla establecida: '{regex_description}'.")

            template_str = template_str.replace(phold, new_text)
        
        new_elem = ET.fromstring(template_str)
        
        ######### REFACTORIZAR: Utilizar el atributo unique del xml
        # Reviso que no haya colisiones de nombres
        tagsNew,msgNew = findNames(new_elem)
        tagsMain, msgMain = findNames(mytypical)

        duplicated_tags = tagsMain.intersection(tagsNew)
        duplicated_msg = msgMain.intersection(msgNew)

        if len(duplicated_tags) > 0 or len(duplicated_msg)>0:
            if len(duplicated_tags) > 0:
                logging.warning(f"Linea {i} del CSV. Se omiten TAGs existentes: "+", ".join(list(duplicated_tags)) )
            if len(duplicated_msg)>0:
                logging.warning(f"Linea {i} del CSV. Se omiten MSGs existentes: "+", ".join(list(duplicated_msg)) )
            continue

        # Agrego cada uno de los tags dentro del documento principal (ojo! los hijos nomas)
        for child in new_elem:
            mytypical.append(child)
    
    # Actualizo fecha de modificación
    now = datetime.now()
    xmltypes_root.attrib['Date'] = now.strftime("%m/%d/%Y %I:%M:%S %p")
    return xmltypes_tree

def findNames(xml):
    tags=set([])
    messages=set([])
    for elem in xml:
        try:
            name = elem.attrib['Na']
            if elem.tag in ['T', 'ST']:
                tags.add(name)
            elif elem.tag in ['M']:
                messages.add(name)
        except ValueError:
            pass 
    
    return tags, messages


def parseCSV(csvdata_path):
    delimiters = {',',';','\t'}
    
    for d in delimiters:
        input_file = csv.DictReader(open(csvdata_path), delimiter=d)
        if len(input_file.fieldnames) > 1 and "type" in input_file.fieldnames:
            # Delimitador encontrado
            if len(input_file.fieldnames) == len(set(input_file.fieldnames)):
                return input_file
            else:
                raise RuntimeError('Columnas repetidas en CSV')

    raise RuntimeError('CSV malformado')

def processFiles(xmltypes_path, xmltemplates_path, csvdata_path, outfile_path):
    """Abre los archivos, agrega las señales y escribe el archivo de salida"""

    parserxml = ET.XMLParser(strip_cdata=False) # Para que no elimine los CDATA

    # Abro archivos
    try:
        xmltypes_tree = ET.parse(f := xmltypes_path.strip('"'), parserxml)
    except OSError as e:
        raise OSError(f"No se encuentra el archivo principal XML: '{f}'") from e

    try:
        xmltemplates_tree = ET.parse(f := xmltemplates_path.strip('"'), parserxml)
    except OSError as e:
        raise OSError(f"No se encuentra el archivo de templates XML: '{f}'") from e

    try:
        csvdata = parseCSV(f := csvdata_path.strip('"'))
    except OSError as e:
        raise OSError(f"No se encuentra el archivo CSV: '{f}'") from e

    # Proceso
    addsignals(xmltypes_tree=xmltypes_tree, xmltemplates_tree=xmltemplates_tree, csvdata=csvdata)

    # Guardo
    xmltypes_tree.write(outfile_path)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    prog_help = \
    """Utilice este programa para añadir cómodamente señales a un tipo en DBA.
    
    Ingredientes:
    1. Un archivo XML que tenga el Type a modificar (Tools > Export Type(s))
    2. Un archivo que diga cómo agregar las señales de cada tipo (use templates.xml)
    3. Un archivo CSV con las señales a agregar
    """

    print(prog_help)

    xmltypes_path = input('Arrastre el archivo con los tipos a modificar (XML): ')
    xmltemplates_path = input('Arrastre archivo de templates o presione ENTER para usar por defecto templates.xml: ')
    csvdata_path = input('Arrastre el archivo CSV con las señales a agregar: ')
    outfile_path = input('Escriba el nombre del archivo de salida (out.xml): ')
    
    if len(xmltemplates_path) <1:
        xmltemplates_path = "templates.xml"

    if len(outfile_path) <1:
        outfile_path = "out.xml"

    processFiles(xmltypes_path=xmltypes_path, xmltemplates_path=xmltemplates_path, csvdata_path=csvdata_path, outfile_path=outfile_path)
