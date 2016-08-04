#! /usr/bin/python

#most adapted from http://rene.f0o.com/mywiki/PythonGameProgramming tutorials
#Current Verion: 9.3

import os, sys
import pygame
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'


import random
import re
import time
#import sound

import socket, pickle # for networking

DROP_RATE = 20
HOST = '127.0.0.1'
PORT = 84765
D_SIZE = 32

class moving_piece(pygame.sprite.Sprite):
    #THANAT can implement this - here's a skeleton
    
    def __init__(self, screen, x, y, grid, block1_next, block2_next):
        """The piece made up of 2 blocks that the player controls"""
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.block1 = play_block(screen, x, y, grid, block1_next) #the one you rotate around
        self.block2 = play_block(screen, x, y+35, grid, block2_next)
        self.screen = screen
        
        #orientations 0,1,2,3 correspon to "VERTICAL_top","HORIZONTAL_left","VERITCAL_bot","HORIZONTAL_right"
        #_top means the main block1 is on top
        self.orientation_types = ["VERTICAL_top","HORIZONTAL_left","VERITCAL_bot","HORIZONTAL_right"]
        self.orientation = 0
        self.grid = grid
        self.placed = False
    
    def move(self, eventKey):
        """Checks to see if the move is valid. First checks the orientation of the piece,
        then handles how to move the block case by case.""" 
        
        if self.orientation == 0:
            if eventKey == pygame.K_LEFT:
                if not self.grid.collisionLeft(self.block1.col,self.block1.y) and not self.grid.collisionLeft(self.block2.col,self.block2.y):
                    self.block1.move(eventKey)
                    self.block2.move(eventKey)
            elif eventKey == pygame.K_RIGHT:
                
                if not self.grid.collisionRight(self.block1.col,self.block1.y  and not self.grid.collisionRight(self.block2.col,self.block2.y)):
                    self.block1.move(eventKey)
                    self.block2.move(eventKey)
            else:
                self.block1.move(eventKey)
                self.block2.move(eventKey)
            
        elif self.orientation == 1:
            if eventKey == pygame.K_LEFT:
                if not self.grid.collisionLeft(self.block1.col, self.block1.y):
                    self.block1.move(eventKey)
                    self.block2.move(eventKey)
            elif eventKey == pygame.K_RIGHT:
                if not self.grid.collisionRight(self.block2.col, self.block2.y):
                    self.block1.move(eventKey)
                    self.block2.move(eventKey)
            else:
                self.block1.move(eventKey)
                self.block2.move(eventKey)
                
        elif self.orientation == 2:
            if eventKey == pygame.K_LEFT:
                if not self.grid.collisionLeft(self.block1.col,self.block1.y) and not self.grid.collisionLeft(self.block2.col,self.block2.y):
                    self.block1.move(eventKey)
                    self.block2.move(eventKey)
            elif eventKey == pygame.K_RIGHT:
                if not self.grid.collisionRight(self.block1.col,self.block1.y) and not self.grid.collisionRight(self.block2.col,self.block2.y):
                    self.block1.move(eventKey)
                    self.block2.move(eventKey)
            else:
                self.block1.move(eventKey)
                self.block2.move(eventKey)
            
        elif self.orientation == 3:
            if eventKey == pygame.K_LEFT:
                if not self.grid.collisionLeft(self.block2.col, self.block2.y):
                    self.block1.move(eventKey)
                    self.block2.move(eventKey)
            elif eventKey == pygame.K_RIGHT:
                if not self.grid.collisionRight(self.block1.col, self.block1.y):
                    self.block1.move(eventKey)
                    self.block2.move(eventKey)
            else:
                self.block1.move(eventKey)
                self.block2.move(eventKey)
        
        
    def rotate(self):
        """Rotates the moving piece. Orientation 0 = veritcal with mainblock1 on top. Orientation 1  = horizontal with mainblock1 on left
    Orientation 2 = vertical with mainblock1 on bottom. 4 = horizontal with mainblock on right
    Algorithm checks for collision to see if the rotation is valid or not."""
        if self.orientation == 0:
            colRight = self.grid.collisionRight(self.block1.col, self.block1.y)
            if colRight == False:
                #update x, y and col
                self.block2.y -= 35
                self.block2.x += 35
                self.block2.col += 1
                self.orientation = (self.orientation+1)%4
            else:
                self.orientation += 2
                self.block2.y -= 35
                self.block1.y += 35
                
        elif self.orientation == 1:
            #update x, y and col
            self.orientation = (self.orientation+1)%4
            self.block2.y -= 35
            self.block2.x -= 35
            self.block2.col -= 1
 
        elif self.orientation == 2:
            colLeft = self.grid.collisionLeft(self.block1.col, self.block1.y)
            if colLeft == False:
                self.block2.y += 35
                self.block2.x -= 35
                self.block2.col -= 1
                self.orientation = (self.orientation+1)%4
            else:
                self.block2.y += 35
                self.block1.y -=35
                self.orientation = (self.orientation+2)%4
                
        elif self.orientation == 3:
            colBot = self.grid.collisionBottom(self.block1.col, self.block1.y)
            if colBot == False:
                self.block2.y += 35
                self.block2.x += 35
                self.block2.col += 1
                self.orientation = (self.orientation+1)%4
    
    def update(self):
        """ Checks to see if any of the singular play_blocks collide.
        If orientation is horizontal and one collides, then the other block has to 'drop' to the bottom until it also collides.
        While the block is dropping, a new moving piece wont be created for the player and disables player keyboard inputs."""
        block1_collidebot = self.grid.collisionBottom(self.block1.col, self.block1.y)
        block2_collidebot = self.grid.collisionBottom(self.block2.col, self.block2.y)
        if block1_collidebot!=False or block2_collidebot!=False:
            
            #while loops "drop" the block down for orientations 1 and 3
            if block1_collidebot==False and self.orientation%2==1:
                check1 = self.dropBlock(self.block1)
                
                self.block1.update()
                self.block2.placed = True
                self.block2.update()
                
                if check1==False:
                    return 1 #1 freezes the player
                #self.block1.y += 35
                #block1_collidebot = self.grid.collisionBottom(self.block1.col, self.block1.y)
            if block2_collidebot==False and self.orientation%2==1:
                check2 = self.dropBlock(self.block2)
                
                self.block1.placed = True
                self.block1.update()
                self.block2.update()
                
                if check2==False:
                    return 1

            rowList1 = self.grid.getRow(self.block1.col, self.block1.y)
            block1_collidebot = [((rowList1[0]-1)*35 + 49),rowList1[0]]
            rowList2 = self.grid.getRow(self.block2.col, self.block2.y)
            block2_collidebot = [((rowList2[0]-1)*35 + 49),rowList2[0]]            
            #both rows will be "set" -> get their rowlists

            self.placed = True
            self.block1.placed = True
            self.block2.placed = True
            #set the rows
            self.grid.add_block(block1_collidebot[1], self.block1.col, self.block1.blocktype_file)
            self.grid.add_block(block2_collidebot[1], self.block2.col, self.block2.blocktype_file)

            #print "Placed a " + str(self.block1.type) + " at [" + str(block1_collidebot[1]) + "][" + str(self.block1.col) + "]"
            #print "Placed a " + str(self.block2.type) + " at [" + str(block2_collidebot[1]) + "][" + str(self.block2.col) + "]"
            if block1_collidebot[1] == 0 or block2_collidebot[1] == 0:
                #print "GAME OVER!!"
                #pygame.quit()
                #sys.exit(0)
                return 2
        else:
            self.block1.update()
            self.block2.update()
        #self.screen.blit(self.block1.block_sample, (self.block1.x,self.block1.y))
        #self.screen.blit(self.block2.block_sample, (self.block2.x,self.block2.y))

    def dropBlock(self, block):
        """ Drops a block whose 'partner' has collided."""
        block.y += DROP_RATE #block drop speed
        block_collidebot = self.grid.collisionBottom(block.col,block.y)
        if block_collidebot == True:
            return True
        return False
        
                     
