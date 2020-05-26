# Student: Branden Lee

# rushhour.py
# > rushhour(0, ["--B---","--B---","XXB---","--AA--","------","------"])

from queue import PriorityQueue
import math

def rushhour(heuristicMode,startStateArray):
    startState = serialize(startStateArray);
    if not checkValidBoard(startState):
        print("Start state is invalid!")
    else:
        pieceTable = getPieces(startState)
        path, statesExplored = stateSearch(heuristicMode,startState,pieceTable)
        if path == None:
            print("No solution found.")
        else:
            printPath(path)
            print("Total moves:", len(path)-1) # subtract 1 because don't count start state
            print("Total states explored:", statesExplored)
            #movesFileHandle = open("moves.txt", "w")
            #writePath(movesFileHandle, path)

# Piece information and geometry
class Piece:
    __slots__ = ("name", "orientation", "length", "coords")

    def __init__(self):
        # orientation: 0 = horizontal, 1 = vertical
        # used for computing available movements
        self.orientation = self.length = int(0)
        # The name is the single letter character identifier on the board
        self.name = ""

# State
# state[] example:
# --B---
# --B---
# XXB---
# --AA--
# ------
# ------
# becomes =>
# State.id: --B-----B---XXB-----AA--------------
class State:
    __slots__ = ("id", "g", "h")

    def __init__(self):
        self.id = ""
        # g = node depth, h = heuristic value
        # f = g + h, but its the priority so it is stored in the priority queue
        self.g = self.h = 0

    # Tie breaker for equal priorities or f(n)
    # python requires me to add this. I arbitrarily compare h(n) as tie-breaker
    def __lt__(self, other):
        return self.h < other.h
    
    
# Iterative methods are faster than recursion
# This is basically a Best First Search of valid states
# implemented with a priority queue as the frontier.
def stateSearch(heuristicMode, startStateId, pieceTable):
    path = []
    # By default the priority queue orders by smallest first
    # this is the frontier
    queue = PriorityQueue()
    exploredTable = {}
    goalStateId = ""
    statesExplored = 0
    startState = State()
    startState.id = startStateId
    #debugFileHandle = open("debug.txt", "w")
    # the 2D arrays are serialized into a string
    # this makes hashing easier and allows string function use
    if markStateVisited(startState.id, "", exploredTable):
        queue.put((0, startState))
    while not queue.empty():
        statesExplored = statesExplored + 1
        currentStatePair = queue.get()
        currentState = currentStatePair[1]
        #debugFileState(debugFileHandle, currentStatePair, queue)
        # check if serialized current and goal state match
        if checkWinBoard(currentState.id):
            goalStateId = currentState.id
            break
        else:
            newStateList = generatePossibleStates(currentState.id, pieceTable)
            n = len(newStateList)
            for i in range(0,n):
                if heuristicMode == 0:
                    heuristicValue = calculateHeuristicBlocking(newStateList[i])
                elif heuristicMode == 1:
                    heuristicValue = calculateHeuristicCustom(newStateList[i], pieceTable)
                else:
                    print("Error: Unknown heuristic mode ", heuristicMode);
                    break
                if markStateVisited(newStateList[i], currentState.id, exploredTable):
                    # place new states in priority queue
                    newState = State()
                    newState.id = newStateList[i]
                    newState.h = heuristicValue
                    newState.g = currentState.g + 1
                    f = newState.g + newState.h
                    queue.put((f, newState))
                    #debugFileChildState(debugFileHandle,[heuristicValue, newState])
                
    # Back track through explored table to get the path
    path.append(goalStateId)
    goalStateId = exploredTable.get(goalStateId, "")
    while goalStateId != "":
        path.append(goalStateId)
        goalStateId = exploredTable.get(goalStateId, "")
    # reverse path so it goes start to goal
    path.reverse();
    # validate path
    if path[0] == startStateId:
        return path, statesExplored
    return None, None

# Returns unique state identifier
def serialize(currentStateArray):
    serializedString = ""
    return ''.join(currentStateArray)

# Marks a state as visited and checks if it has already been visited.
# Returns False if previously visited a true if first visit
def markStateVisited(stateId, parentStateId, exploredTable):
    # python disctionaries are a hash table implementation
    # checking existance of state is only O(1)
    if(stateId in exploredTable):
        # print("Possible cycle detected. State Id:", stateId, "already added.")
        return False
    else:
        # table is childNode->parentNode
        # important for final path lookup
        exploredTable[stateId] = parentStateId;
    return True

# Check if the start state is valid.
# Returns true if valid.
def checkValidBoard(startStateId):
    # is 6x6 board
    if len(startStateId) != 36:
        print("Error: board not 6x6.")
        return False;
    # XX must exist on the third row
    for i in range(12, 17):
        if startStateId[i] == 'X' and startStateId[i+1] == 'X':
            return True
    print("Error: XX piece does not exist on the third row.")
    return False

# Check win state
# @return true if state is winning state
def checkWinBoard(currentState):
    if currentState[16] == 'X' and currentState[17] == 'X':
        return True
    return False

