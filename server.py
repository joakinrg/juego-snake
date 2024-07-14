import socket
import threading

# Inicializar el tablero
board = [[" " for _ in range(3)] for _ in range(3)]
player_turn = 1
clients = []

def display_board():
    # Función para mostrar el tablero en la consola del servidor
    for row in board:
        print(" | ".join(row))
        print("-" * 9)

def check_winner(marker):
    # Función para verificar si hay un ganador
    for row in board:
        if all(cell == marker for cell in row):
            return True
    for col in range(3):
        if all(row[col] == marker for row in board):
            return True
    if all(board[i][i] == marker for i in range(3)) or all(board[i][2 - i] == marker for i in range(3)):
        return True
    return False

def send_message(conn, message):
    conn.send(f"{message}\n".encode())

def handle_client(conn, player):
    global board, player_turn, clients

    if player == 1:
        send_message(conn, "Bienvenido al juego Tic Tac Toe. Esperando al otro jugador...\n")
    else:
        send_message(conn, "Bienvenido al juego Tic Tac Toe.\n")
    clients.append(conn)

    while len(clients) < 2:
        continue  # Esperar hasta que ambos jugadores estén conectados

    # Informar a ambos jugadores que pueden comenzar
    if player == 1:
        for c in clients:
            send_message(c, "¡Todos los jugadores están conectados! Empezando partida.")
    else:
        pass  # El jugador 2 no necesita este mensaje inicial

    while True:
        try:
            if player == player_turn:
                # Solicitar movimiento al jugador actual
                send_message(conn, f"Es tu turno, jugador {player}. Seleccione una posición (1-9): ")
                
                #Informar al otro jugador que espere
                other_player = 2 if player == 1 else 1
                send_message(clients[other_player - 1], f"Jugador {player} jugando, espera por favor...")

                move = conn.recv(1024).decode().strip()
                move = int(move)
                if 1 <= move <= 9:
                    row = (move - 1) // 3
                    col = (move - 1) % 3
                    if board[row][col] == " ":
                        #Mostrar movimiento del jugador "x"
                        print(f"Movimiento del jugador {player}")

                        board[row][col] = "X" if player == 1 else "O"
                        
                        # Mostrar el tablero actualizado en el servidor
                        display_board()

                        # Enviar estado actualizado del tablero al otro jugador
                        move_message=f"Jugador {player} realizó un movimiento: \n"
                        board_str = "\n".join([" | ".join(row) + "\n" + "-" * 9 for row in board])
                        for c in clients:
                            if c != conn:
                                send_message(c,move_message + board_str)


                        # Verificar si hay un ganador
                        if check_winner("X" if player == 1 else "O"):
                            for c in clients:
                                send_message(c, f"¡Felicidades! ¡Eres el ganador, jugador {player}!")
                            break
                        elif all(all(cell != " " for cell in row) for row in board):
                            for c in clients:
                                send_message(c, "¡Empate!")
                            break

                        # Cambiar turno al otro jugador
                        player_turn = 2 if player_turn == 1 else 1


                        # Informar al jugador actual del estado actual del tablero
                        send_message(conn, f"Tu tiro, jugador {player}:")
                        board_str = "\n".join([" | ".join(row) + "\n" + "-" * 9 for row in board])
                        send_message(conn, board_str)
                    else:
                        send_message(conn, "¡Posición ocupada! Intente nuevamente.")
                else:
                    send_message(conn, "Ingrese un número entre 1 y 9.")
        except ValueError:
            send_message(conn, "Entrada no válida. Ingrese un número.")
        except ConnectionResetError:
            print(f"La conexión con el jugador {player} ha sido reestablecida.")
            break
        except Exception as e:
            print(f"Error inesperado con el jugador {player}: {e}")
            break
    conn.close()

def main():
    host = '127.0.0.1'
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)
    print("Servidor iniciado. Esperando conexiones...")

    player = 1
    while player <= 2:
        conn, addr = server_socket.accept()
        print(f"Jugador {player} conectado desde {addr}")
        threading.Thread(target=handle_client, args=(conn, player)).start()
        player += 1

    server_socket.close()

if __name__ == "__main__":
    main()
