# Student: Branden Lee

# rushhour.py
# > rushhour(0, ["--B---","--B---","XXB---","--AA--","------","------"])

def tilepuzzle(heuristicMode,startStateArray):
    startState = serialize(startStateArray);
    if not checkValidBoard(startState):
        print("Start state is invalid!")
    else:
        pieceTable = getPieces(startState)
        path = stateSearch(startState,pieceTable)
        if path == None:
            print("No solution found.")
        else:
            print("Solution found with", len(path), "moves.")
            print("Moves written to moves.txt")
            pathToFile("moves.txt", startState)

# piece information and geometry
class Piece:
    __slots__ = ("name", "orientation", "length", "coords")

    def __init__(self):
        # orientation: 0 = horizontal, 1 = vertical
        # used for computing available movements
        self.orientation = self.length = int(0)
        # The name is the single letter character identifier on the board
        self.name = self.resName = ""
        # list of coordinate pairs the piece uses
        self.coords = []
    
    
# Orginally the instructors method used recursion, but
# this method was changed to use iteration to prevent stack overflow
# This is basically a Depth First Search of valid states.
def stateSearch(start,goal):
    path = []
    stack = []
    exploredTable = {}
    # the 2D arrays are serialized into a string
    # this makes hashing easier and allows string function use
    boardStateId = serialize(start);
    goalBoardStateId = serialize(goal);
    appendUniqueState(stack, boardStateId, "", exploredTable)
    while len(stack) > 0:
        # print("stack.length=",len(stack)) 
        currentBoardStateId = stack.pop()
        # check if serialized current and goal state match
        if currentBoardStateId == goalBoardStateId:
            break
        else:
            blankPosition = findBlankPosition(currentBoardStateId)
            # Generate new states.
            # New states are generated naively and dont check if we just
            # reversed the last move, but the O(1) hash table check
            # will find we already processed that state before.
            # Swap blank up.
            newStateId = generateSwapUp(currentBoardStateId,blankPosition)
            if newStateId != None:
                appendUniqueState(stack, newStateId, currentBoardStateId, exploredTable)
            # Swap blank down.
            newStateId = generateSwapDown(currentBoardStateId,blankPosition)
            if newStateId != None:
                appendUniqueState(stack, newStateId, currentBoardStateId, exploredTable)
            # Swap blank right.
            newStateId = generateSwapLeft(currentBoardStateId,blankPosition)
            if newStateId != None:
                appendUniqueState(stack, newStateId, currentBoardStateId, exploredTable)
            # Swap blank left.
            newStateId = generateSwapRight(currentBoardStateId,blankPosition)
            if newStateId != None:
                appendUniqueState(stack, newStateId, currentBoardStateId, exploredTable)
    # Back track through explored table to get the path
    path.append(goalBoardStateId)
    goalBoardStateId = exploredTable.get(goalBoardStateId, "")
    while goalBoardStateId != "":
        path.append(goalBoardStateId)
        goalBoardStateId = exploredTable.get(goalBoardStateId, "")
    # reverse path so it goes start to goal
    path.reverse();
    # validate path
    if path[0] == boardStateId:
        return path
    return None
    
                
# find the position of the blank in the puzzle
def findBlankPosition(currentBoardStateId):
    return currentBoardStateId.find('0')

# get unique state identifier
def serialize(currentStateArray):
    serializedString = ""
    return ''.join(currentStateArray)

def appendUniqueState(stack, boardStateId, parentBoardStateId, exploredTable):
    # python disctionaries are a hash table implementation
    # checking existance of state is only O(1)
    if(boardStateId in exploredTable):
        # print("Possible cycle detected. State Id:", boardStateId, "already added.")
        return False
    else:
        # table is childNode->parentNode
        # important for final path lookup
        exploredTable[boardStateId]= parentBoardStateId;
        stack.append(boardStateId)
    return True

# check if the start state is valid
def checkValidBoard(currentState):
    # is 6x6 board
    if len(currentState) != 36:
        print("Error: board not 6x6.")
        return False;
    # XX must exist on the third row
    for i in range(12, 17):
        if currentState[i] = 'X' and currentState[i+1] = 'X':
            return True
    print("Error: XX piece does not exist on the third row.")
    return False

# get board pieces
# pieces are all assumed to be 1 box wide
# and at least 2 long
def getPieces(currentState):
    # create a dictionary of pieces
    pieceTable = {}
    for i in range(0, 36):
        name = currentState[i]
        if name not in pieceTable:
            pieceTable[name] = Piece()
            pieceTable[name].name = name
            pieceTable[name].length = 1
            pieceTable[name].coords.append(i)
            # follow the piece
            if i%6 < 5:
                # check right
                j = i+1
                if name == currentState[j]:
                    pieceTable[name].orientation = 0
                    while j%6 > 0:
                        if name == currentState[j]:
                            pieceTable[name].coords.append(j)
                            pieceTable[name].length = pieceTable[name].length+1
                            j = j+1
                        else:
                            break
            if i < 30:
                # check down
                j = i+6
                if name == currentState[j]:
                    pieceTable[name].orientation = 1
                    while j < 36:
                        if name == currentState[j]:
                            pieceTable[name].coords.append(j)
                            pieceTable[name].length = pieceTable[name].length+1
                            j = j+6
                        else:
                            break
    return pieceTable

# Generate the possible state from available moves

def generateSwapUp(boardStateId,blankPosition):
    # In python, characters cant be edited in place
    # The string must be converted into a list first
    newBoardStateList = list(boardStateId)
    if blankPosition > 2:
        newBoardStateList[blankPosition] = newBoardStateList[blankPosition-3]
        newBoardStateList[blankPosition-3] = '0'
    else:
        return None
    return ''.join(newBoardStateList)

def generateSwapDown(boardStateId,blankPosition):
    # copy board identifier
    newBoardStateList = list(boardStateId)
    if blankPosition < len(newBoardStateList)-3:
        # swap. 0 used for blank tile.
        newBoardStateList[blankPosition] = newBoardStateList[blankPosition+3]
        newBoardStateList[blankPosition+3] = '0'
    else:
        return None
    return ''.join(newBoardStateList)

def generateSwapLeft(boardStateId,blankPosition):
    # copy board identifier
    newBoardStateList = list(boardStateId)
    if blankPosition%3 > 0:
        # swap. 0 used for blank tile.
        newBoardStateList[blankPosition] = newBoardStateList[blankPosition-1]
        newBoardStateList[blankPosition-1] = '0'
    else:
        return None
    return ''.join(newBoardStateList)

def generateSwapRight(boardStateId,blankPosition):
    # copy board identifier
    newBoardStateList = list(boardStateId)
    if blankPosition%3 < 2:
        # swap. 0 used for blank tile.
        newBoardStateList[blankPosition] = newBoardStateList[blankPosition+1]
        newBoardStateList[blankPosition+1] = '0'
    else:
        return None
    return ''.join(newBoardStateList)

# Writes the moves to a file. Good for long move paths.
def pathToFile(fileName, path):
    f = open(fileName, "w")
    for i in range(0, len(path)):
        f.write("Move: "+str(i)+"\n")
        for j in range(0, 36):
            f.write(path[i][j])
            if j%6 == 5:
                f.write("\n")
        f.write("\n")
    f.close()
