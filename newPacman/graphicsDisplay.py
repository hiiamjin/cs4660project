from graphicsUtils import *        
import math, time
from game import Directions

###########################
#  GRAPHICS DISPLAY CODE  #
###########################

# Most code by Dan Klein and John Denero written or rewritten for cs188, UC Berkeley.
# Some code from a Pacman implementation by LiveWires, and used / modified with permission.

FRAME_TIME=0 # The time that pacman's animation last
PAUSE_TIME=0   # Pause time between frames
DEFAULT_GRID_SIZE = 30.0
INFO_PANE_HEIGHT = 35
BACKGROUND_COLOR = formatColor(0,0,0)    
WALL_COLOR = formatColor(0.0/255.0, 51.0/255.0, 255.0/255.0)
INFO_PANE_COLOR = formatColor(.4,.4,0)
SCORE_COLOR = formatColor(.9, .9, .9)
PACMAN_OUTLINE_WIDTH = 4

GHOST_COLORS = []                       
GHOST_COLORS.append(formatColor(.9,0,0)) # Red
GHOST_COLORS.append(formatColor(0,.3,.9)) # Blue
GHOST_COLORS.append(formatColor(.98,.41,.07)) # Orange
GHOST_COLORS.append(formatColor(.1,.75,.7)) # Green
GHOST_COLORS.append(formatColor(1.0,0.6,0.0)) # Yellow
GHOST_COLORS.append(formatColor(.4,0.13,0.91)) # Purple

TEAM_COLORS = GHOST_COLORS[:2]

GHOST_SHAPE = [                
    ( 0,    0.3 ),            
    ( 0.25, 0.75 ),           
    ( 0.5,  0.3 ),
    ( 0.75, 0.75 ),
    ( 0.75, -0.5 ),
    ( 0.5,  -0.75 ),
    (-0.5,  -0.75 ),
    (-0.75, -0.5 ),
    (-0.75, 0.75 ),
    (-0.5,  0.3 ),
    (-0.25, 0.75 )
  ]
GHOST_SIZE = 0.65
SCARED_COLOR = formatColor(1,1,1)    

GHOST_VEC_COLORS = map(colorToVector, GHOST_COLORS)

PACMAN_COLOR = formatColor(255.0/255.0,255.0/255.0,61.0/255)
PACMAN_SCALE = 0.5  
#pacman_speed = 0.25    

# Food
FOOD_COLOR = formatColor(1,1,1)     
FOOD_SIZE = 0.1   

# Laser
LASER_COLOR = formatColor(1,0,0)     
LASER_SIZE = 0.02   
        
# Capsule graphics
CAPSULE_COLOR = formatColor(1,1,1)
CAPSULE_SIZE = 0.25 

# Drawing walls
WALL_RADIUS = 0.15

class InfoPane:
  def __init__(self, layout, gridSize):
    self.gridSize = gridSize
    self.width = (layout.width) * gridSize
    self.base = (layout.height + 1) * gridSize
    self.height = INFO_PANE_HEIGHT 
    self.drawPane()

  def toScreen(self, pos, y = None):
    """
      Translates a point relative from the bottom left of the info pane.
    """
    if y == None:
      x,y = pos
    else:
      x = pos
      
    x = self.gridSize + x # Margin
    y = self.base + y 
    return x,y

  def drawPane(self):
    color = PACMAN_COLOR
    size = 24
    self.scoreText = text( self.toScreen(0, 0  ), color, "SCORE:    0", "Times", size, "bold")
    self.teamText = text( self.toScreen(300, 0  ), color, "Red Team", "Times", size, "bold")
    self.ghostDistanceText = []
    
  def updateScore(self, score):
    changeText(self.scoreText, "SCORE: % 4d" % score)

  def updateTeam(self, isBlue):
    if isBlue:
      changeText(self.teamText, "Blue Team") 
    else:
      changeText(self.teamText, "Red Team") 
  
  def drawGhost(self):
    pass
  
  def drawPacman(self):
    pass
    
  def drawWarning(self):
    pass
    
  def clearIcon(self):
    pass
    
  def updateMessage(self, message):
    pass
    
  def clearMessage(self):
    pass


