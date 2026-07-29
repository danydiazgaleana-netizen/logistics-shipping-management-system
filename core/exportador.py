import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import os

def exportar_a_excel(ruta_control: str, ruta_auditoria: str, ruta_salida: str):
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Control_Envios"
    
    if os.path.exists(ruta_control) and os.path.getsize(ruta_control) > 0:
        df_control = pd.read_csv(ruta_control, encoding='utf-8')
        for r in dataframe_to_rows(df_control, index=False, header=True):
            ws1.append(r)
            
    if os.path.exists(ruta_auditoria) and os.path.getsize(ruta_auditoria) > 0:
        df_auditoria = pd.read_csv(ruta_auditoria, encoding='utf-8')
        ws2 = wb.create_sheet("Auditoria_Errores")
        for r in dataframe_to_rows(df_auditoria, index=False, header=True):
            ws2.append(r)
            
    wb.save(ruta_salida)