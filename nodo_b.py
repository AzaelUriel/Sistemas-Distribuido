import socket
import threading
import os
from tqdm import tqdm


TRACKER_IP = "10.86.28.226"
TRACKER_PORT = 12345

NODO_IP = "10.86.28.226"
NODO_PORT = 5001

CARPETA = "descargas"
os.makedirs(CARPETA, exist_ok=True)

ARCHIVOS_DISPONIBLES = [
    "file1.txt", "file2.mp4", "file3.png",
    "file4.png", "file5.txt", "file6.mp4"
]


def registrar_nodo():
    with socket.socket() as s:
        s.connect((TRACKER_IP, TRACKER_PORT))
        s.send(f"REGISTRAR:{NODO_IP},{NODO_PORT},".encode())
        s.recv(1024)

def solicitar_peers(archivo):
    with socket.socket() as s:
        s.connect((TRACKER_IP, TRACKER_PORT))
        s.send(f"SOLICITAR:{archivo}".encode())
        respuesta = s.recv(1024).decode()
        return respuesta.replace("PEERS:", "").split(";")


def descargar_archivo(archivo):
    peers = solicitar_peers(archivo)

    if not peers or peers == ['']:
        print("❌ No hay peers disponibles")
        return

    progreso = 0
    ruta = os.path.join(CARPETA, archivo)

    with open(ruta, "wb") as f, tqdm(total=100, desc=f"Descargando {archivo}") as barra:
        while progreso < 100:
            ip, port = peers[0].split(":")
            with socket.socket() as s:
                s.connect((ip, int(port)))
                s.send(f"DESCARGAR:{archivo},{progreso}".encode())
                data = s.recv(1024)

                if not data:
                    print("❌ Fragmento vacío")
                    return

                f.write(data)
                progreso += 10
                barra.update(10)

    print(f"✅ {archivo} descargado")


def manejar_peticion(conexion):
    try:
        mensaje = conexion.recv(1024).decode()
        _, datos = mensaje.split(":")
        archivo, progreso = datos.split(",")
        progreso = int(progreso)

        ruta = os.path.join(CARPETA, archivo)
        if not os.path.exists(ruta):
            conexion.send(b"")
            return

        with open(ruta, "rb") as f:
            f.seek(progreso * 1024 // 10)
            conexion.send(f.read(1024))
    finally:
        conexion.close()

def iniciar_servidor():
    s = socket.socket()
    s.bind((NODO_IP, NODO_PORT))
    s.listen(5)
    print("[Nodo B] Servidor activo")

    while True:
        c, _ = s.accept()
        threading.Thread(target=manejar_peticion, args=(c,), daemon=True).start()


def menu():
    while True:
        print("\n===== MENÚ NODO B =====")
        print("1. Descargar archivo")
        print("2. Salir")

        op = input("Opción: ")

        if op == "1":
            for i, a in enumerate(ARCHIVOS_DISPONIBLES, 1):
                print(f"{i}. {a}")
            try:
                sel = int(input("Selecciona archivo: "))
                descargar_archivo(ARCHIVOS_DISPONIBLES[sel - 1])
            except:
                print("Opción inválida")
        elif op == "2":
            break
        else:
            print("Opción inválida")


if __name__ == "__main__":
    registrar_nodo()
    threading.Thread(target=iniciar_servidor, daemon=True).start()
    menu()
