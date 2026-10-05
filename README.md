# 🏦 Sistema Bancário Modular com Filas e SQLite

Sistema de gestão de atendimento bancário desenvolvido em Python, integrando estruturas de dados em memória para controle de filas e persistência relacional com SQLite.

## 📌 Funcionalidades

- **Gerenciamento de Filas com Prioridade:** Alternância automática na proporção 2:1 entre Fila Preferencial e Fila Convencional utilizando `collections.deque`.
- **Operações Bancárias:** Saque, depósito e transferência PIX com atualização atômica de saldos.
- **Auditoria Financeira:** Histórico completo de transações com timestamp, identificação da operação, saldo anterior e saldo resultante.
- **Persistência Relacional:** Dados de clientes e transações armazenados localmente via SQLite (`banco.db`).
- **Validação Defensiva:** Sanitização e validação de entrada de CPF (11 dígitos), entradas monetárias e confirmações.

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+** (módulos nativos: `sqlite3`, `collections`, `dataclasses`, `datetime`)
- **SQLite3**

## 📂 Estrutura do Projeto

```text
sistema-banco/
├── cliente.py       # Modelo de dados do Cliente e logs de transação
├── fila.py          # Implementação da estrutura de dados da Fila
├── banco.py         # Regras de negócio, filas e persistência SQLite
├── main.py          # Interface CLI e fluxo principal
└── relatorio.py     # Script para auditoria e listagem de transações
```

## 🚀 Como Executar

1. Clone o repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)
   cd NOME_DO_REPOSITORIO
   ```

2. Execute o sistema principal:
   ```bash
   python main.py
   ```

3. (Opcional) Para visualizar o relatório de auditoria do banco:
   ```bash
   python relatorio.py
   ```
