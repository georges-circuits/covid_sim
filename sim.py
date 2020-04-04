import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation as fanim
import numpy as np
import numpy.random as rnd
import math

MAX_SPEED = 10

BOUND = 500

#plt.style.use('fivethirtyeight')
#plt.tight_layout()

class World():
    def __init__(self):
        self.people = []
    
    def add_person(self, person):
        self.people.append(person)

    def get_location_of_all(self):
        return ([p.location.x for p in self.people], [p.location.y for p in self.people])


def rand_float_in_range(lower, upper):
    return (rnd.random(1) * (upper - lower)) + lower

def rand_degrees():
    return rnd.randint(0, 360)


class Coordinates():
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    
    def is_within_bound(self, bound):
        if bound.x > abs(self.x) and bound.y > abs(self.y):
            return True
        return False

    def set_random_within_bound(self, bound):
        self.x = rnd.randint(-bound.x, bound.x)
        self.y = rnd.randint(-bound.y, bound.y)

class Person():
    def __init__(self):
        self.center = Coordinates(0, 0)
        self.bound = Coordinates(BOUND, BOUND)
        self.max_speed = MAX_SPEED

        self.location = Coordinates()
        self.location.set_random_within_bound(self.bound)
        self.change_mind()
        
    
    def change_mind(self):
        self.heading = rand_degrees()
        self.speed = rand_float_in_range(0, self.max_speed)
        self.change_holdoff = rnd.randint(10, 50)
    
    
    def update(self):
        if self.change_holdoff > 0:
            self.change_holdoff -= 1
            if self.change_holdoff == 0:
                self.change_mind()
                """ self.heading += 45
                if self.heading > 360:
                   self.heading -= 360
                print (self.heading)
                self.change_holdoff = 10 """
        
        self.location.x += math.cos(math.radians(self.heading)) * self.speed
        self.location.y += math.sin(math.radians(self.heading)) * self.speed

        if not self.location.is_within_bound(self.bound):
            self.heading = self.get_heading_to_center()
            print(self.heading)


    def get_heading_to_center(self):
        # draw it on a piece of paper to see that it works (compare to get_theta)
        x, y = -self.location.x, -self.location.y
        deg = math.degrees(math.asin(abs(y) / math.sqrt(x ** 2 + y ** 2)))
        if x < 0 and y > 0:
            deg = 180 - deg
        elif x < 0 and y < 0:
            deg += 180
        elif x > 0 and y < 0:
            deg = 360 - deg
        return deg
    
    def get_theta(self):
        x, y = self.location.x, self.location.y
        # vector direction
        deg = math.degrees(math.asin(abs(y) / math.sqrt(x ** 2 + y ** 2)))
        if x < 0 and y > 0:
            deg = 180 - deg
        elif x < 0 and y < 0:
            deg += 180
        elif x > 0 and y < 0:
            deg = 360 - deg
        return deg


world = World()
for i in range(1000):
    world.add_person(Person())

def plot_field():
    plt.cla()
    x, y = world.get_location_of_all()
    #print(f"x:{x}\ny:{y}\n\n")
    plt.scatter(x, y, alpha=0.7)
    plt.xlim(-BOUND, BOUND)
    plt.ylim(-BOUND, BOUND)

def field_update(i):
    plot_field()
    for p in world.people:
        p.update()

ani = fanim(plt.gcf(), field_update, interval = 100)

plt.show()
