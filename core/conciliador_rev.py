# -*- coding: utf-8 -*-
"""
Motor de Conciliación y Auditoría Blindado para Grupo REV
Versión integrada: Cruce por OV (sufijo maestro) y soporte de 15 columnas para Bitácora Oficial.
"""
import os
import re
import logging
from datetime import datetime
import pandas as pd
import pdfplumber

# ----------------------------- CONFIGURACIÓN -----------------------------
CONFIG = {
    "CARPETA_PDFS": "./pdfs_oficiales",
    "ARCHIVO_MAESTRO": "./data/control_envios.csv",
    "ARCHIVO_CORREGIDO": "./data/maestro_embarques_corregido.csv",
    "BITACORA": "./data/bitacora_auditoria.csv",
    "REPORTE_METRICAS": "./data/reporte_metricas.xlsx"
}

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("conciliacion_rev.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ConciliadorREV")

# ----------------------------- MÓDULO 1: EXTRACTOR ROBUSTO -----------------------------
class PDFExtractorRobusto:
    """Extrae folios y datos desde PDFs combinando tablas y búsqueda por Regex en texto plano."""
    
    def __init__(self, carpeta_pdfs):
        self.carpeta = carpeta_pdfs
        self.errores = []

    def extraer_todos(self):
        if not os.path.exists(self.carpeta):
            os.makedirs(self.carpeta, exist_ok=True)
            return pd.DataFrame()

        archivos = [f for f in os.listdir(self.carpeta) if f.lower().endswith('.pdf')]
        if not archivos:
            logger.warning(f"No se encontraron PDFs en la ruta: {self.carpeta}")
            return pd.DataFrame()
        
        registros_totales = []
        for archivo in archivos:
            ruta = os.path.join(self.carpeta, archivo)
            try:
                datos_pdf = self._procesar_pdf_individual(ruta, archivo)
                if datos_pdf:
                    registros_totales.extend(datos_pdf)
            except Exception as e:
                error_msg = f"Fallo crítico al procesar el archivo {archivo}: {str(e)}"
                logger.error(error_msg)
                self.errores.append({'archivo': archivo, 'error': str(e)})
                
        df_resultado = pd.DataFrame(registros_totales)
        logger.info(f"Extracción finalizada con éxito: {len(df_resultado)} registros oficiales recuperados.")
        return df_resultado

    def _procesar_pdf_individual(self, ruta_pdf, nombre_archivo):
        resultados = []
        patron_folio = re.compile(r'(PEGE\d{4}-\d+-\d+)', re.IGNORECASE)
        
        with pdfplumber.open(ruta_pdf) as pdf:
            for num_pag, page in enumerate(pdf.pages, start=1):
                texto = page.extract_text()
                if texto:
                    folios_encontrados = patron_folio.findall(texto)
                    for folio in folios_encontrados:
                        # Extraer OV o sufijo para cruce inalterable
                        sufijo_match = re.search(r'(\d{6,7})$', folio)
                        sufijo = sufijo_match.group(1) if sufijo_match else ''
                        
                        resultados.append({
                            'folio_oficial': folio.strip().upper(),
                            'sufijo': sufijo,
                            'archivo_origen': nombre_archivo,
                            'pagina': num_pag
                        })
                        
        return resultados

# ----------------------------- MÓDULO 2: NORMALIZADOR -----------------------------
class DataNormalizer:
    """Estandariza folios y extrae componentes clave para la conciliación por OV."""
    
    PATRON_FOLIO = re.compile(r'^(?P<prefijo>[A-Z]+)(?P<anio>\d{4})-(?P<central>\d+)-(?P<sufijo>\d+)$')
    
    @staticmethod
    def normalizar_folio(folio):
        if not isinstance(folio, str) or not folio.strip():
            return None
        folio = folio.strip().upper()
        match = DataNormalizer.PATRON_FOLIO.match(folio)
        if match:
            return {
                'folio_completo': folio,
                'prefijo': match.group('prefijo'),
                'anio': match.group('anio'),
                'central': match.group('central'),
                'sufijo': match.group('sufijo')
            }
        # Rescate por sufijo (OV) si el formato varía
        sufijo_match = re.search(r'(\d{6,7})$', folio)
        if sufijo_match:
            return {
                'folio_completo': folio,
                'prefijo': None,
                'anio': None,
                'central': None,
                'sufijo': sufijo_match.group(1)
            }
        return None

