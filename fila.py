from collections import deque
from typing import Optional
from cliente import Cliente

class FilaAtendimento:
    def __init__(self):
        self._itens: deque[Cliente] = deque()

    def enfileirar(self, cliente: Cliente) -> None:
        self._itens.append(cliente)

    def desenfileirar(self) -> Optional[Cliente]:
        if self.esta_vazia():
            return None
        return self._itens.popleft()

    def remover_por_cpf(self, cpf: str) -> Optional[Cliente]:
        cliente_removido = None
        for _ in range(len(self._itens)):
            c = self._itens.popleft()
            if c.cpf == cpf and cliente_removido is None:
                cliente_removido = c
            else:
                self._itens.append(c)
        return cliente_removido

    def buscar_por_cpf(self, cpf: str) -> Optional[Cliente]:
        for c in self._itens:
            if c.cpf == cpf:
                return c
        return None

    def esta_vazia(self) -> bool:
        return len(self._itens) == 0

    def tamanho(self) -> int:
        return len(self._itens)

    def listar(self) -> list[Cliente]:
        return list(self._itens)
