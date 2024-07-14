import socket
import sys

def make_move(board, player, client_socket):
    # Función para hacer un movimiento
    while True:
        try:
            move = input(f"Jugador {player}, seleccione una posición (1-9): ")
            move = int(move.strip())
            if 1 <= move <= 9:
                row = (move - 1) // 3
                col = (move - 1) % 3
                if board[row][col] == " ":
                    board[row][col] = "O"  # Asignar "O" para el jugador 2
                    break
                else:
                    print("¡Posición ocupada! Intente nuevamente.")
            else:
                print("Ingrese un número entre 1 y 9.")
        except ValueError:
            print("Entrada no válida. Ingrese un número.")

    # Enviar movimiento al servidor
    move_str = str(move)
    client_socket.send(move_str.encode())

    # Esperar confirmación del servidor
    response = client_socket.recv(1024).decode()
    print(response)
    
    return response  # Devolver la respuesta para que se pueda usar fuera de esta función

def main():
    host = '127.0.0.1'  # localhost
    port = 12345  # Puerto arbitrario

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
    except ConnectionRefusedError:
        print("No se puede conectar al servidor. Asegúrate de que el servidor esté en funcionamiento.")
        sys.exit()

    print("Conectado al servidor. Espere a que comience el juego...")
    print("Usted es el Jugador 2.")

    # Inicializar el tablero
    board = [[" " for _ in range(3)] for _ in range(3)]

    while True:
        # Esperar mensaje del servidor
        response = client_socket.recv(1024).decode()

        if "Es tu turno" in response:
            # Hacer movimiento del jugador 1 y obtener la respuesta del servidor
            print("Es tu turno")
            response = make_move(board, 2, client_socket)  # Jugador 2 (cliente 2)

            # Verificar estado del juego (ganador, empate, continuar)
            if "ganador" in response or "Empate" in response:
                break
        elif "Esperando al otro jugador" in response:
            
            print(response)  # Mostrar el mensaje de espera
        else:
            print(response)
            

    client_socket.close()

if __name__ == "__main__":
    main()