class set_block(pygame.sprite.Sprite):
    
    def __init__(self, screen, x, y, blockcolor,col,grid):
        """The basic sprite for a single game block that is placed in the grid"""
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        block_filename = os.path.join("assets",blockcolor)
        self.block_sample = pygame.image.load(block_filename).convert()
        self.info = re.split(r"[_.]",block_filename)
        self.type = self.info[1] #set block type (i.e. garbage or normal or crash)
        self.color = re.split(r"assets[\\/]*",self.info[0])[1]
        self.garbageCounter = 0
        if self.type == "garbage":
            self.garbageCounter = int(self.info[2])
            #print self.color, self.type, self.garbageCounter
        self.x = x
        self.y = y
        self.screen = screen
        self.col = col
        self.grid = grid
        #print "Set block created at:",self.col
        self.marked = False #used for marking breaking (crash) algorithm
        self.fallStage = 0
            
    
    def update(self):
        """Update called every frame"""
        #update image file: self.block_sample for countdown blocks!
        collideB = self.grid.collisionBottom(self.col, self.y)
        if collideB == False:
            self.y += 10 #move by exactly 1 row, 35
            self.fallStage += 1
            if self.fallStage == 4:
                self.y -= 5 #move it back 5 pixels
                self.fallStage = 0
                self.screen.blit(self.block_sample, (self.x,self.y))
                return 4
            self.screen.blit(self.block_sample, (self.x,self.y))
            return self.fallStage #true means that the SET BLOCK has moved -- need to update grid accordingly!
        self.screen.blit(self.block_sample, (self.x,self.y))

    def draw(self):
        """Draws the block (blits it) but does not update any game logic"""
        self.screen.blit(self.block_sample, (self.x, self.y))

    def __repr__(self):
        output = str(self.color)+"_"+str(self.info[1])+"["
        row = str(int(self.grid.getRow(self.col,self.y)[0]))
        output += row+"]["+str(self.col)+"] "
        return output
        


class play_block(pygame.sprite.Sprite):
    
    def __init__(self, screen, x, y, grid, blocktype):
        """The basic sprite for a single game block that is controlled by the player"""
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.blocktype_file = blocktype
        #self.blocktype_file = "sample_block.bmp"
        block_filename = os.path.join("assets",self.blocktype_file)
        #print "block filename is:",block_filename
        self.block_sample = pygame.image.load(block_filename).convert()
        self.info = re.split(r"[_.]",block_filename)
        self.type = self.info[1]
        self.color = re.split(r"assets[\\/]*",self.info[0])[1]
        self.col = 3 #the block's column position
        self.x = x #the block's screen pixel position
        self.y = y
        self.screen = screen
        self.grid = grid
        self.placeCounter = None #use this to allow player to move the block for a moment after it collides before finalized
        self.placed = False
        #print self.color
    
    def randomizer(self):
        """Chooses a block type and color randomly and returns the filename
        File name convention: color_type.gif   all lower case and uses .gif extension
        e.g.  red_crash.gif
        """
        col_choose = random.randrange(0,4,1) # (0,1,2,3) = (red,green,blue,yellow)
        type_choose = random.randrange(0,4,1) # 0-2 = normal ; 3 = crash --> 75% normal, 25% crash
        colors = {0:"red",1:"green",2:"blue",3:"yellow"}
        types = {0:"normal",1:"normal",2:"normal",3:"crash"}
        return colors[col_choose] + "_" + types[type_choose] + ".gif"
    
    def move(self, eventKey):
        #print eventKey
        if eventKey == pygame.K_LEFT:
            self.x -= 35
            self.col -= 1
        elif eventKey == pygame.K_RIGHT:
            self.x += 35
            self.col += 1
        elif eventKey == pygame.K_DOWN:
            self.y += 20
    
    def update(self):
        """Update called every frame"""
        #add check for colission here
        collideB = self.grid.collisionBottom(self.col, self.y)
        if collideB == False:
            self.y+=1
        elif self.placed != True:
            self.placed = True
            #self.grid.add_block(collideB[1], self.col, self.blocktype_file)
            #print "Placed a " + str(self.type) + " at [" + str(collideB[1]) + "][" + str(self.col) + "]"
            if collideB[1] == 0:
                #print "GAME OVER!!"
                #pygame.quit()
                #sys.exit(0)
                return True
        self.screen.blit(self.block_sample, (self.x,self.y))

        
class gameGrid:

    def __init__(self, zeroX, zeroY): 
        """Create a game grid array depending on the given zero for the upper left box"""
        self.cols = 6
        self.rows = 14 #row 0 is above the playfield - use to check for GAME OVER status
        self.zeroX = zeroX
        self.zeroY = zeroY
