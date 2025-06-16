import os
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
import re
import unicodedata

# Configurar rutas de OCR
pytesseract.pytesseract.tesseract_cmd = "tesseract"
# Usar poppler del sistema

def ocr_from_pdf(pdf_path):
    texto = ""
    paginas = convert_from_path(pdf_path)
    for i, pagina in enumerate(paginas):
        print(f"OCR en página {i+1} de {os.path.basename(pdf_path)}...")
        texto += pytesseract.image_to_string(pagina)
    return texto

def process_NotasMedia(path):
    texto = ocr_from_pdf(path)
    lineas = texto.split("\n")
    lineas_limpias = [l.strip() for l in lineas if len(l.strip()) > 2]
    return lineas_limpias

def obtener_promedios_notas(lineas):
    resultado = {
        "Nota Matematicas": None,
        "Nota Lenguaje": None,
        "Nota Ingles": None,
        "Nota Ciencia": None,
        "Nota Historia": None,
        "Nota Artes": None,
        "Nem": None
    }
    for linea in lineas:
        l = linea.lower()
        try:
            if "mate" in l:
                resultado["Nota Matematicas"] = float(re.findall(r"\d[\d.,]*", linea)[-1].replace(",", "."))
            elif "leng" in l:
                resultado["Nota Lenguaje"] = float(re.findall(r"\d[\d.,]*", linea)[-1].replace(",", "."))
            elif "ingl" in l:
                resultado["Nota Ingles"] = float(re.findall(r"\d[\d.,]*", linea)[-1].replace(",", "."))
            elif "ciencia" in l or "tecno" in l:
                resultado["Nota Ciencia"] = float(re.findall(r"\d[\d.,]*", linea)[-1].replace(",", "."))
            elif "hist" in l or "geogr" in l:
                resultado["Nota Historia"] = float(re.findall(r"\d[\d.,]*", linea)[-1].replace(",", "."))
            elif "arte" in l:
                resultado["Nota Artes"] = float(re.findall(r"\d[\d.,]*", linea)[-1].replace(",", "."))
            elif "promedio" in l or "nem" in l:
                resultado["Nem"] = float(re.findall(r"\d[\d.,]*", linea)[-1].replace(",", "."))
        except:
            continue
    return resultado

def process_CV(path):
    texto = ocr_from_pdf(path)
    texto = texto.replace("\n", " ").replace("\x0c", " ")
    return texto

def split_filename(nombre_archivo):
    partes = os.path.basename(nombre_archivo).split("_")
    rut = partes[0]
    id_postulante = partes[1].replace("Post-", "")
    return rut, id_postulante, partes

def process_two_files_df(path_notas, path_cv):
    rut, id_postulante, _ = split_filename(path_notas)
    fila = {
        "Rut": rut,
        "ID postulante": id_postulante,
        "Curriculum": process_CV(path_cv)
    }
    lineas_notas = process_NotasMedia(path_notas)
    fila.update(obtener_promedios_notas(lineas_notas))
    df = pd.DataFrame([fila])
    return df

def guardar_fila_individual(df):
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    output_csv = os.path.join(data_dir, "fila_individual.csv")
    df.to_csv(output_csv, index=False)
    print(f"CSV guardado como '{output_csv}'")
