import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import numpy.random as rnd
import math

MAX_SPEED = 10
BOUND = 500

COLORS = {
    "H": 1,
    "S": 2,
    "R": 3
}

class World():
    def __init__(self):
        self.states = []
    
    def add_state(self, state):
        self.states.append(state)

class State():
    def __init__(self):
        self.people = []

    def add_person(self, person):
        self.people.append(person)

    def count_people_based_on_status(self, status):
        count = 0
        for i in self.get_people_based_on_status(status):
            count += 1
        return count
        
    def get_people_based_on_status(self, status):
        for person in self.people:
            if person.status == status:
                yield person

    def get_location_of_all(self):
        return [p.location.x for p in self.people], [p.location.y for p in self.people], [COLORS[p.status] for p in self.people]

    def update(self):
        for person in self.people:
            if person.is_infected():
                for prey in self.people:
                    if prey.is_healthy() and prey != person and person.distance_to(prey) <= person.infection_radius:
                        if rnd.random(1) <= person.infection_probability:
                            prey.status = "S"
        for person in self.people:
            person.update()


class Person():
    def __init__(self):
        self.center = Coordinates(0, 0)
        self.bound = Coordinates(BOUND, BOUND)
        self.max_speed = MAX_SPEED

        self.location = Coordinates()
        self.location.set_random_within_bound(self.bound)
        self.change_mind()
        
        self.status = "H"
        self.sickness_duration = rnd.randint(40, 60)
        self.infection_radius = 50
        self.infection_probability = 0.2

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
        
        if self.is_infected():
            if self.sickness_duration:
                self.sickness_duration -= 1
            else:
                self.status = "R"

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

    def is_healthy(self):
        if self.status == "H":
            return True
        return False
    
    def is_infected(self):
        if self.status == "S":
            return True
        return False

    def distance_to(self, to):
        return math.sqrt((self.location.x - to.location.x) ** 2 + (self.location.y - to.location.y) ** 2)


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


def rand_float_in_range(lower, upper):
    return (rnd.random(1) * (upper - lower)) + lower

def rand_degrees():
    return rnd.randint(0, 360)

def create_colormap(colors):
    reverse=False
    name='custom_colormap'
    position=None
    bit=True
    # from https://github.com/CSlocumWX/custom_colormap
    """
    returns a linear custom colormap
    Parameters
    ----------
    colors : array-like
        contain RGB values. The RGB values may either be in 8-bit [0 to 255]
        or arithmetic [0 to 1] (default).
        Arrange your tuples so that the first color is the lowest value for the
        colorbar and the last is the highest.
    position : array like
        contains values from 0 to 1 to dictate the location of each color.
    bit : Boolean
        8-bit [0 to 255] (in which bit must be set to
        True when called) or arithmetic [0 to 1] (default)
    reverse : Boolean
        If you want to flip the scheme
    name : string
        name of the scheme if you plan to save it
    Returns
    -------
    cmap : matplotlib.colors.LinearSegmentedColormap
        cmap with equally spaced colors
    """
    from matplotlib.colors import LinearSegmentedColormap
    if not isinstance(colors, np.ndarray):
        colors = np.array(colors, dtype='f')
    if reverse:
        colors = colors[::-1]
    if position is not None and not isinstance(position, np.ndarray):
        position = np.array(position)
    elif position is None:
        position = np.linspace(0, 1, colors.shape[0])
    else:
        if position.size != colors.shape[0]:
            raise ValueError("position length must be the same as colors")
        elif not np.isclose(position[0], 0) and not np.isclose(position[-1], 1):
            raise ValueError("position must start with 0 and end with 1")
    if bit:
        colors[:] = [tuple(map(lambda x: x / 255., color)) for color in colors]
    cdict = {'red':[], 'green':[], 'blue':[]}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))
    return LinearSegmentedColormap(name, cdict, 256)



plt.rcParams['figure.facecolor'] = 'black'
plt.rcParams['axes.facecolor'] = 'black'
plt.rcParams['axes.edgecolor'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'
plt.rcParams['text.color'] = 'white'


fig = plt.figure(tight_layout=True, figsize=(15, 8))
axWorld = fig.add_subplot(121)
axGraph = fig.add_subplot(122, frameon=False)

cmap = create_colormap([(155, 189, 55), (189, 55, 88), (164, 164, 164)])

world = State()
for i in range(100):
    world.add_person(Person())

world.people[0].status = "S"

healthy = []
sick = []
removed = []
day = []


def plot_update(i):
    axWorld.cla()
    x, y, c = world.get_location_of_all()
    axWorld.scatter(x, y, c=c, alpha=0.7, linewidths=0, cmap=cmap)
    axWorld.set_xlim(-BOUND, BOUND)
    axWorld.set_ylim(-BOUND, BOUND)
    axWorld.axis("off")

    axGraph.cla()
    healthy.append(world.count_people_based_on_status("H"))
    sick.append(world.count_people_based_on_status("S"))
    removed.append(world.count_people_based_on_status("R"))
    day.append(i)
    axGraph.plot(day, healthy, label="Healthy", c="green")
    axGraph.plot(day, sick, label="Sick", c="red")
    axGraph.plot(day, removed, label="Removed", c="grey")
    #axGraph.legend()
    axGraph.set_ylim(0, len(world.people))


def field_update(i):
    plot_update(i)
    world.update()

ani = animation.FuncAnimation(fig, field_update, interval=100)

plt.show()

