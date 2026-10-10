print("BUFFET")

c_cafe = 0
c_medialuna = 0
c_sandwich = 0
recaudado = 0

while True:
    print("\n1) Vender cafe (1500)")
    print("2) Vender medialuna (700)")
    print("3) Vender sandwich (1800)")
    print("4) Ver resumen")
    print("5) Salir")
    
    op = input("opcion: ")
    
    if op == "1":
        cant = int(input("cantidad de cafe: "))
        c_cafe = c_cafe + cant
        recaudado = recaudado + (cant * 1500)
        print("anotado")
        
    elif op == "2":
        cant = int(input("cantidad de medialunas: "))
        c_medialuna = c_medialuna + cant
        recaudado = recaudado + (cant * 700)
        print("anotado")
        
    elif op == "3":
        cant = int(input("cantidad de sandwich: "))
        c_sandwich = c_sandwich + cant
        recaudado = recaudado + (cant * 1800)
        print("anotado")
        
    elif op == "4":
        print("\nRESUMEN")
        print("Cafes:", c_cafe)
        print("Medialunas:", c_medialuna)
        print("Sandwichs:", c_sandwich)
        print("Total plata: $", recaudado)
        
    elif op == "5":
        print("FIN")
        break
    else:
        print("pusiste mal la opcion")