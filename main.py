# -*- coding: utf-8 -*-
"""
Interfaz Gráfica Oficial - Grupo REV (Gestión Multicanal y Estatus)
(Versión con Base de Datos Integrada - SQLite)
"""
import os
import shutil
import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import customtkinter as ctk
import pandas as pd
from datetime import datetime

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class VentanaLogin(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Grupo REV | Control de Acceso Autorizado")
        self.geometry("450x320")
        self.resizable(False, False)
        
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
        frame_main = ctk.CTkFrame(self, fg_color="transparent")
        frame_main.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        ctk.CTkLabel(frame_main, text="GRUPO REV", font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")).pack(pady=(10, 5))
        ctk.CTkLabel(frame_main, text="Credenciales corporativas autorizadas\npara Módulos de Logística y Embarques.", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="gray").pack(pady=(0, 20))

        self.entry_user = ctk.CTkEntry(frame_main, placeholder_text="Correo Electrónico / Usuario", width=350, height=35, font=("Segoe UI", 12))
        self.entry_user.pack(pady=8)
        self.entry_user.focus()

        self.entry_pass = ctk.CTkEntry(frame_main, placeholder_text="Contraseña", show="*", width=350, height=35, font=("Segoe UI", 12))
        self.entry_pass.pack(pady=8)
        self.entry_pass.bind("<Return>", lambda event: self.verificar_credenciales())

        ctk.CTkButton(
            frame_main, text="Ingresar al Sistema", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#0284c7", hover_color="#0369a1", width=350, height=38, command=self.verificar_credenciales
        ).pack(pady=(20, 0))

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


class VentanaToast(ctk.CTkToplevel):
    def __init__(self, parent, titulo, mensaje):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        ancho, alto = 380, 90
        x = parent.winfo_screenwidth() - ancho - 30
        y = parent.winfo_screenheight() - alto - 80
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

        frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        frame.pack(fill=tk.BOTH, expand=True)

        ctk.CTkFrame(frame, fg_color="#0284c7", width=6, corner_radius=0).pack(side=tk.LEFT, fill=tk.Y)
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=10)

        ctk.CTkLabel(content, text=titulo, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="white").pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(content, text=mensaje, font=ctk.CTkFont(family="Segoe UI", size=10), text_color="#cbd5e1", wraplength=330, justify="left").pack(anchor="w")
        self.after(5000, self.destroy)


class AppGrupoREV(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        login = VentanaLogin(self)
        self.wait_window(login)

        if not login.autorizado:
            self.destroy()
            return

        self.title("Grupo REV | Gestión Logística Multicanal (Base de Datos Local)")
        self.geometry("1450x850")
        self.state("zoomed")

        self.carpeta_datos = "./data"
        self.carpeta_guias = "./guias_maestras"
        os.makedirs(self.carpeta_datos, exist_ok=True)
        os.makedirs(self.carpeta_guias, exist_ok=True)

        self.db_path = os.path.join(self.carpeta_datos, "grupo_rev.db")
        self.inicializar_base_datos()

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
        self.frames_vistas = {}

        self.crear_estructura_principal()
        self.cargar_datos_todos_canales()

    def obtener_conexion(self):
        return sqlite3.connect(self.db_path)

    def inicializar_base_datos(self):
        conn = self.obtener_conexion()
        cursor = conn.cursor()
        
        canales = ["VL", "PEGE", "TIAU", "MUESTRAS", "AMAZON", "MH"]
        for canal in canales:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS canal_{canal.lower()} (
                    OV TEXT PRIMARY KEY,
                    Numero_de_pedido TEXT,
                    Nombre_del_cliente TEXT,
                    Cajas TEXT,
                    Bolsas TEXT,
                    fecha_de_envio TEXT,
                    fecha_de_entrega TEXT,
                    ubicacion TEXT,
                    horario_entrega TEXT,
                    nombre_de_quien_entrega TEXT,
                    nombre_de_la_paqueteria TEXT,
                    nombre_de_quien_recibe_chofer TEXT,
                    fecha_de_salida TEXT,
                    hora_de_salida TEXT,
                    valor_MXN TEXT,
                    dias_de_estancia TEXT,
                    Estatus TEXT,
                    Numero_de_guia TEXT,
                    Archivo_guia TEXT
                )
            """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notificaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT,
                area_origen TEXT,
                titulo TEXT,
                mensaje TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT,
                origen TEXT,
                ov TEXT,
                descripcion TEXT
            )
        """)
        conn.commit()
        conn.close()

    def crear_estructura_principal(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=("#1e293b", "#0f172a"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(16, weight=1)

        ctk.CTkLabel(self.sidebar, text="GRUPO REV", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="white").grid(row=0, column=0, padx=20, pady=(25, 10), sticky="w")
        ctk.CTkLabel(self.sidebar, text="MÓDULO LOGÍSTICO", font=ctk.CTkFont(family="Segoe UI", size=10), text_color="#94a3b8").grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        botones_menu = [
            ("📋 Bitácora General", lambda: self.mostrar_vista("general")),
            ("📦 Captura Logística", lambda: self.mostrar_vista("logistica")),
            ("🚚 Captura Embarques", lambda: self.mostrar_vista("embarques")),
            ("🔔 Notificaciones", lambda: self.mostrar_vista("notificaciones")),
            ("⚠️ Historial de Errores", self.abrir_ventana_errores)
        ]

        for idx, (txt, cmd) in enumerate(botones_menu, start=2):
            ctk.CTkButton(
                self.sidebar, text=txt, command=cmd, 
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                fg_color="transparent", text_color="#f8fafc", hover_color="#334155",
                anchor="w", height=38
            ).grid(row=idx, column=0, sticky="ew", padx=12, pady=2)

        ctk.CTkLabel(self.sidebar, text="CANALES", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color="#64748b").grid(row=7, column=0, padx=20, pady=(15, 5), sticky="w")

        for idx, canal in enumerate(self.canales, start=8):
            ctk.CTkButton(
                self.sidebar, text=f"📂  Bitácora {canal}", command=lambda c=canal: self.mostrar_vista(c),
                font=ctk.CTkFont(family="Segoe UI", size=11),
                fg_color="transparent", text_color="#cbd5e1", hover_color="#334155",
                anchor="w", height=30
            ).grid(row=idx, column=0, sticky="ew", padx=16, pady=1)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.crear_vista_general()
        self.crear_vista_logistica()
        self.crear_vista_embarques()
        self.crear_vista_notificaciones()
        for canal in self.canales:
            self.crear_vista_canal(canal)

        self.mostrar_vista("general")

    def mostrar_vista(self, nombre):
        for vista in self.frames_vistas.values():
            vista.grid_remove()
        if nombre in self.frames_vistas:
            self.frames_vistas[nombre].grid()

    def crear_vista_general(self):
        vista = ctk.CTkFrame(self.container, fg_color="transparent")
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_rowconfigure(2, weight=1)
        self.frames_vistas["general"] = vista

        header = ctk.CTkFrame(vista, fg_color="transparent", height=50)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(header, text="Consolidado Global de Pedidos", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(header, text="🔄 Actualizar", width=110, command=self.cargar_datos_todos_canales, fg_color="#334155", hover_color="#475569").pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(header, text="📊 Exportar Consolidado a Excel", width=180, command=self.exportar_general_a_excel, fg_color="#0284c7", hover_color="#0369a1").pack(side=tk.RIGHT, padx=5)

        kpi_frame = ctk.CTkFrame(vista, fg_color="transparent", height=90)
        kpi_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_total = self.crear_tarjeta_kpi(kpi_frame, "Total Pedidos", "0", 0)
        self.kpi_espera = self.crear_tarjeta_kpi(kpi_frame, "En Espera", "0", 1)
        self.kpi_camino = self.crear_tarjeta_kpi(kpi_frame, "En Camino", "0", 2)
        self.kpi_entregados = self.crear_tarjeta_kpi(kpi_frame, "Entregados", "0", 3)

        tabla_frame = ctk.CTkFrame(vista)
        tabla_frame.grid(row=2, column=0, sticky="nsew")
        tabla_frame.grid_columnconfigure(0, weight=1)
        tabla_frame.grid_rowconfigure(0, weight=1)

        cols_general = ['Canal'] + self.columnas_oficiales
        self.tree_general = ttk.Treeview(tabla_frame, columns=cols_general, show='headings', height=18)
        
        scroll_y = ttk.Scrollbar(tabla_frame, orient=tk.VERTICAL, command=self.tree_general.yview)
        scroll_x = ttk.Scrollbar(tabla_frame, orient=tk.HORIZONTAL, command=self.tree_general.xview)
        self.tree_general.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_general.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree_general.heading('Canal', text='Canal')
        self.tree_general.column('Canal', width=90, anchor=tk.W)
        for col in self.columnas_oficiales:
            self.tree_general.heading(col, text=col)
            self.tree_general.column(col, width=120, anchor=tk.W)

    def crear_tarjeta_kpi(self, parent, titulo, valor_inicial, col):
        card = ctk.CTkFrame(parent, fg_color=("#ffffff", "#1e293b"), corner_radius=8, border_width=1, border_color=("#cbd5e1", "#334155"))
        card.grid(row=0, column=col, sticky="nsew", padx=5)
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(family="Segoe UI", size=11), text_color="gray").pack(anchor="w", padx=15, pady=(10, 0))
        lbl_v = ctk.CTkLabel(card, text=valor_inicial, font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"))
        lbl_v.pack(anchor="w", padx=15, pady=(0, 10))
        return lbl_v

    def crear_vista_logistica(self):
        vista = ctk.CTkFrame(self.container, fg_color="transparent")
        vista.grid_columnconfigure(0, weight=1)
        self.frames_vistas["logistica"] = vista

        frame_form = ctk.CTkScrollableFrame(vista, label_text=" Ingreso Logístico Exclusivo (Base de Datos) ")
        frame_form.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.combo_canal_log = ctk.CTkComboBox(frame_form, values=self.canales, width=350, state="readonly")
        self.agregar_campo_formulario(frame_form, "Canal / Bitácora:", self.combo_canal_log, 0)
        self.entry_ov = ctk.CTkEntry(frame_form, width=350, placeholder_text="Ej. OV-9923")
        self.agregar_campo_formulario(frame_form, "Orden de Venta (OV):", self.entry_ov, 1)
        self.entry_pedido = ctk.CTkEntry(frame_form, width=350, placeholder_text="Ej. 54892")
        self.agregar_campo_formulario(frame_form, "Números de pedido:", self.entry_pedido, 2)
        self.entry_cliente = ctk.CTkEntry(frame_form, width=350, placeholder_text="Nombre del cliente")
        self.agregar_campo_formulario(frame_form, "Nombre del cliente:", self.entry_cliente, 3)
        self.entry_cajas = ctk.CTkEntry(frame_form, width=350, placeholder_text="0")
        self.agregar_campo_formulario(frame_form, "Cajas:", self.entry_cajas, 4)
        self.entry_bolsas = ctk.CTkEntry(frame_form, width=350, placeholder_text="0")
        self.agregar_campo_formulario(frame_form, "Bolsas:", self.entry_bolsas, 5)
        self.entry_log_f_envio = ctk.CTkEntry(frame_form, width=350, placeholder_text="AAAA-MM-DD")
        self.agregar_campo_formulario(frame_form, "Fecha de Envío:", self.entry_log_f_envio, 6)
        self.entry_log_f_entrega = ctk.CTkEntry(frame_form, width=350, placeholder_text="AAAA-MM-DD")
        self.agregar_campo_formulario(frame_form, "Fecha de Entrega:", self.entry_log_f_entrega, 7)
        self.entry_ubicacion = ctk.CTkEntry(frame_form, width=350, placeholder_text="Ciudad / Destino")
        self.agregar_campo_formulario(frame_form, "Ubicación:", self.entry_ubicacion, 8)
        self.entry_paqueteria = ctk.CTkEntry(frame_form, width=350, placeholder_text="Empresa de envío")
        self.agregar_campo_formulario(frame_form, "Paquetería:", self.entry_paqueteria, 9)
        self.entry_valor = ctk.CTkEntry(frame_form, width=350, placeholder_text="0.00")
        self.agregar_campo_formulario(frame_form, "Valor ($MXN):", self.entry_valor, 10)
        self.entry_num_guia = ctk.CTkEntry(frame_form, width=350, placeholder_text="Guía de transporte")
        self.agregar_campo_formulario(frame_form, "Número de Guía:", self.entry_num_guia, 11)

        ctk.CTkLabel(frame_form, text="Archivo de Guía (PDF):", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).grid(row=12, column=0, sticky="w", padx=25, pady=10)
        frame_btn_g = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_btn_g.grid(row=12, column=1, sticky="w", padx=20, pady=10)
        ctk.CTkButton(frame_btn_g, text="📂 Seleccionar PDF", width=140, command=self.seleccionar_archivo_guia, fg_color="#334155").pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_ruta_guia = ctk.CTkLabel(frame_btn_g, text="Ningún archivo seleccionado.", text_color="gray", font=ctk.CTkFont(slant="italic"))
        self.lbl_ruta_guia.pack(side=tk.LEFT)

        ctk.CTkButton(
            frame_form, text="💾 Registrar en Base de Datos", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#0284c7", hover_color="#0369a1", height=40, command=self.guardar_datos_logistica
        ).grid(row=13, column=0, columnspan=2, pady=25)

    def agregar_campo_formulario(self, parent, texto, widget, row):
        ctk.CTkLabel(parent, text=texto, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=25, pady=8)
        widget.grid(row=row, column=1, sticky="w", padx=20, pady=8)

    def crear_vista_embarques(self):
        vista = ctk.CTkFrame(self.container, fg_color="transparent")
        vista.grid_columnconfigure(0, weight=1)
        self.frames_vistas["embarques"] = vista

        frame_form = ctk.CTkScrollableFrame(vista, label_text=" Validación de Embarques y Estatus ")
        frame_form.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.combo_canal_emb = ctk.CTkComboBox(frame_form, values=self.canales, width=350, state="readonly")
        self.agregar_campo_formulario(frame_form, "Canal de Destino:", self.combo_canal_emb, 0)
        self.entry_emb_ov = ctk.CTkEntry(frame_form, width=350, placeholder_text="OV correspondiente")
        self.agregar_campo_formulario(frame_form, "Orden de Venta (OV):", self.entry_emb_ov, 1)
        self.entry_emb_pedido = ctk.CTkEntry(frame_form, width=350, placeholder_text="Número de pedido")
        self.agregar_campo_formulario(frame_form, "Número de pedido:", self.entry_emb_pedido, 2)
        self.entry_h_entrega = ctk.CTkEntry(frame_form, width=350, placeholder_text="HH:MM")
        self.agregar_campo_formulario(frame_form, "Horario entrega:", self.entry_h_entrega, 3)
        self.entry_quien_entrega = ctk.CTkEntry(frame_form, width=350, placeholder_text="Personal")
        self.agregar_campo_formulario(frame_form, "Quien entrega:", self.entry_quien_entrega, 4)
        self.entry_chofer = ctk.CTkEntry(frame_form, width=350, placeholder_text="Chofer")
        self.agregar_campo_formulario(frame_form, "Chofer (Recibe):", self.entry_chofer, 5)
        self.entry_f_salida = ctk.CTkEntry(frame_form, width=350, placeholder_text="AAAA-MM-DD")
        self.agregar_campo_formulario(frame_form, "Fecha de salida:", self.entry_f_salida, 6)
        self.entry_h_salida = ctk.CTkEntry(frame_form, width=350, placeholder_text="HH:MM")
        self.agregar_campo_formulario(frame_form, "Hora de salida:", self.entry_h_salida, 7)
        self.entry_dias_estancia = ctk.CTkEntry(frame_form, width=350, placeholder_text="0")
        self.agregar_campo_formulario(frame_form, "Días de estancia:", self.entry_dias_estancia, 8)
        self.combo_emb_estatus = ctk.CTkComboBox(frame_form, values=self.lista_estatus, width=350, state="readonly")
        self.agregar_campo_formulario(frame_form, "Estatus del Pedido:", self.combo_emb_estatus, 9)

        ctk.CTkButton(
            frame_form, text="🚚 Actualizar Salida en Base de Datos", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#1e293b", hover_color="#334155", height=40, command=self.guardar_datos_embarques
        ).grid(row=10, column=0, columnspan=2, pady=25)

    def crear_vista_notificaciones(self):
        vista = ctk.CTkFrame(self.container, fg_color="transparent")
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_rowconfigure(1, weight=1)
        self.frames_vistas["notificaciones"] = vista

        header = ctk.CTkFrame(vista, fg_color="transparent", height=40)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkButton(header, text="🔄 Actualizar", width=110, command=self.cargar_datos_bandeja, fg_color="#334155").pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(header, text="🗑️ Vaciar Historial", width=140, command=self.vaciar_bandeja_notificaciones, fg_color="#ef4444").pack(side=tk.RIGHT, padx=5)

        tabla_frame = ctk.CTkFrame(vista)
        tabla_frame.grid(row=1, column=0, sticky="nsew")
        tabla_frame.grid_columnconfigure(0, weight=1)
        tabla_frame.grid_rowconfigure(0, weight=1)

        cols_noti = ['Fecha/Hora', 'Área / Origen', 'Título', 'Mensaje']
        self.tree_notificaciones = ttk.Treeview(tabla_frame, columns=cols_noti, show='headings', height=20)
        scroll_y = ttk.Scrollbar(tabla_frame, orient=tk.VERTICAL, command=self.tree_notificaciones.yview)
        self.tree_notificaciones.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_notificaciones.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        anchos_noti = {'Fecha/Hora': 160, 'Área / Origen': 140, 'Título': 220, 'Mensaje': 600}
        for col in cols_noti:
            self.tree_notificaciones.heading(col, text=col)
            self.tree_notificaciones.column(col, width=anchos_noti.get(col, 200), anchor=tk.W)
        self.cargar_datos_bandeja()

    def crear_vista_canal(self, canal):
        vista = ctk.CTkFrame(self.container, fg_color="transparent")
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_rowconfigure(1, weight=1)
        self.frames_vistas[canal] = vista

        header = ctk.CTkFrame(vista, fg_color="transparent", height=40)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(header, text=f"Bitácora Oficial: {canal}", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(header, text=f"📊 Exportar [{canal}] a Excel", width=160, command=lambda c=canal: self.exportar_canal_a_excel(c), fg_color="#0284c7").pack(side=tk.RIGHT, padx=5)

        tabla_frame = ctk.CTkFrame(vista)
        tabla_frame.grid(row=1, column=0, sticky="nsew")
        tabla_frame.grid_columnconfigure(0, weight=1)
        tabla_frame.grid_rowconfigure(0, weight=1)

        tree = ttk.Treeview(tabla_frame, columns=self.columnas_oficiales, show='headings', height=20)
        scroll_y = ttk.Scrollbar(tabla_frame, orient=tk.VERTICAL, command=tree.yview)
        scroll_x = ttk.Scrollbar(tabla_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in self.columnas_oficiales:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor=tk.W)

        setattr(self, f"tree_{canal}", tree)

    def registrar_y_mostrar_notificacion(self, tipo_origen, titulo, mensaje):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = self.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notificaciones (fecha_hora, area_origen, titulo, mensaje) VALUES (?, ?, ?, ?)",
                           (timestamp, tipo_origen, titulo, mensaje))
            conn.commit()
            conn.close()
            VentanaToast(self, titulo, mensaje)
            self.cargar_datos_bandeja()
        except Exception as e:
            print("Error notificación BD:", e)

    def cargar_datos_bandeja(self):
        if not hasattr(self, 'tree_notificaciones'): return
        for row in self.tree_notificaciones.get_children(): self.tree_notificaciones.delete(row)
        try:
            conn = self.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT fecha_hora, area_origen, titulo, mensaje FROM notificaciones ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                self.tree_notificaciones.insert("", tk.END, values=row)
        except Exception as e:
            print("Error cargando bandeja BD:", e)

    def vaciar_bandeja_notificaciones(self):
        if messagebox.askyesno("Confirmar", "¿Seguro deseas vaciar todo el historial de notificaciones?"):
            conn = self.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notificaciones")
            conn.commit()
            conn.close()
            self.cargar_datos_bandeja()

    def seleccionar_archivo_guia(self):
        archivo = filedialog.askopenfilename(title="Seleccionar Guía PDF", filetypes=[("Archivos PDF", "*.pdf")])
        if archivo:
            self.archivo_guia_temp = archivo
            self.lbl_ruta_guia.configure(text=os.path.basename(archivo), text_color="green")

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
                messagebox.showerror("Error", "Faltan datos obligatorios.")
                return

            archivo_guia_nombre = "Sin archivo"
            if self.archivo_guia_temp and os.path.exists(self.archivo_guia_temp):
                archivo_guia_nombre = os.path.basename(self.archivo_guia_temp)
                shutil.copy(self.archivo_guia_temp, os.path.join(self.carpeta_guias, archivo_guia_nombre))

            conn = self.obtener_conexion()
            cursor = conn.cursor()
            tabla = f"canal_{canal.lower()}"

            cursor.execute(f"SELECT OV FROM {tabla} WHERE OV = ?", (ov,))
            existe = cursor.fetchone()

            if existe:
                cursor.execute(f"""
                    UPDATE {tabla} SET 
                        Numero_de_pedido = ?, Nombre_del_cliente = ?, Cajas = ?, Bolsas = ?,
                        fecha_de_envio = ?, fecha_de_entrega = ?, ubicacion = ?, nombre_de_la_paqueteria = ?,
                        valor_MXN = ?, Numero_de_guia = ?, Archivo_guia = ?
                    WHERE OV = ?
                """, (pedido, cliente, cajas, bolsas, f_envio, f_entrega, ubicacion, paqueteria, valor, num_guia, archivo_guia_nombre, ov))
            else:
                cursor.execute(f"""
                    INSERT INTO {tabla} (
                        OV, Numero_de_pedido, Nombre_del_cliente, Cajas, Bolsas, fecha_de_envio,
                        fecha_de_entrega, ubicacion, nombre_de_la_paqueteria, valor_MXN, Estatus, Numero_de_guia, Archivo_guia
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'En espera', ?, ?)
                """, (ov, pedido, cliente, cajas, bolsas, f_envio, f_entrega, ubicacion, paqueteria, valor, num_guia, archivo_guia_nombre))

            conn.commit()
            conn.close()

            self.registrar_y_mostrar_notificacion("Área de Logística", "Nueva Captura", f"Canal [{canal}] registró OV: {ov}")
            messagebox.showinfo("Éxito", f"OV {ov} registrada exitosamente en Base de Datos.")
            
            self.entry_ov.delete(0, tk.END)
            self.entry_pedido.delete(0, tk.END)
            self.entry_cliente.delete(0, tk.END)
            self.archivo_guia_temp = ""
            self.lbl_ruta_guia.configure(text="Ningún archivo seleccionado.", text_color="gray")
            self.cargar_datos_todos_canales()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def guardar_datos_embarques(self):
        try:
            canal = self.combo_canal_emb.get().strip()
            ov = self.entry_emb_ov.get().strip()
            h_entrega = self.entry_h_entrega.get().strip()
            q_entrega = self.entry_quien_entrega.get().strip()
            chofer = self.entry_chofer.get().strip()
            f_salida = self.entry_f_salida.get().strip()
            h_salida = self.entry_h_salida.get().strip()
            dias = self.entry_dias_estancia.get().strip()
            nuevo_estatus = self.combo_emb_estatus.get().strip()

            if not ov or not canal:
                messagebox.showerror("Error", "Faltan campos obligatorios.")
                return

            conn = self.obtener_conexion()
            cursor = conn.cursor()
            tabla = f"canal_{canal.lower()}"

            cursor.execute(f"SELECT OV FROM {tabla} WHERE OV = ?", (ov,))
            if not cursor.fetchone():
                conn.close()
                messagebox.showerror("Error", f"La OV {ov} no existe en logística de [{canal}].")
                return

            cursor.execute(f"""
                UPDATE {tabla} SET 
                    horario_entrega = ?, nombre_de_quien_entrega = ?, nombre_de_quien_recibe_chofer = ?,
                    fecha_de_salida = ?, hora_de_salida = ?, dias_de_estancia = ?, Estatus = ?
                WHERE OV = ?
            """, (h_entrega, q_entrega, chofer, f_salida, h_salida, dias, nuevo_estatus, ov))

            conn.commit()
            conn.close()

            self.registrar_y_mostrar_notificacion("Área de Embarques", "Embarque Actualizado", f"Canal [{canal}] - OV: {ov} -> {nuevo_estatus}")
            messagebox.showinfo("Éxito", f"Estatus actualizado a [{nuevo_estatus}].")
            self.entry_emb_ov.delete(0, tk.END)
            self.cargar_datos_todos_canales()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def abrir_ventana_errores(self):
        top = ctk.CTkToplevel(self)
        top.title("Grupo REV | Auditoría de Errores")
        top.geometry("900x450")
        frame = ctk.CTkFrame(top)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        cols = ['Fecha/Hora', 'Origen', 'OV', 'Descripción']
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=16)
        for c in cols: tree.heading(c, text=c)
        
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        try:
            conn = self.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT fecha_hora, origen, ov, descripcion FROM errores ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()
            for r in rows:
                tree.insert("", tk.END, values=r)
        except Exception as e:
            print("Error cargando errores BD:", e)

    def cargar_datos_todos_canales(self):
        try:
            conn = self.obtener_conexion()
            cursor = conn.cursor()
            
            lista_dfs = []
            total_pedidos, espera, camino, entregados = 0, 0, 0, 0

            for canal in self.canales:
                tabla = f"canal_{canal.lower()}"
                cursor.execute(f"SELECT * FROM {tabla}")
                rows = cursor.fetchall()
                cols = [desc[0] for desc in cursor.description]
                
                if rows:
                    df = pd.DataFrame(rows, columns=cols)
                    # Normalizamos columnas para el frontend
                    df.columns = self.columnas_oficiales
                    df.insert(0, 'Canal', canal)
                    lista_dfs.append(df)
                    
                    total_pedidos += len(df)
                    if 'Estatus' in df.columns:
                        espera += len(df[df['Estatus'].str.strip() == 'En espera'])
                        camino += len(df[df['Estatus'].str.strip() == 'En camino'])
                        entregados += len(df[df['Estatus'].str.strip() == 'Entregado'])

                    tree_c = getattr(self, f"tree_{canal}", None)
                    if tree_c:
                        for row in tree_c.get_children(): tree_c.delete(row)
                        for _, row in df.iterrows():
                            tree_c.insert("", tk.END, values=[row.get(col, '') for col in self.columnas_oficiales])

            for row in self.tree_general.get_children(): self.tree_general.delete(row)
            if lista_dfs:
                df_global = pd.concat(lista_dfs, ignore_index=True)
                for _, row in df_global.iterrows():
                    self.tree_general.insert("", tk.END, values=[row.get('Canal', '')] + [row.get(col, '') for col in self.columnas_oficiales])

            self.kpi_total.configure(text=str(total_pedidos))
            self.kpi_espera.configure(text=str(espera))
            self.kpi_camino.configure(text=str(camino))
            self.kpi_entregados.configure(text=str(entregados))
            conn.close()
        except Exception as e:
            print("Error cargando canales BD:", e)

    def exportar_general_a_excel(self):
        try:
            archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
            if not archivo: return
            
            conn = self.obtener_conexion()
            cursor = conn.cursor()
            lista_dfs = []
            for canal in self.canales:
                cursor.execute(f"SELECT * FROM canal_{canal.lower()}")
                rows = cursor.fetchall()
                if rows:
                    cols = [desc[0] for desc in cursor.description]
                    df = pd.DataFrame(rows, columns=cols)
                    df.columns = self.columnas_oficiales
                    df.insert(0, 'Canal', canal)
                    lista_dfs.append(df)
            conn.close()

            if lista_dfs: 
                pd.concat(lista_dfs, ignore_index=True).to_excel(archivo, index=False)
                messagebox.showinfo("Éxito", "Consolidado exportado correctamente a Excel.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def exportar_canal_a_excel(self, canal):
        try:
            archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
            if not archivo: return
            
            conn = self.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM canal_{canal.lower()}")
            rows = cursor.fetchall()
            cols = [desc[0] for desc in cursor.description]
            conn.close()

            if rows:
                df = pd.DataFrame(rows, columns=cols)
                df.columns = self.columnas_oficiales
                df.to_excel(archivo, index=False)
                messagebox.showinfo("Éxito", f"Bitácora {canal} exportada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = AppGrupoREV()
    app.mainloop()