Agregar señales a un DBA Type

1. En el DBA Type Editor, seleccionar el tipo en cuestion (solo uno), e ir a Tools > Export Type(s).
Llamarlo por ejemplo, type_orig.xml

2. Crear un archivo CSV, delimitado por ",", ";" o tabulación (en excel por ejemplo)
donde se listen las señales a agregar. La primera linea debe ser un header como el siguiente:

type;REPLACE_NAME;REPLACE_VAL

La columna type, obligatoria, debe tener el tipo de señal (*)
Las otras columnas, deben llamarse REPLACE_ seguido por algo más

3. Utilice el archivo templates.xml proporcionado.
Explicación: En el archivo templates.xml se encuentan pedazos de XML
correspondientes a los siguientes tipos de señales: DP (variable DWORD), SP (variable BIT)
y ME_FL (variable FLOAT). 
Dentro de cada bloque <signal> se pueden encontrar todos los tags XML que se copiarán al
archivo type_orig.xml, donde se reemplazarán todos los textos REPLACE_ algo definidos
en el archivo CSV (*).

Si el día de mañana es necesario agregar otro tipo de datos, solo pegue un nuevo bloque <signal>
en templates.xml con los reemplazos correspondientes.

4. Ejecute el programa, el cual le pedirá la ubicación de los archivos anteriores.
Puede arrastrar directamente los archivos a la ventana de la aplicación.
(En el caso de templates.xml, presione simplemente enter para usar el proporcionado,
que debe estar junto al ejecutable).

5. Se obtiene un archivo type_modificado.xml, el cual debe ser cargado en DBA Type Editor
utilizando Tools > Import Type(s). Seleccione Overwrite.


Codigo fuente:
El programa está hecho en Python 3. Para crear el exe utilice pyinstall:
pip install pyinstall
pyinstall addsignals.py

Se podrá encontrar el ejecutable dentro de la carpeta dist