"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""


from py4web import action, request, abort, redirect, URL, HTTP
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

#librerias de visualización
import pandas as pd
import plotly.graph_objects as go

#funcion agricola / produccion
#import os
#import pandas as pd
#import plotly.graph_objects as go
#import ipywidgets as widgets
from IPython.display import display, HTML
import markdown
from py4web import action

#librerias adicionales funcion agricola / produccion
import os
#from urllib.parse import unquote // necesario si hay que limpiar la url de simbolos
#import requests Para parsear URLs
#from io import StringIO Igual parsear URLs
from pathlib import Path
import matplotlib.pyplot as plt
import ipywidgets as widgets






url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth)
def index():
    print("User:", get_user_email())
    return dict()

@action('numeros')
@action.uses('numeros.html', db, auth)
def index():
    print("User:", get_user_email())
    return dict()


@action("cal")
@action.uses("cal.html", auth, T)
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(message=message, actions=actions)

@action("registrocal", method=["GET", "POST"])
@action.uses("registrocal.html", db, session, T)
def create_form():
    form = Form(db.calendario, formstyle=FormStyleBulma)
    rows = db(db.calendario).select()
    return dict(form=form, rows=rows)


@action('tablabovcord_a')
@action.uses('tabla-bov-cord-2004-2009.html')
def tablabovcord_a():
    # Load the data from CSV file or database
    df = pd.read_csv('https://comal.redhumus.org/s/KKRjNjDRqszCqax/download/bov-cord-2004-2009.csv')

    # Render the table as HTML
    html_table = df.to_html()

    return dict(html_table=html_table)

    
@action('grafbovcord_a')
@action.uses('graf-bov-cord-2004-2009.html')
def grafbovcord_a():
    # Load the data from CSV file or database
    df = pd.read_csv('https://comal.redhumus.org/s/KKRjNjDRqszCqax/download/bov-cord-2004-2009.csv')

    # Group the DataFrame by 'Año' and 'Orientación' and sum the 'NoAnimales' column (divided by 1 million)
    grouped_df = df.groupby(['Año', 'Orientación'])['NoAnimales'].sum() / 1000000

    # Get unique years and orientations for the x-axis
    years = df['Año'].unique()
    orientations = df['Orientación'].unique()

    # Define custom colors for each orientation
    color_palette = {
        'Carne': 'rgb(31, 119, 180)',
        'Doble Utilidad': 'rgb(255, 127, 14)',
        'Leche': 'rgb(44, 160, 44)'
    }

    # Create a bar chart with grouped bars and custom colors
    data = []
    for orientation in orientations:
        y_values = [grouped_df.loc[(year, orientation)] if (year, orientation) in grouped_df.index else 0 for year in years]
        color = color_palette.get(orientation, 'rgb(0, 0, 0)')  # Use custom color if available, else default to black
        data.append(go.Bar(name=orientation, x=years, y=y_values, marker=dict(color=color)))

    # Set the layout of the chart
    layout = go.Layout(title='Inventario bovino en Córdoba 2004-2009 por año', 
                   title_x=0.5, #centrar el titulo
                   xaxis=dict(title='Año'),
                   yaxis=dict(title='Número de bovinos (vacas) (en millones)'))

    # Create the figure
    fig = go.Figure(data=data, layout=layout)

    # Display the chart
    #fig.show()
    
    # Get the HTML code for embedding the chart
    chart_html = fig.to_html(full_html=False)

    return dict(chart_html=chart_html)


#### Agricola Sinu
###################################
@action('agricola')
@action.uses('agricola_sinu.html')
def agricola():

