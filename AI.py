from math import *
import random
import sys

class GameState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement UCT in any 2-player complete information deterministic 
        zero-sum game, although they can be enhanced and made quicker, for example by using a 
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1 and 2.
    """
    def __init__(self):
            self.playerJustMoved = 2 # At the root pretend the player just moved is player 2 - player 1 has the first move
        
    def Clone(self):
        """ Create a deep clone of this game state.
        """
        st = GameState()
        st.playerJustMoved = self.playerJustMoved
        return st

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved.
        """
        self.playerJustMoved = 3 - self.playerJustMoved
        
    def GetMoves(self):
        """ Get all possible moves from this state.
        """
    
    def GetResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm. 
        """

    def __repr__(self):
        """ Don't need this - but good style.
        """
        pass


class ChompState:


    def __init__(self,width,height):
        #print("height = "+str(height)+"width ="+str(width))
        self.playerJustMoved = 2
        self.board = []
        self.width = width
        self.height = height
        assert width == int(width) and height == int(height)
        for row in list(range(height)):
            cols = ['o' for i in list(range(width))]
            if(row == 0):
                cols[0] = '*'
            self.board.append(cols)

    def Clone(self):
        st = ChompState(self.width,self.height)
        #print(self.playerJustMoved)
        st.playerJustMoved=self.playerJustMoved
        for i in range(self.height):
            for j in range(self.width):
                st.board[i][j] = self.board[i][j]
        
        return st 

    def DoMove(self,move):
        x=move[0]
        y=move[1]
        self.playerJustMoved=3-self.playerJustMoved
        if([x,y] == [0,0]):
            pass
        if((x > self.width) or (y > self.height)):
            print("Out of bounds!")
        if(not self.is_cell_open(x, y) and not self.board[x][y] == '*'):
            print("You can't eat that! (already nommed)")   
        for r in range(self.width):
            for c in range(self.height):
                if((r >= y) and (c >= x)):
                    if(self.playerJustMoved == 1 and self.board[c][r] != 2):
                        self.board[c][r] = 1
                    elif(self.playerJustMoved == 2 and self.board[c][r]!= 1):
                        self.board[c][r] = 2      

    def GetMoves(self):
        return [(x,y) for x in range(self.height) for y in range(self.width) if (self.board[x][y] == 'o' or self.board[x][y] == '*'  )]

    def GetResult(self,player):
        if(self.board[0][0] == '*'):
            return 0.5
        elif (self.board[0][0] == player):
            return 0.0
        return 1.0


    def is_cell_open(self,x,y):
        #print(str(x)+" "+str(y))
        #r = input("Hiii")
        return self.board[x][y] == 'o'

    def __repr__(self):
        game = ""
        for row in range(self.height):
            #print("row = "+str(row))
            for col in range(self.width):
                #print("col="+str(col)+"board="+str(self.board[row][col]))
                game=game+str(self.board[row][col])
                #print("game="+game)
            game = game+"\n"
        return game 


class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.GetMoves() # future child nodes
        #print("-----------")
        #print(str(self.parentNode))
        #print("initialising untried moves")
        #print(self.untriedMoves)
        self.playerJustMoved = state.playerJustMoved # the only part of the state that the Node needs later
        
    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits))[-1]
        return s
    
    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move = m, parent = self, state = s)
        #print(m)
        #print(n)
        self.untriedMoves.remove(m)
        #print(self.untriedMoves)
        self.childNodes.append(n)
        #print(self.childNodes)
        return n
    
    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        #print("into updated"+" "+str(result))
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s

def UCT(rootstate, itermax, verbose = False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state = rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.Clone()
        #print("Entered into for loop")
        #print(str(state))
        #print(node.untriedMoves)
        #asda = input("^")
        # Select
        while node.untriedMoves == [] and node.childNodes != []: # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.DoMove(node.move)
            #print("tried move1 = "+str(node.move))

        # Expand
        if node.untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves) 
            #print(m)
            state.DoMove(m)
            #print("tried move2 = "+str(m))
            node = node.AddChild(m,state) # add child and descend tree
            #print(node)

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves() != []: # while state is non-terminal
            #print(state.GetMoves())
            #print("came into rollout")
            state.DoMove(random.choice(state.GetMoves()))
            

        # Backpropagate
        while node != None: # backpropagate from the expanded node and work back to the root node
            #print("came into backpropogate")
            node.Update(state.GetResult(node.playerJustMoved)) # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode
        #print(node.untriedMoves)
          

    # Output some information about the tree - can be omitted
    if (verbose): print (rootnode.TreeToString(0))
    else: print (rootnode.ChildrenToString())

    return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move # return the move that was most visited
                
def UCTPlayGame():
    """ Play a sample game between two UCT players where each player gets a different number 
        of UCT iterations (= simulations = tree nodes).
    """
    print("<<<<<<       Welcome to CHOMP game    >>>>>>>")
    (x,y)=tuple(map(int,input("Please enter the dimensions of the chocolate\n").split(',')))
    state = ChompState(x,y)
    #print(str(state))
    #a=input("asd") 
    while (state.GetMoves()!=[]):
        #print(state.GetMoves())
        #a=input("asd")
        #print(state.playerJustMoved)
       
        if state.playerJustMoved == 1:
            (x,y)=tuple(map(int,input("Please enter the positions of the chocolate you would like to eat\n").split(',')))
            if([x,y]==[0,0]):
                print("You  lose!!!")
                print("Player 2 wins")
                sys.exit()
            if(not(state.is_cell_open(x,y))):
                while(not(state.is_cell_open(x,y))):
                    print("You have chosen already eaten piece\n")
                    (x,y)=tuple(map(int,input("Please enter the positions of the chocolate you would like to eat").split(',')))
                    #print(state.is_cell_open(x,y))
            state.DoMove((x,y))
            
        else:
            print(str(state))
            #e=input("asd")
            m=UCT(rootstate=state,itermax=1000,verbose=False)
            print("Best Move : "+str(m)+"\n")
            #a = input()
            if(m==(0,0)):
                print("You  win!!!")
                sys.exit()
            state.DoMove(m)

        print(str(state))
        '''
    if state.GetResult(state.playerJustMoved) == 1.0:
        print("Player " + str(state.playerJustMoved) + " wins!")
    elif state.GetResult(state.playerJustMoved) == 0.0:
        print("Player " + str(3 - state.playerJustMoved) + " wins!")
    else: print("Neither player Wins!")
        ''' 
if __name__ == "__main__":
    """ Play a single game to the end using UCT for both players. 
    """
    UCTPlayGame()



