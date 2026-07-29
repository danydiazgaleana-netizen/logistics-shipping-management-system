from dataclasses import dataclass

@dataclass
class ResultadoValidacion:
    exito: bool
    validado: bool
    id_orden: str
    mensaje: str
    sugerencia: str
    detalles: str
    trace_id: str