##        self.screen = screen
        self.toDump = 0 #number of garbage blocks to be dumped
        #x pixel offset of screen -- 49 for left, 624 for right
        #access via grid[row][col]!!!
        self.grid = [[0 for i in range(self.cols)] for j in range(self.rows)] #list comprehension
        self.counter = 0

    def setScreen(self, screen):
        """Sets the surface for the game. I moved this from the constructor because the surface object can't be serialized)"""
        self.screen = screen
    
    def getRow(self, col, y):
        """Returns row that this coordinate occupies, or (row, row+1) if inbetween rows"""
        row = (y-49+35)/35
        if not (y-49+35) % 35.0 == 0.0:
            #the block is between two rows - add the row below it
            row = [row, row+1]
        else:
            row = [row]
        return row
    
    def collisionBottom(self, col, y):
        """Checks if the grid space below the one containing (x,y) is occupied or is the bottom of the grid"""
        rowList = self.getRow(col, y)
        if y >= 469:
            return [471,13]
        #if the row below the block is occupied and the block is at the point of collision
        if rowList.__len__() == 1:
            if not self.grid[rowList[0]+1][col] == 0: 
                if y >= ((rowList[0]-1)*35 + 49):
                    return [((rowList[0]-1)*35 + 49),rowList[0]]
        if rowList.__len__() == 2:
            if not rowList[0] == 13 and not self.grid[rowList[0]+1][col] == 0: 
                if y >= ((rowList[0]-1)*35 + 49):
                    return [((rowList[0]-1)*35 + 49),rowList[0]]
        return False
    
    def collisionRight(self, col, y):
        """Checks if the grid space right of the one containing (x,y) is occupied or is the right of the grid"""
        rowList = self.getRow(col, y)
        if col == 5:
            return True
        if rowList.__len__() == 1:
            if not self.grid[rowList[0]][col+1] == 0:
                return True
        if rowList.__len__() == 2:
            if not self.grid[rowList[1]][col+1] == 0:
                return True
        return False
    
    def collisionLeft(self, col, y):
        """Checks if the grid space left the one containing (x,y) is occupied or is the left of the grid"""
        rowList = self.getRow(col, y)
        if col == 0:
            return True
        if rowList.__len__() == 1:
            if not self.grid[rowList[0]][col-1] == 0:
                return True
        if rowList.__len__() == 2:
            if not self.grid[rowList[1]][col-1] == 0:
                return True
        return False
        
    def add_block(self, row, col, color):
        """Add a placed block that can no longer be directly moved by the player"""
        #print row, col
        if row == 14:
            print "WHAT IS CAUSING THIS???"  #[very rare bug]
            row = 13
        #print color
        self.grid[row][col] = set_block(self.screen, col*35+self.zeroX, (row-1)*35+49, color, col, self)
    
    def delete_block(self, x, y):
        pass

    def convertToString(self):
        '''converts the grid into a string for sending over sockets'''
        '''normal block coding guide: 0 = empty, 1 = red, 2 = yellow, 3 = green, 4 = blue'''
        '''crash block coding guide: red = w, yellow = x, green = y, blue = z'''
        '''generic garbage block: any color = g (if i have more time I'll implement the version below)'''
        '''garbage block coding guide: red1234 = abcd, yellow1234 = efgh, green1234 = ijkl, blue1234 = mnop'''
        li = [] #convert into a string at the end
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 0:
                    li.append('0') #accounts for empty cell in grid
                elif self.grid[i][j] !=0:
                    block = self.grid[i][j] #this is a set_block
                    if block.type == "normal":
                        if block.color == "red":
                            li.append('1')
                        elif block.color == "yellow":
                            li.append('2')
                        elif block.color == "green":
                            li.append('3')
                        elif block.color == "blue":
                            li.append('4')
                    elif block.type == 'crash':
                        if block.color == 'red':
                            li.append('w')
                        elif block.color == 'yellow':
                            li.append('x')
                        elif block.color == 'green':
                            li.append('y')
                        elif block.color == 'blue':
                            li.append('z')
                    elif block.type == 'garbage':
                        li.append('g')
                        
        return ''.join(li) #return the string. it's length will be 84            
                        
                                        
    def update(self):
        """Iterate through grid and draw placed blocks then checks for crash logic"""
        crashCount = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if not self.grid[i][j] == 0:
                    
                    block = self.grid[i][j]
                    #check to destroy crash blocks
                    if block.type == "crash":
                        #self.grid[i][j] = 0
                        currentCrash = self.crashCheck(block)
                        crashCount += currentCrash
                        #if currentCrash > 0:
                            #print "Broke: " + str(currentCrash)

                    # update set blocks
                    if not self.grid[i][j] == 0:
                        set_block_moved = self.grid[i][j].update()
                        if set_block_moved==4: #if a set block has moved update grid accordingly
                            self.grid[i+1][j] = self.grid[i][j]
                            self.grid[i][j] = 0
                            
        if crashCount < 4:
            crashCount = 0
            #print "COMBO CRASH COUNT: " + str(crashCount)
        return crashCount
    
    def multiupdate(self, x):
        """updates the grid multiple times -- useful when a delay is needed to account for chains"""
        myRect = pygame.Rect(49, 49, 220, 35)
        for i in range(x):
            self.update()
            pygame.display.update(myRect)
            
    
    def updateGarbage(self):
        """-1 on all garbage block timers"""
        for i in range(self.rows):
            for j in range(self.cols):
                if not self.grid[i][j] == 0:
                    
                    block = self.grid[i][j]
                    #count down all garbage blocks
                    if block.type == "garbage":
                        block.garbageCounter -= 1
                        #create a new garbage block with the lower counter
                        garbageFile = str(block.color) + "_garbage_" + str(block.garbageCounter) + ".gif"
                        if block.garbageCounter > 0:
                            self.add_block(self.getRow(block.col, block.y)[0], block.col, garbageFile)
                        else:
                            #convert it to a normal block
                            normalFile = str(block.color) + "_normal.gif"
                            self.add_block(self.getRow(block.col, block.y)[0], block.col, normalFile)

    def crashCheck(self, block):
        """ Appends the crash block to the list.
            For each neighboring block, check to see if the color is same. If color is same, add it to list and mark it.
            Repeat check logic for each block on the list to mark all blocks to explode.
            Then calls deleteMarked to explode blocks."""
        crashList = [] #list of blocks to check for crashing
        crashList.append(block)

        while len(crashList) != 0:
            block = crashList.pop(0)
            j = block.col
            i = int(self.getRow(block.col,block.y)[0]) #cast list (of 1 item) as an int
            
            #check 4 surrounding blocks
            if i-1 < 0:
                topblock = 0 #edge case
            else:
                topblock = self.grid[i-1][j]
            if j+1 > self.cols-1:
                rightblock = 0 #edge case
            else:
                rightblock = self.grid[i][j+1]
            if j-1 < 0:
                leftblock = 0
            else:
                leftblock = self.grid[i][j-1]
            if i+1 > self.rows-1:
                bottomblock = 0
            else:
                bottomblock = self.grid[i+1][j]
            #print "crash list: ", "t:"+str(topblock), "r:"+str(rightblock), "l:"+str(leftblock), "b:"+str(bottomblock)

            if (topblock != 0 and block.color==topblock.color and not topblock.type == "garbage"):
                block.marked = True
                if topblock.marked == False:
                    crashList.append(topblock)
                topblock.marked = True
                #print "TOP BLOCK CRASH"
            if (rightblock != 0 and block.color==rightblock.color and not rightblock.type == "garbage"):
                block.marked = True
                if rightblock.marked == False:
                    crashList.append(rightblock)
                rightblock.marked = True
                #print "RIGHT BLOCK CRASH"
            if (leftblock != 0 and block.color==leftblock.color and not leftblock.type == "garbage"):
                block.marked = True
                if leftblock.marked == False:
                    crashList.append(leftblock)
                leftblock.marked = True
                #print "LEFT BLOCK CRASH"
            if (bottomblock != 0 and block.color==bottomblock.color and not bottomblock.type == "garbage"):
                block.marked = True
                if bottomblock.marked == False:
                    crashList.append(bottomblock)
                bottomblock.marked = True
                #print "BOTTOM BLOCK CRASH"

        #now that all the crash blocks are marked, call the delete function which will delete all the marked blocks
        return self.deleteMarked()

    def deleteMarked(self):
        """Iterate through grid and delete marked blocks.  Returns number deleted.  Called by grid"""
        crashCount = 0
        
        for i in range(self.rows):
            for j in range(self.cols):
                block = self.grid[i][j]
                if block != 0 and block.marked==True:
                    self.grid[i][j] = 0
                    crashCount += 1
        
        return crashCount

