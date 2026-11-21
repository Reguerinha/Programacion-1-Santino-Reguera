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


def intercambiar(m, i, j):
    m[i], m[j] = m[j], m[i]


def escalar(m, i, k):
    m[i] = [x * k for x in m[i]]


def restar_multiplo(m, i, j, k):
    """Fila i = fila i - k * fila j."""
    m[i] = [a - k * b for a, b in zip(m[i], m[j])]


def gauss_jordan(m):
    """Reduce una copia de la matriz ampliada. Devuelve (matriz reducida, columnas pivote)."""
    m = [f[:] for f in m]
    fila, pivotes = 0, []
    for c in range(len(m[0]) - 1):
        p = next((i for i in range(fila, len(m)) if m[i][c] != 0), None)
        if p is None:
            continue
        intercambiar(m, fila, p)
        escalar(m, fila, 1 / m[fila][c])
        for i in range(len(m)):
            if i != fila and m[i][c] != 0:
                restar_multiplo(m, i, fila, m[i][c])
        pivotes.append(c)
        fila += 1
        if fila == len(m):
            break
    return m, pivotes


def main(ruta):
    try:
        areas, m = leer_sistema(ruta)
    except (OSError, ValueError) as e:
        print("Error:", e)
        return
    red, piv = gauss_jordan(m)
    print("Columnas pivote:", piv)
    for fila in red:
        print([str(x) for x in fila])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sistema.txt")
