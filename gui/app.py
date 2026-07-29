import sys
import os

# Configuración segura para encontrar la lógica de negocio en la raíz
try:
    from logica_negocio import GestorLogisticaBackend  # type: ignore
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from logica_negocio import GestorLogisticaBackend  # type: ignore

import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AppGrupoREV(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.backend = GestorLogisticaBackend()
        
        self.title("Grupo REV | Red de Datos Implacable - Logística y Embarques")
        self.geometry("1200x750")
        
        # Sistema de Pestañas Principal
        self.tabview = ctk.CTkTabview(self, width=1150, height=680)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.tab_logistica = self.tabview.add("📦 Captura Logística")
        self.tab_embarques = self.tabview.add("🚚 Validación de Embarques")
        self.tab_bitacora = self.tabview.add("📋 Bitácora General")

        self.inicializar_vista_logistica()
        self.inicializar_vista_embarques()
        self.inicializar_vista_bitacora()

    def inicializar_vista_logistica(self):
        lbl_titulo = ctk.CTkLabel(self.tab_logistica, text="Ingreso Logístico Oficial", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_titulo.pack(pady=15)

        self.frame_form = ctk.CTkFrame(self.tab_logistica)
        self.frame_form.pack(padx=20, pady=10, fill="x")

        # Campo OV
        self.lbl_ov = ctk.CTkLabel(self.frame_form, text="Orden de Venta (OV):", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_ov.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.entry_ov = ctk.CTkEntry(self.frame_form, width=300, placeholder_text="Ej. 54892")
        self.entry_ov.grid(row=0, column=1, padx=15, pady=10, sticky="w")

        # Campo Cliente
        self.lbl_cliente = ctk.CTkLabel(self.frame_form, text="Nombre del Cliente:", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_cliente.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.entry_cliente = ctk.CTkEntry(self.frame_form, width=300, placeholder_text="Empresa o Cliente Final")
        self.entry_cliente.grid(row=1, column=1, padx=15, pady=10, sticky="w")

        # Canal de Distribución
        self.lbl_canal = ctk.CTkLabel(self.frame_form, text="Canal de Distribución:", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_canal.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        
        self.combo_canal = ctk.CTkComboBox(self.frame_form, values=self.backend.canales, width=300)
        self.combo_canal.grid(row=2, column=1, padx=15, pady=10, sticky="w")
        self.combo_canal.set("VL")

        # Botón de Guardado
        self.btn_guardar = ctk.CTkButton(
            self.tab_logistica, 
            text="💾 Guardar Registro Logístico", 
            command=self.ejecutar_guardado_logistica, 
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_guardar.pack(pady=25)

    def inicializar_vista_embarques(self):
        lbl_titulo = ctk.CTkLabel(self.tab_embarques, text="Módulo de Validación de Embarques", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_titulo.pack(pady=15)

        # Panel de control de embarques
        self.frame_embarques = ctk.CTkFrame(self.tab_embarques)
        self.frame_embarques.pack(padx=20, pady=10, fill="both", expand=True)

        lbl_instruccion = ctk.CTkLabel(self.frame_embarques, text="Gestión y estatus operativo de salidas en curso:", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_instruccion.pack(padx=20, pady=15, anchor="w")

        self.btn_actualizar_emb = ctk.CTkButton(
            self.frame_embarques, 
            text="🔄 Verificar Órdenes Pendientes", 
            command=self.actualizar_embarques,
            fg_color="#0284c7"
        )
        self.btn_actualizar_emb.pack(padx=20, pady=10, anchor="w")

        self.txt_embarques = ctk.CTkTextbox(self.frame_embarques, width=1050, height=400)
        self.txt_embarques.pack(padx=20, pady=10)
        self.txt_embarques.insert("0.0", "No hay embarques pendientes de validación en este momento.\n")
        self.txt_embarques.configure(state="disabled")

    def inicializar_vista_bitacora(self):
        lbl_titulo = ctk.CTkLabel(self.tab_bitacora, text="Bitácora y Reportes Generales", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_titulo.pack(pady=15)

        self.frame_bitacora = ctk.CTkFrame(self.tab_bitacora)
        self.frame_bitacora.pack(padx=20, pady=10, fill="both", expand=True)

        self.btn_refrescar_bitacora = ctk.CTkButton(
            self.frame_bitacora, 
            text="📊 Cargar Registros de Bitácora", 
            command=self.refrescar_bitacora,
            fg_color="#0284c7"
        )
        self.btn_refrescar_bitacora.pack(padx=20, pady=15, anchor="w")

        self.txt_bitacora = ctk.CTkTextbox(self.frame_bitacora, width=1050, height=400)
        self.txt_bitacora.pack(padx=20, pady=10)
        self.txt_bitacora.insert("0.0", "Haga clic en 'Cargar Registros de Bitácora' para visualizar la información acumulada.\n")
        self.txt_bitacora.configure(state="disabled")

    def ejecutar_guardado_logistica(self):
        ov = self.entry_ov.get().strip()
        cliente = self.entry_cliente.get().strip()
        canal_seleccionado = self.combo_canal.get()
        
        datos = {
            'OV': ov,
            'Nombre del cliente': cliente
        }

        exito, mensaje = self.backend.guardar_logistica(canal_seleccionado, datos)
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.entry_ov.delete(0, 'end')
            self.entry_cliente.delete(0, 'end')
        else:
            messagebox.showerror("Error", mensaje)

    def actualizar_embarques(self):
        registros = self.backend.obtener_registros()
        self.txt_embarques.configure(state="normal")
        self.txt_embarques.delete("0.0", "end")
        
        if not registros:
            self.txt_embarques.insert("0.0", "No hay registros logísticos activos para validar embarques.")
        else:
            texto = "--- Órdenes Listas para Validación de Salida ---\n\n"
            for r in registros:
                texto += f"• OV: {r['OV']} | Cliente: {r['Nombre del cliente']} | Canal: {r['Canal']} | Estatus: {r['Estatus']}\n"
            self.txt_embarques.insert("0.0", texto)
        
        self.txt_embarques.configure(state="disabled")

    def refrescar_bitacora(self):
        registros = self.backend.obtener_registros()
        self.txt_bitacora.configure(state="normal")
        self.txt_bitacora.delete("0.0", "end")
        
        if not registros:
            self.txt_bitacora.insert("0.0", "La bitácora general se encuentra vacía actualmente.")
        else:
            texto = f"Total de registros históricos: {len(registros)}\n\n"
            for idx, r in enumerate(registros, 1):
                texto += f"{idx}. [OV: {r['OV']}] Cliente: {r['Nombre del cliente']} | Canal: {r['Canal']} | Estatus: {r['Estatus']}\n"
            self.txt_bitacora.insert("0.0", texto)
        
        self.txt_bitacora.configure(state="disabled")

if __name__ == "__main__":
    app = AppGrupoREV()
    app.mainloop()