class catcom:
    def __init__(self):
        self.network = False #determines network mode on/off. Defaults to False
        self.is_server = True #defaults to the server when instantiated.
        self.LColCounter = 49 #left columns span from 49 to 224 (49,84,119,154,189,224)
        self.RColCounter = 626 #right columns span from 627 to 801
        self.rowCounter = 14 #row number is the same for either grid
        
        """Initialize the game"""
        self.FRAME_RATE = 50
        self.j = 0
        self.dir=1
        self.width = 885
        self.height = 550
        self.window = pygame.display.set_mode((self.width, self.height))
        self.screen = pygame.display.get_surface() 
        self.linecolor = 255,255,255
        self.bgcolor = 0,0,0
        self.x=self.y=0
        self.clock = pygame.time.Clock()
        
##        self.gridL = gameGrid(49, 49, self.screen)
        self.gridL = gameGrid(49,49)
        self.gridL.setScreen(self.screen)
        self.playerLbusy = False
        self.playerLdump = False
        self.playerLdumpTimer = False
        self.LdumpBuffer = 0

##        self.gridR = gameGrid(626, 49, self.screen)
        self.gridR = gameGrid(626,49)
        self.gridR.setScreen(self.screen)
        self.playerRbusy = False
        self.playerRdump = False
        self.playerRdumpTimer = False   
        self.RdumpBuffer = 0
        
        pygame.key.set_repeat(1,50) #holding down keys

        block1_next = self.randomizer()
        block2_next = self.randomizer()

        #list of the next incoming blocks for the players
        self.nextLBlockList = []
        if self.network == False:
            self.nextRBlockList = []
        
        #graphics - need os.path.join() in order to work on multiple platforms
        #http://rene.f0o.com/mywiki/LectureThree#head-d6c71743c2ad5b022b30e4adca1862e3545d2c01  
        bg_filename = os.path.join("assets","start_start_bg.bmp")
        self.bg = pygame.image.load(bg_filename).convert()
        self.screen.blit(self.bg, (0,0))
        
        #self.movingblock = play_block(self.screen, 154, 14, self.gridL)
        #self.movingblockR = play_block(self.screen, 731, 14, self.gridR)

        self.movingblock = moving_piece(self.screen, 154, 14-14, self.gridL, block1_next, block2_next)
        if self.network == False:
            self.movingblockR = moving_piece(self.screen, 731, 14-14, self.gridR, block1_next, block2_next)
        
    def randomizer(self):
        """Chooses a block type and color randomly and returns the filename
        File name convention: color_type.gif   all lower case and uses .gif extension
        e.g.  red_crash.gif
        """
        col_choose = random.randrange(0,4,1) # (0,1,2,3) = (red,green,blue,yellow)
        type_choose = random.randrange(0,4,1) # 0-2 = normal ; 3 = crash --> 75% normal, 25% crash
        colors = {0:"red",1:"green",2:"blue",3:"yellow"}
        types = {0:"normal",1:"normal",2:"normal",3:"crash"}
        return colors[col_choose] + "_" + types[type_choose] + ".gif"

    def drawNextBlocks(self):
        """ Gets next blocks from the list and draws them for both players"""
        block1_L_next = self.nextLBlockList[0]
        block2_L_next = self.nextLBlockList[1]
        block1_R_next = self.nextRBlockList[0]
        block2_R_next = self.nextRBlockList[1]
        #get image path
        block1_L_next = os.path.join("assets",block1_L_next)
        block2_L_next = os.path.join("assets",block2_L_next)
        block1_R_next = os.path.join("assets",block1_R_next)
        block2_R_next = os.path.join("assets",block2_R_next)
        #convert images
        block1_L_next = pygame.image.load(block1_L_next).convert()
        block2_L_next = pygame.image.load(block2_L_next).convert()
        block1_R_next = pygame.image.load(block1_R_next).convert()
        block2_R_next = pygame.image.load(block2_R_next).convert()

        #blit images
        if self.network:
            if self.is_server:
                self.screen.blit(block1_L_next, (259+4+35,49))
                self.screen.blit(block2_L_next, (259+4+35,49+35))
            elif self.is_server == False:
                self.screen.blit(block1_R_next, (622-70,49))
                self.screen.blit(block2_R_next, (622-70,49+35))
        else:
            self.screen.blit(block1_L_next, (259+4+35,49))
            self.screen.blit(block2_L_next, (259+4+35,49+35))
            self.screen.blit(block1_R_next, (622-70,49))
            self.screen.blit(block2_R_next, (622-70,49+35))
    
    def dumpBlocks(self, side):
        """Dumps one line of garbage blocks for a grid at a time"""
        if side == "Left":
            dumpMe = 0
            if self.LdumpBuffer <= 6 and not self.LdumpBuffer == 0:
                dumpMe = self.LdumpBuffer
                self.LdumpBuffer = 0
            elif self.LdumpBuffer > 6:
                #subtract 6 from dump
                dumpMe = 6
                self.LdumpBuffer -= 6
                
            print dumpMe
            
            for i in range(dumpMe):
                color = 0
                if i == 0 or i==5:
                    color = "red"
                if i == 1 or i==4:
                    color = "green"
                if i == 2:
                    color = "blue"
                if i == 3:
                    color = "yellow"
                self.gridL.add_block(1, i, str(color) + "_garbage_5.gif")
                
        if side == "Right":
            dumpMe = 0
            if self.RdumpBuffer <= 6 and not self.RdumpBuffer == 0:
                dumpMe = self.RdumpBuffer
                self.RdumpBuffer = 0
            elif self.RdumpBuffer > 6:
                #subtract 6 from dump
                dumpMe = 6
                self.RdumpBuffer -= 6
                
            print dumpMe
            
            for i in range(dumpMe):
                color = 0
                if i == 0 or i==5:
                    color = "red"
                if i == 1 or i==4:
                    color = "green"
                if i == 2:
                    color = "blue"
                if i == 3:
                    color = "yellow"
                self.gridR.add_block(1, i, str(color) + "_garbage_5.gif")
    
    def mainLoop(self):
        """Run the main game loop"""
        self.gamestate = "GAMESTART" #initial game state
        
        #can use this code for music - MAKE SURE ONLY CALLING .PLAY ONCE
        #pygame.mixer.init()
        #pygame.mixer.music.load('bgm.mp3')
        #pygame.mixer.music.play()

        #FOR NETWORKING
        deleted_right_grid = False
        deleted_left_grid = False

        #FOR NETWORKING OPTIONS (SERVER VS CLIENT)
        network_options = ["network_client", "network_server"]
        network_pointer = 0
        
        #FOR GAMESTART GAMESTATE:
        start_options = ["start_start", "start_network", "start_exit"]
        start_pointer = 0

        #FOR WINNERS DON'T DO DRUGS GAMESTATE:
        drugs_on = False

        #FOR BLITTING WINNING PLAYER
        blit_win = False
        
        #FOR GAMEOVER GAMESTATE:
        #initialize a list containing user options after game has ended
        #needs to be outside the while loop, else the option_pointer will be set to 0 after each loop iteration
        option_types = ["gameover_replay", "gameover_quit"]
        option_pointer = 0; #starting user selection at game over
        
        while 1:
            time_passed = self.clock.tick(self.FRAME_RATE)
            
            event = pygame.event.poll()
            
            if event.type == pygame.QUIT:
                print "Goodbye!"
                pygame.quit()
                sys.exit(0)

                    
            '''Display Starting Graphics and lets users select start/quit'''
            if self.gamestate == "GAMESTART":
        
                #user selection
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        pygame.key.set_repeat(1,50) #holding down keys
                        if start_pointer == len(start_options)-1: #if pointer is already at end, move to beginning of list
                            start_pointer = 0
                            print start_options[start_pointer]                            
                        else:
                            start_pointer = start_pointer + 1 #else move pointer down one
                            print start_options[start_pointer]
                                
                    if event.key == pygame.K_UP:
                        pygame.key.set_repeat(1,50) #holding down keys
                        if start_pointer == 0: #if pointer is already at beginning, move it to end of the list
                            start_pointer = len(start_options)-1;
                            print start_options[start_pointer]
                        else:
                            start_pointer = start_pointer - 1
                            print start_options[start_pointer]
                                
                    #blit the appropriate screen
                    bg_filename = os.path.join("assets", start_options[start_pointer] + "_bg.bmp")
                    self.bg = pygame.image.load(bg_filename).convert()
                    self.screen.blit(self.bg, (0,0))
                        
                    if event.key == pygame.K_RETURN:
                        pygame.key.set_repeat(1,50) #holding down keys
                        option = start_options[start_pointer] #user selection
                        print option
                        
                        if option == "start_start":
                            self.gamestate = "DRUGS"

                        elif option == "start_network":
                            self.gamestate = "NETWORK_OPTIONS"
                            self.network = True #activate network mode
            
                        elif option == "start_exit":
                            print "Goodbye!"
                            pygame.quit()
                            sys.exit(0)
                            break

            '''Display the anti-drug campaign'''
            if self.gamestate == "DRUGS":

                #pause for 3 seconds if antidrug pic has already been drawn (flipped)
                if drugs_on == True:
                    time.sleep(3)
                    self.gamestate = "2P" #change to 2P gamestate after pic has been displayed for 3 secs
                    
                #blit the antidrug pic (before screen is flipped)
                bg_filename = os.path.join("assets", "start_win_bg.bmp")
                self.bg = pygame.image.load(bg_filename).convert()
                self.screen.blit(self.bg, (0,0))
                drugs_on = True

               

            '''Display Game over graphics and lets users select quit/replay options'''
            if self.gamestate == "GAMEOVER":
                #if in network mode, exit immdeiately
                if self.network:
                    self.conn.close() #close the connection
                    print "Goodbye!"
                    pygame.quit()
                    sys.exit(0)
                    
                #otherwise blit the appropriate screen
                bg_filename = os.path.join("assets", option_types[option_pointer] + "_bg.bmp")
                self.bg = pygame.image.load(bg_filename).convert()
                self.screen.blit(self.bg, (0,0))
                pygame.display.flip()
                
                #user selection
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        pygame.key.set_repeat(1,50) #holding down keys
                        if option_pointer == len(option_types)-1: #if pointer is already at end, move to beginning of list
                            option_pointer = 0
                            print option_types[option_pointer]                            
                        else:
                            option_pointer = option_pointer + 1 #else move pointer down one
                            print option_types[option_pointer]
                    if event.key == pygame.K_UP:
                        pygame.key.set_repeat(1,50) #holding down keys
                        if option_pointer == 0: #if pointer is already at beginning, move it to end of the list
                            option_pointer = len(option_types)-1;
                            print option_types[option_pointer]
                        else:
                            option_pointer = option_pointer - 1
                            print option_types[option_pointer]
                    
                    if event.key == pygame.K_RETURN:
                        pygame.key.set_repeat(1,50) #holding down keys
                        option = option_types[option_pointer] #user selection
                        print option
                        if option == "gameover_replay":
                            #start a new game
                            newgame = catcom()
                            newgame.mainLoop()
                        elif option == "gameover_quit":
                            print "Goodbye!"
                            pygame.quit()
                            sys.exit(0)
                            break

            '''Display user network options'''
            if self.gamestate == "NETWORK_OPTIONS":
                #blit the appropriate screen
                bg_filename = os.path.join("assets", network_options[network_pointer] + "_bg.bmp")
                self.bg = pygame.image.load(bg_filename).convert()
                self.screen.blit(self.bg, (0,0))
                pygame.display.flip()
                
                #user selection
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        pygame.key.set_repeat(1,50) #holding down keys
                        if network_pointer == len(network_options)-1: #if pointer is already at end, move to beginning of list
                            network_pointer = 0
                            print network_options[network_pointer]                            
                        else:
                            network_pointer = network_pointer + 1 #else move pointer down one
                            print network_options[network_pointer]
                    if event.key == pygame.K_UP:
                        pygame.key.set_repeat(1,50) #holding down keys
                        if network_pointer == 0: #if pointer is already at beginning, move it to end of the list
                            network_pointer = len(option_types)-1;
                            print network_options[network_pointer]
                        else:
                            network_pointer = network_pointer - 1
                            print network_options[network_pointer]
                    
                    if event.key == pygame.K_BACKSPACE: 
                        pygame.key.set_repeat(1,50) #holding down keys
                        option = network_options[network_pointer] #user selection
                        print option
                        if option == "network_client":
                            self.is_server = False
                            #create client socket
                            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.client_socket.connect((HOST,PORT))
