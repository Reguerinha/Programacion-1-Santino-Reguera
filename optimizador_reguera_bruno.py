"""Optimizador de horas de soporte: reparte las horas semanales entre areas
resolviendo un sistema de ecuaciones lineales por Gauss-Jordan."""
import sys
from fractions import Fraction


def leer_sistema(ruta):
    """Devuelve (areas, matriz ampliada de Fractions). Valida el formato."""
    with open(ruta, encoding="utf-8") as f:
        lineas = [l.split() for l in f if l.strip() and not l.startswith("#")]
    if not lineas or lineas[0][0] != "areas":
        raise ValueError("La primera linea debe ser: areas A1 A2 ...")
    areas, matriz = lineas[0][1:], []
    for fila in lineas[1:]:
        if len(fila) != len(areas) + 1:
            raise ValueError(f"Cada ecuacion necesita {len(areas) + 1} numeros: {' '.join(fila)}")
        try:
            matriz.append([Fraction(x) for x in fila])
        except ValueError:
            raise ValueError("Valor no numerico en: " + " ".join(fila))
    if not matriz:
        raise ValueError("No hay ecuaciones")
    return areas, matriz


def main(ruta):
    try:
        areas, m = leer_sistema(ruta)
    except (OSError, ValueError) as e:
        print("Error:", e)
        return
    print("Areas:", areas)
    for fila in m:
        print([str(x) for x in fila])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sistema.txt")
