from banco import Banco
from cliente import Cliente

def ler_cpf(mensagem: str = "CPF do cliente (11 dígitos): ") -> str:
    while True:
        entrada = input(mensagem).strip().replace(".", "").replace("-", "")
        if len(entrada) == 11 and entrada.isdigit():
            return entrada
        print("Erro: O CPF deve conter exatamente 11 dígitos numéricos. Digite novamente.")

def ler_sim_ou_nao(mensagem: str) -> bool:
    while True:
        entrada = input(mensagem).strip().lower()
        if entrada in ["s", "sim"]:
            return True
        elif entrada in ["n", "nao", "não"]:
            return False
        print("Erro: Entrada inválida. Digite apenas 'sim' ou 'nao'.")

def ler_servico() -> str:
    opcoes_validas = {
        "saque": "Saque",
        "deposito": "Deposito",
        "depósito": "Deposito",
        "gerencia": "Gerencia",
        "gerência": "Gerencia"
    }
    while True:
        entrada = input("Serviço desejado (Saque, Deposito, Gerencia): ").strip().lower()
        if entrada in opcoes_validas:
            return opcoes_validas[entrada]
        print("Erro: Serviço inválido. Escolha apenas entre Saque, Deposito ou Gerencia.")

def ler_valor_positivo(mensagem: str) -> float:
    while True:
        try:
            valor = float(input(mensagem).strip())
            if valor > 0:
                return valor
            print("Erro: O valor deve ser maior que zero.")
        except ValueError:
            print("Erro: Digite um número válido.")

def exibir_menu():
    print("\n================ SISTEMA BANCÁRIO ================")
    print("1. Inserir cliente na fila")
    print("2. Chamar próximo cliente para atendimento")
    print("3. Cancelar senha / Desistência da fila por CPF")
    print("4. Consultar extrato e histórico de transações por CPF")
    print("5. Visualizar status das filas")
    print("0. Sair")
    print("==================================================")

def realizar_atendimento(cliente: Cliente, agencia: Banco):
    print(f"\n--- ATENDIMENTO EM ANDAMENTO ---")
    print(f"Cliente: {cliente.nome} | CPF: {cliente.cpf} | Serviço: {cliente.tipo_atendimento}")
    print(f"Saldo em conta: R$ {cliente.saldo:.2f}")

    servico = cliente.tipo_atendimento.strip().lower()

    if servico == "saque":
        valor = ler_valor_positivo("Informe o valor do saque (R$): ")
        sucesso, msg, log = cliente.sacar(valor)
        print(msg)
        if sucesso and log:
            agencia.persistir_transacao(cliente.cpf, log)

    elif servico == "deposito":
        valor = ler_valor_positivo("Informe o valor do depósito (R$): ")
        sucesso, msg, log = cliente.depositar(valor)
        print(msg)
        if sucesso and log:
            agencia.persistir_transacao(cliente.cpf, log)

    elif servico == "gerencia":
        while True:
            print("\n--- MENU GERENCIAL ---")
            print("1. Transferência PIX por CPF")
            print("2. Consultar extrato")
            print("3. Alterar tipo de serviço")
            print("0. Concluir atendimento gerencial")
            sub_op = input("Opção gerencial: ").strip()

            if sub_op == "1":
                cpf_dest = ler_cpf("Informe o CPF do destinatário: ")
                if cpf_dest == cliente.cpf:
                    print("Erro: Não é permitido transferir PIX para si mesmo.")
                else:
                    destinatario = agencia.buscar_cliente_geral(cpf_dest)
                    if not destinatario:
                        print("Destinatário com esse CPF não foi encontrado.")
                    else:
                        valor_pix = ler_valor_positivo(f"Valor a transferir para {destinatario.nome} (R$): ")
                        sucesso, msg_pix, log_origem, log_destino = cliente.transferir_pix(destinatario, valor_pix)
                        print(msg_pix)
                        if sucesso and log_origem and log_destino:
                            agencia.persistir_transacao(cliente.cpf, log_origem)
                            agencia.persistir_transacao(destinatario.cpf, log_destino)
                            agencia.persistir_cliente(destinatario)
            elif sub_op == "2":
                logs = agencia.carregar_transacoes(cliente.cpf)
                print(cliente.extrato(logs))
            elif sub_op == "3":
                novo = ler_servico()
                cliente.tipo_atendimento = novo
                print(f"Serviço alterado para: {cliente.tipo_atendimento}")
            elif sub_op == "0":
                break
            else:
                print("Opção inválida.")

    agencia.persistir_cliente(cliente)
    print("Atendimento finalizado com sucesso.")

def main():
    agencia = Banco()
    contador_senha = 1

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cpf = ler_cpf("Digite o CPF (apenas 11 números): ")
            nome = input("Nome do cliente: ").strip()
            while not nome:
                print("Erro: O nome não pode ser vazio.")
                nome = input("Nome do cliente: ").strip()

            servico = ler_servico()

            cliente_salvo = agencia.carregar_cliente_db(cpf)
            if cliente_salvo:
                saldo = cliente_salvo.saldo
                print(f"Cliente já cadastrado. Saldo atual: R$ {saldo:.2f}")
            else:
                while True:
                    try:
                        entrada_saldo = input("Saldo inicial da conta (R$): ").strip()
                        saldo = float(entrada_saldo) if entrada_saldo else 0.0
                        if saldo >= 0:
                            break
                        print("Erro: O saldo não pode ser negativo.")
                    except ValueError:
                        print("Erro: Digite um número válido para o saldo.")

            eh_prio = ler_sim_ou_nao("Atendimento preferencial (sim/nao)? ")

            c = agencia.adicionar_cliente(cpf, contador_senha, nome, servico, saldo, eh_prio)
            tipo_desc = "Preferencial" if eh_prio else "Convencional"
            print(f"Senha #{c.id_cliente:03d} gerada para {c.nome} (CPF: {c.cpf}) na fila [{tipo_desc}].")
            contador_senha += 1

        elif opcao == "2":
            cliente, msg = agencia.chamar_cliente()
            print(f"\n{msg}")
            if cliente:
                realizar_atendimento(cliente, agencia)

        elif opcao == "3":
            cpf_canc = ler_cpf("Informe o CPF para cancelamento da fila: ")
            _, msg = agencia.cancelar_por_cpf(cpf_canc)
            print(msg)

        elif opcao == "4":
            cpf_busca = ler_cpf("Informe o CPF do cliente para ver extrato: ")
            c = agencia.buscar_cliente_geral(cpf_busca)
            if c:
                logs = agencia.carregar_transacoes(c.cpf)
                print(c.extrato(logs))
            else:
                print("Cliente não encontrado com esse CPF.")

        elif opcao == "5":
            status = agencia.status_filas()
            print("\n--- FILAS ---")
            print(f"Preferencial: {status['total_prioritaria']} cliente(s)")
            print(f"Convencional: {status['total_comum']} cliente(s)")
            print(f"Próxima chamada prevista: {status['proximo_esperado']}")

            if status['total_prioritaria'] > 0:
                print("\nAguardando Fila Preferencial:")
                for cl in agencia.fila_prioritaria.listar():
                    print("  " + cl.descricao_formatada())

            if status['total_comum'] > 0:
                print("\nAguardando Fila Convencional:")
                for cl in agencia.fila_comum.listar():
                    print("  " + cl.descricao_formatada())

        elif opcao == "0":
            print("Encerrando sistema.")
            break
        else:
            print("Opção inválida. Escolha entre 0 e 5.")

if __name__ == "__main__":
    main()
