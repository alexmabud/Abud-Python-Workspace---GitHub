import random
import seaborn as sns

class Academia:
    def __init__(self):
        self.halteres = [i for i in range(10, 36, 2)]  # Halteres pares de 10 a 36 kg
        self.porta_halteres = {}
        self.reiniciar_dia()

    def reiniciar_dia(self):
        """Reinicia o dia, organizando os halteres em suas posições corretas."""
        self.porta_halteres = {i: i for i in self.halteres}

    def listar_halteres(self):
        """Retorna uma lista de halteres disponíveis."""
        return [peso for peso in self.porta_halteres.values() if peso != 0]

    def pegar_haltere(self, peso):
        """
        Remove um haltere da posição correspondente.
        Retorna o peso do haltere ou None se não estiver disponível.
        """
        for posicao, valor in self.porta_halteres.items():
            if valor == peso:
                self.porta_halteres[posicao] = 0
                return peso
        return None

    def listar_espacos(self):
        """Retorna uma lista de posições vazias no porta-halteres."""
        return [posicao for posicao, peso in self.porta_halteres.items() if peso == 0]

    def devolver_haltere(self, posicao, peso):
        """
        Devolve um haltere para a posição especificada.
        Levanta um erro se a posição for inválida.
        """
        if posicao not in self.porta_halteres:
            raise ValueError(f"Posição {posicao} inválida.")
        self.porta_halteres[posicao] = peso

    def calcular_caos(self):
        """
        Calcula o nível de caos no porta-halteres.
        Retorna a proporção de halteres fora de suas posições originais.
        """
        desalinhados = sum(1 for posicao, peso in self.porta_halteres.items() if posicao != peso)
        return desalinhados / len(self.porta_halteres)

class Usuario:
    def __init__(self, tipo, academia):
        self.tipo = tipo
        self.academia = academia
        self.peso = 0

    def iniciar_treino(self):
        """Escolhe um haltere aleatório e o pega para o treino."""
        lista_peso = self.academia.listar_halteres()
        if not lista_peso:
            print("Nenhum haltere disponível para treino.")
            return
        self.peso = random.choice(lista_peso)
        self.academia.pegar_haltere(self.peso)

    def finalizar_treino(self):
        """Devolve o haltere após o treino."""
        espacos = self.academia.listar_espacos()
        if not espacos:
            print("Nenhum espaço disponível para devolver o haltere.")
            return

        if self.tipo == 1:  # Usuário organizado
            if self.peso in self.academia.halteres:
                self.academia.devolver_haltere(self.peso, self.peso)
        else:  # Usuário desorganizado
            pos = random.choice(espacos)
            self.academia.devolver_haltere(pos, self.peso)
        self.peso = 0

# Instância da academia
academia = Academia()

# Criação de usuários
usuarios = [Usuario(1, academia) for _ in range(10)]  # 10 usuários organizados
usuarios += [Usuario(2, academia) for _ in range(1)]  # 1 usuário desorganizado
random.shuffle(usuarios)

# Lista para armazenar os níveis de caos
list_chaos = []

# Simulação de 10 dias de treino
for i in range(10):
    random.shuffle(usuarios)
    for user in usuarios:
        user.iniciar_treino()
    for user in usuarios:
        user.finalizar_treino()
    list_chaos.append(academia.calcular_caos())

# Exibe o estado final do porta-halteres e o nível de caos
print("Estado final do porta-halteres:", academia.porta_halteres)
print("Níveis de caos ao longo dos dias:", list_chaos)

# Visualização dos níveis de caos
sns.displot(list_chaos)