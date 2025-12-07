class Asset:
    def __init__(self, simbolo, titulo, cantidad, precio_actual, importe_total, dividendos, tipo_activo, broker):
        self.simbolo = simbolo
        self.titulo = titulo
        self.cantidad = cantidad
        self.precio_actual = precio_actual
        self.importe_total = importe_total
        self.dividendos = dividendos
        self.tipo_activo = tipo_activo
        self.broker = broker

    def to_dict(self):
        return {
            "símbolo": self.simbolo,
            "título": self.titulo,
            "cantidad": self.cantidad,
            "precio_actual": self.precio_actual,
            "importe_total": self.importe_total,
            "dividendos": self.dividendos,
            "tipo_activo": self.tipo_activo,
            "broker": self.broker,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["símbolo"],
            data["título"],
            data["cantidad"],
            data["precio_actual"],
            data["importe_total"],
            data["dividendos"],
            data["tipo_activo"],
            data["broker"],
        )
