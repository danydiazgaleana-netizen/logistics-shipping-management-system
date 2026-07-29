# -*- coding: utf-8 -*-
"""
Interfaz Gráfica Oficial - Red de Datos Implacable Grupo REV (Gestión Multicanal y Estatus)
Con Control de Acceso, Notificaciones Flotantes, Badges y Bandeja de Notificaciones Persistente
(Versión con Diseño Profesional y Moderno)
"""
import os
import shutil
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime

# ==========================================
# CLASE DE AUTENTICACIÓN (CONTROL DE ACCESO)
# ==========================================
class VentanaLogin(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Grupo REV | Control de Acceso Autorizado")
        self.geometry("480x360")
        self.resizable(False, False)
        self.config(bg="#f4f6f9")
        
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        self.autorizado = False

        self.usuarios_autorizados = {
            "danydiazgaleana@gmail.com": "Caretas24",
            "logistica@gruporev.com": "Caretas24",
            "embarques@gruporev.com": "Caretas24",
            "admin@gruporev.com": "Caretas24"
        }

        self.crear_widgets_login()
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def crear_widgets_login(self):
        # Contenedor principal con estilo moderno
        frame_main = tk.Frame(self, bg="#ffffff", bd=1, relief=tk.SOLID)
        frame_main.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=430, height=310)

        lbl_header = tk.Label(frame_main, text="GRUPO REV", font=("Segoe UI", 14, "bold"), fg="#1e293b", bg="#ffffff")
        lbl_header.pack(pady=(20, 5))

        lbl_info = tk.Label(
            frame_main, 
            text="Credenciales corporativas autorizadas\npara Módulos de Logística y Embarques.", 
            font=("Segoe UI", 9), 
            fg="#64748b",
            bg="#ffffff",
            justify=tk.CENTER
        )
        lbl_info.pack(pady=(0, 15))

        frame_inputs = tk.Frame(frame_main, bg="#ffffff")
        frame_inputs.pack(fill=tk.X, padx=30)

        lbl_user = tk.Label(frame_inputs, text="Correo Electrónico / Usuario", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#ffffff")
        lbl_user.pack(anchor=tk.W, pady=(0, 2))
        
        self.entry_user = ttk.Entry(frame_inputs, font=("Segoe UI", 10))
        self.entry_user.pack(fill=tk.X, pady=(0, 10))
        self.entry_user.focus()

        lbl_pass = tk.Label(frame_inputs, text="Contraseña", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#ffffff")
        lbl_pass.pack(anchor=tk.W, pady=(0, 2))
        
        self.entry_pass = ttk.Entry(frame_inputs, font=("Segoe UI", 10), show="*")
        self.entry_pass.pack(fill=tk.X, pady=(0, 15))
        self.entry_pass.bind("<Return>", lambda event: self.verificar_credenciales())

        btn_ingresar = tk.Button(
            frame_main, text="Ingresar al Sistema", font=("Segoe UI", 10, "bold"),
            bg="#0f172a", fg="#ffffff", activebackground="#1e293b", activeforeground="#ffffff",
            relief=tk.FLAT, cursor="hand2", command=self.verificar_credenciales
        )
        btn_ingresar.pack(fill=tk.X, padx=30, ipady=6)

    def verificar_credenciales(self):
        usuario = self.entry_user.get().strip().lower()
        password = self.entry_pass.get().strip()

        if usuario in self.usuarios_autorizados and self.usuarios_autorizados[usuario] == password:
            self.autorizado = True
            self.destroy()
        else:
            messagebox.showerror("Acceso Denegado", "Credenciales incorrectas o usuario no autorizado.")
            self.entry_pass.delete(0, tk.END)

    def cerrar_aplicacion(self):
        self.parent.destroy()


# ==========================================
# CLASE DE NOTIFICACIÓN FLOTANTE (TOAST)
# ==========================================
class VentanaToast(tk.Toplevel):
    def __init__(self, parent, titulo, mensaje):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.config(bg="#0f172a")
        
        ancho = 380
        alto = 90
        x = parent.winfo_screenwidth() - ancho - 30
        y = parent.winfo_screenheight() - alto - 80
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

        frame_interior = tk.Frame(self, bg="#ffffff", bd=0)
        frame_interior.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Barra lateral estética de acento
        accent_bar = tk.Frame(frame_interior, bg="#0284c7", width=6)
        accent_bar.pack(side=tk.LEFT, fill=tk.Y)

        content_frame = tk.Frame(frame_interior, bg="#ffffff")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=8)

        lbl_titulo = tk.Label(content_frame, text=f"{titulo}", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg="#ffffff", anchor="w")
        lbl_titulo.pack(fill=tk.X, pady=(2, 2))

        lbl_msg = tk.Label(content_frame, text=mensaje, font=("Segoe UI", 9), fg="#475569", bg="#ffffff", anchor="w", justify=tk.LEFT, wraplength=330)
        lbl_msg.pack(fill=tk.X)

        self.after(5000, self.destroy)


# ==========================================
# CLASE PRINCIPAL DE LA APLICACIÓN
# ==========================================
class AppGrupoREV(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        
        login = VentanaLogin(self)
        self.wait_window(login)

        if not login.autorizado:
            self.destroy()
            return

        self.deiconify()
        self.title("Grupo REV | Red de Datos Implacable: Gestión Multicanal de Embarques")
        self.geometry("1500x850")
        self.state("zoomed")
        
        # Configurar Estilos Modernos (TTK Themes/Styles)
        self.configurar_estilos()

        self.carpeta_datos = "./data"
        self.carpeta_guias = "./guias_maestras"
        
        if not os.path.exists(self.carpeta_datos):
            os.makedirs(self.carpeta_datos, exist_ok=True)
        if not os.path.exists(self.carpeta_guias):
            os.makedirs(self.carpeta_guias, exist_ok=True)

        self.canales = ["VL", "PEGE", "TIAU", "MUESTRAS", "AMAZON", "MH"]
        self.lista_estatus = ["En espera", "En camino", "Entregado", "Devolucion"]
        
        self.columnas_oficiales = [
            'OV', 'Numero de pedido', 'Nombre del cliente', 'Cajas', 'Bolsas',
            'fecha de envio', 'fecha de entrega', 'ubicacion', 'horario entrega',
            'nombre de quien entrega', 'nombre de la paqueteria',
            'nombre de quien recibe (chofer)', 'fecha de salida', 'hora de salida',
            'valor ($MXN)', 'dias de estancia', 'Estatus', 'Numero de guia', 'Archivo guia'
        ]

        self.archivo_guia_temp = ""

        self.crear_widgets()
        self.cargar_datos_todos_canales()

    def configurar_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Paleta de colores corporativa limpia y profesional
        COLOR_BG = "#f8fafc"
        COLOR_PRIMARY = "#0f172a"
        COLOR_ACCENT = "#0284c7"
        
        self.config(bg=COLOR_BG)
        
        # Configuración general de componentes TTK
        self.style.configure('.', background=COLOR_BG, foreground="#334155", font=("Segoe UI", 9))
        self.style.configure('TNotebook', background=COLOR_BG, borderwidth=0)
        self.style.configure('TNotebook.Tab', font=("Segoe UI", 10, "bold"), padding=[14, 8], background="#e2e8f0", foreground="#475569")
        self.style.map('TNotebook.Tab', background=[('selected', COLOR_PRIMARY)], foreground=[('selected', '#ffffff')])
        
        self.style.configure('TLabelframe', background=COLOR_BG, bordercolor="#cbd5e1", relief="solid")
        self.style.configure('TLabelframe.Label', font=("Segoe UI", 10, "bold"), foreground=COLOR_PRIMARY, background=COLOR_BG)
        
        self.style.configure('Treeview', font=("Segoe UI", 9), rowheight=26, background="#ffffff", fieldbackground="#ffffff", bordercolor="#cbd5e1")
        self.style.configure('Treeview.Heading', font=("Segoe UI", 9, "bold"), background="#1e293b", foreground="#ffffff", relief="flat")
        self.style.map('Treeview.Heading', background=[('active', COLOR_ACCENT)])

    def registrar_y_mostrar_notificacion(self, tipo_origen, titulo, mensaje):
        """Guarda la notificación en archivo persistente y lanza el toast visual"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ruta_notis = os.path.join(self.carpeta_datos, "bandeja_notificaciones.csv")
            
            nueva_notificacion = pd.DataFrame([{
                'Fecha/Hora': timestamp,
                'Área / Origen': tipo_origen,
                'Título': titulo,
                'Mensaje': mensaje
            }])

            if os.path.exists(ruta_notis):
                df_notis = pd.read_csv(ruta_notis, dtype=str)
                df_notis = pd.concat([df_notis, nueva_notificacion], ignore_index=True)
            else:
                df_notis = nueva_notificacion

            df_notis.to_csv(ruta_notis, index=False, encoding='utf-8-sig')

            # Mostrar la alerta flotante instantánea
            VentanaToast(self, titulo, mensaje)

            # Refrescar la tabla de la bandeja si está creada
            if hasattr(self, 'tree_notificaciones'):
                self.cargar_datos_bandeja()

        except Exception as e:
            print("Error al registrar notificación:", e)

    def obtener_ruta_csv(self, canal):
        return os.path.join(self.carpeta_datos, f"maestro_embarques_{canal.lower()}.csv")

    def crear_widgets(self):
        frame_top_menu = ttk.Frame(self, padding=8)
        frame_top_menu.pack(side=tk.TOP, fill=tk.X)
        
        btn_auditoria_errores = ttk.Button(frame_top_menu, text="Auditoría: Ver Historial de Errores y Discrepancias", command=self.abrir_ventana_errores)
        btn_auditoria_errores.pack(side=tk.RIGHT, padx=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=5)

        # PESTAÑA 1: Bitácora General
        self.tab_general = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_general, text=" 📋 1. Bitácora General Consolidada ")
        self.crear_vista_bitacora_general()

        # PESTAÑAS 2 a 7: Canales individuales
        self.trees_canales = {}
        for canal in self.canales:
            tab_canal = ttk.Frame(self.notebook)
            self.notebook.add(tab_canal, text=f" 📂 {canal} ")
            self.crear_vista_canal_individual(tab_canal, canal)

        # PESTAÑA 8: Captura Logística
        self.tab_logistica = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_logistica, text=" 📦 2. Captura Logística ")
        self.crear_formulario_logistica()

        # PESTAÑA 9: Captura Embarques
        self.tab_embarques = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_embarques, text=" 🚚 [0] 3. Captura Embarques ")
        self.crear_formulario_embarques()

        # PESTAÑA 10: Bandeja de Notificaciones Persistente
        self.tab_bandeja = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_bandeja, text=" 🔔 Bandeja de Notificaciones ")
        self.crear_vista_bandeja_notificaciones()

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.actualizar_panel_detalle_activo())

    def crear_vista_bandeja_notificaciones(self):
        frame_superior = ttk.Frame(self.tab_bandeja, padding=5)
        frame_superior.pack(fill=tk.X, padx=10, pady=5)

        btn_refrescar_notis = ttk.Button(frame_superior, text="🔄 Actualizar Bandeja", command=self.cargar_datos_bandeja)
        btn_refrescar_notis.pack(side=tk.LEFT, padx=5)

        btn_limpiar_notis = ttk.Button(frame_superior, text="🗑️ Vaciar Historial de Notificaciones", command=self.vaciar_bandeja_notificaciones)
        btn_limpiar_notis.pack(side=tk.RIGHT, padx=5)

        frame_tabla = ttk.LabelLabelFrame if hasattr(ttk, 'LabelLabelFrame') else ttk.LabelFrame
        frame_tabla_box = frame_tabla(self.tab_bandeja, text=" Historial de Avisos y Actividad Cruzada (Logística & Embarques) ")
        frame_tabla_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols_noti = ['Fecha/Hora', 'Área / Origen', 'Título', 'Mensaje']
        
        scroll_y = ttk.Scrollbar(frame_tabla_box, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame_tabla_box, orient=tk.HORIZONTAL)

        self.tree_notificaciones = ttk.Treeview(
            frame_tabla_box, columns=cols_noti, show='headings', height=15,
            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
        )
        scroll_y.config(command=self.tree_notificaciones.yview)
        scroll_x.config(command=self.tree_notificaciones.xview)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_notificaciones.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        anchos_noti = {'Fecha/Hora': 160, 'Área / Origen': 140, 'Título': 220, 'Mensaje': 650}
        for col in cols_noti:
            self.tree_notificaciones.heading(col, text=col)
            self.tree_notificaciones.column(col, width=anchos_noti.get(col, 200), anchor=tk.W)

        self.cargar_datos_bandeja()

    def cargar_datos_bandeja(self):
        if not hasattr(self, 'tree_notificaciones'):
            return
        
        for row in self.tree_notificaciones.get_children():
            self.tree_notificaciones.delete(row)

        ruta_notis = os.path.join(self.carpeta_datos, "bandeja_notificaciones.csv")
        try:
            if os.path.exists(ruta_notis):
                df_notis = pd.read_csv(ruta_notis, dtype=str)
                for _, row in df_notis.iterrows():
                    valores = [row.get('Fecha/Hora', ''), row.get('Área / Origen', ''), row.get('Título', ''), row.get('Mensaje', '')]
                    self.tree_notificaciones.insert("", 0, values=valores)
        except Exception as e:
            print("Error cargando bandeja de notificaciones:", e)

    def vaciar_bandeja_notificaciones(self):
        if messagebox.askyesno("Confirmar", "¿Seguro deseas vaciar todo el historial de notificaciones?"):
            ruta_notis = os.path.join(self.carpeta_datos, "bandeja_notificaciones.csv")
            if os.path.exists(ruta_notis):
                os.remove(ruta_notis)
            self.cargar_datos_bandeja()
            messagebox.showinfo("Éxito", "La bandeja de notificaciones ha sido vaciada.")

    def actualizar_contadores_pendientes(self):
        try:
            total_pendientes = 0
            for canal in self.canales:
                ruta_csv = self.obtener_ruta_csv(canal)
                if os.path.exists(ruta_csv):
                    df = pd.read_csv(ruta_csv, dtype=str)
                    if 'Estatus' in df.columns:
                        pendientes_canal = df[df['Estatus'].str.strip() == 'En espera']
                        total_pendientes += len(pendientes_canal)

            idx_embarques = self.notebook.index(self.tab_embarques)
            self.notebook.tab(idx_embarques, text=f" 🚚 [{total_pendientes}] 3. Captura Embarques ")
        except Exception as e:
            print("Error actualizando contadores de pestañas:", e)

    def crear_vista_bitacora_general(self):
        frame_superior = ttk.Frame(self.tab_general, padding=5)
        frame_superior.pack(fill=tk.X, padx=10, pady=5)

        btn_exportar_general = ttk.Button(frame_superior, text="📊 Exportar Consolidado General a Excel", command=self.exportar_general_a_excel)
        btn_exportar_general.pack(side=tk.LEFT, padx=5)

        btn_refrescar = ttk.Button(frame_superior, text="🔄 Refrescar Vistas", command=self.cargar_datos_todos_canales)
        btn_refrescar.pack(side=tk.RIGHT, padx=5)

        frame_tabla = ttk.LabelFrame(self.tab_general, text=" Consolidado Global de Pedidos (Todos los Canales) ")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols_general = ['Canal'] + self.columnas_oficiales
        
        scroll_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)

        self.tree_general = ttk.Treeview(
            frame_tabla, columns=cols_general, show='headings', height=12,
            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
        )
        scroll_y.config(command=self.tree_general.yview)
        scroll_x.config(command=self.tree_general.xview)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_general.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree_general.heading('Canal', text='Canal')
        self.tree_general.column('Canal', width=90, anchor=tk.W)
        for col in self.columnas_oficiales:
            self.tree_general.heading(col, text=col)
            self.tree_general.column(col, width=120, anchor=tk.W)

        self.tree_general.bind("<<TreeviewSelect>>", self.mostrar_detalle_general_seleccionado)

        self.frame_detalle = ttk.LabelFrame(self.tab_general, text=" 🔍 Visualización Detallada del Pedido Seleccionado y Acceso a Guía ")
        self.frame_detalle.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.crear_panel_detalle_vacio()

    def crear_vista_canal_individual(self, tab_canal, canal):
        frame_superior = ttk.Frame(tab_canal, padding=5)
        frame_superior.pack(fill=tk.X, padx=10, pady=5)

        btn_exportar_excel = ttk.Button(frame_superior, text=f"📊 Exportar Bitácora [{canal}] a Excel", command=lambda c=canal: self.exportar_canal_a_excel(c))
        btn_exportar_excel.pack(side=tk.LEFT, padx=5)

        frame_tabla = ttk.LabelFrame(tab_canal, text=f" Bitácora Oficial: {canal} ")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tree = ttk.Treeview(frame_tabla, columns=self.columnas_oficiales, show='headings', height=14)
        scroll_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tree.yview)
        scroll_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in self.columnas_oficiales:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor=tk.W)

        tree.bind("<<TreeviewSelect>>", self.mostrar_detalle_canal_seleccionado)
        self.trees_canales[canal] = tree

    def crear_formulario_logistica(self):
        frame = ttk.LabelFrame(self.tab_logistica, text=" Ingreso Logístico Exclusivo (Lista de Empaque Oficial, Fechas y Guía) ")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        lbl_canal = ttk.Label(frame, text="Canal / Bitácora de Destino:", font=("Segoe UI", 9, "bold"))
        lbl_canal.grid(row=0, column=0, sticky=tk.W, padx=20, pady=8)
        self.combo_canal_log = ttk.Combobox(frame, values=self.canales, state="readonly", width=46, font=("Segoe UI", 9))
        self.combo_canal_log.grid(row=0, column=1, sticky=tk.W, padx=20, pady=8)
        self.combo_canal_log.set(self.canales[0])

        campos = [
            ("Orden de Venta (OV):", "entry_ov"),
            ("Números de pedido:", "entry_pedido"),
            ("Nombre del cliente:", "entry_cliente"),
            ("Cajas:", "entry_cajas"),
            ("Bolsas:", "entry_bolsas"),
            ("Fecha de Envío (AAAA-MM-DD):", "entry_log_f_envio"),
            ("Fecha de Entrega (AAAA-MM-DD) [Logística]:", "entry_log_f_entrega"),
            ("Ubicación:", "entry_ubicacion"),
            ("Nombre de la paquetería:", "entry_paqueteria"),
            ("Valor ($MXN):", "entry_valor"),
            ("Número de Guía:", "entry_num_guia")
        ]

        for i, (label_text, attr_name) in enumerate(campos, start=1):
            lbl = ttk.Label(frame, text=label_text, font=("Segoe UI", 9, "bold"))
            lbl.grid(row=i, column=0, sticky=tk.W, padx=20, pady=5)
            ent = ttk.Entry(frame, width=48, font=("Segoe UI", 9))
            ent.grid(row=i, column=1, sticky=tk.W, padx=20, pady=5)
            setattr(self, attr_name, ent)

        row_idx = len(campos) + 1
        lbl_guia = ttk.Label(frame, text="Adjuntar Archivo de Guía (PDF):", font=("Segoe UI", 9, "bold"))
        lbl_guia.grid(row=row_idx, column=0, sticky=tk.W, padx=20, pady=8)
        
        frame_archivo = ttk.Frame(frame)
        frame_archivo.grid(row=row_idx, column=1, sticky=tk.W, padx=20, pady=8)

        btn_explorar_guia = ttk.Button(frame_archivo, text="📂 Examinar Guía PDF", command=self.seleccionar_archivo_guia)
        btn_explorar_guia.pack(side=tk.LEFT, padx=5)

        self.lbl_ruta_guia = ttk.Label(frame_archivo, text="Ningún archivo seleccionado.", font=("Segoe UI", 9, "italic"), foreground="gray")
        self.lbl_ruta_guia.pack(side=tk.LEFT, padx=5)

        btn_guardar = ttk.Button(frame, text="💾 Registrar en Maestro Logístico del Canal", command=self.guardar_datos_logistica)
        btn_guardar.grid(row=row_idx+1, column=0, columnspan=2, pady=15)

    def seleccionar_archivo_guia(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo PDF de guía por logística",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.archivo_guia_temp = archivo
            self.lbl_ruta_guia.config(text=os.path.basename(archivo), foreground="black")

    def guardar_datos_logistica(self):
        try:
            canal = self.combo_canal_log.get().strip()
            ov = self.entry_ov.get().strip()
            pedido = self.entry_pedido.get().strip()
            cliente = self.entry_cliente.get().strip()
            cajas = self.entry_cajas.get().strip()
            bolsas = self.entry_bolsas.get().strip()
            f_envio = self.entry_log_f_envio.get().strip()
            f_entrega = self.entry_log_f_entrega.get().strip()
            ubicacion = self.entry_ubicacion.get().strip()
            paqueteria = self.entry_paqueteria.get().strip()
            valor = self.entry_valor.get().strip()
            num_guia = self.entry_num_guia.get().strip()

            if not ov or not cliente or not pedido or not canal:
                messagebox.showerror("Error", "Faltan datos obligatorios (Canal, OV, Pedido, Cliente).")
                return

            resumen = (
                f"¿Seguro quieres registrar/capturar los datos?\n\n"
                f"• Canal: {canal}\n"
                f"• OV: {ov}\n"
                f"• Pedido: {pedido}\n"
                f"• Cliente: {cliente}\n"
                f"• Fecha de Envío: {f_envio if f_envio else '(Vacía)'}\n"
                f"• Fecha de Entrega: {f_entrega if f_entrega else '(Vacía)'}\n"
                f"• Paquetería: {paqueteria if paqueteria else '(Vacía)'}"
            )
            
            confirmar = messagebox.askyesno("Confirmación de Captura", resumen)
            if not confirmar:
                return

            archivo_guia_nombre = "Sin archivo"
            if self.archivo_guia_temp and os.path.exists(self.archivo_guia_temp):
                nombre_base = os.path.basename(self.archivo_guia_temp)
                archivo_guia_nombre = nombre_base
                destino_guia = os.path.join(self.carpeta_guias, archivo_guia_nombre)
                shutil.copy(self.archivo_guia_temp, destino_guia)

            ruta_csv_canal = self.obtener_ruta_csv(canal)
            if os.path.exists(ruta_csv_canal):
                df = pd.read_csv(ruta_csv_canal, dtype=str)
                for col in self.columnas_oficiales:
                    if col not in df.columns:
                        df[col] = ""
            else:
                df = pd.DataFrame(columns=self.columnas_oficiales)

            df = df[df['OV'].astype(str).str.lower() != 'nan']

            if not df.empty and 'OV' in df.columns and ov in df['OV'].astype(str).values:
                df.loc[df['OV'].astype(str) == ov, 'Numero de pedido'] = pedido
                df.loc[df['OV'].astype(str) == ov, 'Nombre del cliente'] = cliente
                df.loc[df['OV'].astype(str) == ov, 'Cajas'] = cajas
                df.loc[df['OV'].astype(str) == ov, 'Bolsas'] = bolsas
                if f_envio:
                    df.loc[df['OV'].astype(str) == ov, 'fecha de envio'] = f_envio
                if f_entrega:
                    df.loc[df['OV'].astype(str) == ov, 'fecha de entrega'] = f_entrega
                df.loc[df['OV'].astype(str) == ov, 'ubicacion'] = ubicacion
                df.loc[df['OV'].astype(str) == ov, 'nombre de la paqueteria'] = paqueteria
                df.loc[df['OV'].astype(str) == ov, 'valor ($MXN)'] = valor
                df.loc[df['OV'].astype(str) == ov, 'Numero de guia'] = num_guia
                if 'Estatus' not in df.columns or not df.loc[df['OV'].astype(str) == ov, 'Estatus'].values[0]:
                    df.loc[df['OV'].astype(str) == ov, 'Estatus'] = 'En espera'
                if self.archivo_guia_temp:
                    df.loc[df['OV'].astype(str) == ov, 'Archivo guia'] = archivo_guia_nombre
            else:
                nueva_fila = {col: "" for col in self.columnas_oficiales}
                nueva_fila.update({
                    'OV': ov,
                    'Numero de pedido': pedido,
                    'Nombre del cliente': cliente,
                    'Cajas': cajas,
                    'Bolsas': bolsas,
                    'fecha de envio': f_envio,
                    'fecha de entrega': f_entrega,
                    'ubicacion': ubicacion,
                    'nombre de la paqueteria': paqueteria,
                    'valor ($MXN)': valor,
                    'Estatus': 'En espera',
                    'Numero de guia': num_guia,
                    'Archivo guia': archivo_guia_nombre
                })
                df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

            df.to_csv(ruta_csv_canal, index=False, encoding='utf-8-sig')
            
            # Registrar en bandeja y lanzar toast
            self.registrar_y_mostrar_notificacion(
                "Área de Logística",
                "Nueva Captura Logística",
                f"Canal [{canal}] registró la OV: {ov} | Cliente: {cliente} (Pendiente de embarcar)"
            )

            messagebox.showinfo("Éxito", f"OV {ov} registrada exitosamente en logística para el canal [{canal}].")
            
            for ent in [self.entry_ov, self.entry_pedido, self.entry_cliente, self.entry_cajas, self.entry_bolsas, self.entry_log_f_envio, self.entry_log_f_entrega, self.entry_ubicacion, self.entry_paqueteria, self.entry_valor, self.entry_num_guia]:
                ent.delete(0, tk.END)
            self.archivo_guia_temp = ""
            self.lbl_ruta_guia.config(text="Ningún archivo seleccionado.", foreground="gray")
            
            self.cargar_datos_todos_canales()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def crear_formulario_embarques(self):
        frame = ttk.LabelFrame(self.tab_embarques, text=" Validación Cruzada de Embarques, Salidas y Actualización de Estatus ")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        lbl_canal = ttk.Label(frame, text="Canal / Bitácora a Embarcar:", font=("Segoe UI", 9, "bold"))
        lbl_canal.grid(row=0, column=0, sticky=tk.W, padx=20, pady=8)
        self.combo_canal_emb = ttk.Combobox(frame, values=self.canales, state="readonly", width=38, font=("Segoe UI", 9))
        self.combo_canal_emb.grid(row=0, column=1, sticky=tk.W, padx=20, pady=8)
        self.combo_canal_emb.set(self.canales[0])

        lbl_ov_sel = ttk.Label(frame, text="Orden de Venta (OV):", font=("Segoe UI", 9, "bold"))
        lbl_ov_sel.grid(row=1, column=0, sticky=tk.W, padx=20, pady=8)
        self.entry_emb_ov = ttk.Entry(frame, width=40, font=("Segoe UI", 9))
        self.entry_emb_ov.grid(row=1, column=1, sticky=tk.W, padx=20, pady=8)

        lbl_ped_val = ttk.Label(frame, text="Número de pedido:", font=("Segoe UI", 9, "bold"))
        lbl_ped_val.grid(row=2, column=0, sticky=tk.W, padx=20, pady=8)
        self.entry_emb_pedido = ttk.Entry(frame, width=40, font=("Segoe UI", 9))
        self.entry_emb_pedido.grid(row=2, column=1, sticky=tk.W, padx=20, pady=8)

        campos_emb = [
            ("Horario de entrega:", "entry_h_entrega"),
            ("Nombre de quien entrega:", "entry_quien_entrega"),
            ("Nombre del chofer (Recibe):", "entry_chofer"),
            ("Fecha de salida:", "entry_f_salida"),
            ("Hora de salida:", "entry_h_salida"),
            ("Días de estancia:", "entry_dias_estancia")
        ]

        for i, (label_text, attr_name) in enumerate(campos_emb, start=3):
            lbl = ttk.Label(frame, text=label_text, font=("Segoe UI", 9, "bold"))
            lbl.grid(row=i, column=0, sticky=tk.W, padx=20, pady=6)
            ent = ttk.Entry(frame, width=40, font=("Segoe UI", 9))
            ent.grid(row=i, column=1, sticky=tk.W, padx=20, pady=6)
            setattr(self, attr_name, ent)

        row_est = len(campos_emb) + 3
        lbl_estatus = ttk.Label(frame, text="Actualizar Estatus del Pedido:", font=("Segoe UI", 9, "bold"))
        lbl_estatus.grid(row=row_est, column=0, sticky=tk.W, padx=20, pady=8)
        self.combo_emb_estatus = ttk.Combobox(frame, values=self.lista_estatus, state="readonly", width=38, font=("Segoe UI", 9))
        self.combo_emb_estatus.grid(row=row_est, column=1, sticky=tk.W, padx=20, pady=8)
        self.combo_emb_estatus.set("En camino")

        btn_guardar_emb = ttk.Button(frame, text="🚚 Validar, Actualizar Estatus y Salida en Embarques", command=self.guardar_datos_embarques)
        btn_guardar_emb.grid(row=row_est+1, column=0, columnspan=2, pady=20)

    def guardar_datos_embarques(self):
        try:
            canal = self.combo_canal_emb.get().strip()
            ov_embarques = self.entry_emb_ov.get().strip()
            pedido_embarques = self.entry_emb_pedido.get().strip()
            h_entrega = self.entry_h_entrega.get().strip()
            q_entrega = self.entry_quien_entrega.get().strip()
            chofer = self.entry_chofer.get().strip()
            f_salida = self.entry_f_salida.get().strip()
            h_salida = self.entry_h_salida.get().strip()
            dias = self.entry_dias_estancia.get().strip()
            nuevo_estatus = self.combo_emb_estatus.get().strip()

            if not ov_embarques or not pedido_embarques or not canal:
                messagebox.showerror("Error", "Debes especificar canal, OV y número de pedido.")
                return

            ruta_csv_canal = self.obtener_ruta_csv(canal)
            if os.path.exists(ruta_csv_canal):
                df = pd.read_csv(ruta_csv_canal, dtype=str)
            else:
                messagebox.showerror("Error", f"No existe base de datos logística para el canal [{canal}].")
                return

            df = df[df['OV'].astype(str).str.lower() != 'nan']

            match_log = df[df['OV'].astype(str) == ov_embarques]
            if match_log.empty:
                self.registrar_error(f"Embarques - {canal}", ov_embarques, f"Intento de embarcar OV inexistente en canal {canal} con datos: {pedido_embarques}.")
                messagebox.showerror("Error Crítico", f"La OV {ov_embarques} NO existe en la bitácora del canal [{canal}].")
                return

            fila_log = match_log.iloc[0]
            pedido_logistica = str(fila_log.get('Numero de pedido', ''))
            pedidos_log_lista = [p.strip() for p in pedido_logistica.split(',')]

            if pedido_embarques not in pedidos_log_lista:
                desc_error = f"Discrepancia en canal {canal} (OV {ov_embarques}). Logística tenía [{pedido_logistica}] pero Embarques intentó registrar [{pedido_embarques}]."
                self.registrar_error(f"Ventas / Embarques - {canal}", ov_embarques, desc_error)
                messagebox.showwarning("⚠️ Discrepancia Registrada", f"El pedido ingresado ({pedido_embarques}) no coincide con logística en [{canal}]. Se registró la incidencia.")

            df.loc[df['OV'].astype(str) == ov_embarques, 'horario entrega'] = h_entrega
            df.loc[df['OV'].astype(str) == ov_embarques, 'nombre de quien entrega'] = q_entrega
            df.loc[df['OV'].astype(str) == ov_embarques, 'nombre de quien recibe (chofer)'] = chofer
            df.loc[df['OV'].astype(str) == ov_embarques, 'fecha de salida'] = f_salida
            df.loc[df['OV'].astype(str) == ov_embarques, 'hora de salida'] = h_salida
            df.loc[df['OV'].astype(str) == ov_embarques, 'dias de estancia'] = dias
            df.loc[df['OV'].astype(str) == ov_embarques, 'Estatus'] = nuevo_estatus

            df.to_csv(ruta_csv_canal, index=False, encoding='utf-8-sig')
            
            self.registrar_y_mostrar_notificacion(
                "Área de Embarques",
                "Actualización de Embarques",
                f"Canal [{canal}] - OV: {ov_embarques} | Nuevo estatus: [{nuevo_estatus}]"
            )

            messagebox.showinfo("Éxito", f"Embarque y estatus [{nuevo_estatus}] actualizados correctamente para la OV {ov_embarques} en [{canal}].")
            
            self.entry_emb_ov.delete(0, tk.END)
            self.entry_emb_pedido.delete(0, tk.END)
            for ent in [self.entry_h_entrega, self.entry_quien_entrega, self.entry_chofer, self.entry_f_salida, self.entry_h_salida, self.entry_dias_estancia]:
                ent.delete(0, tk.END)

            self.cargar_datos_todos_canales()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar embarques: {str(e)}")

    def registrar_error(self, origen, ov, descripcion):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ruta_errores = os.path.join(self.carpeta_datos, "historial_errores.csv")
            nuevo = pd.DataFrame([{'Fecha/Hora': timestamp, 'Origen': origen, 'OV': ov, 'Descripción': descripcion}])
            if os.path.exists(ruta_errores):
                df_err = pd.read_csv(ruta_errores, dtype=str)
                df_err = pd.concat([df_err, nuevo], ignore_index=True)
            else:
                df_err = nuevo
            df_err.to_csv(ruta_errores, index=False, encoding='utf-8-sig')
        except Exception as e:
            print("Error al registrar auditoría de error:", e)

    def abrir_ventana_errores(self):
        top = tk.Toplevel(self)
        top.title("Grupo REV | Auditoría de Historial de Errores y Discrepancias")
        top.geometry("900x450")
        
        frame = ttk.LabelFrame(top, text=" Registro Histórico de Discrepancias e Incidencias ")
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        cols = ['Fecha/Hora', 'Origen', 'OV', 'Descripción']
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=15)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=180 if c != 'Descripción' else 320, anchor=tk.W)
        
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ruta_errores = os.path.join(self.carpeta_datos, "historial_errores.csv")
        try:
            if os.path.exists(ruta_errores):
                df_err = pd.read_csv(ruta_errores, dtype=str)
                for _, row in df_err.iterrows():
                    tree.insert("", tk.END, values=[row.get('Fecha/Hora',''), row.get('Origen',''), row.get('OV',''), row.get('Descripción','')])
        except Exception as e:
            print("Error cargando errores:", e)

    def cargar_datos_todos_canales(self):
        try:
            lista_dfs = []
            for canal in self.canales:
                ruta = self.obtener_ruta_csv(canal)
                if os.path.exists(ruta):
                    df = pd.read_csv(ruta, dtype=str)
                    df = df[df['OV'].astype(str).str.lower() != 'nan']
                    df.insert(0, 'Canal', canal)
                    lista_dfs.append(df)
                    
                    if canal in self.trees_canales:
                        tree_c = self.trees_canales[canal]
                        for row in tree_c.get_children():
                            tree_c.delete(row)
                        for _, row in df.iterrows():
                            vals = [row.get(col, '') for col in self.columnas_oficiales]
                            tree_c.insert("", tk.END, values=vals)

            for row in self.tree_general.get_children():
                self.tree_general.delete(row)

            if lista_dfs:
                df_global = pd.concat(lista_dfs, ignore_index=True)
                for _, row in df_global.iterrows():
                    vals = [row.get('Canal', '')] + [row.get(col, '') for col in self.columnas_oficiales]
                    self.tree_general.insert("", tk.END, values=vals)

            self.actualizar_contadores_pendientes()
        except Exception as e:
            print("Error al cargar datos consolidados:", e)

    def crear_panel_detalle_vacio(self):
        for widget in self.frame_detalle.winfo_children():
            widget.destroy()
        lbl = ttk.Label(self.frame_detalle, text="Seleccione un pedido de la tabla superior para ver su información detallada y abrir archivos adjuntos.", font=("Segoe UI", 9, "italic"))
        lbl.pack(padx=15, pady=15)

    def mostrar_detalle_general_seleccionado(self, event):
        seleccion = self.tree_general.selection()
        if not seleccion:
            return
        item = self.tree_general.item(seleccion)
        valores = item['values']
        if not valores:
            return
        
        canal = valores[0]
        ov = valores[1]
        self.renderizar_panel_detalle(canal, ov)

    def mostrar_detalle_canal_seleccionado(self, event):
        # Identificar qué árbol de canal disparó el evento
        for canal, tree in self.trees_canales.items():
            seleccion = tree.selection()
            if seleccion:
                item = tree.item(seleccion)
                valores = item['values']
                if valores:
                    ov = valores[0]
                    self.renderizar_panel_detalle(canal, ov)
                break

    def actualizar_panel_detalle_activo(self):
        # Opcional al cambiar de pestaña
        pass

    def renderizar_panel_detalle(self, canal, ov):
        for widget in self.frame_detalle.winfo_children():
            widget.destroy()

        ruta_csv = self.obtener_ruta_csv(canal)
        if not os.path.exists(ruta_csv):
            return
        
        df = pd.read_csv(ruta_csv, dtype=str)
        match = df[df['OV'].astype(str) == str(ov)]
        if match.empty:
            return

        row = match.iloc[0]

        # Contenedor interior dividido en dos columnas (Información y Acciones)
        frame_content = ttk.Frame(self.frame_detalle, padding=10)
        frame_content.pack(fill=tk.BOTH, expand=True)

        info_texto = (
            f"Canal: {canal}   |   Orden de Venta (OV): {row.get('OV', '')}   |   Pedido: {row.get('Numero de pedido', '')}\n"
            f"Cliente: {row.get('Nombre del cliente', '')}   |   Estatus Actual: {row.get('Estatus', '')}\n"
            f"Paquetería: {row.get('nombre de la paqueteria', '')}   |   Guía: {row.get('Numero de guia', '')}"
        )

        lbl_info = ttk.Label(frame_content, text=info_texto, font=("Segoe UI", 9), justify=tk.LEFT)
        lbl_info.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

        archivo_guia = row.get('Archivo guia', '')
        if archivo_guia and archivo_guia != 'Sin archivo':
            btn_abrir = ttk.Button(frame_content, text="📂 Abrir Guía PDF Adjunta", command=lambda: self.abrir_guia_pdf(archivo_guia))
            btn_abrir.pack(side=tk.RIGHT, padx=10)
        else:
            lbl_no_guia = ttk.Label(frame_content, text="📄 Sin guía PDF adjunta", font=("Segoe UI", 9, "italic"), foreground="gray")
            lbl_no_guia.pack(side=tk.RIGHT, padx=10)

    def abrir_guia_pdf(self, nombre_archivo):
        ruta_completa = os.path.join(self.carpeta_guias, nombre_archivo)
        if os.path.exists(ruta_completa):
            try:
                if platform.system() == 'Windows':
                    os.startfile(ruta_completa)
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', ruta_completa])
                else:
                    subprocess.run(['xdg-open', ruta_completa])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo PDF: {str(e)}")
        else:
            messagebox.showerror("Error", f"El archivo de guía no se encuentra en la ruta:\n{ruta_completa}")

    def exportar_general_a_excel(self):
        try:
            archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos de Excel", "*.xlsx")], title="Guardar Consolidado General")
            if not archivo:
                return
            lista_dfs = []
            for canal in self.canales:
                ruta = self.obtener_ruta_csv(canal)
                if os.path.exists(ruta):
                    df = pd.read_csv(ruta, dtype=str)
                    df.insert(0, 'Canal', canal)
                    lista_dfs.append(df)
            if lista_dfs:
                df_total = pd.concat(lista_dfs, ignore_index=True)
                df_total.to_excel(archivo, index=False)
                messagebox.showinfo("Éxito", "Consolidado general exportado exitosamente a Excel.")
            else:
                messagebox.showwarning("Aviso", "No hay datos para exportar.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def exportar_canal_a_excel(self, canal):
        try:
            ruta = self.obtener_ruta_csv(canal)
            if not os.path.exists(ruta):
                messagebox.showwarning("Aviso", f"No hay datos para el canal [{canal}].")
                return
            archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos de Excel", "*.xlsx")], title=f"Guardar Bitácora {canal}")
            if not archivo:
                return
            df = pd.read_csv(ruta, dtype=str)
            df.to_excel(archivo, index=False)
            messagebox.showinfo("Éxito", f"Bitácora del canal [{canal}] exportada exitosamente a Excel.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

if __name__ == "__main__":
    app = AppGrupoREV()
    app.mainloop()