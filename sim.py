import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation as fanim
import numpy as np
import numpy.random as rnd
import math

WIDTH = 1000
HEIGHT = 1000
MAX_SPEED = 50

#plt.style.use('fivethirtyeight')
#plt.tight_layout()

class Person():
    def __init__(self):
        self.x = rnd.randint(0, WIDTH)
        self.y = rnd.randint(0, HEIGHT)
        self.direction = rnd.randint(0, 360)
        self.dir_holdoff = rnd.randint(0, 50)
        self.speed = MAX_SPEED * rnd.random(1)
    
    def step(self):
        if self.direction >= 360:
            self.direction -= 360
        
        if self.dir_holdoff > 0:
            #self.dir_holdoff -= 1
            if self.dir_holdoff == 0:
               self.dir_holdoff = rnd.randint(0, 50)
               self.direction = rnd.randint(0, 360)
               self.speed = MAX_SPEED * rnd.random(1)
        
        self.x += math.sin(math.radians(self.direction))
        self.y += math.cos(math.radians(self.direction))

        if self.x > WIDTH:
            self.x -= WIDTH - self.x
            self.direction = rnd.randint(90, 270)
        if self.x < 0:
            self.x = -self.x
            self.direction = rnd.randint(270, 450)
        
        if self.y > HEIGHT:
            self.y -= HEIGHT - self.y
            self.direction = rnd.randint(180, 360)
        if self.y < 0:
            self.y = -self.y
            self.direction = rnd.randint(0, 180)

p = Person()

def field(i):
    plt.cla()
    plt.scatter(p.x, p.y, alpha=0.7)
    p.step()

ani = fanim(plt.gcf(), field, interval = 10)

plt.show()
