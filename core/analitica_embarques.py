import pandas as pd

def analizar_embarques(ruta_csv):
    # Cargar el archivo CSV
    df = pd.read_csv(ruta_csv)
    
    print("--- REPORTE DE ANALÍTICA DE EMBARQUES ---")
    print(f"Total de embarques procesados: {len(df)}\n")
    
    # 1. Promedio de días de estancia (Lead Time de almacén)
    promedio_estancia = df['dias de estancia'].mean()
    print(f"⏱️ Promedio de días de estancia: {promedio_estancia:.2f} días")
    
    # 2. Valor total de la mercancía en tránsito
    valor_total = df['valor ($MXN)'].sum()
    print(f"💰 Valor total de la mercancía: ${valor_total:,.2f} MXN")
    
    # 3. Distribución de carga por paquetería
    print("\n📦 Volumen de envíos por Paquetería:")
    conteo_paqueterias = df['nombre de la paqueteria'].value_counts()
    for paqueteria, cantidad in conteo_paqueterias.items():
        print(f"   - {paqueteria}: {cantidad} embarque(s)")
        
    # 4. Resumen por ubicación de destino
    print("\n📍 Destinos principales:")
    conteo_destinos = df['ubicacion'].value_counts()
    for destino, cantidad in conteo_destinos.items():
        print(f"   - {destino}: {cantidad} envío(s)")

if __name__ == "__main__":
    # Ruta del archivo dummy que subimos a GitHub
    archivo_maestro = "data/maestro_embarques_dummy.csv"
    analizar_embarques(archivo_maestro)

    import pandas as pd

def predecir_riesgo_retraso(df):
    """
    Función predictiva básica: Evalúa la estancia actual y la paquetería 
    para anticipar un riesgo potencial de retraso en la entrega.
    """
    print("\n--- MOTOR DE ANÁLISIS PREDICTIVO (RIESGO DE RETRASO) ---")
    
    # Criterio predictivo de ejemplo: 
    # Si la estancia registrada es >= 2 días o si ciertos destinos superan el umbral
    condicion_riesgo = (df['Estancia (Días)'] >= 2.0) | (df['Paquetería'] == 'Estafeta')
    
    df['Riesgo_予測'] = 'Bajo'
    df.loc[condicion_riesgo, 'Riesgo_予測'] = 'Alto (Posible Cuello de Botella)'
    
    for index, row in df.iterrows():
        print(f"OV: {row['OV']} | Destino: {row['Ubicación']} | Paquetería: {row['Paquetería']} -> Alerta: {row['Riesgo_予測']}")
        
    return df