#### inicio codigo
# V.3.0.1


    # Directorio que contiene los archivos CSV
    #directory = "https://comal.redhumus.org/apps/files/?dir=/Documents/Agua-contando-historias/Datos-UPRA"

    directory = os.path.join(os.path.dirname(__file__), 'uploads/DatosUPRA')
    #if not os.path.isdir(directory):
    #os.mkdir(directory)


    # Obtener la lista de archivos CSV en el directorio
    csv_files = [file for file in os.listdir(directory) if file.endswith(".csv")]

    # Verificar si hay archivos CSV en el directorio
    if len(csv_files) == 0:
        response.flash("No se encontraron archivos CSV en el directorio especificado.")
        exit()

    # Cargar los datos de los archivos CSV en un DataFrame
    dfs = []

    for file in csv_files:
        file_path = os.path.join(directory, file)
        try:
            df = pd.read_csv(file_path)
            # Agregar la columna "Producto" con el nombre del archivo sin extensión
            df["Producto"] = os.path.splitext(file)[0]
            dfs.append(df)
        except pd.errors.EmptyDataError:
            response.flash(f"El archivo {file} está vacío y no se puede cargar.")

    # Verificar si se cargaron datos en el DataFrame
    if len(dfs) == 0:
        response.flash("No se pudo cargar ningún archivo CSV con datos.")
        exit()

    # Concatenar los DataFrames en uno solo
    data = pd.concat(dfs)

    # Mostrar los campos disponibles
    fields = data.columns
    #print("Campos disponibles:")
    #print(fields)

    # Obtener la lista de productos
    product_list = data["Producto"].unique()

    # Obtener la lista de municipios
    municipio_list = data["Municipio"].unique()

    # Crear las listas desplegables para seleccionar las variables y el tipo de gráfico
    variable_dropdown = [{'value': variable, 'label': variable} for variable in ["Area Sembrada", "Area Cosechada", "Produccion (ton)", "Rendimiento (ha/ton)"]]
    product_dropdown = [{'value': producto, 'label': producto} for producto in product_list]
    municipio_dropdown = [{'value': municipio, 'label': municipio} for municipio in municipio_list]
    index_dropdown = [{'value': field, 'label': field} for field in fields]
    x_axis_dropdown = [{'value': field, 'label': field} for field in fields]
    y_axis_dropdown = [{'value': field, 'label': field} for field in fields]
    chart_type_dropdown = [{'value': chart_type, 'label': chart_type} for chart_type in ["bar", "line", "scatter"]]



    # Función para generar y mostrar la tabla y el gráfico seleccionados
    def generate_output(change):
        global pivot_table
        variable = variable_dropdown.value
        chart_type = chart_type_dropdown.value
        products_selected = product_dropdown.value
        municipios_selected = municipio_dropdown.value
        index_field = index_dropdown.value
        x_field = x_axis_dropdown.value
        y_field = y_axis_dropdown.value
    
        # Filtrar el DataFrame por los productos seleccionados
        filtered_data = data[data["Producto"].isin(products_selected)]
    
        # Crear la tabla de pivote
        pivot_table = pd.pivot_table(filtered_data, values=variable, index=index_field, columns=["Producto", "Municipio"])
    
        global table_data
        
        # Limpiar las salidas HTML
        #table_output.clear_output()
        #chart_output.clear_output()
    

        # Crear una cadena HTML para la tabla
        table_data = pivot_table.to_html()

        # Pasar la cadena HTML a la plantilla
        
        return dict(
            table_data=XML(table_data)  # Usar XML para evitar el escape HTML
        )



               
        # Generar y mostrar el gráfico
        global chart_output
        with chart_output:
            try:
                fig = go.Figure()
            
                if chart_type == "bar":
                    for product in products_selected:
                        for municipio in municipios_selected:
                            if product in pivot_table.columns.get_level_values("Producto") and municipio in pivot_table.columns.get_level_values("Municipio"):
                                fig.add_trace(go.Bar(
                                    x=pivot_table.index,
                                    y=pivot_table[(product, municipio)],
                                    name=f"{product} ({municipio})"
                                ))
                else:
                    for product in products_selected:
                        for municipio in municipios_selected:
                            if product in pivot_table.columns.get_level_values("Producto") and municipio in pivot_table.columns.get_level_values("Municipio"):
                                fig.add_trace(go.Scatter(
                                    x=pivot_table[x_field][(product, municipio)],
                                    y=pivot_table[y_field][(product, municipio)],
                                    mode="lines+markers",
                                    name=f"{product} ({municipio})"
                                ))

                fig.update_layout(
                     title=f"Gráfico de {chart_type} de {variable} por {x_field} y {y_field}",
                     xaxis=dict(title=x_field),
                     yaxis=dict(title=y_field)
                )

                fig.show()
            except ValueError as e:
                print(f"No se pudo generar la gráfica. Error: {str(e)}")

        chart_output = "<h2>Gráfico</h2>" + fig.to_html()
        return dict(chart_output=chart_output)

    
            
    # Función para manejar las solicitudes del lado del cliente en lugar de observe en los dropdowns
    #@action("obtener_datos", method="GET")
    def obtener_datos():
        variable = request.params["variable"]
        chart_type = request.params["chart_type"]
        producto = request.params["producto"]
        municipio = request.params["municipio"]
        index = request.params["index"]
        x_axis = request.params["x_axis"]
        y_axis = request.params["y_axis"]    

    # Lógica para obtener los datos actualizados según las variables seleccionadas
    # Puedes utilizar la función existente generate_output o implementar una lógica similar aquí
    # Devuelve los datos en formato JSON
        datos = {"variable": variable, "producto": producto, "otra_data": "lo_que_sea"}
        return response.json(datos)



    #@action("exportar_tabla", method="GET")
    #def exportar_tabla():
    # Lógica para exportar la tabla a Markdown y devolver un enlace de descarga
    #    return dict()


    # Función para exportar la tabla como archivo Markdown
    #def export_table_to_markdown(button):
    #    if pivot_table is None:
    #        print("No se ha generado ninguna tabla todavía.")
    #        return

        # Convertir la tabla a Markdown y guardarla en un archivo
    #    table = pivot_table.to_markdown()
    #    with open("tabla.md", "w") as f:
    #        f.write(table)
    
    #    print("La tabla se ha exportado exitosamente como archivo Markdown.")



    # Botón para exportar la tabla
    #export_button = widgets.Button(description="Exportar tabla")
    #export_button.on_click(export_table_to_markdown)    




    #### final codigo

    # Crear las salidas HTML para la tabla y el gráfico
    #table_output = "<h2>Tabla</h2>" + pivot_table.to_markdown()
    #chart_output = "<h2>Gráfico</h2>" + fig.to_html()
   
    return dict(
        variable_dropdown=variable_dropdown, 
        product_dropdown=product_dropdown, 
        municipio_dropdown=municipio_dropdown, 
        index_dropdown=index_dropdown, 
        x_axis_dropdown=x_axis_dropdown, 
        y_axis_dropdown=y_axis_dropdown, 
        chart_type_dropdown=chart_type_dropdown,
    )
    
    


