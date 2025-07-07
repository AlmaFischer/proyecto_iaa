
##  Instalación y Configuración

El sistema deberia instalar todo automaticamente al usar docker compose, puede tardar dependiendo del sistema y de la conexion a internet

2. **Ejecutar con Docker Compose:**
```bash
docker-compose up --build
```

##  Cómo Usar el Sistema

### 1. Preparar los Documentos

El sistema necesita 2 archivos PDF:

- **Archivo de Notas Académicas**: Certificado o concentración de notas que contenga:
  - Notas de Matemáticas, Lenguaje, Ciencias, Historia, Inglés, Artes
  - NEM (Notas de Enseñanza Media)

- **Currículum Vitae**: Documento con información sobre:
  - Experiencias de liderazgo
  - Actividades deportivas
  - Talentos especiales
  - Información académica adicional

### 2. Ejecutar la Aplicación

1. **Abrir la aplicación**:
   - Docker: `docker-compose up`

2. **Cargar documentos**:
   - Hacer clic en "Seleccionar Archivo de Notas"
   - Hacer clic en "Seleccionar Archivo de CV"

3. **Iniciar análisis**:
   - Hacer clic en "INICIAR ANÁLISIS DE PERFIL"
   - Esperar a que el procesamiento termine (puede tomar 1-3 minutos)

4. **Ver resultados**:
   - El sistema mostrará las top 3 recomendaciones
   - Análisis detallado por cada modelo de IA
   - Información extraída de los documentos

### 3. Archivos de Prueba

En la carpeta `files/` encontrarás archivos de ejemplo para probar el sistema:




