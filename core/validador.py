import os
import pandas as pd
from datetime import datetime
from core.lector_pdf import extraer_ids_desde_pdf
from core.modelos import ResultadoValidacion

RUTA_CONTROL = 'data/control_envios.csv'
RUTA_AUDITORIA = 'data/auditoria_errores.csv'

def procesar_validacion(id_orden_input: str, numero_pedido_input: str, cliente: str, cajas: int, bolsas: int, pdf_path: str, usuario: str) -> ResultadoValidacion:
    pares = extraer_ids_desde_pdf(pdf_path)
    
    # Extraemos listas de los PDFs oficiales
    pedidos_en_pdf = [p[0] for p in pares if p[0]]
    ovs_en_pdf = [p[1] for p in pares]
    
    id_orden_input = str(id_orden_input).strip().upper()
    numero_pedido_input = str(numero_pedido_input).strip().upper()
    
    # Validaciones cruzadas para encontrar la discrepancia exacta
    ov_coincide = id_orden_input in ovs_en_pdf or any(id_orden_input in p for p in pedidos_en_pdf)
    pedido_completo_coincide = numero_pedido_input in pedidos_en_pdf
    
    trace_id = f"ADU-{datetime.now().strftime('%Y%m%d%H%M%S')}-{id_orden_input[:4]}"
    
    if pedido_completo_coincide and ov_coincide:
        mensaje = "✅ VALIDADO: Coincide número de pedido y OV con la lista de empaque."
        sugerencia = "Proceder con el embarque sin problemas."
        detalles = f"Pedido '{numero_pedido_input}' verificado correctamente."
        validado = True
        guardar_csv(RUTA_CONTROL, [numero_pedido_input, id_orden_input, cliente, cajas, bolsas, "VALIDADO", datetime.now().strftime('%Y-%m-%d %H:%M'), usuario])
        
    elif ov_coincide and not pedido_completo_coincide:
        # ¡Aquí detectamos el problema principal de discrepancia de base de datos!
        mensaje = "⚠️ DISCREPANCIA DETECTADA: La OV coincide, pero el Número de Pedido difiere del PDF."
        sugerencia = "Revisar base de datos de Embarques vs Logística (El código central no coincide)."
        detalles = f"En base de datos tienes '{numero_pedido_input}', pero el PDF oficial exige otra codificación."
        validado = False
        guardar_csv(RUTA_AUDITORIA, [numero_pedido_input, id_orden_input, cliente, cajas, bolsas, "RECHAZADO_DISCREPANCIA_PEDIDO", datetime.now().strftime('%Y-%m-%d %H:%M'), usuario])
        
    else:
        mensaje = "❌ RECHAZADO: El ID o número de pedido no figura en el documento oficial."
        sugerencia = "Verificar folio o reasignar documento PDF correcto."
        detalles = f"Ninguna coincidencia para '{numero_pedido_input}' en el archivo."
        validado = False
        guardar_csv(RUTA_AUDITORIA, [numero_pedido_input, id_orden_input, cliente, cajas, bolsas, "RECHAZADO_AUSENTE", datetime.now().strftime('%Y-%m-%d %H:%M'), usuario])
        
    return ResultadoValidacion(exito=True, validado=validado, id_orden=numero_pedido_input, mensaje=mensaje, sugerencia=sugerencia, detalles=detalles, trace_id=trace_id)

def guardar_csv(ruta: str, fila: list):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    existe = os.path.exists(ruta)
    df = pd.DataFrame([fila], columns=['Numero_Pedido', 'OV', 'Cliente', 'Cajas', 'Bolsas', 'Estatus', 'Fecha_Hora', 'Usuario'])
    df.to_csv(ruta, mode='a', header=not existe, index=False, encoding='utf-8')

def indexar_pdfs(carpeta_pdfs: str) -> dict:
    indice = {}
    if not os.path.exists(carpeta_pdfs):
        return indice
    for archivo in os.listdir(carpeta_pdfs):
        if archivo.lower().endswith('.pdf'):
            ruta = os.path.join(carpeta_pdfs, archivo)
            try:
                pares = extraer_ids_desde_pdf(ruta)
                for pedido_comp, ov in pares:
                    if pedido_comp and pedido_comp not in indice:
                        indice[pedido_comp] = ruta
                    if ov and ov not in indice:
                        indice[ov] = ruta
            except Exception as e:
                print(f"Error al leer {archivo}: {e}")
    return indice

def procesar_lote_con_indice(carpeta_pdfs: str, archivo_entrada: str, usuario: str = 'operador'):
    indice = indexar_pdfs(carpeta_pdfs)
    df_entrada = pd.read_csv(archivo_entrada, encoding='utf-8')
    resultados = []
    
    for idx, row in df_entrada.iterrows():
        id_orden = str(row['OV']).strip().upper()
        num_pedido = str(row['Numero_de_Pedido']).strip().upper()
        
        # Buscar por pedido completo o por OV en el índice
        pdf_path = None
        if num_pedido in indice:
            pdf_path = indice[num_pedido]
        elif id_orden in indice:
            pdf_path = indice[id_orden]
            
        if pdf_path:
            resultado = procesar_validacion(
                id_orden_input=id_orden,
                numero_pedido_input=num_pedido,
                cliente=str(row['Nombre_del_Pedido']),
                cajas=int(row['Caja']),
                bolsas=0,
                pdf_path=pdf_path,
                usuario=usuario
            )
        else:
            resultado = ResultadoValidacion(
                exito=True,
                validado=False,
                id_orden=num_pedido,
                mensaje="❌ RECHAZADO: Pedido no encontrado en la carpeta de PDFs oficiales.",
                sugerencia="Agregue el PDF correspondiente a la carpeta de listas oficiales.",
                detalles=f"No se encontró el pedido '{num_pedido}' ni la OV '{id_orden}'.",
                trace_id=f"ADU-{datetime.now().strftime('%Y%m%d%H%M%S')}-{id_orden[:4]}"
            )
        resultados.append(resultado)
    return resultados, indice