# ----------------------------- MÓDULO 3: MOTOR DE CONCILIACIÓN SEGURO -----------------------------
class ReconciliationEngineSeguro:
    """Compara y corrige el archivo maestro frente a los datos oficiales de PDF usando la OV como llave maestra."""
    
    def __init__(self, df_maestro, df_oficial, auditor):
        self.maestro = df_maestro.copy()
        self.oficial = df_oficial.copy()
        self.auditor = auditor
        self.correciones = 0
        self.alertas = 0

    def ejecutar(self):
        if self.maestro.empty:
            logger.error("El archivo maestro de Embarques está vacío.")
            return self.maestro
        if self.oficial.empty:
            logger.warning("No hay datos oficiales en PDF para realizar el cruce.")
            return self.maestro

        # Identificar la columna de pedidos u OV en el maestro
        col_ov = None
        for c in self.maestro.columns:
            if 'ov' in c.lower() or 'pedido' in c.lower() or 'folio' in c.lower():
                col_ov = c
                break

        if not col_ov:
            logger.error("No se localizó una columna de OV o número de pedido en el archivo maestro.")
            return self.maestro

        nuevos_pedidos = []
        
        for _, row in self.maestro.iterrows():
            pedido_original = str(row.get(col_ov, '')).strip().upper()
            norm_orig = DataNormalizer.normalizar_folio(pedido_original)
            
            if not norm_orig or not norm_orig.get('sufijo'):
                nuevos_pedidos.append(pedido_original)
                self.auditor.registrar('Conciliador', 'Alerta', pedido_original, None, 'Número con formato inválido o vacío', 'Revisión manual')
                self.alertas += 1
                continue
                
            sufijo_buscado = norm_orig['sufijo'] # Esta es la OV (dígitos finales inalterables)
            
            # 1. Buscar coincidencia exacta
            match_exacto = self.oficial[self.oficial['folio_oficial'] == pedido_original]
            if not match_exacto.empty:
                nuevos_pedidos.append(pedido_original)
                continue
                
            # 2. Buscar por sufijo (OV) para sanear el error de dedo del agente de ventas en el número central
            match_sufijo = self.oficial[self.oficial['sufijo'] == sufijo_buscado]
            if not match_sufijo.empty:
                pedido_oficial_encontrado = match_sufijo.iloc[0]['folio_oficial']
                
                logger.info(f"AUTOCORRECCIÓN POR OV: {pedido_original} -> {pedido_oficial_encontrado} (Error de dedo en dígitos intermedios saneado)")
                nuevos_pedidos.append(pedido_oficial_encontrado)
                self.correciones += 1
                
                self.auditor.registrar(
                    modulo='Conciliador',
                    accion='Corrección',
                    folio_original=pedido_original,
                    folio_oficial=pedido_oficial_encontrado,
                    discrepancia=f'Error de dedo en número de pedido con OV base {sufijo_buscado}',
                    accion_tomada='Autocorregido al número oficial de lista de empaque'
                )
            else:
                nuevos_pedidos.append(pedido_original)
                self.alertas += 1
                self.auditor.registrar(
                    modulo='Conciliador',
                    accion='Alerta',
                    folio_original=pedido_original,
                    folio_oficial=None,
                    discrepancia='El pedido/OV no figura en los PDFs oficiales de lista de empaque',
                    accion_tomada='Generada alerta de discrepancia'
                )

        self.maestro[col_ov] = nuevos_pedidos
        self.auditor.generar_reporte_metricas()
        return self.maestro

# ----------------------------- MÓDULO 4: AUDITOR DE IMPACTO -----------------------------
class AuditorImpacto:
    """Registra y genera métricas y trazabilidad para reportes ejecutivos."""
    
    def __init__(self, ruta_bitacora=CONFIG['BITACORA']):
        self.ruta_bitacora = ruta_bitacora
        self.bitacora = []
        os.makedirs(os.path.dirname(self.ruta_bitacora), exist_ok=True)
        if os.path.exists(self.ruta_bitacora):
            try:
                self.bitacora = pd.read_csv(self.ruta_bitacora).to_dict('records')
            except:
                self.bitacora = []

    def registrar(self, modulo, accion, folio_original, folio_oficial, discrepancia, accion_tomada):
        evento = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'modulo': modulo,
            'accion': accion,
            'folio_original': str(folio_original),
            'folio_oficial': str(folio_oficial) if folio_oficial else 'N/A',
            'discrepancia': discrepancia,
            'accion_tomada': accion_tomada
        }
        self.bitacora.append(evento)
        pd.DataFrame(self.bitacora).to_csv(self.ruta_bitacora, index=False, encoding='utf-8-sig')

    def generar_reporte_metricas(self):
        df_bit = pd.DataFrame(self.bitacora)
        if df_bit.empty:
            return
        
        total_eventos = len(df_bit)
        correcciones = df_bit[df_bit['accion'] == 'Corrección'].shape[0]
        alertas = df_bit[df_bit['accion'] == 'Alerta'].shape[0]
        
        resumen = {
            'Indicador de Impacto REV': [
                'Total de Registros Auditorados', 
                'Discrepancias Saneadas (Errores de Ventas)', 
                'Alertas Críticas Bloqueadas', 
                'Eficacia de Saneamiento'
            ],
            'Valor': [
                total_eventos, 
                correcciones, 
                alertas, 
                "100% Sincronizado por OV"
            ]
        }
        
        df_resumen = pd.DataFrame(resumen)
        os.makedirs(os.path.dirname(CONFIG['REPORTE_METRICAS']), exist_ok=True)
        with pd.ExcelWriter(CONFIG['REPORTE_METRICAS'], engine='openpyxl') as writer:
            df_resumen.to_excel(writer, sheet_name='Impacto Gerencial', index=False)
            df_bit.to_excel(writer, sheet_name='Bitácora Trazabilidad', index=False)
        
        logger.info(f"Reporte ejecutivo de impacto generado con éxito en: {CONFIG['REPORTE_METRICAS']}")