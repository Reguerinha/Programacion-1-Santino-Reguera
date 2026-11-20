from pathlib import Path
from typing import List, Tuple


MAX_MODULOS = 15


def cargar_desde_teclado() -> Tuple[List[str], List[List[int]]]:
    """RF1: Carga módulos (hasta 15) y matriz de adyacencia desde teclado."""
    while True:
        try:
            n = int(input(f"Cantidad de módulos (1 a {MAX_MODULOS}): ").strip())
            if 1 <= n <= MAX_MODULOS:
                break
            print(f"Debe ingresar un número entre 1 y {MAX_MODULOS}.")
        except ValueError:
            print("Entrada inválida. Ingrese un número entero.")

    modulos: List[str] = []
    for i in range(n):
        nombre = input(f"Nombre del módulo {i + 1}: ").strip() or f"M{i + 1}"
        modulos.append(nombre)

    print("\nIngrese la matriz de adyacencia fila por fila (0 o 1 separados por espacio).")
    print("Recordatorio: A[i][j] = 1 significa que el módulo i depende del módulo j.")
    matriz: List[List[int]] = []
    for i in range(n):
        while True:
            partes = input(f"Fila {i + 1} ({modulos[i]}): ").strip().split()
            if len(partes) == n and all(x in ("0", "1") for x in partes):
                matriz.append([int(x) for x in partes])
                break
            print(f"Ingrese exactamente {n} valores de 0 o 1.")

    return modulos, matriz


def cargar_desde_archivo(ruta_archivo: str) -> Tuple[List[str], List[List[int]]]:
    """
    RF1: Carga módulos y matriz de adyacencia desde un archivo de texto.
    Formato esperado:
      Línea 1: nombres de módulos separados por coma o espacio (máx. 15)
      Siguientes N líneas: filas de 0s y 1s separadas por espacio o coma
    """
    lineas = [
        linea.strip()
        for linea in Path(ruta_archivo).read_text(encoding="utf-8").splitlines()
        if linea.strip() and not linea.strip().startswith("#")
    ]
    if not lineas:
        raise ValueError("El archivo está vacío.")

    modulos = [m.strip() for m in lineas[0].replace(",", " ").split() if m.strip()]
    n = len(modulos)
    if not (1 <= n <= MAX_MODULOS):
        raise ValueError(f"La cantidad de módulos debe estar entre 1 y {MAX_MODULOS} (se encontraron {n}).")

    if len(lineas) - 1 != n:
        raise ValueError(f"Se esperaban {n} filas de matriz, pero se encontraron {len(lineas) - 1}.")

    matriz: List[List[int]] = []
    for idx, fila_str in enumerate(lineas[1:]):
        elementos = [x.strip() for x in fila_str.replace(",", " ").split() if x.strip()]
        if len(elementos) != n or any(x not in ("0", "1") for x in elementos):
            raise ValueError(f"Fila {idx + 1} inválida: se esperaban {n} valores binarios (0/1).")
        matriz.append([int(x) for x in elementos])

    return modulos, matriz


def calcular_alcanzabilidad_warshall(matriz_adyacencia: List[List[int]]) -> List[List[int]]:
    """RF2: Calcula el cierre transitivo (matriz de alcanzabilidad A*) usando Warshall."""
    n = len(matriz_adyacencia)
    alcanzable = [[1 if matriz_adyacencia[i][j] != 0 else 0 for j in range(n)] for i in range(n)]

    for k in range(n):
        for i in range(n):
            if alcanzable[i][k]:
                for j in range(n):
                    if alcanzable[k][j]:
                        alcanzable[i][j] = 1

    return alcanzable


def modulos_afectados_por_modificacion(
    modulo_objetivo: str,
    modulos: List[str],
    alcanzabilidad: List[List[int]],
) -> List[str]:
    """
    RF2: Dado un módulo j, lista los módulos i que dependen (directa o indirectamente) de j.
    En la convención del documento, i -> j significa 'i depende de j', por lo que si se modifica j,
    se ven afectados los módulos i tales que alcanzabilidad[i][j] == 1.
    """
    indice_modulos = {nombre.upper(): idx for idx, nombre in enumerate(modulos)}
    clave = modulo_objetivo.strip().upper()
    if clave not in indice_modulos:
        raise ValueError(f"El módulo '{modulo_objetivo}' no existe en el sistema.")

    j = indice_modulos[clave]
    return [modulos[i] for i in range(len(modulos)) if alcanzabilidad[i][j] == 1]


def imprimir_matriz(titulo: str, modulos: List[str], matriz: List[List[int]]) -> None:
    """Muestra una matriz etiquetada con los nombres de los módulos."""
    ancho = max([len(m) for m in modulos] + [4])
    print(f"\n--- {titulo} ---")
    encabezado = " " * (ancho + 2) + " ".join(f"{m:>{ancho}}" for m in modulos)
    print(encabezado)
    for i, fila in enumerate(matriz):
        contenido = " ".join(f"{val:>{ancho}}" for val in fila)
        print(f"{modulos[i]:>{ancho}}  {contenido}")


def menu_principal() -> None:
    modulos: List[str] = []
    matriz_ady: List[List[int]] = []
    matriz_alc: List[List[int]] = []

    while True:
        print("\n=== LOGIX-ANALYZER (2 Requerimientos) ===")
        print("1. RF1 - Cargar módulos y matriz de adyacencia (teclado)")
        print("2. RF1 - Cargar módulos y matriz de adyacencia (archivo)")
        print("3. RF2 - Calcular matriz de alcanzabilidad (Warshall) y consultar afectados")
        print("4. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            modulos, matriz_ady = cargar_desde_teclado()
            matriz_alc = []
            imprimir_matriz("Matriz de Adyacencia (A)", modulos, matriz_ady)

        elif opcion == "2":
            ruta = input("Ruta del archivo: ").strip()
            try:
                modulos, matriz_ady = cargar_desde_archivo(ruta)
                matriz_alc = []
                imprimir_matriz("Matriz de Adyacencia (A)", modulos, matriz_ady)
            except Exception as exc:
                print(f"Error al cargar el archivo: {exc}")

        elif opcion == "3":
            if not modulos or not matriz_ady:
                print("Primero debe cargar los datos con RF1 (opción 1 o 2).")
                continue

            matriz_alc = calcular_alcanzabilidad_warshall(matriz_ady)
            imprimir_matriz("Matriz de Alcanzabilidad (A* - Warshall)", modulos, matriz_alc)

            modulo_consulta = input("\nIngrese el módulo a modificar: ").strip()
            try:
                afectados = modulos_afectados_por_modificacion(modulo_consulta, modulos, matriz_alc)
                if afectados:
                    print(f"Módulos afectados al modificar '{modulo_consulta}': {', '.join(afectados)}")
                else:
                    print(f"Ningún módulo depende de '{modulo_consulta}' (0 módulos afectados).")
            except ValueError as exc:
                print(exc)

        elif opcion == "4":
            print("Saliendo de LOGIX-ANALYZER.")
            break

        else:
            print("Opción no válida.")


if __name__ == "__main__":
    menu_principal()