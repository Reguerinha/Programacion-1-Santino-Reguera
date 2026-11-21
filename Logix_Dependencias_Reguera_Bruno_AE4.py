"""Analizador de dependencias LOGIX. grafo = {modulo: [modulos de los que depende]}"""
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


# ---------- Recorridos (RF05) ----------
def dfs_recursivo(grafo, actual, visitados):
    visitados.append(actual)
    for vecino in grafo[actual]:
        if vecino not in visitados:
            dfs_recursivo(grafo, vecino, visitados)


def bfs_cola(grafo, inicio):
    visitados, cola = [inicio], [inicio]
    while cola:
        for vecino in grafo[cola.pop(0)]:
            if vecino not in visitados:
                visitados.append(vecino)
                cola.append(vecino)
    return visitados


def modulos_afectados(grafo, modulo):
    """Modulos que dependen (directa o indirectamente) de 'modulo'. BFS invertido.
    El propio modulo aparece solo si esta en un ciclo."""
    afectados, cola = [], [m for m in grafo if modulo in grafo[m]]
    while cola:
        actual = cola.pop(0)
        if actual not in afectados:
            afectados.append(actual)
            cola += [m for m in grafo if actual in grafo[m]]
    return [m for m in grafo if m in afectados]


# ---------- Ciclos (RF06) y orden de migracion (RF07) ----------
def detectar_ciclos(grafo):
    """DFS con estados (0 sin visitar, 1 en el camino, 2 terminado).
    Devuelve la lista de ciclos; cada ciclo es una lista de modulos."""
    estado, camino, ciclos = {m: 0 for m in grafo}, [], []

    def recorrer(u):
        estado[u] = 1
        camino.append(u)
        for v in grafo[u]:
            if estado[v] == 1:
                ciclos.append(camino[camino.index(v):])
            elif estado[v] == 0:
                recorrer(v)
        camino.pop()
        estado[u] = 2

    for m in grafo:
        if estado[m] == 0:
            recorrer(m)
    return ciclos


def orden_topologico_kahn(grafo):
    """Orden de migracion con cola. ValueError si hay ciclos."""
    pendientes = {m: len(d) for m, d in grafo.items()}
    cola, orden = [m for m in grafo if pendientes[m] == 0], []
    while cola:
        actual = cola.pop(0)
        orden.append(actual)
        for m in grafo:
            if actual in grafo[m]:
                pendientes[m] -= 1
                if pendientes[m] == 0:
                    cola.append(m)
    if len(orden) < len(grafo):
        raise ValueError("El grafo contiene ciclos: no existe orden valido")
    return orden


def exportar_reporte(grafo, nombre_archivo="reporte_analisis.txt"):
    ciclos = detectar_ciclos(grafo)
    try:
        orden = " -> ".join(orden_topologico_kahn(grafo))
    except ValueError as e:
        orden = str(e)
    lineas = ["REPORTE DE ANALISIS - LOGIX", "", *mostrar_lista_adyacencia(grafo), "",
              *[f"{m}: salida {s}, entrada {e}" for m, (s, e) in calcular_grados(grafo).items()], "",
              "Ciclos: " + ("; ".join(" -> ".join(c + [c[0]]) for c in ciclos) or "ninguno"),
              "Orden de migracion: " + orden]
    escribir(nombre_archivo, "\n".join(lineas) + "\n")


# ---------- Menu ----------
MENU = """
=== ANALIZADOR DE DEPENDENCIAS LOGIX ===
 1. Lista de adyacencia        9. Cargar grafo desde archivo
 2. Matriz de adyacencia      10. Agregar modulo
 3. Grados de entrada/salida  11. Agregar dependencia
 4. Recorrido DFS (recursivo) 12. Eliminar dependencia
 5. Recorrido BFS (con cola)  13. Eliminar modulo
 6. Impacto en cascada        14. Guardar grafo (logix_editado.txt)
 7. Detectar ciclos           15. Exportar reporte (reporte_analisis.txt)
 8. Orden de migracion         0. Salir"""


def ejecutar(op, grafo):
    """Ejecuta una opcion del menu y devuelve el grafo (cambia al cargar otro)."""
    if not grafo and op in "1 2 3 4 5 6 7 8 11 12 13 14 15".split():
        raise ValueError("El grafo esta vacio. Cargalo primero con la opcion 9.")
    if op in ("4", "5", "6"):
        ini = input("Modulo: ").strip().upper()
        if ini not in grafo:
            print("Modulo no encontrado. Modulos:", ", ".join(grafo))
        elif op == "4":
            vis = []
            dfs_recursivo(grafo, ini, vis)
            print("DFS:", " -> ".join(vis))
        elif op == "5":
            print("BFS:", " -> ".join(bfs_cola(grafo, ini)))
        else:
            af = modulos_afectados(grafo, ini)
            print(f"Si se modifica {ini} se afectan {len(af)}:", ", ".join(af) or "ninguno")
    elif op == "1":
        print("\n".join(mostrar_lista_adyacencia(grafo)))
    elif op == "2":
        mods, mat = generar_matriz_adyacencia(grafo)
        print("     " + " ".join(f"{m:>4}" for m in mods))
        for m, fila in zip(mods, mat):
            print(f"{m:>4} " + " ".join(f"{x:>4}" for x in fila))
    elif op == "3":
        for m, (s, e) in calcular_grados(grafo).items():
            print(f"{m}: salida {s}, entrada {e}")
    elif op == "7":
        ciclos = detectar_ciclos(grafo)
        print("\n".join("Ciclo: " + " -> ".join(c + [c[0]]) for c in ciclos) or "No hay ciclos.")
    elif op == "8":
        print("Orden de migracion:", " -> ".join(orden_topologico_kahn(grafo)))
    elif op == "9":
        grafo = cargar_grafo(input("Archivo (Enter = logix_reestructurado.txt): ").strip()
                             or "logix_reestructurado.txt")
        print("Grafo cargado:", len(grafo), "modulos.")
    elif op == "10":
        agregar_modulo(grafo, input("Nombre del modulo nuevo: "))
    elif op == "11":
        agregar_dependencia(grafo, input("Modulo que depende: "), input("Depende de: "))
    elif op == "12":
        eliminar_dependencia(grafo, input("Modulo que depende: "), input("Deja de depender de: "))
    elif op == "13":
        eliminar_modulo(grafo, input("Modulo a eliminar: "))
    elif op == "14":
        guardar_grafo(grafo, "logix_editado.txt")
        print("Guardado en logix_editado.txt")
    elif op == "15":
        exportar_reporte(grafo)
        print("Reporte guardado en reporte_analisis.txt")
    else:
        print("Opcion invalida.")
    return grafo


def main():
    try:
        grafo = cargar_grafo("logix_legacy.txt")
    except ValueError as e:
        print("Error:", e, "- grafo vacio (opcion 9 para cargar otro).")
        grafo = {}
    while True:
        print(MENU)
        op = input("Opcion: ").strip()
        if op == "0":
            break
        try:
            grafo = ejecutar(op, grafo)
        except ValueError as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
