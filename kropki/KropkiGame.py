from Game import Game

from .KropkiBoard import KropkiBoard
from .KropkiBoard import N

# player: 1 - White, -1 - Black
class KropkiGame(Game):
    def __init__(self):
        pass

    def getInitBoard(self):
        return KropkiBoard.init()

    def getBoardSize(self):
        return (N+2, N+2)

    def getActionSize(self):
        return (N+2)*(N+2)

    def getNextState(self, board, player, action):
        b = KropkiBoard.clone(board)
        b.place(action, player)
        return (b, -player)

    def getValidMoves(self, board, player):
        valids = [0]*self.getActionSize()
        if board.NumEmptyFields > 0:
            cur = board.FirstEmptyField
            while True:
                valids[cur] = 1
                cur = board.Chains[cur]
                if cur == board.FirstEmptyField:
                    break
        return valids

    def getGameEnded(self, board, player):
        if board.NumEmptyFields > 0:
            return 0
        if board.WhiteCaptured == board.BlackCaptured:
            return 1e-4
        if player == 1 and (board.BlackCaptured > board.WhiteCaptured):
            return 1
        return -1

    def getCanonicalForm(self, board, player):
        if player == 1:
            return board
        return KropkiBoard.inverted(board)

    def getSymmetries(self, board, pi):
        return [(KropkiBoard.clone(board), pi)]

    def stringRepresentation(self, board):
        return board.toString()
