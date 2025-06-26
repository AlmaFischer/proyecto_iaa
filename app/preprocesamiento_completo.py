import pandas as pd
import re
import unicodedata
from tqdm import tqdm
import os

# Inicializar tqdm y analizador de sentimiento
tqdm.pandas()

# -------------------------------
# CARGA DE DATOS (desde CSV local)
# -------------------------------
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

input_csv = os.path.join(data_dir, "fila_individual.csv")
output_csv = os.path.join(data_dir, "Postulaciones_tabulares.csv")

df = pd.read_csv(input_csv)

# -------------------------------
# FUNCIONES
# -------------------------------

def quitar_tildes(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def get_num_word_text(text):
    try:
        largo = len(text.split())
    except:
        largo = 0
    return largo

def verify_is_liderazgo(text):
    keywords = [
        "liderazgo", "lider", "lidere", "guie", "dirigi", "coordine", "jefe de grupo",
        "jefe", "encargado", "responsable de equipo", "representante", "capitan", "vocero",
        "delegado", "presidente", "vicepresidente", "coordinador", "coordinadora", "monitor",
        "monitora", "organizador", "organizadora", "fui responsable de", "lidere un proyecto",
        "encabece la organizacion de", "coordine un grupo", "asumi el rol de", "fui elegido para"
    ]
    try:
        text_clean = quitar_tildes(text.lower())
        return int(any(k in text_clean for k in keywords))
    except:
        return 0

def verify_is_deporte(text):
    keywords = [
        "deporte", "deportes", "actividad fisica", "vida sana", "disciplina deportiva",
        "entrenamiento", "competencia", "competicion", "rendimiento fisico", "deportivo",
        "futbol", "basquetbol", "basket", "voleibol", "voley", "atletismo", "natacion",
        "tenis", "rugby", "ciclismo", "gimnasia", "karate", "taekwondo", "artes marciales",
        "escalada", "handball", "balonmano", "jugador", "capitan", "entrenador", "seleccionado",
        "equipo", "seleccion", "club", "representante", "medalla", "trofeo", "campeonato",
        "torneo", "inter-escolar", "interescolar", "liga escolar", "preparacion fisica",
        "actividad extracurricular", "participe en", "fui parte del equipo", "obtuve medalla",
        "represente a mi colegio"
    ]
    try:
        text_clean = quitar_tildes(text.lower())
        return int(any(k in text_clean for k in keywords))
    except:
        return 0

def verify_is_talento(text):
    keywords = [
        "talento", "talentoso", "talentosa", "dotado", "dotada", "aptitud", "aptitudes",
        "habilidades destacadas", "capacidades sobresalientes", "potencial", "destreza",
        "habilidad especial", "facilidad para", "destacado en", "precoz", "premio", "premiado",
        "reconocimiento", "galardonado", "beca por merito", "beca de talento", "finalista",
        "ganador", "ganadora", "excelencia academica", "mejor promedio", "mejor alumno",
        "alto rendimiento", "distincion"
    ]
    try:
        text_clean = quitar_tildes(text.lower())
        return int(any(k in text_clean for k in keywords))
    except:
        return 0

def delete_unnecesary_rows(df):
    mask = (df["num_word_cv"] == 0) & (df["Nem"].isna())
    return df[~mask]

# -------------------------------
# APLICAR FUNCIONES
# -------------------------------

df["num_word_cv"] = df["Curriculum"].progress_apply(get_num_word_text)
df["liderazgo_cv"] = df["Curriculum"].progress_apply(verify_is_liderazgo)
df["deporte_cv"] = df["Curriculum"].progress_apply(verify_is_deporte)
df["talento_cv"] = df["Curriculum"].progress_apply(verify_is_talento)

df = delete_unnecesary_rows(df)

# -------------------------------
# TRANSFORMACIONES
# -------------------------------

# Generar variables adicionales
df["Nota Humanista"] = ((df["Nota Lenguaje"] + df["Nota Historia"]) / 2).round(1)
df["Nota Cientifico"] = ((df["Nota Matematicas"] + df["Nota Ciencia"]) / 2).round(1)

# Eliminar columnas redundantes
df.drop(columns=["Nota Matematicas", "Nota Lenguaje", "Nota Ciencia", "Nota Historia"], inplace=True)

# Reordenar columnas
nuevo_orden = [
    "Nota Cientifico", "Nota Humanista", "Nota Ingles", "Nota Artes", "Nem",
    "liderazgo_cv", "deporte_cv", "talento_cv"
]

df = df[nuevo_orden]

# Guardar resultado final
df.to_csv(output_csv, index=False)
print(f"Preprocesamiento finalizado. Archivo guardado como '{output_csv}'")
