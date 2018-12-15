import numpy as np

EMPTY=0
WHITE=1
BLACK=-1
WHITE_WALL=2
BLACK_WALL=-2
CAPTURED_WHITE=3
CAPTURED_BLACK=-3
EMPTY_SURROUNDED_BY_WHITE=4
EMPTY_SURROUNDED_BY_BLACK=-4

N = 10
INDICES_AROUND = [-(N+2)-1, -(N+2), -(N+2)+1, 1, (N+2)+1, N+2, (N+2)-1, -1]
DXS = [-1, 0, 1, 1, 1, 0, -1, -1]
DYS = [-1, -1, -1, 0, 1, 1, 1, 0]


def _indexToX(index):
    return index % (N + 2) - 1;
def _indexToY(index):
    return index / (N + 2) - 1
def _indexToCoords(index):
    return _indexToX(index), _indexToY(index)
def _indexOnBoard(index):
  x, y = _indexToCoords(index);
  return x >= 0 and x < N and y >= 0 and y < N


class KropkiBoard():
    def __init__(self):
        pass

    def coordsToIndex(x, y):
        return (y+1)*(N+2)+x+1

    def place(self, index, player):
        assert self.Pieces[index] == EMPTY
        self._removeEmptyField(index)
        self.Pieces[index] = player
        self.Chains[index] = index
        self.Areas[index] = 1
        self._markSurroundedAreas(index, player)
        self._mergeAdjacentChains(index, player)

    def _removeEmptyField(self, index):
        assert self.NumEmptyFields > 0
        self.NumEmptyFields -= 1
        nextEmptyField = self.Chains[index]
        prevEmptyField = self.Areas[index]
        assert self.NumEmptyFields == 0 or self.Pieces[nextEmptyField] == EMPTY, "_removeEmptyField(%d), NumEmpty: %d, nextEmptyField: %d, Pieces[nextEmptyField]: %d" % (index, self.NumEmptyFields, nextEmptyField, self.Pieces[nextEmptyField])
        assert self.NumEmptyFields == 0 or self.Pieces[prevEmptyField] == EMPTY, "_removeEmptyField(%d), NumEmpty: %d, prevEmptyField: %d, Pieces[prevEmptyField]: %d" % (index, self.NumEmptyFields, prevEmptyField, self.Pieces[prevEmptyField])
        self.Areas[nextEmptyField] = prevEmptyField
        self.Chains[prevEmptyField] = nextEmptyField
        if index == self.FirstEmptyField:
            self.FirstEmptyField = nextEmptyField

    def _markSurroundedAreas(self, index, side):
        assert _indexOnBoard(index), "_markSurroundedAreas((%d,%d),%d" % (_indexToX(index),_indexToY(index),side)
        piece = self.Pieces[index]
        separatedGroupBegins, separatedGroupEnds = [],[]
        requiredSeparation = 0
        for i in range(8):
            neighbourIndex = index + INDICES_AROUND[i]
            neighbourPiece = self.Pieces[neighbourIndex]
            if not KropkiBoard._piecesMayBelongToSameChain(piece, neighbourPiece):
                requiredSeparation -= 1
                continue
            if requiredSeparation > 0:
                separatedGroupEnds[-1] = i
                requiredSeparation = 1 + (i%2)
                continue
            separatedGroupBegins.append(i)
            separatedGroupEnds.append(i)
            requiredSeparation = 1 + (i%2)
        if len(separatedGroupBegins) <= 1:
            return
        if separatedGroupEnds[-1] == 7 and separatedGroupBegins[0] <= 1:
            separatedGroupBegins[0] = separatedGroupBegins[-1]
            separatedGroupBegins.pop()
            separatedGroupEnds.pop()
        if len(separatedGroupBegins) <= 1:
            return

        y = _indexToY(index)
        for i,si in enumerate(separatedGroupBegins):
            iIndex = index + INDICES_AROUND[si]
            iChain = self.Chains[iIndex]
            iArea = (0 if iIndex == iChain else self.Areas[iIndex]) + DXS[si] * (y + y + DYS[si])
            for j,sj in enumerate(separatedGroupBegins[i+1:]):
                jIndex = index + INDICES_AROUND[sj]
                jChain = self.Chains[jIndex];
                if iChain != jChain:
                    continue
                jArea = (0 if jIndex == jChain else self.Areas[jIndex]) + DXS[sj] * (y + y + DYS[sj])
                assert iArea != jArea
                if jArea - iArea > 0:
                    k = (separatedGroupEnds[i]+1)%8
                    while k != separatedGroupBegins[j]:
                        self._floodFillFrom(index + INDICES_AROUND[k], side)
                        k=(k+1)%8
                else:
                    k = (separatedGroupEnds[j]+1)%8
                    while k != separatedGroupBegins[i]:
                        self._floodFillFrom(index + INDICES_AROUND[k], side)
                        k=(k+1)%8

    def _floodFillFrom(self, index, side):
        assert _indexOnBoard(index), "_floodFillFrom((%d,%d), %d)" % (_indexToX(index), _indexToY(index), side)
        capture = False
        piece = self.Pieces[index]
        if piece == EMPTY:
            if side == WHITE:
                self.Pieces[index] = EMPTY_SURROUNDED_BY_WHITE
            else:
                self.Pieces[index] = EMPTY_SURROUNDED_BY_BLACK
            self._removeEmptyField(index)
        elif piece == WHITE or piece == WHITE_WALL:
            if side == WHITE:
                self.Pieces[index] = WHITE_WALL
                return
            self.Pieces[index] = CAPTURED_WHITE
            self.WhiteCaptured += 1
            capture = True
        elif piece == BLACK or piece == BLACK_WALL:
            if side == BLACK:
                self.Pieces[index] = BLACK_WALL
                return
            self.Pieces[index] = CAPTURED_BLACK
            self.BlackCaptured += 1
            capture = True
        elif piece == CAPTURED_WHITE:
            if side == BLACK:
                return
            self.Pieces[index] = WHITE_WALL
            self.WhiteCaptured -= 1
        elif piece == CAPTURED_BLACK:
            if side == WHITE:
                return
            self.Pieces[index] = BLACK_WALL
            self.BlackCaptured -= 1
        elif piece == EMPTY_SURROUNDED_BY_WHITE:
            if side == WHITE:
                return
            self.Pieces[index] = EMPTY_SURROUNDED_BY_BLACK
        else:
            assert piece == EMPTY_SURROUNDED_BY_BLACK
            if side == BLACK:
                return
            self.Pieces[index] = EMPTY_SURROUNDED_BY_WHITE
        self._floodFillFrom(index - 1, side)
        self._floodFillFrom(index + 1, side)
        self._floodFillFrom(index - (N+2), side)
        self._floodFillFrom(index + (N+2), side)
        if not capture:
            return
        chain = self.Chains[index]
        for i in [1, 3, 5, 7]:
            neighbourIndex = index + INDICES_AROUND[i]
            neighbourState = self.Pieces[neighbourIndex]
            nextNeighbourIndex = index + INDICES_AROUND[(i+1)%8]
            nextNeighbourState = self.Pieces[nextNeighbourIndex]
            nextNeighbourChain = self.Chains[nextNeighbourIndex]
            nextNextNeighbourIndex = index + INDICES_AROUND[(i+2)%8]
            nextNextNeighbourState = self.Pieces[nextNextNeighbourIndex]
            if side == BLACK and neighbourState == BLACK_WALL and (
                    nextNeighbourState == WHITE or nextNeighbourState == WHITE_WALL) and nextNextNeighbourState == BLACK_WALL and chain == nextNeighbourChain:
                if nextNeighbourChain != nextNeighbourIndex:
                    self._makeRoot(nextNeighbourIndex, nextNeighbourState, nextNeighbourChain)
            elif side == WHITE and neighbourState == WHITE_WALL and (
                    nextNeighbourState == BLACK or nextNeighbourState == BLACK_WALL
            ) and nextNextNeighbourState == WHITE_WALL and chain == nextNeighbourChain:
                if nextNeighbourChain != nextNeighbourIndex:
                    self._makeRoot(nextNeighbourIndex, nextNeighbourState, nextNeighbourChain)
        self.Chains[index] = index
        self.Areas[index] = 1


    def _makeRoot(self, index, currentState, currentChain):
        self.Chains[index] = index
        self.Areas[index] = 1

        isToReRoot = []
        for i in range(8):
            neighbourIndex = index + INDICES_AROUND[i]
            if self.Chains[neighbourIndex] == currentChain and KropkiBoard._piecesMayBelongToSameChain(currentState, self.Pieces[neighbourIndex]):
                self.Chains[neighbourIndex] = index
                isToReRoot.append(i)
        for dir in isToReRoot:
            neighbourIndex = index + INDICES_AROUND[dir]
            self._reRootPiecesTo(currentChain, index, neighbourIndex, 0, dir)

    def _reRootPiecesTo(self, sourceChain, targetChain, currentIndex, currentArea, chainDirection):
        self.Chains[currentIndex] = targetChain
        if targetChain != currentIndex:
            y = _indexToY(currentIndex)
            dx = -DXS[chainDirection]
            dy = -DYS[chainDirection]
            currentArea += dx * (y+y+dy)
        self.Areas[currentIndex] = currentArea
        self.Areas[targetChain] += 1

        currentState = self.Pieces[currentIndex]

        isToReRoot = []
        for i in range(8):
            neighbourIndex = currentIndex + INDICES_AROUND[i]
            if self.Chains[neighbourIndex] == sourceChain and KropkiBoard._piecesMayBelongToSameChain(currentState, self.Pieces[neighbourIndex]):
                self.Chains[neighbourIndex] = targetChain
                isToReRoot.append(i)
        for dir in isToReRoot:
            neighbourIndex = currentIndex + INDICES_AROUND[dir]
            self._reRootPiecesTo(sourceChain, targetChain, neighbourIndex, currentArea, dir)

    def _mergeAdjacentChains(self, index, side):
        piece = self.Pieces[index]
        largestNeighbourChain = 0
        largestNeighbourChainI = 0
        largestNeighbourChainSize = 0
        neighbourChainIs= []
        for i in range(8):
            neighbourIndex = index + INDICES_AROUND[i]
            neighbourPiece = self.Pieces[neighbourIndex]
            if KropkiBoard._piecesMayBelongToSameChain(piece, neighbourIndex):
                neighbourChainIs.append(i)
                neighbourChain = self.Chains[neighbourIndex]
                neighbourChainSize = self.Areas[neighbourChain]
                if neighbourChainSize > largestNeighbourChainSize or (
                        neighbourChainSize == largestNeighbourChainSize and largestNeighbourChainSize % 2 == 0 and i % 2 == 1):
                    largestNeighbourChain = neighbourChain
                    largestNeighbourChainI = i
                    largestNeighbourChainSize = neighbourChainSize
        if largestNeighbourChainSize == 0:
            return
        largestNeighbourChainIndex = INDICES_AROUND[largestNeighbourChainI]
        assert self.Areas[self.Chains[index]] > 0
        self.Chains[index] = largestNeighbourChain
        self.Areas[largestNeighbourChain] += 1
        dx, dy = DXS[largestNeighbourChainI], DYS[largestNeighbourChainI]
        y = _indexToY(index)
        area = (0 if largestNeighbourChainIndex == largestNeighbourChain else self.Areas[largestNeighbourChainIndex]) + dx * (y + y + dy)
        self.Areas[index] = area
        for neighbourI in neighbourChainIs:
            neighbourIndex = index + INDICES_AROUND[neighbourI]
            neighbourChain = self.Chains[neighbourIndex]
            if neighbourChain == largestNeighbourChain:
                continue
            self._reRootPiecesTo(neighbourChain, largestNeighbourChain, neighbourIndex, area, neighbourI)

    def toString(self):
        s = []
        a = ord('H')
        for piece in np.nditer(self.Pieces):
            s.append(chr(a+piece))
        return ''.join(s)

    def _piecesMayBelongToSameChain(piece1, piece2):
        if piece1 == WHITE or piece1 == WHITE_WALL:
            return piece2 == WHITE or piece2 == WHITE_WALL
        if piece1 == BLACK or piece1 == BLACK_WALL:
            return piece2 == BLACK or piece2 == BLACK_WALL
        return False

    @classmethod
    def initEmpty(cls):
        board = cls()
        board.NumEmptyFields = N * N
        board.WhiteCaptured = 0
        board.BlackCaptured = 0
        arraySize = (N+2)*(N+2)
        board.Pieces = np.array([EMPTY]*arraySize, dtype=np.int8)
        nextFree = [0]*arraySize
        prevFree = [0]*arraySize
        for x in range(N):
            nextX = x+1 if x < N-1 else 0
            prevX = x-1 if x > 0 else N-1
            for y in range(N):
                nextY = y if x < N-1 else (y+1 if y < N-1 else 0)
                prevY = y if x > 0 else (y-1 if y > 0 else N-1)
                index = KropkiBoard.coordsToIndex(x, y)
                nextFree[index] = KropkiBoard.coordsToIndex(nextX, nextY)
                prevFree[index] = KropkiBoard.coordsToIndex(prevX, prevY)
        board.Chains = np.array(nextFree, dtype=np.uint16)
        board.Areas = np.array(prevFree, dtype=np.int16)
        board.FirstEmptyField = KropkiBoard.coordsToIndex(0, 0)
        return board

    @classmethod
    def init(cls):
        board = KropkiBoard.initEmpty()
        board.place(KropkiBoard.coordsToIndex(N // 2, N // 2), 1)
        board.place(KropkiBoard.coordsToIndex((N // 2) + 1, (N // 2) + 1), 1)
        board.place(KropkiBoard.coordsToIndex(N // 2, (N // 2) + 1), -1)
        board.place(KropkiBoard.coordsToIndex((N // 2) + 1, N // 2), -1)
        return board

    @classmethod
    def clone(cls, board):
        copy = cls()
        copy.NumEmptyFields = board.NumEmptyFields
        copy.WhiteCaptured = board.WhiteCaptured
        copy.BlackCaptured = board.BlackCaptured
        copy.Pieces = board.Pieces.copy()
        copy.Chains = board.Chains.copy()
        copy.Areas = board.Areas.copy()
        copy.FirstEmptyField = board.FirstEmptyField
        return copy

    @classmethod
    def inverted(cls, board):
        copy = cls()
        copy.NumEmptyFields = board.NumEmptyFields
        copy.WhiteCaptured = board.BlackCaptured
        copy.BlackCaptured = board.WhiteCaptured
        copy.Pieces = board.Pieces * -1
        copy.Chains = board.Chains.copy()
        copy.Areas = board.Areas.copy()
        copy.FirstEmptyField = board.FirstEmptyField
        return copy


