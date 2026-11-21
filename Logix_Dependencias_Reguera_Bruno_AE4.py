"""Analizador de dependencias LOGIX - Etapa 2: lista, matriz de adyacencia y grados."""
import os

CARPETA = os.path.dirname(os.path.abspath(__file__))


def ruta(nombre):
    """Los archivos se buscan junto al programa, sin importar mayusculas ni un '.txt' repetido."""
    if os.path.isabs(nombre):
        return nombre
    for f in os.listdir(CARPETA):
        if f.lower() in (nombre.lower(), nombre.lower() + ".txt"):
            return os.path.join(CARPETA, f)
    return os.path.join(CARPETA, nombre)


def escribir(nombre, texto):
    try:
        with open(ruta(nombre), "w", encoding="utf-8") as f:
            f.write(texto)
    except OSError:
        raise ValueError(f"No se pudo guardar el archivo: {nombre}")


# ---------- Archivos (RF01, RF08) ----------
def cargar_grafo(nombre_archivo):
    """Lee 'MODULO: DEP1, DEP2' (o NINGUNA). Lanza ValueError si hay un error."""
    try:
        with open(ruta(nombre_archivo), encoding="utf-8-sig") as f:
            lineas = [l.strip().upper() for l in f if l.strip() and l[0] != "#"]
    except OSError:
        raise ValueError(f"No se encontro {ruta(nombre_archivo)}. Archivos en la carpeta: "
                         + ", ".join(os.listdir(CARPETA)))
    grafo = {}
    for linea in lineas:
        if ":" not in linea:
            raise ValueError(f"Falta ':' en la linea '{linea}'")
        nombre = linea.split(":")[0].strip()
        if not nombre.isalnum():
            raise ValueError(f"Nombre de modulo invalido en '{linea}'")
        grafo[nombre] = []
    for linea in lineas:
        mod, deps = [t.strip() for t in linea.split(":", 1)]
        for d in ([] if deps in ("NINGUNA", "") else [x.strip() for x in deps.split(",")]):
            if not d.isalnum():
                raise ValueError(f"Dependencia invalida en '{linea}'")
            grafo.setdefault(d, [])
            if d not in grafo[mod]:
                grafo[mod].append(d)
    if not grafo:
        raise ValueError("El archivo no tiene modulos")
    return grafo


def guardar_grafo(grafo, nombre_archivo):
    escribir(nombre_archivo, "".join(f"{m}: {', '.join(d) or 'NINGUNA'}\n" for m, d in grafo.items()))


# ---------- Edicion (RF02) ----------
def agregar_modulo(grafo, nombre):
    nombre = nombre.strip().upper()
    if not nombre.isalnum() or nombre in grafo:
        raise ValueError("Nombre invalido o modulo ya existente")
    grafo[nombre] = []


def agregar_dependencia(grafo, origen, destino):
    """origen depende de destino."""
    o, d = origen.strip().upper(), destino.strip().upper()
    if o not in grafo or d not in grafo or o == d:
        raise ValueError("Los dos modulos deben existir y ser distintos")
    if d not in grafo[o]:
        grafo[o].append(d)


def eliminar_dependencia(grafo, origen, destino):
    o, d = origen.strip().upper(), destino.strip().upper()
    if o not in grafo or d not in grafo[o]:
        raise ValueError("Esa dependencia no existe")
    grafo[o].remove(d)


def eliminar_modulo(grafo, nombre):
    nombre = nombre.strip().upper()
    if nombre not in grafo:
        raise ValueError(f"El modulo {nombre} no existe")
    del grafo[nombre]
    for deps in grafo.values():
        if nombre in deps:
            deps.remove(nombre)


# ---------- Representaciones (RF03) y grados (RF04) ----------
def mostrar_lista_adyacencia(grafo):
    return [f"{m} -> {', '.join(d) or '(sin dependencias)'}" for m, d in grafo.items()]


def generar_matriz_adyacencia(grafo):
    """(modulos, matriz): matriz[i][j] = 1 si el modulo i depende del j."""
    mods = list(grafo)
    return mods, [[int(b in grafo[a]) for b in mods] for a in mods]


def calcular_grados(grafo):
    """{modulo: (grado_salida, grado_entrada)}"""
    return {m: (len(d), sum(m in x for x in grafo.values())) for m, d in grafo.items()}


def main():
    """Prueba de la etapa: lista, matriz y grados del grafo original."""
    grafo = cargar_grafo("logix_legacy.txt")
    print("\n".join(mostrar_lista_adyacencia(grafo)))
    mods, mat = generar_matriz_adyacencia(grafo)
    print("\n     " + " ".join(f"{m:>4}" for m in mods))
    for m, fila in zip(mods, mat):
        print(f"{m:>4} " + " ".join(f"{x:>4}" for x in fila))
    print()
    for m, (s, e) in calcular_grados(grafo).items():
        print(f"{m}: salida {s}, entrada {e}")


if __name__ == "__main__":
    main()
