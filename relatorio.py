import sqlite3

conn = sqlite3.connect("banco.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        cpf TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        tipo_atendimento TEXT NOT NULL,
        saldo REAL NOT NULL,
        prioritario INTEGER NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf TEXT NOT NULL,
        data_hora TEXT NOT NULL,
        tipo TEXT NOT NULL,
        valor REAL NOT NULL,
        saldo_anterior REAL NOT NULL,
        saldo_resultante REAL NOT NULL,
        detalhe TEXT,
        FOREIGN KEY(cpf) REFERENCES clientes(cpf)
    )
""")
conn.commit()

print("\n=== CLIENTES CADASTRADOS ===")
cursor.execute("SELECT cpf, nome, saldo, prioritario FROM clientes")
clientes = cursor.fetchall()
if not clientes:
    print("Nenhum cliente cadastrado ainda.")
else:
    for c in clientes:
        prio = "Preferencial" if c[3] else "Convencional"
        print(f"CPF: {c[0]} | {c[1]:<15} | Saldo Atual: R$ {c[2]:>8.2f} | Fila: {prio}")

print("\n=== HISTÓRICO GERAL DE TRANSAÇÕES ===")
cursor.execute("SELECT cpf, data_hora, tipo, valor, saldo_anterior, saldo_resultante, detalhe FROM transacoes")
transacoes = cursor.fetchall()
if not transacoes:
    print("Nenhuma transação registrada.")
else:
    for t in transacoes:
        sinal = "-" if "SAQUE" in t[2] or "ENVIADO" in t[2] else "+"
        detalhe_txt = f" | {t[6]}" if t[6] else ""
        print(
            f"CPF: {t[0]} | [{t[1]}] {t[2]:<12} {sinal}R$ {t[3]:>8.2f} | "
            f"Antes: R$ {t[4]:>8.2f} -> Depois: R$ {t[5]:>8.2f}{detalhe_txt}"
        )

conn.close()
