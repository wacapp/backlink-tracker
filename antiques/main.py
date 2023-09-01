import streamlit as st
import pandas as pd
import openpyxl
import re
import pickle
import os
from urllib.parse import urlparse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import nltk
import base64
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils import Utils

nltk.download('stopwords')

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CREDENTIALS_FILE = 'client_secret.json'
URI_REDIRECCIONAMIENTO = ['http://localhost:55876/']


# Función para guardar las credenciales en un archivo pickle
def guardar_credenciales(credenciales):
    with open('credenciales.pickle', 'wb') as f:
        pickle.dump(credenciales, f)

# Función para cargar las credenciales desde un archivo pickle
def cargar_credenciales():
    try:
        with open('credenciales.pickle', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

# Función para autenticar o cargar las credenciales
def autenticar():
    credenciales = cargar_credenciales()

    if credenciales:
        return build('webmasters', 'v3', credentials=credenciales)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES, redirect_uri=URI_REDIRECCIONAMIENTO[0])
        credenciales = flow.run_local_server(port=55876)

        guardar_credenciales(credenciales)
        return build('webmasters', 'v3', credentials=credenciales)

# Autenticar a la API de Google Search Console
gsc_service = autenticar()

file_path = 'Pedidos Backlinks.xlsx'

def process_and_organize_data(file_path):
    """
    Process the Excel data:
    - Load sheets with month-year format
    - Ignore the first two rows, use the third row as headers
    - Reorder columns based on provided order
    - Filter out rows where 'URL' column is empty
    - Return processed data in a dictionary format
    """

    # Load all sheets from the Excel file into a dictionary of dataframes
    all_sheets = pd.read_excel(file_path, sheet_name=None, skiprows=2, header=0)

    # Regular expression pattern to match "month year" format
    pattern = r"^(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre) \d{4}$"

    # Filter sheets by the pattern and store in a dictionary
    month_year_sheets = {name: df for name, df in all_sheets.items() if re.match(pattern, name)}

    # Column order based on provided instructions
    columns_order = ['URL', 'fecha', 'medio', 'backlink', 'tipo de paquete']

    # Process each sheet
    for name, df in month_year_sheets.items():
        # If the DataFrame doesn't have the 'URL' column, continue to the next sheet
        if "URL" not in df.columns:
            continue

        # Filter out rows where 'URL' column is empty
        df = df[df['URL'].notna()]
            
        # Select and reorder columns if they exist
        existing_columns = [col for col in columns_order if col in df.columns]
        df = df[existing_columns]
        
        # Update the dictionary with the processed dataframe
        month_year_sheets[name] = df

    print("ya se ejecuto la primera funcion")
    return month_year_sheets

result = process_and_organize_data(file_path)

def get_domain(url):
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain

# Función para filtrar un DataFrame por un dominio específico
def filtrar_por_dominio(df, dominio):
    return df[df['domain'] == dominio]

def get_backlinks_data_gsc(gsc_service, domain, url, start_date):
    def date_range(start_date):
        current_date = start_date
        today = datetime.today()
        while current_date <= today:
            yield current_date, current_date + relativedelta(months=1) - relativedelta(days=1)
            current_date += relativedelta(months=1)

    data = []

    # Esta parte genera un rango de fechas por mes
    for interval_start, interval_end in date_range(start_date):
        start_date_str = interval_start.strftime("%Y-%m-%d")
        end_date_str = interval_end.strftime("%Y-%m-%d")

        # Preparar la solicitud
        request = {
            'startDate': start_date_str,
            'endDate': end_date_str,
            'dimensions': ['page'],  # Quitamos la dimensión 'date'
            'rowLimit': 3000,
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'contains',
                    'expression': url
                }]
            }],
        }

        # Ejecutar la solicitud
        response = gsc_service.searchanalytics().query(siteUrl=domain, body=request).execute()

        # Convertir la respuesta a un DataFrame de pandas
        for row in response.get('rows', []):
            query = row['keys'][0]  # Ahora solo hay una clave: 'page'
            clicks = row['clicks']
            impressions = row['impressions']
            ctr = row['ctr']
            position = row['position']
            data.append([start_date_str, query, clicks, impressions, ctr, position])  # Usamos start_date_str como la fecha

    df = pd.DataFrame(data, columns=['Date', 'Query', 'Clicks', 'Impressions', 'CTR', 'Position'])

    return df


