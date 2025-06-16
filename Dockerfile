FROM python:3.10-slim

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y tesseract-ocr poppler-utils python3-tk python3-pil.imagetk libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia el código del proyecto
COPY . /app

# Crea la carpeta data si no existe
RUN mkdir -p /app/data

# Comando por defecto: ejecuta la app gráfica
CMD ["python3", "app/app_tkinter.py"]