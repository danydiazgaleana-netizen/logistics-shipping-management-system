import pandas as pd
import os

def cargar_y_validar_datos(ruta_csv):
    """
    Valida, limpia y estandariza el maestro de embarques antes de procesarlo.
    Normaliza los nombres de las columnas para evitar errores de coincidencia.
    """
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"Error crítico: No se encontró el archivo en la ruta {ruta_csv}")
    
    try:
        df = pd.read_csv(ruta_csv)
    except Exception as e:
        raise IOError(f"Error al leer el archivo CSV: {e}")
    
    # Normalizar nombres de columnas: quitar espacios y convertir a minúsculas para un mapeo seguro
    df.columns = df.columns.str.strip()
    
    # Diccionario para renombrar columnas variantes a un estándar unificado en el script
    mapeo_columnas = {
        'dias de estancia': 'Estancia (Días)',
        'estancia (días)': 'Estancia (Días)',
        'valor ($mxn)': 'Valor (MXN)',
        'valor (mxn)': 'Valor (MXN)',
        'nombre de la paqueteria': 'Paquetería',
        'paquetería': 'Paquetería',
        'paqueteria': 'Paquetería',
        'ubicacion': 'Ubicación',
        'ubicación': 'Ubicación'
    }
    
    # Renombrar columnas si coinciden (ignorando mayúsculas/minúsculas del CSV original)
    df = df.rename(columns={col: mapeo_columnas[col.lower()] for col in df.columns if col.lower() in mapeo_columnas})
    
    # Limpieza de espacios en columnas de texto principales
    columnas_texto = ['Cliente', 'Ubicación', 'Paquetería', 'Guía']
    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Forzar tipado numérico para evitar errores en cálculos
    columnas_numericas = ['Cajas', 'Bolsas', 'Valor (MXN)', 'Estancia (Días)']
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
    return df

def predecir_riesgo_retraso(df):
    """
    Motor analítico predictivo: Evalúa la estancia actual y la paquetería 
    para anticipar un riesgo potencial de retraso o cuello de botella.
    """
    print("\n--- MOTOR DE ANÁLISIS PREDICTIVO (RIESGO DE RETRASO) ---")
    
    condicion_riesgo = (df['Estancia (Días)'] >= 2.0) | (df['Paquetería'] == 'Estafeta')
    
    df['Riesgo_Prediccion'] = 'Bajo'
    df.loc[condicion_riesgo, 'Riesgo_Prediccion'] = 'Alto (Posible Cuello de Botella)'
    
    for index, row in df.iterrows():
        # Validar si las columnas existen antes de imprimirlas para evitar fallos de despliegue
        dest = row.get('Ubicación', 'N/D')
        paq = row.get('Paquetería', 'N/D')
        ov = row.get('OV', f"Fila {index}")
        print(f"OV: {ov} | Destino: {dest} | Paquetería: {paq} -> Alerta: {row['Riesgo_Prediccion']}")
        
    return df

def analizar_embarques(ruta_csv):
    # 1. Cargar y validar usando la función robusta con mapeo automático
    df = cargar_y_validar_datos(ruta_csv)
    
    print("--- REPORTE DE ANALÍTICA DE EMBARQUES ---")
    print(f"Total de embarques procesados: {len(df)}\n")
    
    # 2. Promedio de días de estancia
    promedio_estancia = df['Estancia (Días)'].mean()
    print(f"⏱️ Promedio de días de estancia: {promedio_estancia:.2f} días")
    
    # 3. Valor total de la mercancía en tránsito
    valor_total = df['Valor (MXN)'].sum()
    print(f"💰 Valor total de la mercancía: ${valor_total:,.2f} MXN")
    
    # 4. Distribución de carga por paquetería
    print("\n📦 Volumen de envíos por Paquetería:")
    conteo_paqueterias = df['Paquetería'].value_counts()
    for paqueteria, cantidad in conteo_paqueterias.items():
        print(f"   - {paqueteria}: {cantidad} embarque(s)")
        
    # 5. Resumen por ubicación de destino
    print("\n📍 Destinos principales:")
    conteo_destinos = df['Ubicación'].value_counts()
    for destino, cantidad in conteo_destinos.items():
        print(f"   - {destino}: {cantidad} envío(s)")
        
    # 6. Ejecutar el motor predictivo integrado
    predecir_riesgo_retraso(df)

if __name__ == "__main__":
    archivo_maestro = "data/maestro_embarques_dummy.csv"
    analizar_embarques(archivo_maestro)