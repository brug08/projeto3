from jogo import Jogo
from filabacklog import FilaBacklog
from pilharecentes import PilhaRecentes
import csv


class SteamPy:

    def __init__(self):
        self.catalogo = []
        self.jogos_dict = {}
        self.backlog = FilaBacklog()
        self.recentes = PilhaRecentes()
        self.historico = []
        self.tempo_jogado = {}

    # =========================
    # CARREGAR DATASET
    # =========================
    def carregar_jogos(self, nome_arquivo):
        try:
            with open(nome_arquivo, encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)

                for linha in reader:
                    if len(linha) < 13:
                        continue

                    try:
                        jogo = Jogo(
                            linha[0], linha[1], linha[2], linha[3],
                            linha[4], linha[5],
                            float(linha[6]) if linha[6] else 0,
                            float(linha[7]) if linha[7] else 0,
                            float(linha[8]) if linha[8] else 0,
                            float(linha[9]) if linha[9] else 0,
                            float(linha[10]) if linha[10] else 0,
                            float(linha[11]) if linha[11] else 0,
                            linha[12]
                        )

                        self.catalogo.append(jogo)
                        self.jogos_dict[jogo.id_jogo] = jogo

                    except:
                        continue

            print("Catálogo carregado com sucesso!")

        except FileNotFoundError:
            print("ERRO: dataset.csv não encontrado.")

    # =========================
    # BUSCA
    # =========================
    def buscar_jogo_por_nome(self, termo):
        resultados = []

        for jogo in self.catalogo:
            if termo.lower() in jogo.titulo.lower():
                resultados.append(jogo)

        if not resultados:
            print("Nenhum jogo encontrado.")
        else:
            for j in resultados:
                print(j.exibir())

        return resultados

    # =========================
    # BACKLOG
    # =========================
    def adicionar_ao_backlog(self, jogo):
        self.backlog.enqueue(jogo)
        print("Jogo adicionado ao backlog.")

    def jogar_proximo(self):
        jogo = self.backlog.dequeue()

        if jogo:
            print("Jogando:", jogo.titulo)
            self.recentes.push(jogo)
            return jogo
        else:
            print("Backlog vazio.")
            return None

    def salvar_backlog(self):
        with open("backlog.txt", "w", encoding="utf-8") as f:
            for j in self.backlog.dados:
                f.write(j.linha_backlog() + "\n")

    def carregar_backlog(self):
        try:
            with open("backlog.txt", "r", encoding="utf-8") as f:
                for linha in f:
                    partes = linha.strip().split(";")
                    if len(partes) >= 1:
                        id_jogo = partes[0]
                        if id_jogo in self.jogos_dict:
                            self.backlog.enqueue(self.jogos_dict[id_jogo])
        except:
            pass

    # =========================
    # RECENTES
    # =========================
    def salvar_recentes(self):
        with open("recentes.txt", "w", encoding="utf-8") as f:
            for j in self.recentes.dados:
                f.write(j.linha_recentes() + "\n")

    def carregar_recentes(self):
        try:
            with open("recentes.txt", "r", encoding="utf-8") as f:
                for linha in f:
                    partes = linha.strip().split(";")
                    if len(partes) >= 1:
                        id_jogo = partes[0]
                        if id_jogo in self.jogos_dict:
                            self.recentes.push(self.jogos_dict[id_jogo])
        except:
            pass

    # =========================
    # SESSÃO
    # =========================
    def registrar_sessao(self, jogo, tempo):
        if jogo.id_jogo not in self.tempo_jogado:
            self.tempo_jogado[jogo.id_jogo] = 0

        self.tempo_jogado[jogo.id_jogo] += tempo
        total = self.tempo_jogado[jogo.id_jogo]

        if total < 2:
            status = "iniciado"
        elif total < 10:
            status = "em andamento"
        elif total < 20:
            status = "muito jogado"
        else:
            status = "concluido"

        self.historico.append((jogo.titulo, tempo, total, status))
        print(f"Sessão registrada: {jogo.titulo} ({tempo}h)")

    # =========================
    # DASHBOARD
    # =========================
    def exibir_dashboard(self):
        print("\n----- DASHBOARD -----")
        print("Total de jogos no catálogo:", len(self.catalogo))
        print("Total no backlog:", self.backlog.tamanho())
        print("Total recentes:", self.recentes.tamanho())
        print("Total sessões:", len(self.historico))
        print("Tempo total jogado:", sum(self.tempo_jogado.values()))

    # =========================
    # MOSTRAR RECENTES
    # =========================
    def mostrar_recentes(self):
        self.recentes.mostrar()


# =========================
# MENU
# =========================
def menu():
    sistema = SteamPy()

    sistema.carregar_jogos("dataset.csv")
    sistema.carregar_backlog()
    sistema.carregar_recentes()

    while True:
        print("\n===== MENU =====")
        print("1 - Buscar jogo")
        print("2 - Adicionar ao backlog")
        print("3 - Ver backlog")
        print("4 - Jogar próximo")
        print("5 - Ver recentes")
        print("6 - Registrar sessão")
        print("7 - Dashboard")
        print("0 - Sair")

        op = input("Escolha: ")

        if op == "1":
            termo = input("Digite o nome: ")
            sistema.buscar_jogo_por_nome(termo)

        elif op == "2":
            id_jogo = input("ID do jogo: ")
            if id_jogo in sistema.jogos_dict:
                sistema.adicionar_ao_backlog(sistema.jogos_dict[id_jogo])
            else:
                print("ID não encontrado.")

        elif op == "3":
            sistema.backlog.mostrar()

        elif op == "4":
            sistema.jogar_proximo()

        elif op == "5":
            sistema.mostrar_recentes()

        elif op == "6":
            id_jogo = input("ID do jogo: ")
            if id_jogo in sistema.jogos_dict:
                tempo = float(input("Tempo jogado (horas): "))
                sistema.registrar_sessao(sistema.jogos_dict[id_jogo], tempo)
            else:
                print("ID inválido.")

        elif op == "7":
            sistema.exibir_dashboard()

        elif op == "0":
            sistema.salvar_backlog()
            sistema.salvar_recentes()
            print("Dados salvos. Encerrando...")
            break

        else:
            print("Opção inválida.")


# EXECUÇÃO
if __name__ == "__main__":
    menu()