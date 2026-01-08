import socket
import os
from tqdm import tqdm

NODO_B_IP = "10.86.28.226"
NODO_B_PORT = 5001

CARPETA = "descargas_c"
os.makedirs(CARPETA, exist_ok=True)

def descargar_archivo(archivo):
    progreso = 0
    ruta = os.path.join(CARPETA, archivo)

    with open(ruta, "wb") as f, tqdm(total=100, desc=f"Descargando {archivo}") as barra:
        while progreso < 100:
            with socket.socket() as s:
                s.connect((NODO_B_IP, NODO_B_PORT))
                s.send(f"DESCARGAR:{archivo},{progreso}".encode())
                data = s.recv(1024)

                if not data:
                    print("❌ Archivo no disponible en Nodo B")
                    return

                f.write(data)
                progreso += 10
                barra.update(10)

    print(f"✅ {archivo} descargado desde Nodo B")

def menu():
    while True:
        print("\n===== MENÚ NODO C =====")
        print("1. Descargar archivo desde Nodo B")
        print("2. Salir")

        op = input("Opción: ")

        if op == "1":
            archivo = input("Nombre EXACTO del archivo: ")
            descargar_archivo(archivo)
        elif op == "2":
            break
        else:
            print("Opción inválida")

if __name__ == "__main__":
    menu()