##                            self.client_socket.setblocking(0)
                            self.gamestate = "NETWORK"
                            
                        elif option == "network_server":
                            self.is_server = True
                            #create server socket
                            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.server_socket.bind((HOST,PORT))
##                            self.server_socket.setblocking(0)
                            self.server_socket.listen(1)
                            self.conn, self.addr = self.server_socket.accept()#only make the connection once
                            self.gamestate = "NETWORK"
                            

            
            '''Display Graphics for Networking Mode'''
            if self.gamestate == "NETWORK":
                #if the game is run as server, delete the right grid and all of its componenets
                if self.is_server == True:
                    if deleted_right_grid == False:
                        self.gridR = None
                        #self.playerRbusy = None
                        #self.playerRdump = None
                        #self.playerRdumpTimer = None
                        #self.RdumpBuffer = None
                        #self.nextRBlockList = None
                        self.movingblockR = None
                        deleted_right_grid = True
                # if the game is run as the client, delete the left grid and all of its components
                elif self.is_server == False:
                    if deleted_left_grid == False:
                        self.gridL = None
                        #self.playerLbusy = None
                        #self.playerLdump = None
                        #self.playerLdumpTimer = None
                        #self.LdumpBuffer = None
                        #self.nextLBlockList = None
                        self.movingblock = None
                        print 'deleted left side check'
                        deleted_left_grid = True                    
                            
                #blit the appropriate background
                bg_filename = os.path.join("assets", "main_bg.bmp")
                self.bg = pygame.image.load(bg_filename).convert()
                self.screen.blit(self.bg, (0,0))
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print "Goodbye!"
                        pygame.quit()
                        sys.exit(0)

                    #server mode player keys (player 1)
                    if self.is_server == True:
                        #if self.playerLbusy == False:
                            if event.key == pygame.K_LEFT:
                                pygame.key.set_repeat(1,50) #holding down keys
                                self.movingblock.move(pygame.K_LEFT)
                            if event.key == pygame.K_RIGHT:
                                pygame.key.set_repeat(1,50) #holding down keys
                                self.movingblock.move(pygame.K_RIGHT)
                            if event.key == pygame.K_DOWN:
                                self.movingblock.move(pygame.K_DOWN)
                            if event.key == pygame.K_UP:
                                pygame.key.set_repeat(1,50) #holding down keys
                                self.movingblock.rotate()

                    #client mode player keys (player 2)
                    elif self.is_server == False:
                        #if self.playerRBusy == False:
                            if event.key == pygame.K_LEFT:
                                pygame.key.set_repeat(1,50) #holding down keys
                                self.movingblockR.move(pygame.K_LEFT)
                            if event.key == pygame.K_RIGHT:
                                pygame.key.set_repeat(1,50) #holding down keys
                                self.movingblockR.move(pygame.K_RIGHT)
                            if event.key == pygame.K_DOWN:
                                self.movingblockR.move(pygame.K_DOWN)
                            if event.key == pygame.K_UP:
                                pygame.key.set_repeat(1,50) #holding down keys
                                self.movingblockR.rotate()

                self.screen.blit(self.bg, (0,0))
                
                #add SAME randomly generated blocks to both lists
                while len(self.nextLBlockList) < 4 or len(self.nextRBlockList) < 4:
                    
                    nextblock = self.randomizer()