#########
#####################

### Linea de tiempo 
#########################################
import pandas as pd
import plotly.express as px

@action('lineat')
@action.uses('lineat.html')
def lineat():

    # Cargar el archivo CSV en un DataFrame de Pandas
    df = pd.read_csv('https://comal.redhumus.org/s/n62jLgbHa5AjrZb/download/linea_sinu.csv')

    # Asegurarse de que las columnas de fecha sean de tipo datetime
    df['Datetime1'] = pd.to_datetime(df['Datetime1'])
    df['Datetime2'] = pd.to_datetime(df['Datetime2'])
    # format='%Y-%m-%d'

    # Crear la figura de la línea de tiempo
    fig = px.timeline(df, x_start='Datetime1', x_end='Datetime2', y='Hecho', color='Categoría')
    #fig = px.timeline(df, x_start='Datetime1', x_end='Datetime2', y='Hecho', color='Categoría',hover_data={'Descripción': True})
    
    

    # Personalizar la apariencia de la línea de tiempo
    fig.update_layout(title='Línea de tiempo',
                    autosize=True,  # Ajustar automáticamente el tamaño de la figura
                    #width=800,
                    #height=600,
                    margin=dict(l=10, r=50, t=50, b=50),  # Ajustar los márgenes para evitar recortes
                    xaxis=dict(title='Fecha'), yaxis=dict(title='Hecho', showticklabels=True))
                    #xaxis=dict(title='Fecha'), yaxis=dict(title='Hecho', fixedrange=True))

    # Rango de tiempo

    fig.update_xaxes(range=['2021-01-01', '2023-12-31'])

    # Mostrar la línea de tiempo interactiva
    #fig.show()

    # Get the HTML code for embedding the chart
    lineat_html = fig.to_html(full_html=False)

    return dict(lineat_html=lineat_html)


####
##################################################################3


######## Función bovinos hoy

##### Tabla bovinos 2023



@action('tablabovcord_c')
@action.uses('tabla-bov-cord-2004-2009.html')
def tablabovcord_c():
    # Load the data from CSV file or database
    df = pd.read_csv('https://comal.redhumus.org/s/MsSa2qnKTr9RikW/download/ICA-CENSOS-BOVINOS-2023-Final_limpio.csv')

    # Render the table as HTML
    html_table = df.to_html()

    return dict(html_table=html_table)




