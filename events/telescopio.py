from math import log10, sqrt

def calcular_telescopio(apertura_mm, focal_telescopio_mm, focal_ocular_mm, afov=52):
    """
    apertura_mm           — diámetro del espejo/lente en mm
    focal_telescopio_mm   — longitud focal del telescopio en mm
    focal_ocular_mm       — longitud focal del ocular en mm
    afov                  — campo visual aparente del ocular en grados (52 por defecto)
    """

    # Magnificación
    magnificacion = round(focal_telescopio_mm / focal_ocular_mm, 1)

    # Relación focal (f/)
    relacion_focal = round(focal_telescopio_mm / apertura_mm, 1)

    # Campo visual real en grados
    campo_visual = round(afov / magnificacion, 2)

    # Pupila de salida en mm
    pupila_salida = round(apertura_mm / magnificacion, 2)

    # Límite de magnitud visual
    limite_magnitud = round(2.1 + 5 * log10(apertura_mm), 1)

    # Magnificación mínima útil (pupila de salida = 7mm)
    mag_minima = round(apertura_mm / 7, 1)

    # Magnificación máxima útil
    mag_maxima = round(apertura_mm * 2, 0)

    # Poder resolvente (segundos de arco)
    poder_resolvente = round(116 / apertura_mm, 2)

    # Evaluación de la configuración
    advertencias = []
    if magnificacion > mag_maxima:
        advertencias.append(f"Magnificación muy alta — imagen borrosa. Máximo recomendado: {int(mag_maxima)}x")
    if magnificacion < mag_minima:
        advertencias.append(f"Magnificación muy baja — desperdicia apertura. Mínimo recomendado: {int(mag_minima)}x")
    if pupila_salida > 7:
        advertencias.append("Pupila de salida mayor a 7mm — luz desperdiciada")
    if pupila_salida < 0.5:
        advertencias.append("Pupila de salida muy pequeña — imagen muy oscura")

    # Objetos recomendados según magnificación
    if magnificacion < 50:
        objetos = ["Cúmulos abiertos", "Nebulosas grandes", "Galaxias grandes", "Luna llena"]
    elif magnificacion < 150:
        objetos = ["Luna", "Planetas brillantes", "Cúmulos globulares", "Nebulosa de Orión"]
    elif magnificacion < 300:
        objetos = ["Saturno y sus anillos", "Júpiter y sus lunas", "Marte", "Cráteres lunares"]
    else:
        objetos = ["Dobles estrechas", "Detalles planetarios", "Cráteres lunares finos"]

    return {
        'entrada': {
            'apertura_mm':          apertura_mm,
            'focal_telescopio_mm':  focal_telescopio_mm,
            'focal_ocular_mm':      focal_ocular_mm,
            'afov':                 afov,
        },
        'resultados': {
            'magnificacion':      magnificacion,
            'relacion_focal':     f"f/{relacion_focal}",
            'campo_visual':       campo_visual,
            'pupila_salida':      pupila_salida,
            'limite_magnitud':    limite_magnitud,
            'mag_minima_util':    int(mag_minima),
            'mag_maxima_util':    int(mag_maxima),
            'poder_resolvente':   poder_resolvente,
        },
        'advertencias': advertencias,
        'objetos_recomendados': objetos,
    }

if __name__ == '__main__':
    # Ejemplo: telescopio 130mm f/7.7 con ocular de 10mm
    resultado = calcular_telescopio(130, 1000, 10)
    r = resultado['resultados']
    print(f"\nTelescopio 130mm f/7.7 — Ocular 10mm\n")
    print(f"  Magnificación:       {r['magnificacion']}x")
    print(f"  Relación focal:      {r['relacion_focal']}")
    print(f"  Campo visual:        {r['campo_visual']}°")
    print(f"  Pupila de salida:    {r['pupila_salida']} mm")
    print(f"  Límite magnitud:     {r['limite_magnitud']}")
    print(f"  Mag. mínima útil:    {r['mag_minima_util']}x")
    print(f"  Mag. máxima útil:    {r['mag_maxima_util']}x")
    print(f"  Poder resolvente:    {r['poder_resolvente']}\"")
    print(f"\n  Objetos recomendados: {', '.join(resultado['objetos_recomendados'])}")
    if resultado['advertencias']:
        print(f"\n  ⚠ {resultado['advertencias'][0]}")