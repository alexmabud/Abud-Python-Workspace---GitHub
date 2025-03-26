import os
import random

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  
        self.current_winner = None  

    def print_board(self):
        
        for row in [self.board[i * 3:(i + 1) * 3] for i in range(3)]:
            print('| ' + ' | '.join(row) + ' |')

    @staticmethod
    def print_board_positions():
        
        print("\nPosições do tabuleiro:")
        for row in [[str(i) for i in range(j * 3, (j + 1) * 3)] for j in range(3)]:
            print('| ' + ' | '.join(row) + ' |')

    def make_move(self, square, letter):
       
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.check_winner(square, letter):
                self.current_winner = letter
            return True
        return False

    def check_winner(self, square, letter):
        
        row_ind = square // 3
        row = self.board[row_ind * 3:(row_ind + 1) * 3]
        if all([spot == letter for spot in row]):
            return True

        
        col_ind = square % 3
        column = [self.board[col_ind + i * 3] for i in range(3)]
        if all([spot == letter for spot in column]):
            return True

       
        if square % 2 == 0:  
            diagonal1 = [self.board[i] for i in [0, 4, 8]]  
            if all([spot == letter for spot in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]  
            if all([spot == letter for spot in diagonal2]):
                return True

        return False

    def empty_squares(self):
        
        return ' ' in self.board

    def available_moves(self):
        
        return [i for i, spot in enumerate(self.board) if spot == ' ']

    def num_empty_squares(self):
        
        return self.board.count(' ')

def play(game, x_player, o_player, print_game=True):
    
    if print_game:
        game.print_board_positions()

    letter = 'X'  # Começa com 'X'
    while game.empty_squares():
        if letter == 'O':
            square = o_player.get_move(game)
        else:
            square = x_player.get_move(game)

        if game.make_move(square, letter):
            if print_game:
                print(f'\n{letter} faz um movimento na posição {square}')
                game.print_board()
                print('')  # Linha em branco

            if game.current_winner:
                if print_game:
                    print(f'{letter} venceu!')
                return letter

           
            letter = 'O' if letter == 'X' else 'X'

        if game.num_empty_squares() == 0:
            if print_game:
                print('Empate!')
            return None

class HumanPlayer:
    def __init__(self, letter):
        self.letter = letter

    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            square = input(f'{self.letter}, escolha uma posição (0-8): ')
            try:
                val = int(square)
                if val not in game.available_moves():
                    raise ValueError
                valid_square = True
            except ValueError:
                print('Posição inválida. Tente novamente.')
        return val

class RandomComputerPlayer:
    def __init__(self, letter):
        self.letter = letter

    def get_move(self, game):
        square = random.choice(game.available_moves())
        return square

if __name__ == '__main__':
    t = TicTacToe()
    x_player = HumanPlayer('X')
    o_player = HumanPlayer('O')  
    play(t, x_player, o_player, print_game=True)