def obtener_urls_por_dominio(file_path, dominio_a_consultar):
    """
    Obtiene todas las URLs de un archivo Excel que pertenecen a un dominio específico.

    Parámetros:
    - file_path: Ruta al archivo Excel.
    - dominio_a_consultar: Dominio específico a consultar.

    Retorna:
    - Una lista de URLs que pertenecen al dominio especificado.
    """

    # Procesar y organizar los datos del archivo
    month_year_sheets = process_and_organize_data(file_path)

    # Lista para almacenar las URLs encontradas
    urls_del_dominio = []

    # Recorrer cada hoja en el archivo
    for _, df in month_year_sheets.items():
        # Si el DataFrame no tiene la columna 'URL', continuar con la siguiente hoja
        if 'URL' not in df.columns:
            continue

        # Filtrar las URLs por el dominio especificado
        df['domain'] = df['URL'].apply(get_domain)
        urls_filtradas = df[df['domain'] == dominio_a_consultar]['URL'].tolist()

        # Agregar las URLs filtradas a la lista
        urls_del_dominio.extend(urls_filtradas)

    return urls_del_dominio

# Pide al usuario ingresar el dominio a consultar
dominio_a_consultar = input("Por favor, ingrese el dominio a consultar (ejemplo: https://ejemplo.com/): ")
urls = obtener_urls_por_dominio('Pedidos Backlinks.xlsx', dominio_a_consultar)
url =  urls

def fetch_gsc_data_for_sheets(gsc_service, month_year_sheets):
    # Contenedor para almacenar todos los DataFrames de resultados
    all_results = {}

    # Mapeo de meses en español a su número correspondiente
    months_map = {
        'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04',
        'Mayo': '05', 'Junio': '06', 'Julio': '07', 'Agosto': '08',
        'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'
    }
    
    for sheet_name, df in month_year_sheets.items():
        # If the DataFrame doesn't have the 'URL' column, continue to the next sheet
        if 'URL' not in df.columns:
            continue
        # Extraer el mes y el año del nombre de la hoja
        month, year = sheet_name.split()

        # Construir la fecha de inicio (último día del mes especificado en la hoja)
        start_date = (datetime.strptime(f"{year}-{months_map[month]}-01", "%Y-%m-%d") + relativedelta(months=1)) - relativedelta(days=1)
        
        # Asignar el dominio a cada URL
        df['domain'] = df['URL'].apply(get_domain)

        # Filtrar las URLs por el dominio especificado
        df = filtrar_por_dominio(df, dominio_a_consultar)

        # Si el DataFrame filtrado está vacío, continuar con la siguiente hoja
        if df.empty:
            continue

        # Contenedor para esta hoja
        sheet_results = []

        # Agrupar URLs por dominio
        grouped = df.groupby('domain')

        for domain, group in grouped:
            unique_urls = group['URL'].drop_duplicates()
            for url in unique_urls:
                try:
                    result = get_backlinks_data_gsc(gsc_service, domain, url, start_date)
                    sheet_results.append(result)
                except Exception as e:
                    # Imprimir el error y continuar con la siguiente URL
                    print(f"Error al obtener datos para {url}: {e}")

        # Actualizar el contenedor `all_results` con los datos de esta hoja
        all_results[sheet_name] = pd.concat(sheet_results, ignore_index=True)

    return all_results

# Obtener los datos de GSC para las hojas procesadas
gsc_results = fetch_gsc_data_for_sheets(gsc_service, result)

# Imprimir los resultados (esto es solo para verificar, puedes adaptarlo como necesites)
def guardar_resultados_en_excel(resultados, dominio):
    # Obtener el nombre del dominio (sin "https://", "www.", etc.) para usarlo como nombre de archivo
    nombre_dominio = urlparse(dominio).netloc.replace("www.", "")
    nombre_archivo = f"{nombre_dominio}.xlsx"

    # Crear un ExcelWriter para guardar los resultados
    with pd.ExcelWriter(nombre_archivo) as writer:
        for sheet_name, df in resultados.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Resultados guardados en {nombre_archivo}")

# Llamar a la función para guardar los resultados en un archivo Excel
guardar_resultados_en_excel(gsc_results, dominio_a_consultar)

