# snakeotron.py

import time
import random
from collections import deque

import appuifw
import e32
import graphics
from key_codes import EKeyRightArrow, EKeyUpArrow, EKeyLeftArrow, EKeyDownArrow


class State:
    """ Enum-like behavior for the game's current state """
    RUNNING = object()
    PAUSED  = object()
    EXITING = object()

    def __init__(self):
        raise Exception("Please don't instantiate me")

class Direction:
    """ Enum-like behavior for the snake's current direction """
    UP    = object()
    DOWN  = object()
    LEFT  = object()
    RIGHT = object()

    def __init__(self):
        raise Exception("Please don't instantiate me")

    @staticmethod
    def opposite(direction):
        opposites = ([Direction.UP, Direction.DOWN]
                    ,[Direction.LEFT, Direction.RIGHT]
                    )
        for opp in opposites:
            if direction in opp:
                opp.remove(direction)
                return opp[0]


class Snake:
    """
    A Snake in the game
    
    Stores the color, length and current place the of snake,
    also responsible for moving itself one step at a time

    The snake is represented with a deque, a list-like datastructure
    that allows efficient pop/push on both ends of the list. 
    """

    def __init__(self, start_pos = (1,1), color = (0,0,200)):
        self.color = color
        self.direction = Direction.RIGHT
        self.length = 8 # default snake length
        self.body = deque([start_pos])

    def eat(self, blocks = 3):
        self.length += blocks

    def move(self):
        headx, heady = self.body[0]
        if self.direction == Direction.UP:
            newhead = (headx, heady - 1)
        elif self.direction == Direction.DOWN:
            newhead = (headx, heady + 1)
        elif self.direction == Direction.LEFT:
            newhead = (headx - 1, heady)
        elif self.direction == Direction.RIGHT:
            newhead = (headx + 1, heady)
        self.body.appendleft(newhead)

        if len(self.body) > self.length:
            self.body.pop()

class GameState:
    def __init__(self):

        self.reset()

    def reset(self):
        """ Set the game's state to default values """

        self.TICKLENGTH = 0.2 # length of one step in second
        self.BLOCKSIZE = 8 # size of one block on the map in pixels

        self.playersnake = Snake(start_pos = (10, 10),
                                 color = (0, 0, 200))
        self.AIsnakes = []
        self.food = None

        # Nokia C5 display size: 240x320
        # available "large" canvas size: 240x293
        self.set_wall(240,293) # FIXME hardwired resolution data
        self.wallcolor = (116, 0, 0)

        self.foodcolor = (59, 255, 0)
        self.place_new_food()

    def set_wall(self, width, height):
        self.wall = []

        mapwidth = width // self.BLOCKSIZE 
        mapheight = height // self.BLOCKSIZE
        for x in range(0, mapwidth):
            self.wall.append((x, 0))
            self.wall.append((x, mapheight -1))
        for y in range(0, mapheight):
            self.wall.append((0, y))
            self.wall.append((mapwidth - 1, y))

        self.mapwidth = mapwidth - 1
        self.mapheight = mapheight - 1

    def set_player_direction(self, direction):
        if Direction.opposite(direction) == self.playersnake.direction:
            return
        self.playersnake.direction = direction

    def place_new_food(self):
        def occupied(x,y):
            if (x,y) in self.playersnake.body:
                return True
            # for snake in aisnakes
            return False
        x = random.randint(1, self.mapwidth - 1)
        y = random.randint(1, self.mapheight -1)
        while occupied(x,y):
            x = random.randint(1, self.mapwidth -1)
            y = random.randint(1, self.mapheight -1)

        self.food = (x, y)

    def collision_check(self):
        head = self.playersnake.body.popleft()
        if head in self.wall:
            exit(1)
        if head in self.playersnake.body:
            exit(1)
        self.playersnake.body.appendleft(head)

    def update_world(self, steps):
        #move snakes <steps> times
        for _ in range(steps):
            self.playersnake.move()
            # for snake in self.AIsnakes: 
            #   snake.move()
            self.collision_check()
            
            if self.food in self.playersnake.body:
                self.playersnake.eat()
                self.food = None
        # create new food if it got eaten
        if not self.food:
            self.place_new_food()


class SnakeOTron:
    def __init__(self):
        appuifw.app.screen="large"
        appuifw.app.title = u"SNAKE-O-TRON"

        appuifw.app.exit_key_handler=self.on_exit

        self.bgcolor = (154, 154, 154)
        self.canvas=appuifw.Canvas(redraw_callback=self.redraw)
        self.draw=graphics.Draw(self.canvas)

        self.canvas.bind(EKeyUpArrow,    lambda:self.turnto(Direction.UP))
        self.canvas.bind(EKeyDownArrow,  lambda:self.turnto(Direction.DOWN))
        self.canvas.bind(EKeyLeftArrow,  lambda:self.turnto(Direction.LEFT))
        self.canvas.bind(EKeyRightArrow, lambda:self.turnto(Direction.RIGHT))

        self.old_body = appuifw.app.body
        appuifw.app.body = self.canvas

        random.seed()

        self.gamestate = GameState()
    
    def turnto(self, direction):
        self.gamestate.set_player_direction(direction)


    def draw_block(self, x, y, color):
        BLOCKSIZE = 8
        rect_x1 = BLOCKSIZE * x
        rect_x2 = rect_x1 + BLOCKSIZE
        rect_y1 = BLOCKSIZE * y
        rect_y2 = rect_y1 + BLOCKSIZE
        self.draw.rectangle((rect_x1, rect_y1,
                             rect_x2,rect_y2),
                             fill=color)

    def draw_snake(self, snake):
        for (x,y) in snake.body:
            self.draw_block(x,y,snake.color)

    def draw_walls(self):
        for (x,y) in self.gamestate.wall:
            self.draw_block(x,y,self.gamestate.wallcolor)

    def draw_food(self):
        x, y = self.gamestate.food
        self.draw_block(x ,y, self.gamestate.foodcolor)

    def redraw(self, rect = None):
        self.draw.clear(self.bgcolor)
        self.draw_walls()
        self.draw_snake(self.gamestate.playersnake)
        self.draw_food()
        #for snake in aisnakes
        #   draw_snake(snake)
        #draw_food

    def on_exit(self):
        self.state = State.EXITING

    def close_canvas(self):
        appuifw.app.body=self.old_body
        self.canvas=None
        appuifw.app.exit_key_handler=None

    def mainloop(self):
        """ The infinite main loop of the game """
        lastupdate = time.clock()

        while self.state == State.RUNNING:
            loop_started = time.clock() # get the current time and...
            # ...decide how many steps happened since the last update
            steps, _ = divmod(loop_started - lastupdate, self.gamestate.TICKLENGTH)

            # update the world according to the steps
            if steps > 0:
                self.gamestate.update_world(steps)
                lastupdate = time.clock()

            # draw the updated world
            self.redraw()

            # if the whole loop took less time than one step supposed to 
            # then sleep until the next step
            remaining_time = self.gamestate.TICKLENGTH - (time.clock() - loop_started)
            if remaining_time > 0:
                e32.ao_sleep(remaining_time)
        self.close_canvas()

    def startgame(self):
        self.state = State.RUNNING
        self.mainloop()

def start(x, y, score, energy):
    """ entry point for the HomeWoRPG framework """
    return (score, energy)


g = SnakeOTron()
g.startgame()
print " ---- exiting ---- "
