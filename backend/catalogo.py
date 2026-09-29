"""Campos predeterminados (el negocio puede agregar categorías desde Flet)."""


def campo(clave, etiqueta, tipo='texto', ayuda='', opciones=None):
    return {'clave': clave, 'etiqueta': etiqueta, 'tipo': tipo,
            'ayuda': ayuda, 'opciones': opciones or []}


CABLES = [
    campo('seccion_mm2', 'Sección (mm²)', 'numero', 'Ej.: 2.5'),
    campo('tipo_cable', 'Tipo de cable', 'opcion', opciones=['Unipolar', 'Multipolar', 'Taller', 'Subterráneo', 'Otro']),
    campo('color', 'Color', 'texto', 'Ej.: Rojo'),
    campo('material', 'Conductor', 'opcion', opciones=['Cobre', 'Aluminio', 'Otro']),
]
TERMICAS = [
    campo('corriente_a', 'Corriente nominal (A)', 'numero', 'Ej.: 20'),
    campo('polos', 'Número de polos', 'opcion', opciones=['1P', '2P', '3P', '4P']),
    campo('curva', 'Curva', 'opcion', opciones=['B', 'C', 'D', 'Otra']),
    campo('poder_corte_ka', 'Poder de corte (kA)', 'numero', 'Ej.: 6'),
    campo('tension_v', 'Tensión nominal (V)', 'texto', 'Ej.: 230/400'),
]
DIFERENCIALES = [
    campo('corriente_a', 'Corriente nominal (A)', 'numero', 'Ej.: 40'),
    campo('sensibilidad_ma', 'Sensibilidad (mA)', 'numero', 'Ej.: 30'),
    campo('polos', 'Número de polos', 'opcion', opciones=['2P', '4P']),
    campo('tipo', 'Tipo', 'opcion', opciones=['AC', 'A', 'F', 'B', 'Otro']),
]
LEDS = [
    campo('potencia_w', 'Potencia (W)', 'numero', 'Ej.: 12'),
    campo('tension_v', 'Tensión nominal (V)', 'texto', 'Ej.: 220-240'),
    campo('temperatura_k', 'Temperatura de color (K)', 'numero', 'Ej.: 4000'),
    campo('formato', 'Formato', 'opcion', opciones=['Lámpara', 'Panel', 'Reflector', 'Tubo', 'Otro']),
]
PREDEFINIDAS = {
    'Cables': CABLES,
    'Conductores': CABLES,
    'Termomagnéticas': TERMICAS,
    'Interruptores termomagnéticos': TERMICAS,
    'Diferenciales': DIFERENCIALES,
    'Interruptores diferenciales': DIFERENCIALES,
    'Iluminación LED': LEDS,
    'Canalización': [],
    'Protecciones': [],
    'Otros': [campo('detalle', 'Detalle técnico')],
}