@action('tablabovcord_b')
@action.uses('layout.html', 'tabla-bov-nal-2023.html')
def tablabovcord_b():
    # Load the data from CSV file or database
    df = pd.read_csv('https://comal.redhumus.org/s/MsSa2qnKTr9RikW/download/ICA-CENSOS-BOVINOS-2023-Final_limpio.csv')
    
    # Obtener la lista de departamentos y municipios únicos
    departamentos = sorted(df['DEPARTAMENTO'].unique())
    municipios = sorted(df['MUNICIPIO'].unique())

    if request.method == 'POST':
        # Obtener el formato seleccionado para descargar la tabla
        format = request.params.get('format')

        # Obtener el HTML de la tabla
        html_table = request.params.get('html_table')

        # Descargar la tabla en el formato seleccionado
        if format == 'markdown':
            response.headers['Content-Type'] = 'text/markdown'
            response.headers['Content-Disposition'] = 'attachment; filename="tabla.md"'
            return html_table
        elif format == 'html':
            response.headers['Content-Type'] = 'text/html'
            response.headers['Content-Disposition'] = 'attachment; filename="tabla.html"'
            return html_table

    # Obtener los valores seleccionados en los filtros
    selected_departamentos = request.params.getlist('departamentos')
    selected_municipios = request.params.getlist('municipios')
    
    # Filtrar el DataFrame según los valores seleccionados en los filtros
    filtered_df = df[df['DEPARTAMENTO'].isin(selected_departamentos) & df['MUNICIPIO'].isin(selected_municipios)]
    
    # Renderizar la tabla filtrada como HTML
    html_table = filtered_df.to_html()

    return dict(departamentos=departamentos, municipios=municipios, html_table=html_table)



##### Grafico bovinos 2023



    
@action('grafbovcord_b')
@action.uses('graf-bov-nal-2023.html')
def grafbovcord_a():
    # Load the data from CSV file or database
    df = pd.read_csv('https://comal.redhumus.org/s/YQJHnJ7gPyjbibF/download/ICA-CENSOS-BOVINOS-2023-Final.csv')

    # Group the DataFrame by 'Año' and 'Orientación' and sum the 'NoAnimales' column (divided by 1 million)
    grouped_df = df.groupby(['Año', 'Orientación'])['NoAnimales'].sum() / 1000000

    # Get unique years and orientations for the x-axis
    years = df['Año'].unique()
    orientations = df['Orientación'].unique()

    # Define custom colors for each orientation
    color_palette = {
        'Carne': 'rgb(31, 119, 180)',
        'Doble Utilidad': 'rgb(255, 127, 14)',
        'Leche': 'rgb(44, 160, 44)'
    }

    # Create a bar chart with grouped bars and custom colors
    data = []
    for orientation in orientations:
        y_values = [grouped_df.loc[(year, orientation)] if (year, orientation) in grouped_df.index else 0 for year in years]
        color = color_palette.get(orientation, 'rgb(0, 0, 0)')  # Use custom color if available, else default to black
        data.append(go.Bar(name=orientation, x=years, y=y_values, marker=dict(color=color)))

    # Set the layout of the chart
    layout = go.Layout(title='Inventario bovino en Colombia 2023', 
                   title_x=0.5, #centrar el titulo
                   xaxis=dict(title='Fincas'),
                   yaxis=dict(title='Número de bovinos (vacas) (en millones)'))

    # Create the figure
    fig = go.Figure(data=data, layout=layout)

    # Display the chart
    #fig.show()
    
    # Get the HTML code for embedding the chart
    chart_html = fig.to_html(full_html=False)

    return dict(chart_html=chart_html)
    



########


#Funcion produccion