class PacmanGraphics:
  def __init__(self, zoom=1.0, capture=False):  
    self.have_window = 0
    self.currentGhostImages = {}
    self.pacmanImage = None
    self.zoom = zoom
    self.gridSize = DEFAULT_GRID_SIZE * zoom
    self.capture = capture
  
  def initialize(self, state, isBlue = False):
    self.isBlue = isBlue
    self.startGraphics(state)
    self.drawInitialObjects(state)
    
  def startGraphics(self, state):
    self.layout = state.layout
    layout = self.layout
    self.width = layout.width
    self.height = layout.height
    self.make_window(self.width, self.height)
    self.infoPane = InfoPane(layout, self.gridSize)
    self.infoPane.updateTeam(self.isBlue)
    self.currentState = layout
    self.closed = False
    
  def drawInitialObjects(self, state):
    layout = self.layout
    self.drawWalls(layout.walls)
    self.food = self.drawFood(layout.food)
    self.capsules = self.drawCapsules(layout.capsules)
    refresh
    
    self.agentImages = [] # (agentState, image)
    for index, agent in enumerate(state.agentStates):
      if agent.isPacman:
        image = self.drawPacman(agent, index)
        self.agentImages.append( (agent, image) )
      else:
        image = self.drawGhost(agent, index)
        self.agentImages.append( (agent, image) )
        
    if self.capture:
      self.drawCenterLine()
    refresh
  
  def drawCenterLine(self):
    """
      Draws a line in the center of the board
    """
    pass
  
  def swapImages(self, agentIndex, newState):
    """
      Changes an image from a ghost to a pacman or vis versa (for capture)
    """
    prevState, prevImage = self.agentImages[agentIndex]
    for item in prevImage: remove_from_screen(item)
    if newState.isPacman:
      image = self.drawPacman(newState, agentIndex)
      self.agentImages[agentIndex] = (newState, image )
    else:
      image = self.drawGhost(newState, agentIndex)
      self.agentImages[agentIndex] = (newState, image )
    refresh
    
  def update(self, newState):
    if self.closed:
      return
    agentIndex = newState._agentMoved
    agentState = newState.agentStates[agentIndex]
    
    if self.agentImages[agentIndex][0].isPacman != agentState.isPacman: self.swapImages(agentIndex, agentState)
    prevState, prevImage = self.agentImages[agentIndex]
    if agentState.isPacman:
      self.animatePacman(agentState, prevState, prevImage)
    else:
      self.moveGhost(agentState, agentIndex, prevState, prevImage)
    self.agentImages[agentIndex] = (agentState, prevImage)
      
    if newState._foodEaten != None:
      self.removeFood(newState._foodEaten, self.food)
    if newState._capsuleEaten != None:
      self.removeCapsule(newState._capsuleEaten, self.capsules)
      
    self.infoPane.updateScore(newState.score)
    
  def make_window(self, width, height):
    grid_width = (width-1) * self.gridSize 
    grid_height = (height-1) * self.gridSize 
    screen_width = 2*self.gridSize + grid_width
    screen_height = 2*self.gridSize + grid_height + INFO_PANE_HEIGHT 

    begin_graphics(screen_width,    
                   screen_height,
                   BACKGROUND_COLOR,
                   "CS188 Pacman")
    
  def drawPacman(self, pacman, index):
    position = self.getPosition(pacman)
    screen_point = self.to_screen(position)
    endpoints = self.getEndpoints(self.getDirection(pacman))
    # width = (index == 0 and 1) or 4
    width = PACMAN_OUTLINE_WIDTH
    outlineColor = PACMAN_COLOR
    if self.capture:
      outlineColor = TEAM_COLORS[index % 2]
      
    return [circle(screen_point, PACMAN_SCALE * self.gridSize, 
                   fillColor = GHOST_COLORS[index], outlineColor = outlineColor, 
                   endpoints = endpoints,
                   width = width)]

  def getEndpoints(self, direction, position=(0,0)):
    x, y = position
    pos = x - int(x) + y - int(y)
    width = 30 + 80 * math.sin(math.pi*pos)
    
    delta = width / 2
    if (direction == 'West'):
      endpoints = (180+delta, 180-delta)
    elif (direction == 'North'):
      endpoints = (90+delta, 90-delta)
    elif (direction == 'South'):
      endpoints = (270+delta, 270-delta)
    else:
      endpoints = (0+delta, 0-delta)
    return endpoints

  def movePacman(self, position, direction, image):
    screenPosition = self.to_screen(position)
    endpoints = self.getEndpoints( direction, position )
    r = PACMAN_SCALE * self.gridSize 
    moveCircle(image[0], screenPosition, r, endpoints)
    refresh
    
  def animatePacman(self, pacman, prevPacman, image):
    if FRAME_TIME > 0.01:
      start = time.time()
      fx, fy = self.getPosition(prevPacman)
      px, py = self.getPosition(pacman)
      frames = 4.0
      for i in range(int(frames)):
        pos = px*i/frames + fx*(frames-i)/frames, py*i/frames + fy*(frames-i)/frames 
        self.movePacman(pos, self.getDirection(pacman), image)
        # if time.time() - start > FRAME_TIME: return
        # sleep(FRAME_TIME / 2 / frames)
    else:
      self.movePacman(self.getPosition(pacman), self.getDirection(pacman), image)
      

  def getGhostColor(self, ghost, ghostIndex):
    if ghost.scaredTimer > 0:
      return SCARED_COLOR
    else:
      return GHOST_COLORS[ghostIndex]

  def drawGhost(self, ghost, agentIndex):
    pos = self.getPosition(ghost)
    dir = self.getDirection(ghost)
    (screen_x, screen_y) = (self.to_screen(pos) ) 
    coords = []          
    for (x, y) in GHOST_SHAPE:
      coords.append((x*self.gridSize*GHOST_SIZE + screen_x, y*self.gridSize*GHOST_SIZE + screen_y))
    
    color = self.getGhostColor(ghost, agentIndex)
    body = polygon(coords, color, filled = 1)
    bodyColor = self.getGhostColor(ghost, agentIndex)
    WHITE = formatColor(1.0, 1.0, 1.0)
    BLACK = formatColor(0.0, 0.0, 0.0)
    
    dx = 0
    dy = 0
    if dir == 'North':
      dy = -0.2
    if dir == 'South':
      dy = 0.2
    if dir == 'East':
      dx = 0.2
    if dir == 'West':
      dx = -0.2
    leftEye = circle((screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2, WHITE, WHITE)
    rightEye = circle((screen_x+self.gridSize*GHOST_SIZE*(0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2, WHITE, WHITE)
    leftPupil = circle((screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08, BLACK, BLACK)
    rightPupil = circle((screen_x+self.gridSize*GHOST_SIZE*(0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08, BLACK, BLACK)
    ghostImageParts = []
    ghostImageParts.append(body)
    ghostImageParts.append(leftEye)
    ghostImageParts.append(rightEye)
    ghostImageParts.append(leftPupil)
    ghostImageParts.append(rightPupil)
    
    return ghostImageParts
  
  def moveEyes(self, pos, dir, eyes):
    (screen_x, screen_y) = (self.to_screen(pos) ) 
    dx = 0
    dy = 0
    if dir == 'North':
      dy = -0.2
    if dir == 'South':
      dy = 0.2
    if dir == 'East':
      dx = 0.2
    if dir == 'West':
      dx = -0.2
    moveCircle(eyes[0],(screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2)
    moveCircle(eyes[1],(screen_x+self.gridSize*GHOST_SIZE*(0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2)
    moveCircle(eyes[2],(screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08)
    moveCircle(eyes[3],(screen_x+self.gridSize*GHOST_SIZE*(0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08)
    
  def moveGhost(self, ghost, ghostIndex, prevGhost, ghostImageParts):
    old_x, old_y = self.to_screen(self.getPosition(prevGhost))
    new_x, new_y = self.to_screen(self.getPosition(ghost))
    delta = new_x - old_x, new_y - old_y
    
    for ghostImagePart in ghostImageParts:
      move_by(ghostImagePart, delta)
    refresh
    
    if ghost.scaredTimer > 0:
      color = SCARED_COLOR
    else:
      color = GHOST_COLORS[ghostIndex]
    edit(ghostImageParts[0], ('fill', color), ('outline', color))  
    self.moveEyes(self.getPosition(ghost), self.getDirection(ghost), ghostImageParts[-4:])
    refresh
    
  def getPosition(self, agentState):
    if agentState.configuration == None: return (-1000, -1000)
    return agentState.getPosition()
  
  def getDirection(self, agentState):
    if agentState.configuration == None: return Directions.STOP
    return agentState.configuration.getDirection()
  
  def finish(self):
    self.closed = True
    end_graphics()
  
  def to_screen(self, point):
    ( x, y ) = point
    #y = self.height - y
    x = (x + 1)*self.gridSize
    y = (self.height  - y)*self.gridSize
    return ( x, y )
  
  # Fixes some TK issue with off-center circles
  def to_screen2(self, point):
    ( x, y ) = point
    #y = self.height - y
    x = (x + 1)*self.gridSize
    y = (self.height  - y)*self.gridSize
    return ( x, y )
  
  def drawWalls(self, wallMatrix):
    wallColor = WALL_COLOR
    for xNum, x in enumerate(wallMatrix):
      if self.capture and (xNum * 2) < wallMatrix.width: wallColor = TEAM_COLORS[0]
      if self.capture and (xNum * 2) >= wallMatrix.width: wallColor = TEAM_COLORS[1]

      for yNum, cell in enumerate(x):
        if cell: # There's a wall here
          pos = (xNum, yNum)
          screen = self.to_screen(pos)
          screen2 = self.to_screen2(pos)
          
          # draw each quadrant of the square based on adjacent walls
          wIsWall = self.isWall(xNum-1, yNum, wallMatrix)
          eIsWall = self.isWall(xNum+1, yNum, wallMatrix)
          nIsWall = self.isWall(xNum, yNum+1, wallMatrix)
          sIsWall = self.isWall(xNum, yNum-1, wallMatrix)
          nwIsWall = self.isWall(xNum-1, yNum+1, wallMatrix)
          swIsWall = self.isWall(xNum-1, yNum-1, wallMatrix)
          neIsWall = self.isWall(xNum+1, yNum+1, wallMatrix)
          seIsWall = self.isWall(xNum+1, yNum-1, wallMatrix)
          
          # NE quadrant
          if (not nIsWall) and (not eIsWall):
            # inner circle
            circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (0,91), 'arc')
          if (nIsWall) and (not eIsWall):
            # vertical line
            line(add(screen, (self.gridSize*WALL_RADIUS, 0)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(-0.5)-1)), wallColor)
          if (not nIsWall) and (eIsWall):
            # horizontal line
            line(add(screen, (0, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5+1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
          if (nIsWall) and (eIsWall) and (not neIsWall):
            # outer circle
            circle(add(screen2, (self.gridSize*2*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (180,271), 'arc')
            line(add(screen, (self.gridSize*2*WALL_RADIUS-1, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5+1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
            line(add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS+1)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(-0.5))), wallColor)
          
          # NW quadrant
          if (not nIsWall) and (not wIsWall):
            # inner circle
            circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (90,181), 'arc')
          if (nIsWall) and (not wIsWall):
            # vertical line
            line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, 0)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-0.5)-1)), wallColor)
          if (not nIsWall) and (wIsWall):
            # horizontal line
            line(add(screen, (0, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5)-1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
          if (nIsWall) and (wIsWall) and (not nwIsWall):
            # outer circle
            circle(add(screen2, (self.gridSize*(-2)*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (270,361), 'arc')
            line(add(screen, (self.gridSize*(-2)*WALL_RADIUS+1, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5), self.gridSize*(-1)*WALL_RADIUS)), wallColor)
            line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS+1)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-0.5))), wallColor)
          
          # SE quadrant
          if (not sIsWall) and (not eIsWall):
            # inner circle
            circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (270,361), 'arc')
          if (sIsWall) and (not eIsWall):
            # vertical line
            line(add(screen, (self.gridSize*WALL_RADIUS, 0)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(0.5)+1)), wallColor)
          if (not sIsWall) and (eIsWall):
            # horizontal line
            line(add(screen, (0, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5+1, self.gridSize*(1)*WALL_RADIUS)), wallColor)
          if (sIsWall) and (eIsWall) and (not seIsWall):
            # outer circle
            circle(add(screen2, (self.gridSize*2*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (90,181), 'arc')
            line(add(screen, (self.gridSize*2*WALL_RADIUS-1, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5, self.gridSize*(1)*WALL_RADIUS)), wallColor)
            line(add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS-1)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(0.5))), wallColor)
          
          # SW quadrant
          if (not sIsWall) and (not wIsWall):
            # inner circle
            circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (180,271), 'arc')
          if (sIsWall) and (not wIsWall):
            # vertical line
            line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, 0)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(0.5)+1)), wallColor)
          if (not sIsWall) and (wIsWall):
            # horizontal line
            line(add(screen, (0, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5)-1, self.gridSize*(1)*WALL_RADIUS)), wallColor)
          if (sIsWall) and (wIsWall) and (not swIsWall):
            # outer circle
            circle(add(screen2, (self.gridSize*(-2)*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (0,91), 'arc')
            line(add(screen, (self.gridSize*(-2)*WALL_RADIUS+1, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5), self.gridSize*(1)*WALL_RADIUS)), wallColor)
            line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS-1)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(0.5))), wallColor)
          
  def isWall(self, x, y, walls):
    if x < 0 or y < 0:
      return False
    if x >= walls.width or y >= walls.height:
      return False
    return walls[x][y]
  
  def drawFood(self, foodMatrix ):
    foodImages = []
    color = FOOD_COLOR
    for xNum, x in enumerate(foodMatrix):
      if self.capture and (xNum * 2) <= foodMatrix.width: color = TEAM_COLORS[0]
      if self.capture and (xNum * 2) > foodMatrix.width: color = TEAM_COLORS[1]
      imageRow = []
      foodImages.append(imageRow)
      for yNum, cell in enumerate(x):
        if cell: # There's food here
          screen = self.to_screen((xNum, yNum ))
          dot = circle( screen, 
                        FOOD_SIZE * self.gridSize, 
                        outlineColor = color, fillColor = color,
                        width = 1)
          imageRow.append(dot)
        else:
          imageRow.append(None)
    return foodImages
  
  def drawCapsules(self, capsules ):
    capsuleImages = {}
    for capsule in capsules:
      ( screen_x, screen_y ) = self.to_screen(capsule)
      dot = circle( (screen_x, screen_y), 
                        CAPSULE_SIZE * self.gridSize, 
                        color = CAPSULE_COLOR, 
                        filled = 1,
                        width = 1)
      capsuleImages[capsule] = dot
    return capsuleImages
  
  def removeFood(self, cell, foodImages ):
    x, y = cell
    remove_from_screen(foodImages[x][y])
    
  def removeCapsule(self, cell, capsuleImages ):
    x, y = cell
    remove_from_screen(capsuleImages[(x, y)])

  def drawExpandedCells(self, cells):
    """
    Draws an overlay of expanded grid positions for search agents
    """
    n = float(len(cells))
    baseColor = [1.0, 0.0, 0.0]
    self.clearExpandedCells()
    self.expandedCells = []
    for k, cell in enumerate(cells):
       screenPos = self.to_screen( cell)
       cellColor = formatColor(*[(n-k) * c * .5 / n + .25 for c in baseColor])
       block = square(screenPos, 
                0.5 * self.gridSize, 
                color = cellColor, 
                filled = 1, behind=True)
       self.expandedCells.append(block)
  
  def clearExpandedCells(self):
    if 'expandedCells' in dir(self) and len(self.expandedCells) > 0:
      for cell in self.expandedCells:
        remove_from_screen(cell)

