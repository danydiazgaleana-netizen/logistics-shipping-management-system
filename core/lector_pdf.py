import pdfplumber
import re
from typing import List, Tuple

def extraer_ids_desde_pdf(ruta_pdf: str) -> List[Tuple[str, str]]:
    # Patrón robusto para capturar folios completos tipo PEGE2026-496-2003267 o similares
    patron_pedido_completo = re.compile(r'PEGE\d{4}-\d{3}-\d{7}', re.IGNORECASE)
    patron_ov = re.compile(r'\b(\d{7})\b')
    
    resultados = []
    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue
            
            # Buscar coincidencias exactas del pedido completo en el texto del PDF
            pedidos_encontrados = patron_pedido_completo.findall(texto)
            for pedido_completo in pedidos_encontrados:
                # Extraer también la OV de 7 dígitos del final para cruce secundario
                match_ov = patron_ov.search(pedido_completo)
                ov = match_ov.group(1) if match_ov else ""
                
                if (pedido_completo, ov) not in resultados:
                    resultados.append((pedido_completo.upper(), ov))
                    
            # Respaldo por si el PDF solo muestra la OV suelta
            if not pedidos_encontrados:
                for linea in texto.split('\n'):
                    match_ov = patron_ov.search(linea)
                    if match_ov:
                        ov = match_ov.group(1)
                        if ("", ov) not in resultados:
                            resultados.append(("", ov))
                            
    return resultados