@action('produccion')
def produccion():
    # Especifica la ruta relativa del directorio que deseas acceder
    directory_path = 'uploads/DatosUPRA'

    # Obtiene la ruta absoluta del archivo actual
    current_file = Path(__file__).resolve()

    # Construye la ruta absoluta al directorio
    absolute_path = current_file.parent / directory_path

    # Lista los archivos CSV en el directorio
    csv_files = [file.name for file in absolute_path.iterdir() if file.is_file() and file.suffix == '.csv']

    if len(csv_files) == 0:
        return "No se encontraron archivos CSV en el directorio especificado."




    # V.3.0.1


    # Cargar los datos de los archivos CSV en un DataFrame
    dfs = []

    for file in csv_files:
        file_path = os.path.join(directory, file)
        try:
            df = pd.read_csv(file_path)
            # Agregar la columna "Producto" con el nombre del archivo sin extensión
            df["Producto"] = os.path.splitext(file)[0]
            dfs.append(df)
        except pd.errors.EmptyDataError:
            print(f"El archivo {file} está vacío y no se puede cargar.")

    # Verificar si se cargaron datos en el DataFrame
    if len(dfs) == 0:
        print("No se pudo cargar ningún archivo CSV con datos.")
        exit()

    # Concatenar los DataFrames en uno solo
    data = pd.concat(dfs)

    # Mostrar los campos disponibles
    fields = data.columns
    print("Campos disponibles:")
    print(fields)

    # Obtener la lista de productos
    product_list = data["Producto"].unique()

    # Obtener la lista de municipios
    municipio_list = data["Municipio"].unique()

    # Crear las listas desplegables para seleccionar las variables y el tipo de gráfico
    variable_dropdown = widgets.Dropdown(options=["Area Sembrada", "Area Cosechada", "Produccion (ton)", "Rendimiento (ha/ton)"], description="Variable:")
    product_dropdown = widgets.SelectMultiple(options=product_list, description="Productos:")
    municipio_dropdown = widgets.SelectMultiple(options=municipio_list, description="Municipios:")
    index_dropdown = widgets.Dropdown(options=fields, description="Index:")
    x_axis_dropdown = widgets.Dropdown(options=fields, description="Eje X:")
    y_axis_dropdown = widgets.Dropdown(options=fields, description="Eje Y:")
    chart_type_dropdown = widgets.Dropdown(options=["bar", "line", "scatter"], description="Tipo de gráfico:")

    # Crear las salidas HTML para la tabla y el gráfico
    table_output = widgets.Output()
    chart_output = widgets.Output()

    # Función para generar y mostrar la tabla y el gráfico seleccionados
    def generate_output(change):
        global pivot_table
        variable = variable_dropdown.value
        chart_type = chart_type_dropdown.value
        products_selected = product_dropdown.value
        municipios_selected = municipio_dropdown.value
        index_field = index_dropdown.value
        x_field = x_axis_dropdown.value
        y_field = y_axis_dropdown.value
    
        # Filtrar el DataFrame por los productos seleccionados
        filtered_data = data[data["Producto"].isin(products_selected)]
    
        # Crear la tabla de pivote
        pivot_table = pd.pivot_table(filtered_data, values=variable, index=index_field, columns=["Producto", "Municipio"])
    
    
        # Limpiar las salidas HTML
        table_output.clear_output()
        chart_output.clear_output()
    
        # Generar y mostrar la tabla
        with table_output:
            display(HTML("<h2>Tabla</h2>"))
            display(pivot_table)

               
        # Generar y mostrar el gráfico
        with chart_output:
            try:
                fig = go.Figure()
            
                if chart_type == "bar":
                    for product in products_selected:
                        for municipio in municipios_selected:
                            if product in pivot_table.columns.get_level_values("Producto") and municipio in pivot_table.columns.get_level_values("Municipio"):
                                fig.add_trace(go.Bar(
                                    x=pivot_table.index,
                                    y=pivot_table[(product, municipio)],
                                    name=f"{product} ({municipio})"
                                ))
                else:
                    for product in products_selected:
                        for municipio in municipios_selected:
                            if product in pivot_table.columns.get_level_values("Producto") and municipio in pivot_table.columns.get_level_values("Municipio"):
                                fig.add_trace(go.Scatter(
                                    x=pivot_table[x_field][(product, municipio)],
                                    y=pivot_table[y_field][(product, municipio)],
                                    mode="lines+markers",
                                    name=f"{product} ({municipio})"
                                ))

                fig.update_layout(
                    title=f"Gráfico de {chart_type} de {variable} por {x_field} y {y_field}",
                    xaxis=dict(title=x_field),
                    yaxis=dict(title=y_field)
                )

                fig.show()
            except ValueError as e:
                print(f"No se pudo generar la gráfica. Error: {str(e)}")

            
    # Asignar la función de generación de tabla y gráfico al evento "change" de los dropdown menús
    variable_dropdown.observe(generate_output, 'value')
    product_dropdown.observe(generate_output, 'value')
    municipio_dropdown.observe(generate_output, 'value')
    index_dropdown.observe(generate_output, 'value')
    x_axis_dropdown.observe(generate_output, 'value')
    y_axis_dropdown.observe(generate_output, 'value')
    chart_type_dropdown.observe(generate_output, 'value')


    # Función para exportar la tabla como archivo Markdown
    def export_table_to_markdown(button):
        if pivot_table is None:
            print("No se ha generado ninguna tabla todavía.")
            return

        # Convertir la tabla a Markdown y guardarla en un archivo
        table = pivot_table.to_markdown()
        with open("tabla.md", "w") as f:
            f.write(table)
    
        print("La tabla se ha exportado exitosamente como archivo Markdown.")



    # Botón para exportar la tabla
    export_button = widgets.Button(description="Exportar tabla")
    export_button.on_click(export_table_to_markdown)    


    # Mostrar los dropdown menús, el botón y la salida de la tabla
    display(variable_dropdown, product_dropdown, municipio_dropdown, index_dropdown, x_axis_dropdown, y_axis_dropdown, chart_type_dropdown)
    display(export_button)
    display(table_output)
    display(chart_output)


    # Generar la gráfica inicialmente
    #generate_chart(None)

    # Renderizar la plantilla HTML con el formulario y los datos de la gráfica y tabla
    #return dict(form=form, chart_html=chart_html, table_html=table_html)