class FirstPersonPacmanGraphics(PacmanGraphics):
  def initialize(self, state):
    
    PacmanGraphics.startGraphics(self, state)
    # Initialize distribution images
    walls = state.layout.walls
    dist = []
    self.layout = state.layout
    
    for x in range(len(walls)):
      distx = []
      dist.append(distx)
      for y in range(len(walls[0])):
          ( screen_x, screen_y ) = self.to_screen( (x, y) )
          block = square( (screen_x, screen_y), 
                          0.5 * self.gridSize, 
                          color = BACKGROUND_COLOR, 
                          filled = 1)
          distx.append(block)
    self.distributionImages = dist

    # Draw the rest
    PacmanGraphics.drawInitialObjects(self, state)
    
    # Information
    self.laserImage = None
    self.infoPane.initializeGhostDistances(state.getGhostDistances())
    self.previousState = state
    
  def updateDistribution(self, distributions, pacConfiguration):
    (pacRow, pacCol), pacVec = pacConfiguration.getPosition(), pacConfiguration.getDirection()
    for x in range(len(self.distributionImages)):
      for y in range(len(self.distributionImages[0])):
        image = self.distributionImages[x][y]
        weights = distributions[x][y]
        
        # Fog of war
        color = [0.0,0.0,0.0]
        for weight, gcolor in zip(weights, GHOST_VEC_COLORS):
          color = [min(1.0, c + 0.95 * g * weight ** .3) for c,g in zip(color, gcolor)]
        changeColor(image, formatColor(*color))
    
  def drawLaser(self, config, state):
    if config.getDirection() == 'Stop':
      return
    else:
      self.laserImage = [] 
      x, y = config.getPosition()
      direction = config.getDirection()
      for cell in state.layout.visibility[int(x)][int(y)][direction]:
        ( screen_x, screen_y ) = self.to_screen(cell)
        dot = circle( (screen_x, screen_y), 
                        LASER_SIZE * self.gridSize, 
                        color = LASER_COLOR, 
                        filled = 1,
                        width = 1)
        self.laserImage.append(dot)

  def lookAhead(self, config, state):
    if config.getDirection() == 'Stop':
      return
    else:
      pass
      # Draw relevant ghosts
      allGhosts = state.getGhostStates()
      visibleGhosts = state.getVisibleGhosts()
      for i, ghost in enumerate(allGhosts):
        if ghost in visibleGhosts:
          self.drawGhost(ghost, i)
        else:
          self.currentGhostImages[i] = None
    
  def update(self, newState):
    agentIndex = newState._agentMoved
    if agentIndex != 0:
      return
    
    # Update laser
    if self.laserImage != None:
      for part in self.laserImage:
        remove_from_screen(part)
    self.drawLaser(newState.getPacmanState().configuration, newState)
        

    # Erase old field of view
    for index, image in self.currentGhostImages.items():
      if image != None:
        for part in image:
          remove_from_screen(part)
    
    # Draw visible ghosts and laser sight
    self.lookAhead(newState.getPacmanState().configuration, newState)
    
    # Move pacman
    self.animatePacman(newState.getPacmanState())
    self.previousPacman = newState.getPacmanState()
    
    if newState._foodEaten != None:
      self.removeFood(newState._foodEaten, self.food)
    if newState._capsuleEaten != None:
      self.removeCapsule(newState._capsuleEaten, self.capsules)
      
    # Information
    self.infoPane.updateScore(newState.score)
    self.infoPane.updateGhostDistances(newState.getGhostDistances())

  def getGhostColor(self, ghost, ghostIndex):
    return GHOST_COLORS[ghostIndex]

def add(x, y):
  return (x[0] + y[0], x[1] + y[1])