##                    if self.is_server == True:
##                        self.nextLBlockList.append(nextblock)
##                    elif self.is_server == False:
##                        self.nextRBlockList.append(nextblock)
                    self.nextLBlockList.append(nextblock)
                    self.nextRBlockList.append(nextblock) #both block lists are updated, but only one is used depending on client/server

                #draws the next incoming blocks for both players
                self.drawNextBlocks()

                for i in range(4):
                    #replace these with alice's border graphics
                    #left grid (no right grid since this is in networking mode)
                    pygame.draw.line(self.screen,self.linecolor,(45,45+i),(259,45+i))
                    pygame.draw.line(self.screen,self.linecolor,(45+i,45),(45+i,507))
                    pygame.draw.line(self.screen,self.linecolor,(45,504+i),(259,504+i))
                    pygame.draw.line(self.screen,self.linecolor,(259+i,45),(259+i,507))

                    #right grid
                    pygame.draw.line(self.screen,self.linecolor,(622,45+i),(836,45+i))
                    pygame.draw.line(self.screen,self.linecolor,(622+i,45),(622+i,507))
                    pygame.draw.line(self.screen,self.linecolor,(622,504+i),(836,504+i))
                    pygame.draw.line(self.screen,self.linecolor,(836+i,45),(836+i,507))                    

                #blocks
                if self.is_server == True:
                    gameOverL = self.movingblock.update()
                    #send gameOverL to client, and received gameOverR from client
                    if gameOverL == None: gameOverL = 0
                    gameOverR = self.server_game(str(gameOverL))
                elif self.is_server == False:
                    gameOverR = self.movingblockR.update()
                    #semd gameOverR to server, and receive gameOverL from server
                    if gameOverR == None: gameOverR = 0
                    gameOverL = self.client_game(str(gameOverR))

                if gameOverL== 2 or gameOverR == 2:
                    WINNER = "IS YOU"
                    
                    if gameOverL == 2:
                        WINNER = "Player 2"
                        bg_filename = os.path.join("assets", "gameover_p2win_bg.bmp")
                        self.bg = pygame.image.load(bg_filename).convert()
                        self.screen.blit(self.bg, (0,0))
                        blit_win = True
                        
                    else:
                        WINNER = "Player 1"
                        bg_filename = os.path.join("assets", "gameover_p1win_bg.bmp")
                        self.bg = pygame.image.load(bg_filename).convert()
                        self.screen.blit(self.bg, (0,0))
                        blit_win = True                        
                    print "GAME OVER!!! " + WINNER + " WINS!"
                    #time.sleep(3)
                    #pygame.quit()
                    #sys.exit(0)
                    #break
                    if blit_win == True:
                        pygame.display.flip()
                        time.sleep(3)
                        self.gamestate = "GAMEOVER"

                elif gameOverL==1:
                    self.playerLbusy = True
                elif gameOverR == 1:
                    self.playerRbusy = True
                    
                #server: if a block is placed, add it to the grid and make a new moveable block
                if self.is_server:
                    if self.movingblock.placed == True:                        
                        #check not in the middle of a dump
                        if self.playerLdump == False:
                            self.gridL.updateGarbage() #update garbage
                            self.playerLdumpTimer = 0
                            #pops the next 2 blocks to be created from list
                            block1_next = self.nextLBlockList.pop(0)
                            block2_next = self.nextLBlockList.pop(0)
                            #check if need to dump
                            if self.gridL.toDump > 3:
                                self.playerLbusy = True
                                self.playerLdump = True
                                self.playerLdumpTimer = 60
                                print "Dumping " + str(self.gridL.toDump)
                                self.LdumpBuffer = self.gridL.toDump
                                self.gridL.toDump = 0
                                self.dumpBlocks("Left")
                        #finished dump
                        if self.playerLdumpTimer == 0:
                            self.movingblock = moving_piece(self.screen, 154, 14-14, self.gridL, block1_next, block2_next)
                            self.playerLdump = False
                            self.playerLbusy = False

                #client: if a block is placed, add it to the grid and make a new moveable block
                if self.is_server == False:
                    if self.movingblockR.placed == True:                        
                        #check not in the middle of a dump
                        if self.playerRdump == False:
                            self.gridR.updateGarbage() #update garbage
                            self.playerRdumpTimer = 0
                            #pops the next 2 blocks to be created from list
                            block1_next = self.nextRBlockList.pop(0)
                            block2_next = self.nextRBlockList.pop(0)
                            #check if need to dump
                            if self.gridR.toDump > 3:
                                self.playerRbusy = True
                                self.playerRdump = True
                                self.playerRdumpTimer = 60
                                print "Dumping " + str(self.gridR.toDump)
                                self.RdumpBuffer = self.gridR.toDump
                                self.gridR.toDump = 0
                                self.dumpBlocks("Right")
                        #finished dump
                        if self.playerRdumpTimer == 0:
                            self.movingblockR = moving_piece(self.screen, 731, 14-14, self.gridR, block1_next, block2_next)
                            self.playerRdump = False
                            self.playerRbusy = False


                #server timer  
                if self.playerLdumpTimer > 0:
                    if self.playerLdumpTimer % 11 == 0:
                        self.dumpBlocks("Left")
                    self.playerLdumpTimer -= 1
                #client timer
                if self.playerRdumpTimer > 0:
                    if self.playerRdumpTimer % 11 == 0:
                        self.dumpBlocks("Right")
                    self.playerRdumpTimer -= 1

                #server crash count
                if self.is_server:
                    crashCountL = self.gridL.update()
                    #if crashCountL > 0:
                        #add garbage to the other grid
                        #self.gridR.toDump += crashCountL #FIGURE OUT HOW TO SEND GARBAGE BLOCKS TO THE OTHER SIDE

                #client crash count
                elif self.is_server == False:
                    crashCountR = self.gridR.update()
                    #if crashCountR > 0:
                        #add garbage to the other grid
                        #self.gridL.toDump += crashCountR


                '''NETWORKING CODE: IF SERVER, SEND INFO TO CLIENT. IF CLIENT, SEND INFO TO SERVER'''
                if self.is_server == True:
                    self.serve(self.gridL) #sends the server grid to client, blits the client grid
                    pygame.display.flip()
                elif self.is_server == False:
                    self.contact(self.gridR) #sends the client grid to the server, blits server grid
                    pygame.display.flip()
                    
            if blit_win == False: #nobody's won yet
                pygame.display.flip()

                
            '''Display Graphics for local 2-Player mode'''
            if self.gamestate == "2P":
                #blit the appropriate background
                bg_filename = os.path.join("assets", "main_bg.bmp")
                self.bg = pygame.image.load(bg_filename).convert()
                self.screen.blit(self.bg, (0,0))
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print "Goodbye!"
                        pygame.quit()
                        sys.exit(0)
                    if self.playerLbusy == False:
                        #PLAYER 1 KEYS
                        if event.key == pygame.K_a:
                            pygame.key.set_repeat(1,50) #holding down keys
                            self.movingblock.move(pygame.K_LEFT)
                        if event.key == pygame.K_d:
                            pygame.key.set_repeat(1,50) #holding down keys
                            self.movingblock.move(pygame.K_RIGHT)
                        if event.key == pygame.K_s:
                            self.movingblock.move(pygame.K_DOWN)
                        if event.key == pygame.K_w:
                            pygame.key.set_repeat(1,50) #holding down keys
                            self.movingblock.rotate()
                    if self.playerRbusy == False:
                        #PLAYER 2 KEYS
                        if event.key == pygame.K_LEFT:
                            pygame.key.set_repeat(1,50) #holding down keys
                            self.movingblockR.move(pygame.K_LEFT)
                        if event.key == pygame.K_RIGHT:
                            pygame.key.set_repeat(1,50) #holding down keys
                            self.movingblockR.move(pygame.K_RIGHT)
                        if event.key == pygame.K_DOWN:
                            self.movingblockR.move(pygame.K_DOWN)
                        if event.key == pygame.K_UP:
                            pygame.key.set_repeat(1,50) #holding down keys
                            self.movingblockR.rotate()
                    
                self.screen.blit(self.bg, (0,0))
    
                while len(self.nextLBlockList) < 4 or len(self.nextRBlockList) < 4:
                    nextblock = self.randomizer()
                    #add SAME randomly generated blocks to both lists
                    self.nextLBlockList.append(nextblock)
                    self.nextRBlockList.append(nextblock)
    
                #draws the next incoming blocks for both players
                self.drawNextBlocks()
                
                for i in range(4):
                    #replace these with alice's border graphics
                    #left grid
                    pygame.draw.line(self.screen,self.linecolor,(45,45+i),(259,45+i))
                    pygame.draw.line(self.screen,self.linecolor,(45+i,45),(45+i,507))
                    pygame.draw.line(self.screen,self.linecolor,(45,504+i),(259,504+i))
                    pygame.draw.line(self.screen,self.linecolor,(259+i,45),(259+i,507))
                    #right grid
                    pygame.draw.line(self.screen,self.linecolor,(622,45+i),(836,45+i))
                    pygame.draw.line(self.screen,self.linecolor,(622+i,45),(622+i,507))
                    pygame.draw.line(self.screen,self.linecolor,(622,504+i),(836,504+i))
                    pygame.draw.line(self.screen,self.linecolor,(836+i,45),(836+i,507))
    
    
                
                #blocks
                gameOverL = self.movingblock.update()
                gameOverR = self.movingblockR.update()
                #movingblock update returns 1 = freeze the player, 2 = game over
                
                if gameOverL==2 or gameOverR==2:
                    WINNER = "IS YOU"
                    
                    if gameOverL == 2:
                        WINNER = "Player 2"
                        bg_filename = os.path.join("assets", "gameover_p2win_bg.bmp")
                        self.bg = pygame.image.load(bg_filename).convert()
                        self.screen.blit(self.bg, (0,0))
                        blit_win = True
                        
                    else:
                        WINNER = "Player 1"
                        bg_filename = os.path.join("assets", "gameover_p1win_bg.bmp")
                        self.bg = pygame.image.load(bg_filename).convert()
                        self.screen.blit(self.bg, (0,0))
                        blit_win = True                        
                    print "GAME OVER!!! " + WINNER + " WINS!"
                    #time.sleep(3)
                    #pygame.quit()
                    #sys.exit(0)
                    #break
                    if blit_win == True:
                        pygame.display.flip()
                        time.sleep(3)
                        self.gamestate = "GAMEOVER"

                elif gameOverL==1:
                    self.playerLbusy = True
                elif gameOverR==1:
                    self.playerRbusy = True
                
                
                
                #if a block is placed, add it to the grid and make a new moveable block
                if self.movingblock.placed == True:                    
                    #check not in the middle of a dump
                    if self.playerLdump == False:
                        self.gridL.updateGarbage() #update garbage
                        self.playerLdumpTimer = 0
                        #pops the next 2 blocks to be created from list
                        block1_next = self.nextLBlockList.pop(0)
                        block2_next = self.nextLBlockList.pop(0)
                        #check if need to dump
                        if self.gridL.toDump > 3:
                            self.playerLbusy = True
                            self.playerLdump = True
                            self.playerLdumpTimer = 60
                            print "Dumping " + str(self.gridL.toDump)
                            self.LdumpBuffer = self.gridL.toDump
                            self.gridL.toDump = 0
                            self.dumpBlocks("Left")
                    #finished dump
                    if self.playerLdumpTimer == 0:
                        self.movingblock = moving_piece(self.screen, 154, 14-14, self.gridL, block1_next, block2_next)
                        self.playerLdump = False
                        self.playerLbusy = False
                        
                #if a block is placed, add it to the grid and make a new moveable block
                if self.movingblockR.placed == True:                    
                    #check not in the middle of a dump
                    if self.playerRdump == False:
                        self.gridR.updateGarbage() #update garbage
                        self.playerRdumpTimer = 0
                        #pops the next 2 blocks to be created from list
                        block1_next = self.nextRBlockList.pop(0)
                        block2_next = self.nextRBlockList.pop(0)
                        #check if need to dump
                        if self.gridR.toDump > 3:
                            self.playerRbusy = True
                            self.playerRdump = True
                            self.playerRdumpTimer = 60
                            print "Dumping " + str(self.gridR.toDump)
                            self.RdumpBuffer = self.gridR.toDump
                            self.gridR.toDump = 0
                            self.dumpBlocks("Right")
                    #finished dump
                    if self.playerRdumpTimer == 0:
                        self.movingblockR = moving_piece(self.screen, 731, 14-14, self.gridR, block1_next, block2_next)
                        self.playerRdump = False
                        self.playerRbusy = False
                    
                if self.playerLdumpTimer > 0:
                    if self.playerLdumpTimer % 11 == 0:
                        self.dumpBlocks("Left")
                    self.playerLdumpTimer -= 1
                
                if self.playerRdumpTimer > 0:
                    if self.playerRdumpTimer % 11 == 0:
                        self.dumpBlocks("Right")
                    self.playerRdumpTimer -= 1
      
                crashCountL = self.gridL.update()
                if crashCountL > 0:
                    #add garbage to the other grid
                    self.gridR.toDump += crashCountL
                
                crashCountR = self.gridR.update()
                if crashCountR > 0:
                    #add garbage to the other grid
                    self.gridL.toDump += crashCountR
                    
            if blit_win == False: #nobody's won yet
                pygame.display.flip()


    '''NETWORKING CODE'''
    # sends the server's gameOverL value to the client, and retrieves the client's gameOverR
    def server_game(self, status):
        try:
            client_status = self.conn.recv(1)
            self.conn.send(status)
            return int(client_status)
        
        except IOError: #if the client disconnects, exit
            time.sleep(3)
            pygame.quit()
            sys.exit(0)

    #sends the client's gameOverR value to the server, and retrieves the server's gameOverL
    def client_game(self, status):
        try:
            self.client_socket.send(status)
            server_status = self.client_socket.recv(1)
            return int(server_status)
        
        except:# if the server disconnects, exit
            time.sleep(3)
            pygame.quit()
            sys.exit(0)
        
    # SERVER CODE
    def serve(self,grid):
        try:

            #receive the client grid in string form
            client_grid = self.conn.recv(84)
