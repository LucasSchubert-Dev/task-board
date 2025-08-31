import mysql.connector
import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    config = {
        "host": input("Host do MySQL (ex: localhost): "),
        "port": int(input("Porta do MySQL (ex: 3306): ")),
        "user": input("Usuário do MySQL: "),
        "password": input("Senha do MySQL: "),
        "database": input("Banco de dados (ex: taskboard): ")
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    return config

def get_connection():
    cfg = load_config()
    return mysql.connector.connect(**cfg)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    with open("schema.sql", "r") as f:
        cur.execute(f.read(), multi=True)
    conn.commit()
    conn.close()

def criar_board():
    nome = input("Nome do board: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO boards (name) VALUES (%s)", (nome,))
    conn.commit()
    conn.close()
    print("Board criado com sucesso!")

def listar_boards():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM boards")
    boards = cur.fetchall()
    conn.close()
    if not boards:
        print("Nenhum board encontrado.")
        return []
    for b in boards:
        print(f"{b[0]} - {b[1]}")
    return boards

def excluir_board():
    boards = listar_boards()
    if not boards: return
    bid = input("Digite o ID do board para excluir: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM boards WHERE id=%s", (bid,))
    conn.commit()
    conn.close()
    print("Board excluído.")

def menu_board(board_id):
    while True:
        print("\n--- Menu do Board ---")
        print("1. Criar coluna")
        print("2. Criar card")
        print("3. Listar cards")
        print("4. Mover card")
        print("0. Voltar")
        op = input("Escolha: ")

        if op == "1":
            criar_coluna(board_id)
        elif op == "2":
            criar_card(board_id)
        elif op == "3":
            listar_cards(board_id)
        elif op == "4":
            mover_card(board_id)
        elif op == "0":
            break

def criar_coluna(board_id):
    nome = input("Nome da coluna: ")
    pos = int(input("Posição da coluna: "))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO columns_board (board_id, name, position) VALUES (%s,%s,%s)", (board_id, nome, pos))
    conn.commit()
    conn.close()
    print("Coluna criada!")

def criar_card(board_id):
    titulo = input("Título do card: ")
    desc = input("Descrição: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM columns_board WHERE board_id=%s ORDER BY position", (board_id,))
    colunas = cur.fetchall()
    if not colunas:
        print("Crie pelo menos uma coluna antes.")
        conn.close()
        return
    for c in colunas:
        print(f"{c[0]} - {c[1]}")
    col_id = input("ID da coluna inicial: ")
    cur.execute("INSERT INTO cards (board_id, title, description, current_column_id) VALUES (%s,%s,%s,%s)", 
                (board_id, titulo, desc, col_id))
    conn.commit()
    conn.close()
    print("Card criado!")

def listar_cards(board_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT cards.id, cards.title, columns_board.name 
                   FROM cards 
                   LEFT JOIN columns_board ON cards.current_column_id=columns_board.id
                   WHERE cards.board_id=%s""", (board_id,))
    cards = cur.fetchall()
    conn.close()
    if not cards:
        print("Nenhum card.")
    else:
        for c in cards:
            print(f"{c[0]} - {c[1]} (Coluna: {c[2]})")

def mover_card(board_id):
    listar_cards(board_id)
    cid = input("ID do card: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM columns_board WHERE board_id=%s ORDER BY position", (board_id,))
    colunas = cur.fetchall()
    for c in colunas:
        print(f"{c[0]} - {c[1]}")
    nova_col = input("ID da nova coluna: ")
    cur.execute("UPDATE cards SET current_column_id=%s WHERE id=%s", (nova_col, cid))
    conn.commit()
    conn.close()
    print("Card movido!")

def main():
    init_db()
    while True:
        print("\n--- Menu Principal ---")
        print("1. Criar board")
        print("2. Selecionar board")
        print("3. Excluir board")
        print("0. Sair")
        op = input("Escolha: ")

        if op == "1":
            criar_board()
        elif op == "2":
            boards = listar_boards()
            if boards:
                bid = input("Digite o ID do board: ")
                menu_board(bid)
        elif op == "3":
            excluir_board()
        elif op == "0":
            break

if __name__ == "__main__":
    main()
