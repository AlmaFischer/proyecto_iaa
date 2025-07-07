import os
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
import re
import unicodedata

# Configurar rutas de OCR
pytesseract.pytesseract.tesseract_cmd = "tesseract"
# Usar poppler del sistema

def validate_pdf_file(pdf_path):
    """Valida si un archivo es un PDF válido"""
    try:
        if not os.path.exists(pdf_path):
            return False, "Archivo no existe"
        
        if os.path.getsize(pdf_path) == 0:
            return False, "Archivo vacío"
        
        # Verificar cabecera PDF
        with open(pdf_path, 'rb') as f:
            header = f.read(5)
            if not header.startswith(b'%PDF-'):
                return False, "No es un archivo PDF válido"
        
        return True, "PDF válido"
    except Exception as e:
        return False, f"Error validando PDF: {str(e)}"

def ocr_from_pdf(pdf_path):
    """Extrae texto de un PDF usando OCR con manejo robusto de errores"""
    texto = ""
    try:
        # Validar archivo PDF
        is_valid, message = validate_pdf_file(pdf_path)
        if not is_valid:
            raise ValueError(f"Archivo PDF inválido: {message}")
        
        print(f"Procesando PDF: {os.path.basename(pdf_path)}")
        
        # Intentar convertir el PDF a imágenes con parámetros más robustos
        try:
            paginas = convert_from_path(
                pdf_path,
                dpi=200,  # Reducir DPI para archivos problemáticos
                first_page=1,
                last_page=None,
                fmt='jpeg',  # Formato específico
                poppler_path=None,  # Usar poppler del sistema
                timeout=30  # Timeout de 30 segundos
            )
        except Exception as e:
            print(f"Error al convertir PDF con poppler: {e}")
            # Intentar con parámetros más básicos
            try:
                paginas = convert_from_path(pdf_path, dpi=150, fmt='jpeg')
            except Exception as e2:
                raise Exception(f"No se pudo procesar el PDF: {str(e2)}")
        
        if not paginas:
            raise ValueError("No se pudieron extraer páginas del PDF")
        
        print(f"PDF convertido exitosamente. {len(paginas)} página(s) encontrada(s)")
        
        # Procesar cada página
        for i, pagina in enumerate(paginas):
            try:
                print(f"OCR en página {i+1} de {len(paginas)}...")
                texto_pagina = pytesseract.image_to_string(
                    pagina, 
                    config='--oem 3 --psm 6'  # Configuración OCR optimizada
                )
                texto += texto_pagina + "\n"
            except Exception as e:
                print(f"Error en OCR de página {i+1}: {e}")
                continue
                
    except Exception as e:
        error_msg = f"Error procesando {os.path.basename(pdf_path)}: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)
    
    if not texto.strip():
        raise ValueError(f"No se pudo extraer texto del archivo {os.path.basename(pdf_path)}")
    
    return texto

def process_NotasMedia(path):
    """Procesa archivo de notas con manejo de errores mejorado"""
    try:
        texto = ocr_from_pdf(path)
        lineas = texto.split("\n")
        lineas_limpias = [l.strip() for l in lineas if len(l.strip()) > 2]
        
        if not lineas_limpias:
            raise ValueError("No se encontraron líneas de texto válidas en el archivo de notas")
        
        print(f"Archivo de notas procesado: {len(lineas_limpias)} líneas extraídas")
        return lineas_limpias
    except Exception as e:
        raise Exception(f"Error procesando archivo de notas: {str(e)}")

def process_CV(path):
    """Procesa archivo de CV con manejo de errores mejorado"""
    try:
        texto = ocr_from_pdf(path)
        # Limpiar el texto
        texto = texto.replace("\n", " ").replace("\x0c", " ")
        texto = " ".join(texto.split())  # Normalizar espacios
        
        if len(texto.strip()) < 10:
            raise ValueError("El texto extraído del CV es muy corto o está vacío")
        
        print(f"CV procesado exitosamente: {len(texto)} caracteres extraídos")
        return texto
    except Exception as e:
        raise Exception(f"Error procesando archivo de CV: {str(e)}")

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

def split_filename(nombre_archivo):
    """Extrae información del nombre del archivo"""
    try:
        partes = os.path.basename(nombre_archivo).split("_")
        if len(partes) >= 2:
            rut = partes[0]
            id_postulante = partes[1].replace("Post-", "")
            return rut, id_postulante, partes
        else:
            # Si no tiene el formato esperado, usar valores por defecto
            return "unknown", "unknown", [os.path.basename(nombre_archivo)]
    except Exception as e:
        print(f"Warning: No se pudo parsear nombre de archivo {nombre_archivo}: {e}")
        return "unknown", "unknown", [os.path.basename(nombre_archivo)]

def process_two_files_df(path_notas, path_cv):
    """Procesa ambos archivos y retorna un DataFrame con manejo robusto de errores"""
    try:
        print("="*60)
        print(f"INICIANDO PROCESAMIENTO DE ARCHIVOS")
        print(f"Archivo de notas: {path_notas}")
        print(f"  - Existe: {os.path.exists(path_notas)}")
        print(f"  - Ruta absoluta: {os.path.abspath(path_notas)}")
        print(f"Archivo de CV: {path_cv}")
        print(f"  - Existe: {os.path.exists(path_cv)}")
        print(f"  - Ruta absoluta: {os.path.abspath(path_cv)}")
        print("="*60)
        
        # Validar que los archivos existen
        if not os.path.exists(path_notas):
            raise FileNotFoundError(f"Archivo de notas no encontrado: {path_notas}")
        if not os.path.exists(path_cv):
            raise FileNotFoundError(f"Archivo de CV no encontrado: {path_cv}")
        
        # Extraer información del archivo
        rut, id_postulante, _ = split_filename(path_notas)
        
        # Inicializar fila con datos básicos
        fila = {
            "Rut": rut,
            "ID postulante": id_postulante
        }
        
        # Procesar CV primero (suele ser más rápido)
        try:
            print("Procesando archivo de CV...")
            curriculum_texto = process_CV(path_cv)
            fila["Curriculum"] = curriculum_texto
        except Exception as e:
            print(f"Error procesando CV: {e}")
            fila["Curriculum"] = f"Error: {str(e)}"
        
        # Procesar archivo de notas
        try:
            print("Procesando archivo de notas...")
            lineas_notas = process_NotasMedia(path_notas)
            notas_extraidas = obtener_promedios_notas(lineas_notas)
            fila.update(notas_extraidas)
        except Exception as e:
            print(f"Error procesando notas: {e}")
            # Agregar valores por defecto para las notas
            fila.update({
                "Nota Matematicas": None,
                "Nota Lenguaje": None,
                "Nota Ingles": None,
                "Nota Ciencia": None,
                "Nota Historia": None,
                "Nota Artes": None,
                "Nem": None
            })
        
        # Crear DataFrame
        df = pd.DataFrame([fila])
        print("Procesamiento completado exitosamente")
        return df
        
    except Exception as e:
        error_msg = f"Error en process_two_files_df: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)

def guardar_fila_individual(df):
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    output_csv = os.path.join(data_dir, "fila_individual.csv")
    df.to_csv(output_csv, index=False)
    print(f"CSV guardado como '{output_csv}'")
