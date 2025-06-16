import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import os
import Proyecto4  # Importa las funciones de procesamiento
import threading
import subprocess
import pandas as pd
import joblib

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Carga de Archivos: Notas y Currículum")
        self.geometry("900x800")
        self.configure(bg="#f4f8fb")  # Fondo más claro
        self.resizable(True, True)
        self.notas_path = tk.StringVar()
        self.cv_path = tk.StringVar()
        self.loading_label = None
        self.frame = None
        self.btn_salir = None
        self.text_resultado = None

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 13, 'bold'), padding=10, background='#4a90e2', foreground='white', borderwidth=0)
        style.map('TButton', background=[('active', '#357abd')])
        style.configure('TLabel', font=('Segoe UI', 12), background='#f4f8fb', foreground='#222e3a')
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground='#357abd', background='#f4f8fb')
        style.configure('Path.TLabel', font=('Segoe UI', 10), foreground='#4a90e2', background='#f4f8fb')
        style.configure('TFrame', background='#f4f8fb')

        self.frame = ttk.Frame(self, padding=30, style='TFrame')
        self.frame.pack(expand=True, fill='both')

        # Configurar grid responsivo
        for i in range(2):
            self.frame.columnconfigure(i, weight=1)
        for i in range(10):
            self.frame.rowconfigure(i, weight=1)

        # Logo opcional (puedes reemplazarlo por tu propio logo.png)
        logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
        if os.path.exists(logo_path):
            img = Image.open(logo_path).resize((70, 70))
            self.logo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(self.frame, image=self.logo, bg='#f4f8fb')
            logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='nsew')
        else:
            ttk.Label(self.frame, text="Bienvenido", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='nsew')

        ttk.Label(self.frame, text="Archivo de Notas:").grid(row=1, column=0, sticky='w', pady=(10, 5))
        ttk.Button(self.frame, text="Seleccionar Notas", command=self.cargar_notas).grid(row=1, column=1, padx=10, sticky='ew')
        ttk.Label(self.frame, textvariable=self.notas_path, style='Path.TLabel').grid(row=2, column=0, columnspan=2, sticky='w')

        ttk.Label(self.frame, text="Archivo de Currículum:").grid(row=3, column=0, sticky='w', pady=(20, 5))
        ttk.Button(self.frame, text="Seleccionar Currículum", command=self.cargar_cv).grid(row=3, column=1, padx=10, sticky='ew')
        ttk.Label(self.frame, textvariable=self.cv_path, style='Path.TLabel').grid(row=4, column=0, columnspan=2, sticky='w')

        ttk.Separator(self.frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky='ew', pady=20)
        self.btn_procesar = ttk.Button(self.frame, text="Procesar y Guardar", command=self.iniciar_flujo_completo, state='disabled')
        self.btn_procesar.grid(row=6, column=0, columnspan=2, pady=5, sticky='ew')
        self.btn_salir = ttk.Button(self.frame, text="Salir", command=self.destroy)
        self.btn_salir.grid(row=7, column=0, columnspan=2, pady=5, sticky='ew')
        self.text_resultado = tk.Text(
            self.frame,
            height=8,
            state='disabled',
            bg='#eaf4fb',  # Azul muy claro
            fg='#205080',  # Azul oscuro
            font=('Segoe UI', 16, 'bold'),
            bd=0,
            highlightthickness=0,
            wrap='word',
            padx=20,
            pady=20
        )
        self.text_resultado.grid(row=8, column=0, columnspan=2, pady=15, sticky='nsew')

    def cargar_notas(self):
        path = filedialog.askopenfilename(title="Selecciona el archivo de notas", filetypes=[("PDF files", "*.pdf")])
        if path:
            filename = os.path.basename(path)
            if not (filename.endswith('_NotasMedia.pdf')):
                messagebox.showerror("Error", "El archivo de notas debe terminar en _NotasMedia.pdf y ser PDF.")
                return
            self.notas_path.set(path)
            self.validar_coincidencia()

    def cargar_cv(self):
        path = filedialog.askopenfilename(title="Selecciona el archivo de currículum", filetypes=[("PDF files", "*.pdf")])
        if path:
            filename = os.path.basename(path)
            if not (filename.endswith('_CV.pdf')):
                messagebox.showerror("Error", "El archivo de currículum debe terminar en _CV.pdf y ser PDF.")
                return
            self.cv_path.set(path)
            self.validar_coincidencia()

    def extraer_post_num(self, filename):
        import re
        m = re.search(r'post-([0-9]+)', filename, re.IGNORECASE)
        if m:
            print(f"[DEBUG] POST extraído de {filename}: {m.group(1)}")
        else:
            print(f"[DEBUG] No se encontró post- en {filename}")
        return m.group(1) if m else None

    def validar_coincidencia(self):
        notas = self.notas_path.get()
        cv = self.cv_path.get()
        if notas and cv:
            num_notas = self.extraer_post_num(os.path.basename(notas))
            num_cv = self.extraer_post_num(os.path.basename(cv))
            if num_notas != num_cv:
                messagebox.showerror("Error", "El número después de POST- debe coincidir en ambos archivos.")
                self.notas_path.set("")
                self.cv_path.set("")
                self.btn_procesar.config(state='disabled')
            else:
                self.btn_procesar.config(state='normal')
        else:
            self.btn_procesar.config(state='disabled')

    def iniciar_flujo_completo(self):
        self.btn_procesar.config(state='disabled')
        self.btn_salir.config(state='disabled')
        if not self.loading_label:
            self.loading_label = ttk.Label(self.frame, text="Procesando, por favor espere...", style='Title.TLabel')
            self.loading_label.grid(row=9, column=0, columnspan=2, pady=10)
        self.text_resultado.config(state='normal')
        self.text_resultado.delete(1.0, tk.END)
        self.text_resultado.config(state='disabled')
        self.update_idletasks()
        hilo = threading.Thread(target=self.flujo_completo)
        hilo.start()

    def flujo_completo(self):
        notas_path = self.notas_path.get()
        cv_path = self.cv_path.get()
        try:
            # 1. Proyecto4.py procesamiento
            df = Proyecto4.process_two_files_df(notas_path, cv_path)
            Proyecto4.guardar_fila_individual(df)
            # 2. Ejecutar preprocesamiento_completo.py
            subprocess.run(["python3", "app/preprocesamiento_completo.py"], check=True)
            # 3. Ejecutar y mostrar predicciones directamente
            resultado = self.obtener_predicciones()
            self.after(0, lambda: self.mostrar_resultado(resultado))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error en procesamiento", str(e)))
        finally:
            self.after(0, self.finalizar_proceso)

    def obtener_predicciones(self):
        CLASES = [
            'Administración de Servicios', 'Bachillerato de Derecho', 'Bachillerato de Ingeniería Civil',
            'Bachillerato de Ingeniería Comercial', 'Bachillerato de Medicina', 'Bachillerato de Psicología',
            'Comunicación Audiovisual', 'Derecho', 'Enfermería', 'Ingeniería Civil', 'Ingeniería Comercial',
            'International Business', 'Kinesiología', 'Medicina', 'Nutrición', 'Obstetricia y Puericultura',
            'Odontología', 'Periodismo', 'Psicología', 'Publicidad', 'Terapia Ocupacional'
        ]
        data_dir = "data"
        input_csv = os.path.join(data_dir, "Postulaciones_tabulares.csv")
        models_dir = 'models'
        model_file = 'model_xgboost.joblib'
        resultado = ''
        try:
            df = pd.read_csv(input_csv)
            df = df.fillna(df.mean(numeric_only=True))
            model_path = os.path.join(models_dir, model_file)
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                try:
                    y_pred = model.predict(df)
                    clases_predichas = [CLASES[i] if 0 <= i < len(CLASES) else f'Clase desconocida ({i})' for i in y_pred]
                    resultado = clases_predichas[0] if clases_predichas else 'Sin predicción'
                except Exception:
                    resultado = 'Error al predecir.'
            else:
                resultado = 'Modelo XGBoost no encontrado.'
        except Exception as e:
            resultado = f"Error al cargar datos o modelo: {e}"
        return resultado

    def mostrar_resultado(self, resultado):
        self.text_resultado.config(state='normal')
        self.text_resultado.delete(1.0, tk.END)
        # Insertar el texto centrado
        texto = f"Carrera recomendada\n{resultado}"
        self.text_resultado.insert(tk.END, texto)
        self.text_resultado.tag_configure('center', justify='center')
        self.text_resultado.tag_add('center', '1.0', 'end')
        self.text_resultado.config(state='disabled')

    def finalizar_proceso(self):
        if self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None
        self.btn_procesar.config(state='normal')
        self.btn_salir.config(state='normal')

if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        import subprocess
        subprocess.check_call(['pip', 'install', 'pillow'])
        from PIL import Image, ImageTk
    app = App()
    app.mainloop()
