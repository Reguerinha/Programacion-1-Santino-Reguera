import json, os
 
INSC, PAR = 'inscriptos.json', 'parejas.json'
 
def cargar(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, encoding='utf-8') as f:
        return json.load(f)
 
def guardar(ruta, datos):
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
 
# Ordenamientos sobre una copia. antes(a, b) = True si a va antes que b.
def seleccion(lista, antes):
    v, comp, inter = lista[:], 0, 0
    for i in range(len(v) - 1):
        m = i
        for j in range(i + 1, len(v)):
            comp += 1
            if antes(v[j], v[m]):
                m = j
        if m != i:
            v[i], v[m] = v[m], v[i]
            inter += 1
    return v, comp, inter
 
def burbuja(lista, antes):
    v, comp, inter = lista[:], 0, 0
    for i in range(len(v) - 1):
        for j in range(len(v) - 1 - i):
            comp += 1
            if antes(v[j + 1], v[j]):
                v[j], v[j + 1] = v[j + 1], v[j]
                inter += 1
    return v, comp, inter
 
alfabetico = lambda a, b: a['nombre'].lower() < b['nombre'].lower()
por_categoria = lambda a, b: (a['categoria'], a['nombre'].lower()) < (b['categoria'], b['nombre'].lower())
por_puntos = lambda a, b: a['puntos'] > b['puntos']
 
def inscribir(jugadores):
    for i in range(int(input("¿Cuántos jugadores? "))):
        nombre = input(f"Nombre del jugador {i + 1}: ")
        categoria = input("Categoría (4ª, 5ª, 6ª): ")
        jugadores.append({'nombre': nombre, 'categoria': categoria})
    guardar(INSC, jugadores)
 
def armar_parejas(jugadores, parejas):
    usados = [j['nombre'] for p in parejas for j in p['jugadores']]
    libres = [j for j in jugadores if j['nombre'] not in usados]
    while len(libres) >= 2:
        nombre = input("Nombre de la pareja (Enter para terminar): ")
        if not nombre:
            break
        for k, j in enumerate(libres):
            print(f"{k + 1}. {j['nombre']} ({j['categoria']})")
        try:
            a, b = [int(x) - 1 for x in input("Dos números separados por coma: ").split(',')]
            assert a != b and 0 <= a < len(libres) and 0 <= b < len(libres)
        except (ValueError, AssertionError):
            print("Elección inválida.")
            continue
        j1, j2 = libres[a], libres[b]
        parejas.append({'nombre': nombre, 'jugadores': [j1, j2], 'puntos': 0})
        libres = [j for j in libres if j is not j1 and j is not j2]
        guardar(PAR, parejas)
 
def cargar_puntos(parejas):
    for k, p in enumerate(parejas):
        print(f"{k + 1}. {p['nombre']} ({p['puntos']} pts)")
    try:
        parejas[int(input("Pareja: ")) - 1]['puntos'] += int(input("Puntos: "))
        guardar(PAR, parejas)
    except (ValueError, IndexError):
        print("Dato inválido.")
 
def tabla(parejas):
    for k, p in enumerate(seleccion(parejas, por_puntos)[0]):
        print(f"{k + 1}. {p['nombre']:<15} {p['puntos']}")
 
def lista_alfabetica(jugadores):
    for j in seleccion(jugadores, alfabetico)[0]:
        print(j['nombre'])
 
def lista_categorias(jugadores):
    cat = None
    for j in burbuja(jugadores, por_categoria)[0]:
        if j['categoria'] != cat:
            cat = j['categoria']
            print(f"\nCategoría {cat}:")
        print(f"  {j['nombre']}")
 
def comparar(jugadores):
    _, c1, i1 = seleccion(jugadores, alfabetico)
    _, c2, i2 = burbuja(jugadores, por_categoria)
    print(f"1. Alfabético  Selección  comparaciones={c1}  intercambios={i1}")
    print(f"2. Categoría   Burbuja    comparaciones={c2}  intercambios={i2}")
 
def main():
    jugadores, parejas = cargar(INSC), cargar(PAR)
    while True:
        print("\n1.Inscribir 2.Parejas 3.Puntos 4.Tabla 5.Alfabético 6.Categorías 7.Comparar 0.Salir")
        op = input("Opción: ")
        if op == '1': inscribir(jugadores)
        elif op == '2': armar_parejas(jugadores, parejas)
        elif op == '3': cargar_puntos(parejas)
        elif op == '4': tabla(parejas)
        elif op == '5': lista_alfabetica(jugadores)
        elif op == '6': lista_categorias(jugadores)
        elif op == '7': comparar(jugadores)
        elif op == '0': break
 
if __name__ == "__main__":
    main()