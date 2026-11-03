"""Constantes de dominio del sistema de control de gastos."""

CATEGORIA_SIN_CATEGORIZAR = "Sin Categorizar"
COLOR_SIN_CATEGORIZAR = "#6B7280"

METODOS_PAGO: list[str] = [
    "Efectivo",
    "Tarjeta de débito",
    "Tarjeta de crédito",
    "QR",
    "Transferencia",
    "Otros",
]

MONEDA_POR_DEFECTO = "BOB"

MAX_DESCORIPCION = 255
MAX_METODO_PAGO = 50
MAX_PALABRA_CLAVE = 100
MAX_NOMBRE_CATEGORIA = 100

COLOR_HEX_PATTERN = r"^#[0-9A-Fa-f]{6}$"
