import sys
import time

# --- stale ---
BLANK = 0  # symbolizuje wolne pole
UP = 'U'  # oznaczenie ruchu w gore
DOWN = 'D'  # oznaczenie ruchu w dol
LEFT = 'L'  # oznaczenie ruchu w lewo
RIGHT = 'R'  # oznaczenie ruchu w prawo
MAX_MOVES = 20  # maksymalna dozwolona glebokosc rekursji (ilosc ruchow)


def read_board(file_name):  # odczytanie planszy z pliku, zwrocenie tablicy i jej rozmiarow
    board = []
    with open(file_name, 'r') as file:
        rows, columns = map(int, file.readline().split())
        for _ in range(rows):
            row = list(map(int, file.readline().split()))
            board.append(row)
    return board, [rows, columns]


def print_board(board):  # wypisanie planszy (CELE TESTOWE)
    for x in range(SIZE_X):
        for y in range(SIZE_Y):
            print(board[x][y], end=" ")
        print(" ")
    print(" ")


def split_into_chars(string):  # konwersja permutacji liter oznaczających porządek przeszukiwania sadziedztwa
    return [char for char in string]  # na tablice znakow

# WYWOLANIE (NA RAZIE): python main.py [PERMUTACJA] [PLIK Z PLANSZA] [ROZWIAZANIE] [STATYSTYKI]


args = sys.argv  # pobranie argumentow z linii wywolania programu (args[0] - nazwa programu)
ORDER = args[1]  # permutacja liter oznaczajaca porzadek przeszukiwania sasiedztwa
NEIGHBOUR_ORDER = split_into_chars(ORDER)  # konwersja ORDER na tablice charow
START_BOARD_FILE = args[2]  # nazwa pliku z plansza startowa
START_BOARD, SIZE = read_board(START_BOARD_FILE)  # pobranie planszy i jej rozmiaru z pliku
SIZE_X = SIZE[0]  # ilosc wierszy (rozmiar x)
SIZE_Y = SIZE[1]  # ilosc kolumn (rozmiar y)
SOLUTION_FILE = args[3]  # nazwa pliku na rozwiazanie
STATS_FILE = args[4]  # nazwa pliku na statystyki


def get_standard_board():  # wygenerowanie planszy wzorcowej dla danego rozmiaru planszy
    standard_board = [[0] * SIZE_Y for _ in range(SIZE_X)]
    number = 1
    for x in range(SIZE_X):
        for y in range(SIZE_Y):
            if x == SIZE_X - 1 and y == SIZE_Y - 1:
                standard_board[x][y] = 0
            else:
                standard_board[x][y] = number
                number += 1
    return standard_board


STANDARD_BOARD = get_standard_board()  # zapisanie planszy wzorcowej w tablicy


def find_blank_space(board):  # znalezienie wspolrzednych wolnego pola
    for x in range(SIZE_X):
        for y in range(SIZE_Y):
            if board[x][y] == BLANK:
                return [x, y]


def make_move(board, move):  # wykonanie ruchu
    bx, by = find_blank_space(board)  # bx, by - wspolrzedne wolnego pola
    tx, ty = 0, 0  # tx, ty - wspolrzedne pola, ktore bedzie przesuniete
    if move == UP:
        tx = bx - 1
        ty = by
    elif move == DOWN:
        tx = bx + 1
        ty = by
    elif move == RIGHT:
        tx = bx
        ty = by + 1
    elif move == LEFT:
        tx = bx
        ty = by - 1
    board[bx][by], board[tx][ty] = board[tx][ty], board[bx][by]  # zamiana pol miejscami


def undo_move(board, move):  # cofniecie ruchu
    if move == UP:
        make_move(board, DOWN)
    elif move == DOWN:
        make_move(board, UP)
    elif move == LEFT:
        make_move(board, RIGHT)
    elif move == RIGHT:
        make_move(board, LEFT)


def get_valid_moves(board, prev_move=None):  # pobranie listy ruchow dozwolonych dla danego stanu
    bx, by = find_blank_space(board)         # oprocz polozenia pola pustego sprawdza poprzednio wykonany ruch
    valid_moves = []                         # aby go nie powtorzyc
    if bx != SIZE_X - 1 and prev_move != UP:
        valid_moves.append(DOWN)
    if bx != 0 and prev_move != DOWN:
        valid_moves.append(UP)
    if by != 0 and prev_move != RIGHT:
        valid_moves.append(LEFT)
    if by != SIZE_Y - 1 and prev_move != LEFT:
        valid_moves.append(RIGHT)
    return valid_moves


def attempt_move(board, moves_made, moves_remaining, prev_move):  # f. rekurencyjna przeszukujaca stany (DFS)
    if moves_remaining < 0:  # przeszukuje, dopoki nie wykonano maksymalnej ilosci ruchow
        return False
    if board == STANDARD_BOARD:  # jezeli uzyskano plansze wzorcowa, to funkcja zwraca prawde
        return True
    for move in NEIGHBOUR_ORDER:  # dla kazdego ruchu w okreslonym porzadku ruchow
        if move in get_valid_moves(board, prev_move):  # sprawdzamy czy jest dozwolony i go wykonujemy
            make_move(board, move)
            moves_made.append(move)  # dodajemy do listy wykonany ruch
            if attempt_move(board, moves_made, moves_remaining - 1, move):  # jezeli po probie wykonania ruchu
                undo_move(board, move)  # otrzymamy plansze wzorcowa, cofamy kazdy wykonany uprzednio ruch i zwracamy
                return True  # prawde
            undo_move(board, move)  # jezeli wszystkie proby ruchu zakoncza sie porazka cofamy ruch i usuwamy jego
            moves_made.pop()  # oznaczenie z listy
    return False


solution_moves = []  # tablica na rozwiazanie z symbolami ruchow


def solve(board):  # metoda rozwiazujaca
    is_solved = attempt_move(board, solution_moves, MAX_MOVES, None)
    if is_solved:
        print_board(board)
        for move in solution_moves:
            print("Move: ", move)
            make_move(board, move)
            print()
            print_board(board)
            print()
        print('Solved in', len(solution_moves), 'moves:')
        print(', '.join(solution_moves))
        return True
    else:
        return False


start_time = time.time()  # rozpoczecie mierzenia czasu


if solve(START_BOARD):  # zapisanie do pliku w przypadku znalezienia rozwiazania
    duration = round((time.time() - start_time) * 1000, 3)
    with open(SOLUTION_FILE, "w") as file:
        file.write(f"{len(solution_moves)}\n")
        file.write(''.join(solution_moves))
    with open(STATS_FILE, "w") as file:
        file.write(f"{len(solution_moves)}\n")
        file.write(f"{duration} milisekund")
else:  # a tu w przypadku gdy rozwiazania nie ma
    duration = round((time.time() - start_time) * 1000, 3)
    with open(SOLUTION_FILE, "w") as file:
        file.write("-1\n")
    with open(STATS_FILE, "w") as file:
        file.write("-1\n")
        file.write(f"{duration} milisekund")
