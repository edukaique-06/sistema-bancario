import sqlite3
from typing import Optional
from fila import FilaAtendimento
from cliente import Cliente, Transacao

class Banco:
    def __init__(self, db_path: str = "banco.db"):
        self.db_path = db_path
        self.fila_comum = FilaAtendimento()
        self.fila_prioritaria = FilaAtendimento()
        self._contador_prioritarios_atendidos = 0
        self.LIMITE_PRIORIDADE = 2
        self._inicializar_banco_dados()

    def _conectar(self):
        return sqlite3.connect(self.db_path, timeout=10.0)

    def _inicializar_banco_dados(self):
        with self._conectar() as conn:
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

    def persistir_cliente(self, cliente: Cliente):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (cpf, nome, tipo_atendimento, saldo, prioritario)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(cpf) DO UPDATE SET
                    nome=excluded.nome,
                    tipo_atendimento=excluded.tipo_atendimento,
                    saldo=excluded.saldo,
                    prioritario=excluded.prioritario
            """, (cliente.cpf, cliente.nome, cliente.tipo_atendimento, cliente.saldo, 1 if cliente.prioritario else 0))
            conn.commit()

    def persistir_transacao(self, cpf: str, transacao: Transacao):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transacoes (cpf, data_hora, tipo, valor, saldo_anterior, saldo_resultante, detalhe)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cpf,
                transacao.data_hora,
                transacao.tipo,
                transacao.valor,
                transacao.saldo_anterior,
                transacao.saldo_resultante,
                transacao.detalhe
            ))
            conn.commit()

    def carregar_transacoes(self, cpf: str) -> list[Transacao]:
        transacoes = []
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data_hora, tipo, valor, saldo_anterior, saldo_resultante, detalhe 
                FROM transacoes 
                WHERE cpf = ? 
                ORDER BY id ASC
            """, (cpf,))
            for linha in cursor.fetchall():
                transacoes.append(Transacao(
                    data_hora=linha[0],
                    tipo=linha[1],
                    valor=linha[2],
                    saldo_anterior=linha[3],
                    saldo_resultante=linha[4],
                    detalhe=linha[5]
                ))
        return transacoes

    def carregar_cliente_db(self, cpf: str) -> Optional[Cliente]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cpf, nome, tipo_atendimento, saldo, prioritario 
                FROM clientes 
                WHERE cpf = ?
            """, (cpf,))
            row = cursor.fetchone()
            if row:
                return Cliente(
                    cpf=row[0],
                    id_cliente=0,
                    nome=row[1],
                    tipo_atendimento=row[2],
                    saldo=row[3],
                    prioritario=bool(row[4])
                )
        return None

    def adicionar_cliente(self, cpf: str, id_cliente: int, nome: str, servico: str, saldo: float, prioritario: bool) -> Cliente:
        cliente_existente = self.carregar_cliente_db(cpf)
        if cliente_existente:
            cliente = Cliente(cpf, id_cliente, nome, servico, cliente_existente.saldo, prioritario)
        else:
            cliente = Cliente(cpf, id_cliente, nome, servico, saldo, prioritario)
            
        self.persistir_cliente(cliente)
        if prioritario:
            self.fila_prioritaria.enfileirar(cliente)
        else:
            self.fila_comum.enfileirar(cliente)
        return cliente

    def cancelar_por_cpf(self, cpf: str) -> tuple[bool, str]:
        removido = self.fila_prioritaria.remover_por_cpf(cpf)
        if removido:
            return True, f"Cliente {removido.nome} (CPF: {cpf}) removido da Fila Preferencial."
        
        removido = self.fila_comum.remover_por_cpf(cpf)
        if removido:
            return True, f"Cliente {removido.nome} (CPF: {cpf}) removido da Fila Convencional."

        return False, f"CPF {cpf} não encontrado nas filas ativas."

    def chamar_cliente(self) -> tuple[Cliente | None, str]:
        if self.fila_prioritaria.esta_vazia() and self.fila_comum.esta_vazia():
            return None, "Nenhum cliente aguardando na fila."

        if not self.fila_prioritaria.esta_vazia() and (
            self._contador_prioritarios_atendidos < self.LIMITE_PRIORIDADE or self.fila_comum.esta_vazia()
        ):
            cliente = self.fila_prioritaria.desenfileirar()
            self._contador_prioritarios_atendidos += 1
            tipo_chamada = "Preferencial"
        else:
            if not self.fila_comum.esta_vazia():
                cliente = self.fila_comum.desenfileirar()
                self._contador_prioritarios_atendidos = 0
                tipo_chamada = "Convencional"
            else:
                cliente = self.fila_prioritaria.desenfileirar()
                tipo_chamada = "Preferencial"

        msg = f"Guichê chamou [{tipo_chamada}]: {cliente.nome} (CPF: {cliente.cpf} | Senha #{cliente.id_cliente:03d})"
        return cliente, msg

    def buscar_cliente_geral(self, cpf: str) -> Optional[Cliente]:
        c = self.fila_prioritaria.buscar_por_cpf(cpf)
        if c:
            return c
        c = self.fila_comum.buscar_por_cpf(cpf)
        if c:
            return c
        return self.carregar_cliente_db(cpf)

    def status_filas(self) -> dict:
        total_prio = self.fila_prioritaria.tamanho()
        total_com = self.fila_comum.tamanho()
        if total_prio == 0 and total_com == 0:
            proximo = "Nenhum"
        elif total_prio > 0 and (self._contador_prioritarios_atendidos < self.LIMITE_PRIORIDADE or total_com == 0):
            proximo = "Fila Preferencial"
        else:
            proximo = "Fila Convencional" if total_com > 0 else "Fila Preferencial"

        return {
            "total_prioritaria": total_prio,
            "total_comum": total_com,
            "proximo_esperado": proximo
        }
