import socket
import threading

# Inicialización del tablero
board = [[" " for _ in range(3)] for _ in range(3)]
player_turn = 1  # Variable global para controlar el turno de los jugadores

# Función para mostrar el tablero
def display_board():
    for row in board:
        print(" | ".join(row))
        print("-" * 9)

# Función para verificar si hay un ganador
def check_winner(mark):
    # Verificar filas
    for row in board:
        if all(cell == mark for cell in row):
            return True

    # Verificar columnas
    for col in range(3):
        if all(board[row][col] == mark for row in range(3)):
            return True

    # Verificar diagonales
    if all(board[i][i] == mark for i in range(3)) or all(board[i][2 - i] == mark for i in range(3)):
        return True

    return False

# Función para manejar la lógica del juego Tic Tac Toe para un cliente específico
def handle_client(conn, player):
    global board, player_turn

    conn.send(f"Bienvenido al juego Tic Tac Toe. Esperando al otro jugador...\n".encode())

    while True:
        try:
            # Mostrar tablero actualizado
            display_board()

            # Verificar turno del jugador
            if player != player_turn:
                conn.send(f"Esperando al otro jugador...\n".encode())
                continue

            # Solicitar movimiento al jugador
            conn.send(f"Es tu turno, jugador {player}. Seleccione una posición (1-9): ".encode())
            move = conn.recv(1024).decode().strip()

            move = int(move)
            if 1 <= move <= 9:
                row = (move - 1) // 3
                col = (move - 1) % 3
                if board[row][col] == " ":
                    board[row][col] = "X" if player == 1 else "O"

                    # Verificar si hay un ganador
                    if check_winner("X" if player == 1 else "O"):
                        conn.send(f"¡Felicidades! ¡Eres el ganador, jugador {player}!\n".encode())
                        break
                    elif all(all(cell != " " for cell in row) for row in board):
                        conn.send("¡Empate!\n".encode())
                        break

                    # Cambiar turno al otro jugador
                    player_turn = 2 if player_turn == 1 else 1
                else:
                    conn.send("¡Posición ocupada! Intente nuevamente.\n".encode())
            else:
                conn.send("Ingrese un número entre 1 y 9.\n".encode())
        except ValueError:
            conn.send("Entrada no válida. Ingrese un número.\n".encode())
        except ConnectionResetError:
            print(f"La conexión con el jugador {player} ha sido restablecida.")
            break
        except Exception as e:
            print(f"Error inesperado con el jugador {player}: {e}")
            break

    conn.close()

# Función para iniciar el servidor
def start_server():
    host = '127.0.0.1'  # localhost
    port = 12345  # Puerto arbitrario

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)  # Servidor aceptará conexiones de hasta 2 clientes

    print(f"Servidor iniciado en {host}:{port}")

    players = []
    while len(players) < 2:
        try:
            conn, addr = server_socket.accept()
            players.append((conn, addr))
            print(f"Jugador {len(players)} conectado desde {addr}")

            # Iniciar un hilo para manejar al cliente
            threading.Thread(target=handle_client, args=(conn, len(players))).start()
        except Exception as e:
            print(f"Error al aceptar la conexión: {e}")

    server_socket.close()

if __name__ == "__main__":
    start_server()
