import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Carga de Archivos: Notas y Currículum")
        self.geometry("480x320")
        self.configure(bg="#eaf0fb")
        self.resizable(False, False)
        self.notas_path = tk.StringVar()
        self.cv_path = tk.StringVar()

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 12, 'bold'), padding=8, background='#4a90e2', foreground='white')
        style.map('TButton', background=[('active', '#357abd')])
        style.configure('TLabel', font=('Segoe UI', 11), background='#eaf0fb')
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#4a90e2', background='#eaf0fb')
        style.configure('Path.TLabel', font=('Segoe UI', 9), foreground='#357abd', background='#eaf0fb')
        style.configure('TFrame', background='#eaf0fb')

        frame = ttk.Frame(self, padding=25, style='TFrame')
        frame.pack(expand=True, fill='both')

        # Logo opcional (puedes reemplazarlo por tu propio logo.png)
        logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
        if os.path.exists(logo_path):
            img = Image.open(logo_path).resize((60, 60))
            self.logo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(frame, image=self.logo, bg='#eaf0fb')
            logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        else:
            ttk.Label(frame, text="Bienvenido", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 10))

        ttk.Label(frame, text="Archivo de Notas:").grid(row=1, column=0, sticky='w', pady=(10, 5))
        ttk.Button(frame, text="Seleccionar Notas", command=self.cargar_notas).grid(row=1, column=1, padx=10)
        ttk.Label(frame, textvariable=self.notas_path, style='Path.TLabel').grid(row=2, column=0, columnspan=2, sticky='w')

        ttk.Label(frame, text="Archivo de Currículum:").grid(row=3, column=0, sticky='w', pady=(20, 5))
        ttk.Button(frame, text="Seleccionar Currículum", command=self.cargar_cv).grid(row=3, column=1, padx=10)
        ttk.Label(frame, textvariable=self.cv_path, style='Path.TLabel').grid(row=4, column=0, columnspan=2, sticky='w')

        ttk.Separator(frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky='ew', pady=20)
        ttk.Button(frame, text="Salir", command=self.destroy).grid(row=6, column=0, columnspan=2, pady=5)

        # Botón para seleccionar desde Google Drive
        ttk.Button(frame, text="Google Drive", command=self.seleccionar_drive).grid(row=7, column=0, columnspan=2, pady=5)

    def cargar_notas(self):
        path = filedialog.askopenfilename(title="Selecciona el archivo de notas", filetypes=[("PDF files", "*.pdf")])
        if path:
            filename = os.path.basename(path)
            if not (filename.endswith('_NotasMedia.pdf')):
                tk.messagebox.showerror("Error", "El archivo de notas debe terminar en _NotasMedia.pdf y ser PDF.")
                return
            self.notas_path.set(path)
            self.validar_coincidencia()

    def cargar_cv(self):
        path = filedialog.askopenfilename(title="Selecciona el archivo de currículum", filetypes=[("PDF files", "*.pdf")])
        if path:
            filename = os.path.basename(path)
            if not (filename.endswith('_CV.pdf')):
                tk.messagebox.showerror("Error", "El archivo de currículum debe terminar en _CV.pdf y ser PDF.")
                return
            self.cv_path.set(path)
            self.validar_coincidencia()

    def seleccionar_drive(self):
        import threading
        threading.Thread(target=self._seleccionar_drive, daemon=True).start()

    def _seleccionar_drive(self):
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaIoBaseDownload
            import io
            import os
            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
            creds = None
            if os.path.exists('token.json'):
                from google.oauth2.credentials import Credentials
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            service = build('drive', 'v3', credentials=creds)
            # Mostrar archivos PDF recientes
            results = service.files().list(q="mimeType='application/pdf'", pageSize=20, fields="files(id, name)").execute()
            items = results.get('files', [])
            if not items:
                tk.messagebox.showinfo("Google Drive", "No se encontraron archivos PDF en tu Drive.")
                return
            # Mostrar selección simple en Tkinter
            import tkinter.simpledialog
            opciones = [f"{item['name']} ({item['id']})" for item in items]
            seleccion = tkinter.simpledialog.askstring("Google Drive", "Escribe el número del archivo a descargar:\n" + '\n'.join(f"{i+1}. {opciones[i]}" for i in range(len(opciones))))
            if not seleccion or not seleccion.isdigit() or int(seleccion) < 1 or int(seleccion) > len(items):
                return
            file_id = items[int(seleccion)-1]['id']
            file_name = items[int(seleccion)-1]['name']
            # Descargar archivo
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(file_name, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            tk.messagebox.showinfo("Google Drive", f"Archivo '{file_name}' descargado.")
        except Exception as e:
            tk.messagebox.showerror("Google Drive", f"Error: {e}")

    def extraer_post_num(self, filename):
        # Busca la parte después de post- y antes del siguiente guion bajo o punto
        import re
        m = re.search(r'post-([0-9]+)', filename, re.IGNORECASE)
        if m:
            # Para depuración, muestra el número extraído
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
                tk.messagebox.showerror("Error", "El número después de POST- debe coincidir en ambos archivos.")
                self.notas_path.set("")
                self.cv_path.set("")

if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        import subprocess
        subprocess.check_call(['pip', 'install', 'pillow'])
        from PIL import Image, ImageTk
    app = App()
    app.mainloop()