# get board pieces
# pieces are all assumed to be 1 box wide
# and at least 2 long
def getPieces(currentState):
    # create a dictionary of pieces
    pieceTable = {}
    for i in range(0, 36):
        name = currentState[i]
        if name != '-' and name not in pieceTable:
            pieceTable[name] = Piece()
            pieceTable[name].name = name
            pieceTable[name].length = 1
            # follow the piece
            if i%6 < 5:
                # check right
                j = i+1
                if name == currentState[j]:
                    pieceTable[name].orientation = 0
                    while j%6 > 0:
                        if name == currentState[j]:
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
                            pieceTable[name].length = pieceTable[name].length+1
                            j = j+6
                        else:
                            break
    return pieceTable

# Generate the possible states from available moves.
# Wasted CPU cycles visiting each cell on the board.
# Iterating through pieces would be more efficient,
# but saving piece.name => cellPosition uses more memory
def generatePossibleStates(stateId, pieceTable):
    newStateList = []
    pieceVisited = {}
    for i in range(0, 36):
        name = stateId[i]
        # not blank and piece not already visited
        if name != '-' and name not in pieceVisited:
            pieceVisited[name] = True;
            pieceOrientation = pieceTable[name].orientation
            pieceLength = pieceTable[name].length
            # piece is horizontal
            if pieceOrientation == 0:
                shift = pieceLength-1
                # move left
                if i%6 > 0 and stateId[i-1] == '-':
                    newBoardStateList = list(stateId)
                    newBoardStateList[i-1] = name
                    newBoardStateList[i+pieceLength-1] = '-'
                    newStateList.append(''.join(newBoardStateList))
                # move right
                if i%6 < (6-pieceLength) and stateId[i+pieceLength] == '-':
                    newBoardStateList = list(stateId)
                    newBoardStateList[i+pieceLength] = name
                    newBoardStateList[i] = '-'
                    newStateList.append(''.join(newBoardStateList))
            # piece is vertical
            elif pieceOrientation == 1:
                # move up
                if i > 5 and stateId[i-6] == '-':
                    newBoardStateList = list(stateId)
                    newBoardStateList[i-6] = name
                    newBoardStateList[i+(pieceLength-1)*6] = '-'
                    newStateList.append(''.join(newBoardStateList))
                # move down
                if i < (36-pieceLength*6) and stateId[i+pieceLength*6] == '-':
                    newBoardStateList = list(stateId)
                    newBoardStateList[i+pieceLength*6] = name
                    newBoardStateList[i] = '-'
                    newStateList.append(''.join(newBoardStateList))
    return newStateList

# blocking heuristic
# score is based on pieces blocking the exit path
# lower is better
def calculateHeuristicBlocking(stateId):
    pieceXFound = False
    blockFound = False;
    # find pieces on third row
    if checkWinBoard(stateId):
        return 0
    score = 1
    for i in range(12, 18):
        if not pieceXFound and stateId[i] == 'X':
            pieceXFound = True
        elif pieceXFound and stateId[i] != '-' and stateId[i] != 'X':
            # all the pieces on the third row are vertical
            # or else the puzzle would be impossible
            score = score+1
    return score

# custom heuristic
# score is the distance
# vertical pieces from bottom
# horizontal pieces from left
# then logarithm taken and rounded to nearest integer
# lower is better.
# The idea is moving other pieces away from the exit will help the XX piece exit
def calculateHeuristicCustom(stateId, pieceTable):
    score = 0
    pieceVisited = {}
    for i in range(0, 36):
        name = stateId[i]
        # not blank and piece not already visited
        if name != '-' and name != 'X' and name not in pieceVisited:
            pieceVisited[name] = True;
            pieceOrientation = pieceTable[name].orientation
            pieceLength = pieceTable[name].length
            # piece is horizontal
            if pieceOrientation == 0:
                distance = i%6
                score = score + distance
            # piece is vertical
            elif pieceOrientation == 1:
                distance = 6 - math.floor(i/6) - pieceLength
                score = score + distance
    if score == 0:
        return 0
    return int(round(math.log(score,2),0))

# writes the stateId to readable board to console
def printState(stateId):
    for i in range(0, 36):
        print(stateId[i], end = '')
        if i%6 == 5:
            print("\n", end = '')

# writes the stateId to readable board to file
def writeState(fileHandle, stateId):
    for i in range(0, 36):
        fileHandle.write(stateId[i])
        if i%6 == 5:
            fileHandle.write("\n")

# Writes the path of states to the console.
def printPath(path):
    n = len(path)
    for i in range(0, n):
        printState(path[i])
        print("\n", end = '')

# Writes the path of states to a file.
def writePath(fileHandle, path):
    n = len(path)
    for i in range(0, n):
        fileHandle.write("Move: "+str(i)+"\n")
        writeState(fileHandle, path[i])
        fileHandle.write("\n")

# FOR DEBUG USE
# writes the parent state board to a file
def debugFileState(fileHandle, statePair, queue):
    fileHandle.write("==============================================\n")
    fileHandle.write("PriorityQueue.length = " + str(queue.qsize()) + "\n")
    fileHandle.write("Priority " + str(statePair[0]) + "\n")
    writeState(fileHandle,statePair[1].id)

# FOR DEBUG USE
# writes the child or successor state board to a file
def debugFileChildState(fileHandle, statePair):
    fileHandle.write("CHILD Priority " + str(statePair[0]) + "\n")
    writeState(fileHandle,statePair[1].id)