##            print 'received client: ', client_grid

            rc = self.rowCounter            

            #now iterate through each character in the client_grid and blit the appropriate images
            for i in client_grid:
                if i == '1': file_name = os.path.join('assets','red_normal.gif') #normal red block
                elif i == '2': file_name = os.path.join('assets', 'yellow_normal.gif') #normal yellow block
                elif i == '3': file_name = os.path.join('assets', 'green_normal.gif') #normal green block
                elif i == '4': file_name = os.path.join('assets', 'blue_normal.gif') #normal blue block
                elif i == 'w': file_name = os.path.join('assets', 'red_crash.gif')
                elif i == 'x': file_name = os.path.join('assets', 'yellow_crash.gif')
                elif i == 'y': file_name = os.path.join('assets', 'green_crash.gif')
                elif i == 'z': file_name = os.path.join('assets', 'blue_crash.gif')
                elif i == 'g': file_name = os.path.join('assets', 'sample_block.bmp') #garbage block (any)

                if i != '0':           
                    block = pygame.image.load(file_name).convert()
##                    print "BLITTING "+str(block)+" AT ("+str(self.RColCounter)+","+str(rc)+")"
                    self.screen.blit(block, (self.RColCounter, rc))

                #update the RColCounter                    
                if self.RColCounter == 801:
                    self.RColCounter = 626
                    rc = rc+35 #INCREMENT row
                else:
                    self.RColCounter = self.RColCounter + 35                  


            #convert server grid to string and send to client
            server_grid = grid.convertToString()
            self.conn.send(server_grid)
