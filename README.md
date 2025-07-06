# 🎓 Sistema Inteligente de Recomendación de Carreras

## ✨ Características Principales

### Nueva Interfaz Moderna y Profesional
- **Diseño Dark Mode Elegante**: Interfaz moderna con colores oscuros y acentos vibrantes
- **Top 3 Recomendaciones**: Muestra las tres carreras más compatibles con tu perfil
- **Análisis Personalizado**: Mensaje inteligente que dice "Según tu perfil, estas son las carreras más afines a ti"
- **Carga de Archivos Flexible**: Acepta cualquier tipo de archivo (PDF, Word, imágenes, texto, etc.)
- **Análisis Multi-Modelo**: Utiliza 4 modelos de IA diferentes para mayor precisión

### Funcionalidades Mejoradas
- ✅ **Sin Restricciones de Archivos**: Sube cualquier tipo de documento
- 🎯 **Recomendaciones Inteligentes**: Top 3 carreras con porcentajes de compatibilidad
- 📊 **Análisis Detallado**: Resultados de cada modelo de IA por separado
- 🎨 **Interfaz Responsive**: Se adapta a diferentes tamaños de pantalla
- ⚡ **Procesamiento Asíncrono**: No bloquea la interfaz durante el análisis

## 🚀 Nuevas Características de la Interfaz

### Diseño Profesional
- **Colores Modernos**: Paleta de colores oscuros con acentos en azul y morado
- **Tipografía Elegante**: Fuente Segoe UI en diferentes pesos y tamaños
- **Cards Interactivas**: Tarjetas elegantes para cada recomendación
- **Iconos y Emojis**: Interfaz más visual e intuitiva

### Sistema de Recomendaciones
1. **🥇 Primera Recomendación**: La carrera más compatible (color verde)
2. **🥈 Segunda Recomendación**: Segunda opción más viable (color morado)  
3. **🥉 Tercera Recomendación**: Tercera alternativa recomendada (color rosa)

### Análisis Multi-Modelo
- **XGBoost**: Modelo de gradient boosting
- **Random Forest**: Bosque aleatorio
- **Red Neuronal**: Deep learning
- **SVM**: Support Vector Machine

Cada modelo contribuye al consenso final para determinar las mejores recomendaciones.

## 📱 Cómo Usar la Nueva Aplicación

1. **Ejecutar la Aplicación**:
   ```bash
   python3 app/app_tkinter.py
   ```

2. **Cargar Archivos**:
   - Haz clic en "Seleccionar Archivo" para notas
   - Haz clic en "Seleccionar Archivo" para currículum
   - ✨ **Novedad**: Acepta cualquier formato de archivo

3. **Analizar Perfil**:
   - Haz clic en "🚀 Analizar Perfil y Obtener Recomendaciones"
   - Observa la barra de progreso durante el procesamiento

4. **Ver Resultados**:
   - Revisa las **Top 3 recomendaciones** con porcentajes de compatibilidad
   - Opcionalmente, expande "📊 Ver análisis detallado por modelo"

## 🎨 Capturas de Pantalla

La nueva interfaz incluye:
- Título principal con emoji y descripción atractiva
- Cards de carga de archivos con indicadores visuales
- Botón principal destacado para iniciar el análisis
- Resultados en tarjetas elegantes con:
  - Emojis de medallas (🥇🥈🥉)
  - Barras de progreso coloridas
  - Porcentajes de compatibilidad
  - Diseño tipo tarjeta con sombras

## 🔧 Cambios Técnicos Principales

### Eliminación de Restricciones
```python
# ANTES: Solo archivos específicos
if not (filename.endswith('_NotasMedia.pdf')):
    messagebox.showerror("Error", "El archivo debe terminar en _NotasMedia.pdf")

# AHORA: Cualquier tipo de archivo
filetypes=[
    ("Todos los archivos", "*.*"),
    ("PDF files", "*.pdf"),
    ("Documentos de texto", "*.txt"),
    ("Documentos Word", "*.docx"),
    ("Imágenes", "*.png *.jpg *.jpeg")
]
```

### Sistema de Consenso Multi-Modelo
```python
def calcular_consenso(self, predicciones):
    """Calcula un consenso de las predicciones de todos los modelos"""
    puntuaciones = {}
    for modelo, resultados in predicciones.items():
        for i, (carrera, prob) in enumerate(resultados[:3]):
            peso = (3 - i) * prob  # Mayor peso a primeras posiciones
            puntuaciones[carrera] += peso
```

### Interfaz Responsive y Moderna
- Uso de grid system de tkinter
- Estilos TTK personalizados
- Canvas para elementos gráficos personalizados
- Animaciones y transiciones suaves

## 📋 Requisitos

Los mismos requisitos del proyecto original:
- Python 3.x
- tkinter (incluido con Python)
- PIL/Pillow
- pandas
- joblib
- numpy
- pytesseract
- pdf2image

## 🎯 Beneficios de la Nueva Versión

1. **Experiencia de Usuario Mejorada**: Interfaz más intuitiva y atractiva
2. **Mayor Flexibilidad**: Acepta cualquier tipo de archivo
3. **Resultados Más Completos**: Top 3 recomendaciones en lugar de solo una
4. **Mayor Confianza**: Análisis de múltiples modelos de IA
5. **Información Más Rica**: Porcentajes de compatibilidad y análisis detallado
6. **Diseño Profesional**: Apariencia moderna y elegante

---

**¡Disfruta explorando tus opciones de carrera con el nuevo sistema inteligente! 🎓✨**