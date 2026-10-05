from dataclasses import dataclass
from datetime import datetime

@dataclass
class Transacao:
    data_hora: str
    tipo: str
    valor: float
    saldo_anterior: float
    saldo_resultante: float
    detalhe: str

@dataclass
class Cliente:
    cpf: str
    id_cliente: int
    nome: str
    tipo_atendimento: str
    saldo: float = 0.0
    prioritario: bool = False

    def registrar_log(self, tipo: str, valor: float, saldo_antigo: float, detalhe: str = "") -> Transacao:
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return Transacao(
            data_hora=agora,
            tipo=tipo,
            valor=valor,
            saldo_anterior=saldo_antigo,
            saldo_resultante=self.saldo,
            detalhe=detalhe
        )

    def sacar(self, valor: float) -> tuple[bool, str, Transacao | None]:
        if valor <= 0:
            return False, "Valor de saque deve ser positivo.", None
        if valor > self.saldo:
            return False, f"Saldo insuficiente. Saldo disponível: R$ {self.saldo:.2f}", None
        
        saldo_antigo = self.saldo
        self.saldo -= valor
        log = self.registrar_log("SAQUE", valor, saldo_antigo, "")
        return True, f"Saque de R$ {valor:.2f} realizado com sucesso. Saldo restante: R$ {self.saldo:.2f}", log

    def depositar(self, valor: float) -> tuple[bool, str, Transacao | None]:
        if valor <= 0:
            return False, "Valor de depósito deve ser positivo.", None
        
        saldo_antigo = self.saldo
        self.saldo += valor
        log = self.registrar_log("DEPOSITO", valor, saldo_antigo, "")
        return True, f"Depósito de R$ {valor:.2f} realizado com sucesso. Novo saldo: R$ {self.saldo:.2f}", log

    def transferir_pix(self, destino: 'Cliente', valor: float) -> tuple[bool, str, Transacao | None, Transacao | None]:
        if valor <= 0:
            return False, "Valor da transferência deve ser positivo.", None, None
        if valor > self.saldo:
            return False, f"Saldo insuficiente para PIX. Saldo disponível: R$ {self.saldo:.2f}", None, None

        saldo_antigo_origem = self.saldo
        saldo_antigo_destino = destino.saldo

        self.saldo -= valor
        destino.saldo += valor

        log_origem = self.registrar_log("PIX_ENVIADO", valor, saldo_antigo_origem, f"Para: {destino.nome} ({destino.cpf})")
        log_destino = destino.registrar_log("PIX_RECEBIDO", valor, saldo_antigo_destino, f"De: {self.nome} ({self.cpf})")

        msg = f"PIX de R$ {valor:.2f} concluído com sucesso para {destino.nome}. Saldo atual: R$ {self.saldo:.2f}"
        return True, msg, log_origem, log_destino

    def extrato(self, historico_transacoes: list[Transacao]) -> str:
        tipo_fila = "Preferencial" if self.prioritario else "Convencional"
        linhas = [
            "\n================ EXTRATO BANCÁRIO DETALHADO ================",
            f"Titular: {self.nome:<20} CPF: {self.cpf}",
            f"Senha da Vez: #{self.id_cliente:03d} | Atendimento: {self.tipo_atendimento} | Fila: {tipo_fila}",
            f"Saldo Atual: R$ {self.saldo:.2f}",
            "---------------- HISTÓRICO DE TRANSAÇÕES -------------------"
        ]
        if not historico_transacoes:
            linhas.append("Nenhuma movimentação financeira registrada.")
        else:
            for t in historico_transacoes:
                sinal = "-" if "SAQUE" in t.tipo or "ENVIADO" in t.tipo else "+"
                detalhe_extra = f" | {t.detalhe}" if t.detalhe else ""
                linhas.append(
                    f"[{t.data_hora}] {t.tipo:<12} {sinal}R$ {t.valor:>8.2f} | "
                    f"Saldo Anterior: R$ {t.saldo_anterior:>8.2f} -> "
                    f"Saldo Novo: R$ {t.saldo_resultante:>8.2f}{detalhe_extra}"
                )
        linhas.append("=============================================================")
        return "\n".join(linhas)

    def descricao_formatada(self) -> str:
        tipo_fila = "Preferencial" if self.prioritario else "Convencional"
        return f"Senha #{self.id_cliente:03d} | CPF: {self.cpf} | Nome: {self.nome:<12} | Serviço: {self.tipo_atendimento:<10} | Fila: {tipo_fila:<12} | Saldo: R$ {self.saldo:.2f}"
