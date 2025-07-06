import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import Proyecto4  # Importa las funciones de procesamiento
import threading
import subprocess
import pandas as pd
import joblib
import numpy as np

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Inteligente de Recomendación de Carreras")
        self.geometry("1200x800")  # Tamaño inicial más manejable
        self.configure(bg="#ffffff")  # Fondo blanco
        self.resizable(True, True)
        self.notas_path = tk.StringVar()
        self.cv_path = tk.StringVar()
        self.loading_label = None
        self.main_frame = None
        self.result_frame = None
        self.datos_extraidos = None  # Para almacenar lo que detectó el sistema
        
        # Configurar estilos modernos
        self.setup_styles()
        
        # Crear interfaz principal con scroll
        self.create_scrollable_interface()

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Estilos para botones principales
        style.configure('Primary.TButton', 
                       font=('Arial', 14, 'bold'), 
                       padding=(25, 18),
                       background='#dc2626',  # Rojo principal
                       foreground='white',
                       borderwidth=0,
                       relief='flat')
        style.map('Primary.TButton', 
                 background=[('active', '#b91c1c'), ('pressed', '#991b1b')])
        
        # Estilos para botones secundarios
        style.configure('Secondary.TButton', 
                       font=('Arial', 12), 
                       padding=(18, 12),
                       background='#ef4444',  # Rojo claro
                       foreground='white',
                       borderwidth=0,
                       relief='flat')
        style.map('Secondary.TButton', 
                 background=[('active', '#dc2626'), ('pressed', '#b91c1c')])
        
        # Estilos para labels
        style.configure('Title.TLabel', 
                       font=('Arial', 28, 'bold'), 
                       foreground='#dc2626', 
                       background='#ffffff')
        style.configure('Subtitle.TLabel', 
                       font=('Arial', 16), 
                       foreground='#7f1d1d', 
                       background='#ffffff')
        style.configure('Normal.TLabel', 
                       font=('Arial', 13), 
                       foreground='#1f2937', 
                       background='#ffffff')
        style.configure('Path.TLabel', 
                       font=('Arial', 11), 
                       foreground='#dc2626', 
                       background='#ffffff')
        
        # Estilos para frames
        style.configure('Main.TFrame', background='#ffffff')
        style.configure('Card.TFrame', 
                       background='#fef2f2',  # Rosa muy claro
                       relief='solid', 
                       borderwidth=2)
        style.configure('Result.TFrame',
                       background='#fff5f5',  # Rosa aún más claro
                       relief='solid',
                       borderwidth=1)

    def create_scrollable_interface(self):
        """Crea la interfaz principal con capacidad de scroll"""
        # Crear canvas principal y scrollbar
        self.canvas = tk.Canvas(self, bg="#ffffff", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Frame scrollable que contendrá todo el contenido
        self.scrollable_frame = ttk.Frame(self.canvas, style='Main.TFrame')
        
        # Configurar el scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Crear window en el canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Configurar el redimensionamiento del canvas window
        def configure_canvas_window(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.canvas.bind('<Configure>', configure_canvas_window)
        
        # Bind del mouse wheel para scroll
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Empaquetar canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Usar scrollable_frame como main_frame
        self.main_frame = self.scrollable_frame
        
        # Crear el contenido principal
        self.create_main_content()

    def create_main_content(self):
        """Crea el contenido principal de la aplicación"""
        # Configurar padding del frame principal
        self.main_frame.configure(padding=30)
        
        # Configurar grid responsivo
        self.main_frame.columnconfigure(0, weight=1)
        
        # Título principal con mejor espaciado
        title_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        title_frame.grid(row=0, column=0, pady=(0, 20), sticky='ew')
        title_frame.columnconfigure(0, weight=1)
        
        ttk.Label(title_frame, text="SISTEMA INTELIGENTE DE RECOMENDACION", 
                 style='Title.TLabel').grid(row=0, column=0)
        ttk.Label(title_frame, text="DE CARRERAS UNIVERSITARIAS", 
                 style='Title.TLabel').grid(row=1, column=0, pady=(5, 0))
        ttk.Label(title_frame, text="Descubre las carreras perfectas para tu perfil académico", 
                 style='Subtitle.TLabel').grid(row=2, column=0, pady=(10, 0))
        
        # Card para carga de archivos con mejor diseño
        upload_card = ttk.Frame(self.main_frame, style='Card.TFrame', padding=25)
        upload_card.grid(row=1, column=0, pady=15, sticky='ew', padx=40)
        upload_card.columnconfigure(1, weight=1)
        
        # Header del card
        ttk.Label(upload_card, text="CARGAR DOCUMENTOS", 
                 font=('Arial', 16, 'bold'),
                 foreground='#dc2626',
                 background='#fef2f2').grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Archivo de notas
        ttk.Label(upload_card, text="1. Archivo de Notas Académicas:", 
                 style='Normal.TLabel').grid(row=1, column=0, sticky='w', pady=(0, 8))
        ttk.Button(upload_card, text="Seleccionar Archivo de Notas", 
                  command=self.cargar_notas, 
                  style='Secondary.TButton').grid(row=1, column=1, padx=(20, 0), sticky='ew')
        ttk.Label(upload_card, textvariable=self.notas_path, 
                 style='Path.TLabel').grid(row=2, column=0, columnspan=2, sticky='w', pady=(5, 15))
        
        # Archivo de CV
        ttk.Label(upload_card, text="2. Archivo de Currículum Vitae:", 
                 style='Normal.TLabel').grid(row=3, column=0, sticky='w', pady=(0, 8))
        ttk.Button(upload_card, text="Seleccionar Archivo de CV", 
                  command=self.cargar_cv, 
                  style='Secondary.TButton').grid(row=3, column=1, padx=(20, 0), sticky='ew')
        ttk.Label(upload_card, textvariable=self.cv_path, 
                 style='Path.TLabel').grid(row=4, column=0, columnspan=2, sticky='w', pady=(5, 0))
        
        # Separador visual
        separator = tk.Frame(self.main_frame, height=2, bg='#dc2626')
        separator.grid(row=2, column=0, sticky='ew', pady=20, padx=100)
        
        # Botón principal de procesamiento más grande
        self.btn_procesar = ttk.Button(self.main_frame, 
                                      text="INICIAR ANÁLISIS DE PERFIL", 
                                      command=self.iniciar_flujo_completo, 
                                      style='Primary.TButton',
                                      state='disabled')
        self.btn_procesar.grid(row=3, column=0, pady=20, sticky='ew', padx=80)
        
        # Frame para resultados (inicialmente oculto)
        self.create_results_frame()
        
        # Botón de salir
        ttk.Button(self.main_frame, text="SALIR DEL SISTEMA", 
                  command=self.destroy, 
                  style='Secondary.TButton').grid(row=14, column=0, pady=(30, 0), sticky='ew', padx=150)

    def create_results_frame(self):
        """Crea el frame para mostrar los resultados de las recomendaciones"""
        self.result_frame = ttk.Frame(self.main_frame, style='Result.TFrame', padding=25)
        # Inicialmente oculto, se mostrará después del procesamiento
        
    def cargar_notas(self):
        """Permite cargar cualquier tipo de archivo para notas"""
        path = filedialog.askopenfilename(
            title="Selecciona el archivo de notas",
            filetypes=[
                ("Todos los archivos", "*.*"),
                ("PDF files", "*.pdf"),
                ("Documentos de texto", "*.txt"),
                ("Documentos Word", "*.docx"),
                ("Imágenes", "*.png *.jpg *.jpeg")
            ]
        )
        if path:
            self.notas_path.set(f"[OK] {os.path.basename(path)}")
            self.verificar_archivos()

    def cargar_cv(self):
        """Permite cargar cualquier tipo de archivo para CV"""
        path = filedialog.askopenfilename(
            title="Selecciona el archivo de currículum",
            filetypes=[
                ("Todos los archivos", "*.*"),
                ("PDF files", "*.pdf"),
                ("Documentos de texto", "*.txt"),
                ("Documentos Word", "*.docx"),
                ("Imágenes", "*.png *.jpg *.jpeg")
            ]
        )
        if path:
            self.cv_path.set(f"[OK] {os.path.basename(path)}")
            self.verificar_archivos()

    def verificar_archivos(self):
        """Habilita el botón de procesar si ambos archivos están cargados"""
        if self.notas_path.get() and self.cv_path.get():
            self.btn_procesar.config(state='normal')

    def iniciar_flujo_completo(self):
        """Inicia el procesamiento y análisis de archivos"""
        self.btn_procesar.config(state='disabled')
        self.mostrar_loading()
        
        # Ejecutar en hilo separado para no bloquear la UI
        hilo = threading.Thread(target=self.flujo_completo)
        hilo.start()

    def mostrar_loading(self):
        """Muestra indicador de carga elegante"""
        if not self.loading_label:
            loading_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
            loading_frame.grid(row=3, column=0, pady=20, sticky='ew')
            loading_frame.columnconfigure(0, weight=1)
            
            self.loading_label = ttk.Label(loading_frame, 
                                          text="PROCESANDO - Analizando tu perfil académico...", 
                                          font=('Arial', 16, 'bold'),
                                          foreground='#dc2626',
                                          background='#ffffff')
            self.loading_label.grid(row=0, column=0)
            
            # Barra de progreso indeterminada
            self.progress_bar = ttk.Progressbar(loading_frame, mode='indeterminate', length=400)
            self.progress_bar.grid(row=1, column=0, pady=10)
            self.progress_bar.start()

    def flujo_completo(self):
        """Procesa los archivos y obtiene las predicciones"""
        try:
            # Obtener rutas reales de archivos (eliminar el marcador)
            notas_path = self.notas_path.get().replace("[OK] ", "")
            cv_path = self.cv_path.get().replace("[OK] ", "")
            
            # Buscar archivos en directorio actual si no son rutas absolutas
            if not os.path.isabs(notas_path):
                notas_path = self.buscar_archivo_similar(notas_path, "notas")
            if not os.path.isabs(cv_path):
                cv_path = self.buscar_archivo_similar(cv_path, "cv")
            
            # 1. Procesamiento con Proyecto4.py y capturar datos
            df = Proyecto4.process_two_files_df(notas_path, cv_path)
            
            # Guardar los datos extraídos para mostrarlos después
            self.datos_extraidos = {
                'notas': {
                    'Nota Matematicas': df.iloc[0].get('Nota Matematicas', 'No detectado'),
                    'Nota Lenguaje': df.iloc[0].get('Nota Lenguaje', 'No detectado'),
                    'Nota Ingles': df.iloc[0].get('Nota Ingles', 'No detectado'),
                    'Nota Ciencia': df.iloc[0].get('Nota Ciencia', 'No detectado'),
                    'Nota Historia': df.iloc[0].get('Nota Historia', 'No detectado'),
                    'Nota Artes': df.iloc[0].get('Nota Artes', 'No detectado'),
                    'Nem': df.iloc[0].get('Nem', 'No detectado')
                },
                'cv_texto': df.iloc[0].get('Curriculum', 'No se pudo extraer texto'),
                'archivo_notas': os.path.basename(notas_path),
                'archivo_cv': os.path.basename(cv_path)
            }
            
            Proyecto4.guardar_fila_individual(df)
            
            # 2. Ejecutar preprocesamiento y capturar características adicionales
            subprocess.run(["python3", "app/preprocesamiento_completo.py"], check=True)
            
            # Leer el archivo procesado para obtener las características detectadas
            try:
                df_procesado = pd.read_csv("data/Postulaciones_tabulares.csv")
                if not df_procesado.empty:
                    fila = df_procesado.iloc[0]
                    self.datos_extraidos.update({
                        'caracteristicas': {
                            'Nota Cientifico': fila.get('Nota Cientifico', 0),
                            'Nota Humanista': fila.get('Nota Humanista', 0),
                            'Nota Ingles': fila.get('Nota Ingles', 0),
                            'Nota Artes': fila.get('Nota Artes', 0),
                            'Nem': fila.get('Nem', 0),
                            'liderazgo_cv': fila.get('liderazgo_cv', 0),
                            'deporte_cv': fila.get('deporte_cv', 0),
                            'talento_cv': fila.get('talento_cv', 0)
                        }
                    })
            except Exception as e:
                print(f"Error al leer datos procesados: {e}")
            
            # 3. Obtener predicciones de todos los modelos
            predicciones = self.obtener_todas_las_predicciones()
            
            # 4. Mostrar resultados con datos extraídos
            self.after(0, lambda: self.mostrar_resultados_completos(predicciones))
            
        except Exception as e:
            self.after(0, lambda: self.mostrar_error(f"Error en el análisis: {str(e)}"))
        finally:
            self.after(0, self.finalizar_proceso)

    def buscar_archivo_similar(self, filename, tipo):
        """Busca archivos similares en el directorio files/"""
        files_dir = "files"
        if os.path.exists(files_dir):
            for file in os.listdir(files_dir):
                if tipo.lower() in file.lower() or filename.lower() in file.lower():
                    return os.path.join(files_dir, file)
        return filename

    def obtener_todas_las_predicciones(self):
        """Obtiene predicciones de todos los modelos disponibles"""
        CLASES = [
            'Administración de Servicios', 'Bachillerato de Derecho', 'Bachillerato de Ingeniería Civil',
            'Bachillerato de Ingeniería Comercial', 'Bachillerato de Medicina', 'Bachillerato de Psicología',
            'Comunicación Audiovisual', 'Derecho', 'Enfermería', 'Ingeniería Civil', 'Ingeniería Comercial',
            'International Business', 'Kinesiología', 'Medicina', 'Nutrición', 'Obstetricia y Puericultura',
            'Odontología', 'Periodismo', 'Psicología', 'Publicidad', 'Terapia Ocupacional'
        ]
        
        modelos = {
            'XGBoost': 'model_xgboost.joblib',
            'Random Forest': 'model_random_forest.joblib',
            'Red Neuronal': 'model_red_neuronal.joblib',
            'SVM': 'model_SVM.joblib'
        }
        
        predicciones = {}
        
        try:
            # Cargar datos preprocesados
            data_dir = "data"
            input_csv = os.path.join(data_dir, "Postulaciones_tabulares.csv")
            
            if not os.path.exists(input_csv):
                return {"Error": [("Archivo de datos no encontrado", 0.0)]}
                
            df = pd.read_csv(input_csv)
            if df.empty:
                return {"Error": [("Datos vacíos", 0.0)]}
            
            # Mejor limpieza de datos
            # Primero llenar NaN con 0 para columnas numéricas
            df = df.fillna(0)
            
            # Asegurar que tenemos las columnas esperadas
            columnas_esperadas = ['Nota Cientifico', 'Nota Humanista', 'Nota Ingles', 'Nota Artes', 'Nem', 
                                'liderazgo_cv', 'deporte_cv', 'talento_cv']
            
            # Agregar columna sentiment_cv_POS si no existe (para XGBoost)
            if 'sentiment_cv_POS' not in df.columns:
                df['sentiment_cv_POS'] = 0.5  # Valor neutro por defecto
            
            print(f"Columnas en el DataFrame: {list(df.columns)}")
            print(f"Forma del DataFrame: {df.shape}")
            
            models_dir = 'models'
            
            # Obtener predicciones de cada modelo
            for nombre_modelo, archivo_modelo in modelos.items():
                model_path = os.path.join(models_dir, archivo_modelo)
                if os.path.exists(model_path):
                    try:
                        model = joblib.load(model_path)
                        
                        # Preparar datos según el modelo
                        if nombre_modelo == 'XGBoost':
                            # XGBoost necesita todas las columnas incluyendo sentiment_cv_POS
                            X = df[columnas_esperadas + ['sentiment_cv_POS']]
                        else:
                            # Otros modelos solo necesitan las columnas básicas
                            X = df[columnas_esperadas]
                        
                        # Asegurar que no hay NaN
                        X = X.fillna(0)
                        
                        if hasattr(model, 'predict_proba'):
                            probabilidades = model.predict_proba(X)[0]
                            # Obtener las top 3 clases con mayor probabilidad
                            top_indices = np.argsort(probabilidades)[-3:][::-1]
                            predicciones[nombre_modelo] = [
                                (CLASES[i] if i < len(CLASES) else f'Clase {i}', probabilidades[i]) 
                                for i in top_indices
                            ]
                        else:
                            y_pred = model.predict(X)
                            clase_pred = y_pred[0] if len(y_pred) > 0 else 0
                            if 0 <= clase_pred < len(CLASES):
                                predicciones[nombre_modelo] = [(CLASES[clase_pred], 1.0)]
                            else:
                                predicciones[nombre_modelo] = [(f'Clase {clase_pred}', 1.0)]
                                
                    except Exception as e:
                        print(f"Error con modelo {nombre_modelo}: {e}")
                        predicciones[nombre_modelo] = [("Error en predicción", 0.0)]
                else:
                    predicciones[nombre_modelo] = [("Modelo no encontrado", 0.0)]
                    
        except Exception as e:
            print(f"Error general en predicciones: {e}")
            return {"Error": [("Error al cargar datos", 0.0)]}
            
        return predicciones

    def mostrar_resultados_completos(self, predicciones):
        """Muestra los resultados en una interfaz elegante"""
        # Ocultar loading
        try:
            if hasattr(self, 'progress_bar') and self.progress_bar:
                self.progress_bar.stop()
        except:
            pass
        
        # Crear frame de resultados
        self.result_frame.grid(row=4, column=0, pady=25, sticky='ew', padx=40)
        self.result_frame.columnconfigure(0, weight=1)
        
        # Título de resultados
        ttk.Label(self.result_frame, 
                 text="ANÁLISIS COMPLETO DE TU PERFIL ACADÉMICO", 
                 font=('Arial', 20, 'bold'),
                 foreground='#dc2626',
                 background='#fff5f5').grid(row=0, column=0, pady=(0, 15))
        
        # Mostrar datos extraídos de los documentos
        self.mostrar_datos_extraidos(row=1)
        
        # Mostrar información del análisis
        self.mostrar_info_analisis(row=2)
        
        # Separador
        separator = tk.Frame(self.result_frame, height=2, bg='#dc2626')
        separator.grid(row=3, column=0, sticky='ew', pady=20, padx=50)
        
        # Top 3 general (consenso)
        ttk.Label(self.result_frame, 
                 text="TOP 3 RECOMENDACIONES FINALES (CONSENSO DE TODOS LOS MODELOS)", 
                 font=('Arial', 18, 'bold'),
                 foreground='#dc2626',
                 background='#fff5f5').grid(row=4, column=0, pady=(10, 20))
        
        # Obtener consenso de las top 3 recomendaciones
        top_recomendaciones = self.calcular_consenso(predicciones)
        
        # Verificar si hay recomendaciones válidas
        if not top_recomendaciones or top_recomendaciones[0][0] == "No se pudieron generar recomendaciones":
            ttk.Label(self.result_frame, 
                     text="No se pudieron generar recomendaciones válidas.\nVerifica que los archivos sean correctos y vuelve a intentar.", 
                     font=('Arial', 14),
                     foreground='#dc2626',
                     background='#fff5f5').grid(row=4, column=0, pady=20)
            self.update_scroll_region()
            return
        
        # Mostrar top 3 recomendaciones generales
        for i, (carrera, confianza) in enumerate(top_recomendaciones[:3]):
            self.crear_card_recomendacion(i+1, carrera, confianza, i+5)  # Cambiado de i+4 a i+5
        
        # Separador
        separator2 = tk.Frame(self.result_frame, height=2, bg='#dc2626')
        separator2.grid(row=8, column=0, sticky='ew', pady=30, padx=50)  # Cambiado de row=7 a row=8
        
        # Análisis detallado por modelo
        ttk.Label(self.result_frame, 
                 text="ANÁLISIS DETALLADO POR MODELO DE INTELIGENCIA ARTIFICIAL", 
                 font=('Arial', 18, 'bold'),
                 foreground='#dc2626',
                 background='#fff5f5').grid(row=9, column=0, pady=(10, 20))  # Cambiado de row=8 a row=9, agregado emoji y "A"
        
        # Mostrar top 3 de cada modelo
        self.mostrar_analisis_por_modelo(predicciones, start_row=10)  # Cambiado de start_row=9 a start_row=10
        
        # Actualizar scroll region después de agregar contenido
        self.update_scroll_region()
        
        # Scroll automático hacia los resultados
        self.after(100, lambda: self.canvas.yview_moveto(0.3))

    def mostrar_datos_extraidos(self, row):
        """Muestra los datos extraídos de los documentos del usuario"""
        if not self.datos_extraidos:
            return
        
        # Frame contenedor para los datos extraídos
        datos_frame = tk.Frame(self.result_frame, bg='#f8fafc', relief='solid', bd=1)
        datos_frame.grid(row=row, column=0, sticky='ew', pady=15, padx=20)
        datos_frame.columnconfigure(0, weight=1)
        
        # Título de la sección
        titulo_frame = tk.Frame(datos_frame, bg='#e2e8f0', height=40)
        titulo_frame.grid(row=0, column=0, sticky='ew', padx=2, pady=2)
        titulo_frame.columnconfigure(0, weight=1)
        
        ttk.Label(titulo_frame, 
                 text="DATOS DETECTADOS EN TUS DOCUMENTOS", 
                 font=('Arial', 16, 'bold'),
                 foreground='#1e40af',
                 background='#e2e8f0').grid(row=0, column=0, pady=8)
        
        # Contenido de los datos
        contenido_frame = tk.Frame(datos_frame, bg='#f8fafc')
        contenido_frame.grid(row=1, column=0, sticky='ew', padx=15, pady=15)
        contenido_frame.columnconfigure([0, 1], weight=1)
        
        # Información de archivos
        archivos_frame = tk.LabelFrame(contenido_frame, text="Archivos Analizados", 
                                      font=('Arial', 12, 'bold'), fg='#374151', bg='#f8fafc',
                                      relief='groove', bd=2)
        archivos_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        archivos_frame.columnconfigure(0, weight=1)
        
        tk.Label(archivos_frame, 
                text=f"• Notas: {self.datos_extraidos.get('archivo_notas', 'No especificado')}", 
                font=('Arial', 11), bg='#f8fafc', fg='#374151',
                anchor='w').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        tk.Label(archivos_frame, 
                text=f"• CV: {self.datos_extraidos.get('archivo_cv', 'No especificado')}", 
                font=('Arial', 11), bg='#f8fafc', fg='#374151',
                anchor='w').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        # Notas académicas
        notas_frame = tk.LabelFrame(contenido_frame, text="Notas Académicas Detectadas", 
                                   font=('Arial', 12, 'bold'), fg='#374151', bg='#f8fafc',
                                   relief='groove', bd=2)
        notas_frame.grid(row=1, column=0, sticky='new', padx=(0, 10), pady=5)
        notas_frame.columnconfigure(0, weight=1)
        
        if 'notas' in self.datos_extraidos:
            for i, (materia, nota) in enumerate(self.datos_extraidos['notas'].items()):
                if str(nota) != 'No detectado' and nota != '':
                    # Formatear la nota para mostrarla mejor
                    if isinstance(nota, (int, float)) and nota > 0:
                        nota_str = f"{nota:.1f}" if isinstance(nota, float) else str(nota)
                    else:
                        nota_str = str(nota)
                    
                    tk.Label(notas_frame, 
                            text=f"• {materia.replace('Nota ', '').replace('Nem', 'NEM')}: {nota_str}", 
                            font=('Arial', 10), bg='#f8fafc', fg='#374151',
                            anchor='w').grid(row=i, column=0, sticky='w', padx=10, pady=2)
        
        # Características del CV
        cv_frame = tk.LabelFrame(contenido_frame, text="Características Detectadas en CV", 
                                font=('Arial', 12, 'bold'), fg='#374151', bg='#f8fafc',
                                relief='groove', bd=2)
        cv_frame.grid(row=1, column=1, sticky='new', padx=(10, 0), pady=5)
        cv_frame.columnconfigure(0, weight=1)
        
        if 'caracteristicas' in self.datos_extraidos:
            caracteristicas = self.datos_extraidos['caracteristicas']
            caracteristicas_cv = ['liderazgo_cv', 'deporte_cv', 'talento_cv']
            
            for i, caracteristica in enumerate(caracteristicas_cv):
                valor = caracteristicas.get(caracteristica, 0)
                if valor > 0:
                    nombre = caracteristica.replace('_cv', '').capitalize()
                    tk.Label(cv_frame, 
                            text=f"• {nombre} detectado", 
                            font=('Arial', 10), bg='#f8fafc', fg='#16a34a',
                            anchor='w').grid(row=i, column=0, sticky='w', padx=10, pady=2)
            
            # Si no se detectaron características especiales
            if not any(caracteristicas.get(c, 0) > 0 for c in caracteristicas_cv):
                tk.Label(cv_frame, 
                        text="No se detectaron características\nespeciales en el CV", 
                        font=('Arial', 10), bg='#f8fafc', fg='#6b7280',
                        anchor='w', justify='left').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        # Mostrar muestra del texto extraído del CV
        if 'cv_texto' in self.datos_extraidos:
            cv_texto = self.datos_extraidos['cv_texto']
            if cv_texto and cv_texto != 'No se pudo extraer texto' and len(cv_texto.strip()) > 10:
                texto_frame = tk.LabelFrame(contenido_frame, text="Muestra de Texto Extraído del CV", 
                                           font=('Arial', 12, 'bold'), fg='#374151', bg='#f8fafc',
                                           relief='groove', bd=2)
                texto_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(15, 5))
                texto_frame.columnconfigure(0, weight=1)
                
                # Mostrar solo los primeros 200 caracteres como muestra
                muestra_texto = cv_texto[:200] + "..." if len(cv_texto) > 200 else cv_texto
                texto_label = tk.Label(texto_frame, 
                                      text=muestra_texto, 
                                      font=('Arial', 9), bg='#f8fafc', fg='#4b5563',
                                      anchor='nw', justify='left', wraplength=800)
                texto_label.grid(row=0, column=0, sticky='ew', padx=10, pady=8)
                
                # Información adicional
                tk.Label(texto_frame, 
                        text=f"Total de caracteres extraídos: {len(cv_texto)}", 
                        font=('Arial', 9, 'italic'), bg='#f8fafc', fg='#6b7280',
                        anchor='w').grid(row=1, column=0, sticky='w', padx=10, pady=(0, 8))
        
        # Resumen del perfil académico
        if 'caracteristicas' in self.datos_extraidos:
            caracteristicas = self.datos_extraidos['caracteristicas']
            resumen_frame = tk.LabelFrame(contenido_frame, text="Perfil Académico Calculado", 
                                         font=('Arial', 12, 'bold'), fg='#374151', bg='#f8fafc',
                                         relief='groove', bd=2)
            resumen_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(15, 5))  # Cambio de row=2 a row=4
            resumen_frame.columnconfigure([0, 1], weight=1)
            
            # Áreas académicas
            cientifico = caracteristicas.get('Nota Cientifico', 0)
            humanista = caracteristicas.get('Nota Humanista', 0)
            
            if cientifico > 0 or humanista > 0:
                tk.Label(resumen_frame, 
                        text=f"• Área Científica: {cientifico:.1f}" if cientifico > 0 else "• Área Científica: No evaluada", 
                        font=('Arial', 10), bg='#f8fafc', fg='#374151',
                        anchor='w').grid(row=0, column=0, sticky='w', padx=10, pady=2)
                
                tk.Label(resumen_frame, 
                        text=f"• Área Humanista: {humanista:.1f}" if humanista > 0 else "• Área Humanista: No evaluada", 
                        font=('Arial', 10), bg='#f8fafc', fg='#374151',
                        anchor='w').grid(row=0, column=1, sticky='w', padx=10, pady=2)

    def mostrar_info_analisis(self, row):
        """Muestra información sobre cómo funciona el análisis"""
        info_frame = tk.Frame(self.result_frame, bg='#fef2f2', 
                             relief='solid', bd=1, highlightbackground='#fecaca')
        info_frame.grid(row=row, column=0, pady=15, sticky='ew', padx=20)
        info_frame.columnconfigure(0, weight=1)
        
        ttk.Label(info_frame, 
                 text="CÓMO FUNCIONA NUESTRO SISTEMA DE RECOMENDACIÓN", 
                 font=('Arial', 16, 'bold'),
                 foreground='#dc2626',
                 background='#fef2f2').grid(row=0, column=0, pady=(15, 10))
        
        info_text = """
ANÁLISIS DE TUS DOCUMENTOS:
• Notas académicas: Matemáticas, Lenguaje, Ciencias, Historia, Inglés, Artes, NEM
• Currículum: Detectamos automáticamente liderazgo, deportes y talentos especiales

PROCESAMIENTO INTELIGENTE:
• Creamos variables científicas (Matemáticas + Ciencias) y humanistas (Lenguaje + Historia)
• Analizamos tu perfil integral combinando notas académicas y experiencias personales

4 MODELOS DE INTELIGENCIA ARTIFICIAL:
• XGBoost: Modelo de gradient boosting de alta precisión
• Random Forest: Bosque aleatorio robusto para patrones complejos
• Red Neuronal: Deep learning para detectar relaciones no lineales
• SVM: Support Vector Machine para clasificación optimizada

SISTEMA DE CONSENSO:
• Cada modelo genera sus top 3 recomendaciones con probabilidades
• Combinamos resultados dando más peso a las primeras posiciones
• El resultado final es el consenso de los 4 expertos virtuales
        """
        
        tk.Label(info_frame, 
                text=info_text.strip(),
                font=('Arial', 11),
                fg='#1f2937',
                bg='#fef2f2',
                justify='left',
                anchor='w').grid(row=1, column=0, padx=20, pady=(0, 15), sticky='w')

    def mostrar_analisis_por_modelo(self, predicciones, start_row):
        """Muestra el análisis detallado de cada modelo con top 3"""
        current_row = start_row
        
        # Colores para cada modelo
        colores_modelo = {
            'XGBoost': '#dc2626',
            'Random Forest': '#059669', 
            'Red Neuronal': '#7c3aed',
            'SVM': '#ea580c'
        }
        
        # Descripciones de los modelos
        descripciones = {
            'XGBoost': 'Modelo de gradient boosting extremo. Excelente para patrones complejos y muy preciso.',
            'Random Forest': 'Bosque de árboles de decisión. Robusto y estable, reduce el overfitting.',
            'Red Neuronal': 'Deep learning con múltiples capas. Detecta patrones no lineales complejos.',
            'SVM': 'Support Vector Machine. Optimiza fronteras de decisión para máxima separación.'
        }
        
        for modelo, resultados in predicciones.items():
            if modelo != "Error" and resultados:
                # Frame para cada modelo
                modelo_frame = tk.Frame(self.result_frame, bg='#ffffff', 
                                      relief='solid', bd=2, 
                                      highlightbackground=colores_modelo.get(modelo, '#dc2626'))
                modelo_frame.grid(row=current_row, column=0, pady=12, sticky='ew', padx=30)
                modelo_frame.columnconfigure(1, weight=1)
                
                # Ícono y nombre del modelo
                canvas = tk.Canvas(modelo_frame, width=60, height=60, 
                                 bg='#ffffff', highlightthickness=0)
                canvas.grid(row=0, column=0, rowspan=3, padx=(15, 20), pady=15, sticky='n')
                
                # Círculo con las iniciales del modelo
                iniciales = ''.join([palabra[0] for palabra in modelo.split()])
                canvas.create_oval(5, 5, 55, 55, fill=colores_modelo.get(modelo, '#dc2626'), outline='')
                canvas.create_text(30, 30, text=iniciales, 
                                  font=('Arial', 12, 'bold'), fill='white')
                
                # Nombre y descripción del modelo
                tk.Label(modelo_frame, 
                        text=f"🤖 {modelo}", 
                        font=('Arial', 16, 'bold'),
                        fg=colores_modelo.get(modelo, '#dc2626'),
                        bg='#ffffff',
                        anchor='w').grid(row=0, column=1, sticky='w', pady=(15, 5))
                
                tk.Label(modelo_frame, 
                        text=descripciones.get(modelo, 'Modelo de inteligencia artificial'),
                        font=('Arial', 10),
                        fg='#6b7280',
                        bg='#ffffff',
                        anchor='w').grid(row=1, column=1, sticky='w', pady=(0, 10))
                
                # Top 3 del modelo
                if len(resultados) >= 3:
                    top3_text = ""
                    medalias = ["1º", "2º", "3º"]
                    for i, (carrera, prob) in enumerate(resultados[:3]):
                        if carrera and carrera != "Error en predicción":
                            top3_text += f"{medalias[i]} {carrera} ({prob*100:.1f}%)\n"
                    
                    tk.Label(modelo_frame, 
                            text=f"TOP 3 RECOMENDACIONES:\n{top3_text.strip()}",
                            font=('Arial', 12),
                            fg='#1f2937',
                            bg='#ffffff',
                            anchor='w',
                            justify='left').grid(row=2, column=1, sticky='w', pady=(0, 15))
                else:
                    # Si solo hay una predicción
                    if resultados and resultados[0][0] != "Error en predicción":
                        carrera, prob = resultados[0]
                        tk.Label(modelo_frame, 
                                text=f"RECOMENDACIÓN: {carrera} ({prob*100:.1f}%)",
                                font=('Arial', 12),
                                fg='#1f2937',
                                bg='#ffffff',
                                anchor='w').grid(row=2, column=1, sticky='w', pady=(0, 15))
                
                current_row += 1
        
        # Información adicional sobre el consenso
        consensus_frame = tk.Frame(self.result_frame, bg='#f3f4f6', 
                                 relief='solid', bd=1, highlightbackground='#d1d5db')
        consensus_frame.grid(row=current_row, column=0, pady=20, sticky='ew', padx=30)
        consensus_frame.columnconfigure(0, weight=1)
        
        ttk.Label(consensus_frame, 
                 text="CÁLCULO DEL CONSENSO FINAL", 
                 font=('Arial', 14, 'bold'),
                 foreground='#374151',
                 background='#f3f4f6').grid(row=0, column=0, pady=(15, 10))
        
        consensus_text = """
FÓRMULA DE CONSENSO:
• 1ra posición de cada modelo: peso = 3 × probabilidad
• 2da posición de cada modelo: peso = 2 × probabilidad  
• 3ra posición de cada modelo: peso = 1 × probabilidad

RESULTADO FINAL:
Sumamos todos los pesos por carrera y ordenamos de mayor a menor.
La carrera con mayor puntuación total es tu recomendación #1.
        """
        
        tk.Label(consensus_frame, 
                text=consensus_text.strip(),
                font=('Arial', 11),
                fg='#374151',
                bg='#f3f4f6',
                justify='left').grid(row=1, column=0, padx=20, pady=(0, 15))

    def update_scroll_region(self):
        """Actualiza la región de scroll del canvas"""
        self.main_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def calcular_consenso(self, predicciones):
        """Calcula un consenso de las predicciones de todos los modelos"""
        puntuaciones = {}
        
        for modelo, resultados in predicciones.items():
            if modelo != "Error" and resultados:
                for i, (carrera, prob) in enumerate(resultados[:3]):
                    if carrera and carrera != "Error en predicción" and carrera != "Modelo no encontrado":
                        if carrera not in puntuaciones:
                            puntuaciones[carrera] = 0
                        # Dar más peso a las primeras posiciones
                        peso = (3 - i) * prob
                        puntuaciones[carrera] += peso
        
        # Verificar si hay puntuaciones válidas
        if not puntuaciones:
            return [("No se pudieron generar recomendaciones", 0.0)]
        
        # Ordenar por puntuación y normalizar
        carreras_ordenadas = sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True)
        max_puntuacion = carreras_ordenadas[0][1] if carreras_ordenadas else 1
        
        # Evitar división por cero
        if max_puntuacion == 0:
            return [(carrera, 0.0) for carrera, punt in carreras_ordenadas]
        
        return [(carrera, min(punt/max_puntuacion, 1.0)) for carrera, punt in carreras_ordenadas]

    def crear_card_recomendacion(self, posicion, carrera, confianza, row):
        """Crea una tarjeta elegante para cada recomendación final"""
        # Colores rojos para las posiciones
        colores = ['#dc2626', '#ef4444', '#f87171']  # Rojo oscuro, medio, claro
        texto_posicion = ['1°', '2°', '3°']
        medalias = ['1°', '2°', '3°']
        
        # Frame de la card con borde rojo
        card_frame = tk.Frame(self.result_frame, bg='#ffffff', 
                             relief='solid', bd=3, highlightbackground=colores[posicion-1])
        card_frame.grid(row=row, column=0, pady=8, sticky='ew', padx=40)
        card_frame.columnconfigure(1, weight=1)
        
        # Canvas para el círculo de posición
        canvas = tk.Canvas(card_frame, width=60, height=60, 
                          bg='#ffffff', highlightthickness=0)
        canvas.grid(row=0, column=0, rowspan=2, padx=(12, 15), pady=10, sticky='n')
        
        # Círculo de color con medalla
        canvas.create_oval(5, 5, 55, 55, fill=colores[posicion-1], outline='')
        canvas.create_text(30, 30, text=medalias[posicion-1], 
                          font=('Arial', 16), fill='white')
        
        # Nombre de la carrera
        tk.Label(card_frame, text=f"{texto_posicion[posicion-1]} {carrera}", 
                font=('Arial', 16, 'bold'), 
                fg='#1f2937', 
                bg='#ffffff',
                anchor='w').grid(row=0, column=1, sticky='w', pady=(10, 5))
        
        # Barra y porcentaje de compatibilidad
        compat_frame = tk.Frame(card_frame, bg='#ffffff')
        compat_frame.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(0, 12))
        compat_frame.columnconfigure(0, weight=1)
        
        # Canvas para barra de progreso
        progress_canvas = tk.Canvas(compat_frame, height=20, bg='#ffffff', highlightthickness=0)
        progress_canvas.grid(row=0, column=0, sticky='ew')
        
        def dibujar_barra(event=None):
            width = progress_canvas.winfo_width()
            if width > 1:
                progress_canvas.delete("all")
                # Fondo de la barra
                progress_canvas.create_rectangle(2, 6, width-2, 14, fill='#fee2e2', outline='#fecaca', width=1)
                # Barra de progreso
                progress_width = (width-4) * confianza
                progress_canvas.create_rectangle(2, 6, progress_width+2, 14, 
                                               fill=colores[posicion-1], outline='')
                # Texto del porcentaje
                progress_canvas.create_text(width-30, 10, text=f"{confianza*100:.1f}%", 
                                          font=('Arial', 10, 'bold'), fill=colores[posicion-1])
        
        progress_canvas.bind('<Configure>', dibujar_barra)
        self.after(100, dibujar_barra)

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error elegante"""
        messagebox.showerror("Error", mensaje)

    def finalizar_proceso(self):
        """Limpia el estado de carga y habilita controles"""
        try:
            if hasattr(self, 'loading_label') and self.loading_label:
                self.loading_label.master.destroy()
                self.loading_label = None
        except:
            pass
            
        try:
            if hasattr(self, 'progress_bar') and self.progress_bar:
                self.progress_bar.stop()
                delattr(self, 'progress_bar')
        except:
            pass
            
        self.btn_procesar.config(state='normal')

if __name__ == "__main__":
    app = App()
    app.mainloop()
