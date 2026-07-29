import os
import pandas as pd
from datetime import datetime
import shutil

class GestorLogisticaBackend:
    def __init__(self):
        self.carpeta_datos = "./data"
        self.carpeta_guias = "./guias_maestras"
        
        os.makedirs(self.carpeta_datos, exist_ok=True)
        os.makedirs(self.carpeta_guias, exist_ok=True)

        self.canales = ["VL", "PEGE", "TIAU", "MUESTRAS", "AMAZON", "MH"]
        self.columnas_oficiales = [
            'OV', 'Numero de pedido', 'Nombre del cliente', 'Cajas', 'Bolsas',
            'fecha de envio', 'fecha de entrega', 'ubicacion', 'horario entrega',
            'nombre de quien entrega', 'nombre de la paqueteria',
            'nombre de quien recibe (chofer)', 'fecha de salida', 'hora de salida',
            'valor ($MXN)', 'dias de estancia', 'Estatus', 'Numero de guia', 'Archivo guia'
        ]

    def obtener_ruta_csv(self, canal: str) -> str:
        return os.path.join(self.carpeta_datos, f"maestro_embarques_{canal.lower()}.csv")

    def guardar_logistica(self, canal: str, datos: dict, archivo_guia_path: str = "") -> tuple[bool, str]:
        try:
            ov = datos.get('OV', '').strip()
            if not ov or not datos.get('Nombre del cliente', '').strip():
                return False, "Faltan datos obligatorios (OV o Cliente)."

            archivo_guia_nombre = "Sin archivo"
            if archivo_guia_path and os.path.exists(archivo_guia_path):
                archivo_guia_nombre = os.path.basename(archivo_guia_path)
                shutil.copy(archivo_guia_path, os.path.join(self.carpeta_guias, archivo_guia_nombre))

            ruta_csv = self.obtener_ruta_csv(canal)
            if os.path.exists(ruta_csv):
                df = pd.read_csv(ruta_csv, dtype=str)
                for col in self.columnas_oficiales:
                    if col not in df.columns:
                        df[col] = ""
            else:
                df = pd.DataFrame(columns=self.columnas_oficiales)

            df = df[df['OV'].astype(str).str.lower() != 'nan']

            if not df.empty and ov in df['OV'].astype(str).values:
                for k, v in datos.items():
                    if v:
                        df.loc[df['OV'].astype(str) == ov, k] = v
                
                if archivo_guia_path:
                    df.loc[df['OV'].astype(str) == ov, 'Archivo guia'] = archivo_guia_nombre

                estatus_actual = df.loc[df['OV'].astype(str) == ov, 'Estatus']
                if estatus_actual.empty or not estatus_actual.values[0]:
                    df.loc[df['OV'].astype(str) == ov, 'Estatus'] = 'En espera'
            else:
                nueva_fila = {col: "" for col in self.columnas_oficiales}
                nueva_fila.update(datos)
                nueva_fila['Estatus'] = 'En espera'
                nueva_fila['Archivo guia'] = archivo_guia_nombre
                df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

            df.to_csv(ruta_csv, index=False, encoding='utf-8-sig')
            return True, f"OV {ov} registrada exitosamente."
        except Exception as e:
            return False, str(e)