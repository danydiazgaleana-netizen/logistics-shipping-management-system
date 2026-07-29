class GestorLogisticaBackend:
    def __init__(self):
        self.canales = ["VL", "FCL", "LCL", "Aéreo", "Terrestre Nacional"]
        self.registros = []

    def guardar_logistica(self, canal, datos):
        ov = datos.get('OV', '').strip()
        cliente = datos.get('Nombre del cliente', '').strip()

        if not ov:
            return False, "El campo 'Orden de Venta (OV)' no puede estar vacío."
        
        if not cliente:
            return False, "El campo 'Nombre del Cliente' no puede estar vacío."

        if canal not in self.canales:
            return False, f"El canal seleccionado '{canal}' no es válido."

        for registro in self.registros:
            if registro.get('OV') == ov:
                return False, f"La Orden de Venta (OV) '{ov}' ya se encuentra registrada."

        nuevo_registro = {
            'OV': ov,
            'Nombre del cliente': cliente,
            'Canal': canal,
            'Estatus': 'Capturado y Validado'
        }

        self.registros.append(nuevo_registro)
        return True, f"Registro logístico con OV '{ov}' guardado exitosamente."

    def obtener_registros(self):
        return self.registros