from re import findall
from math import inf
from random import choice


class Player:
    def __init__(self, name: str, char: str = None):
        if char is None:
            char = name[0].upper()
        self.name: str = name
        self.char: str = char[0]

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.name == other.name
        return False


class Item:
    def __init__(self, x, y, char):
        self.x: int = x
        self.y: int = y
        self.char: str = char

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"{self.char} at ({self.x},{self.y})"

    def location(self):
        return self.x+1, self.y+1


class Board:
    def __init__(self, p1, p2, width, height, moves=None):
        if moves is None:
            moves = []
        self.width = width
        self.height = height
        self.move_history = moves
        self.p1 = p1
        self.p2 = p2
        self.turn = self.p1 # after making a move, turn immediately switches to other player.

    def move(self, move: Item):
        self.move_history.append(move)
        self.turn = self.p2 if self.turn == self.p1 else self.p1

    def undo(self):
        self.move_history.pop()
        self.turn = self.p2 if self.turn == self.p1 else self.p1

    def evaluate_position(self) -> float | str:
        n_in_a_row = min(self.width, self.height)
        score = 0

        # evaluation is based on the person who just played a move. so self.turn.char is the opponent.
        # subtract score for other player
        for row in range(self.height):
            row_score = len([i for i in self.move_history if i.y == row and i.char == self.turn.char])
            score -= row_score ** 2
            if row_score >= n_in_a_row: return inf

        for col in range(self.width):
            col_score = len([i for i in self.move_history if i.x == col and i.char == self.turn.char])
            score -= col_score ** 2
            if col_score >= n_in_a_row: return inf

        for dia in range(min(0, self.width - self.height), max(0, self.width - self.height) + 1):
            diag_score = len([i for i in self.move_history if i.x - i.y == dia and i.char == self.turn.char])
            score -= diag_score ** 2
            if diag_score >= n_in_a_row: return inf

        for dia in range(min(self.width, self.height) - 1, max(self.width, self.height)):
            diag_score = len([i for i in self.move_history if i.x + i.y == dia and i.char == self.turn.char])
            score -= diag_score ** 2
            if diag_score >= n_in_a_row: return inf

        # add score for current player
        for row in range(self.height):
            row_score = len([i for i in self.move_history if i.y == row and not i.char == self.turn.char])
            score += row_score ** 2
            if row_score >= n_in_a_row: return -inf

        for col in range(self.width):
            col_score = len([i for i in self.move_history if i.x == col and not i.char == self.turn.char])
            score += col_score ** 2
            if col_score >= n_in_a_row: return -inf

        for dia in range(min(0, self.width - self.height), max(0, self.width - self.height) + 1):
            diag_score = len([i for i in self.move_history if i.x - i.y == dia and not i.char == self.turn.char])
            score += diag_score ** 2
            if diag_score >= n_in_a_row: return -inf

        for dia in range(min(self.width, self.height) - 1, max(self.width, self.height)):
            diag_score = len([i for i in self.move_history if i.x + i.y == dia and not i.char == self.turn.char])
            score += diag_score ** 2
            if diag_score >= n_in_a_row: return -inf

        # full board without a win is a draw
        if len(self.move_history) >= self.width * self.height:
            return 0
        return score

    def valid_moves(self) -> list:
        all_moves = {Item(x, y, self.turn.char)
                     for x in range(self.width)
                     for y in range(self.height)}
        valid_moves = list(all_moves - set(self.move_history))
        return valid_moves


class AIPlayer(Player):
    def __init__(self, name, char, difficulty):
        super().__init__(name, char)
        self.difficulty = difficulty

    @staticmethod
    def random_move(game: Board) -> Item:
        return choice(game.valid_moves())

    def negamax(self, board: Board, depth: int) -> int | float | str:
        evaluation = board.evaluate_position()
        if depth == 0 or evaluation == inf or evaluation == -inf or len(board.move_history) >= board.width * board.height:
            return evaluation
        value = -inf
        for move in board.valid_moves():
            board.move(move)
            value = max(value, -self.negamax(board, depth - 1))
            board.undo()
        return value

    def negamax_2(self, board: Board, depth: int, alpha, beta) -> int | float | str:
        evaluation = board.evaluate_position()
        if depth == 0 or evaluation == inf or evaluation == -inf or len(board.move_history) >= board.width * board.height:
            return evaluation

        moves = board.valid_moves()
        # sort move based on heuristic maybe
        value = -inf
        for move in moves:
            board.move(move)
            value = max(value, -self.negamax_2(board, depth - 1, -beta, -alpha))
            alpha = max(alpha, value)
            board.undo()
            if alpha > beta:
                break
        return value

    def think(self, board) -> Item:
        potential_moves = board.valid_moves()
        best_move = potential_moves[0]
        best_evaluation = -inf
        for move in potential_moves:
            board.move(move)
            move_evaluation = -self.negamax_2(board, self.difficulty, -inf, inf)
            # move_evaluation = -self.negamax(board, self.difficulty)
            board.undo()
            if move_evaluation > best_evaluation:
                best_move = move
                best_evaluation = move_evaluation
        if best_evaluation == inf: print(f'{self}: You may as well resign.')
        if best_evaluation == -inf: print(f"{self}: You must've gotten lucky...")
        if best_evaluation == 0: print(f'{self}: I foresee the most boring outcome.')
        return best_move


class TicTacToe:
    def __init__(self, p1: Player, p2: Player, width: int, height: int):
        self.players: list[Player] = [p1, p2]
        self.width: int = width
        self.height: int = height
        self.board = Board(self.players[0], self.players[1], self.width, self.height)

    def within_bounds(self, obj):
        if isinstance(obj, Item):
            return 0 <= obj.x < self.width and 0 <= obj.y < self.height
        return False

    def ask_input(self, player):
        numbers = findall(r'\d+', input('row, col = '))[:2]
        if len(numbers) < 2:
            print('Invalid input, please try again.')
            return self.ask_input(player)
        x, y = [int(num) - 1 for num in numbers]
        move_to_play = Item(x, y, player.char)

        if move_to_play not in self.board.valid_moves():
            print('Invalid position, please try again.')
            return self.ask_input(player)
        return move_to_play

    def display(self):
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        for item in self.board.move_history:
            grid[item.y][item.x] = item.char

        print(' ---' * self.width)
        for row in grid:
            print(f"| {' | '.join(row)} |")
            print(' ---' * self.width)

    def game(self):
        print(
            f"Starting game of size {self.width}x{self.height} for players {[str(player) for player in self.players]}.")
        self.display()
        winner = None
        while not winner:
            for player in self.players:
                if isinstance(player, AIPlayer):
                    print(f"{player.name} is thinking...")
                    self.board.move(player.think(self.board))
                elif isinstance(player, Player):
                    print(
                        f"Your turn, {player.name} playing as {player.char}.")
                    print(f"list of valid moves: {[move.location() for move in self.board.valid_moves()]}")
                    self.board.move(self.ask_input(player))
                self.display()
                evaluation = self.board.evaluate_position()
                if evaluation == -inf:
                    winner = player
                if len(self.board.move_history) >= self.width * self.height:
                    winner = Player('Nobody')
                if winner: break
        print(f"game has come to an end. {winner} has won.")


def main():
    human = Player('Brian', 'O')
    human_2 = Player('Cuttxo','#')
    evil_ai = AIPlayer('Beelzebub', 'X', 5)
    tic_tac_toe = TicTacToe(human, evil_ai, 6, 4)
    tic_tac_toe.game()


if __name__ == '__main__':
    main()