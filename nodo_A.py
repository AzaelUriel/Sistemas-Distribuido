import socket
import threading
import os

TRACKER_IP = "10.86.28.226"
TRACKER_PORT = 12345

NODO_IP = "10.86.28.226"
NODO_PORT = 5000

CARPETA_COMPARTIDA = "shared"

ARCHIVOS = os.listdir(CARPETA_COMPARTIDA)

def registrar_nodo():
    with socket.socket() as s:
        s.connect((TRACKER_IP, TRACKER_PORT))
        archivos_str = ";".join(ARCHIVOS)
        s.send(f"REGISTRAR:{NODO_IP},{NODO_PORT},{archivos_str}".encode())
        print("[Nodo A]", s.recv(1024).decode())

def manejar_peticion(conexion):
    try:
        mensaje = conexion.recv(1024).decode()
        comando, datos = mensaje.split(":", 1)

        if comando == "DESCARGAR":
            archivo, progreso = datos.split(",")
            progreso = int(progreso)

            ruta = os.path.join(CARPETA_COMPARTIDA, archivo)
            if not os.path.exists(ruta):
                conexion.send(b"")
                return

            with open(ruta, "rb") as f:
                f.seek(progreso * 1024 // 10)
                fragmento = f.read(1024)
                conexion.send(fragmento)

    except Exception as e:
        print("[Nodo A] Error:", e)
    finally:
        conexion.close()

def iniciar_servidor():
    servidor = socket.socket()
    servidor.bind((NODO_IP, NODO_PORT))
    servidor.listen(5)
    print("[Nodo A] Seeder activo")

    while True:
        conexion, _ = servidor.accept()
        threading.Thread(target=manejar_peticion, args=(conexion,), daemon=True).start()

if __name__ == "__main__":
    registrar_nodo()
    iniciar_servidor()