##            print "server sent grid to client"
            
        except IOError:
            print "server disconnected!"
            time.sleep(3)
            pygame.quit()
            sys.exit(0)
                   
    # CLIENT CODE
    def contact(self,grid):        
        try:
            #send the client grid to server after converting to string
            client_grid = grid.convertToString()
            self.client_socket.send(client_grid)
##            print "client sent grid to server"
            
            #receive the server grid in string form
            server_grid = self.client_socket.recv(84)
##            print "received server: ", server_grid

            rc = self.rowCounter            

            #now iterate through each character in the client_grid and blit the appropriate images
            for i in server_grid:
                if i == '1': file_name = os.path.join('assets','red_normal.gif') #normal red block
                elif i == '2': file_name = os.path.join('assets', 'yellow_normal.gif') #normal yellow block
                elif i == '3': file_name = os.path.join('assets', 'green_normal.gif') #normal green block
                elif i == '4': file_name = os.path.join('assets', 'blue_normal.gif') #normal blue block
                elif i == 'w': file_name = os.path.join('assets', 'red_crash.gif')
                elif i == 'x': file_name = os.path.join('assets', 'yellow_crash.gif')
                elif i == 'y': file_name = os.path.join('assets', 'green_crash.gif')
                elif i == 'z': file_name = os.path.join('assets', 'blue_crash.gif')
                elif i == 'g': file_name = os.path.join('assets', 'sample_block.bmp') #garbage block (any)

                if i != '0':           
                    block = pygame.image.load(file_name).convert()
##                    print "BLITTING "+str(block)+" AT ("+str(self.LColCounter)+","+str(rc)+")"
                    self.screen.blit(block, (self.LColCounter, rc))

                #update the RColCounter                    
                if self.LColCounter == 224:
                    self.LColCounter = 49
                    rc = rc+35 #INCREMENT row
                else:
                    self.LColCounter = self.LColCounter + 35                            
            
        except:
            print "client disconnected!"
            time.sleep(3)
            pygame.quit()
            sys.exit(0)
    
            
if __name__ == "__main__":
    if len(sys.argv) == 2:
        global HOST
        HOST = sys.argv[1] #ip address argument. If none provided, then use local host
    myCatcom = catcom()
    myCatcom.mainLoop()
    
##    test_screen = pygame.display.get_surface()
##    test_grid = gameGrid(49, 49, test_screen)
##

#FADE CODE - IGNORE - http://www.mail-archive.com/pygame-users@seul.org/msg10851.html
#surf1 = #whatever
#surf2 = #whatever (entirely black or white surface, etc.).
#for step in xrange(transition_length):
#    surf1.set_alpha(int(round((float(step)/transition_length)*255.0)))
    #draw surf1 over surf2
