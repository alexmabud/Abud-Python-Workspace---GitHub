import random
import os

move = ['pedra', 'papel', 'tesoura']
player_count = 0
computer_count = 0

print(*'=========================')
print('Jogo Pedra, Papel e Tesoura')

def main_print():
    print('=========================')
    print('\nPlacar:')
    print('Você: {}'.format(player_count))
    print('Computador: {}'.format(computer_count))
    print('\n')
    print('Escolha seu lance:')
    print('0 - Papel | 1 - Pedra | 2 - Tesoura')

def select_move():
    return random.choice(move)

def get_player_move():
    while True:
        try:
            player_move = int(input('Digite seu lance: '))
            if player_move in [0, 1, 2]:
                return move[player_move]
            else:
                print('Escolha inválida. Tente novamente.')
        except ValueError:
            print('Entrada inválida. Tente novamente.')

def select_winner(player_move, computer_move):
    if player_move == computer_move:
        return 'Empate!'
    elif (player_move == 'papel' and computer_move == 'pedra') or \
         (player_move == 'pedra' and computer_move == 'tesoura') or \
         (player_move == 'tesoura' and computer_move == 'papel'):
        return 'Você ganhou!'
    else:
        return 'Computador ganhou!'

again = 1
while again == 1:
   
    os.system('cls' if os.name == 'nt' else 'clear')
    
    main_print()
    
    player_move = get_player_move()
    computer_move = select_move()
    
    print('Você escolheu: {}'.format(player_move))
    print('Computador escolheu: {}'.format(computer_move))
    
    winner = select_winner(player_move, computer_move)
    print(winner)
    
    if winner == 'Você ganhou!':
        player_count += 1
    elif winner == 'Computador ganhou!':
        computer_count += 1
    
    again = int(input('Deseja jogar novamente? (1 - Sim / 0 - Não): '))