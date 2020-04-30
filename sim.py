import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
import numpy as np
import numpy.random as rnd
import math
import time

MAX_SPEED = 1.5
P_BOUND = 150
DAY = 24

DURATION = 330 # roughly 14 days if we count each update as an hour
PERSONAS = 400

# matplotlib doesn't allow simultaneous video export and preview
# (please prove me wrong), setup paramaters are on the last lines
# export is mostly broken anyways
EXPORT = False

W_BOUND = P_BOUND
sim = None

# also dictates possible statuses
COLORS = {
    'S': {'id': 1, 'rgb': (0, 1, 0)},
    'I': {'id': 2, 'rgb': (1, 0, 0)},
    'R': {'id': 3, 'rgb': (0.5, 0.5, 0.5)}
}

class Simulation(animation.FuncAnimation):
    def __init__(self):
        # dark mode :)
        plt.rcParams['figure.facecolor'] = 'black'
        plt.rcParams['axes.facecolor'] = 'black'
        plt.rcParams['axes.edgecolor'] = 'white'
        plt.rcParams['axes.labelcolor'] = 'white'
        plt.rcParams['xtick.color'] = 'white'
        plt.rcParams['ytick.color'] = 'white'
        plt.rcParams['text.color'] = 'white'

        # init fig and subplots
        self.fig = plt.figure(tight_layout=True, figsize=(15, 8))
        self.axWorld = self.fig.add_subplot(121)
        self.axGraph = self.fig.add_subplot(122, frameon=False)

        # custom color map according to COLORS
        self.cmap = colors.LinearSegmentedColormap.from_list('custom', [c['rgb'] for c in COLORS.values()])
        self.norm = plt.Normalize(1, len(COLORS))

        # time readouts
        self.last_time = time.time()
        
        # create the world
        self.world = World()
        for _ in range(PERSONAS):
            self.world.add_person(Person())

        print(f'Created a world with {self.world.population()} people')
        
        # infect first person
        self.world.people[0].status = "I"

        # init the graph part
        self.population_graph = {'days': [], 'values': []}
        for designator, color in COLORS.items():
            self.population_graph['values'].append({'color': color['rgb'], 'designator': designator, 'data': []})

        # call the FuncAnimation constructor
        animation.FuncAnimation.__init__(self, self.fig, self.field_update, interval=10)

    def plot_update(self, i):
        self.axWorld.cla()
        x, y, c, s = self.world.get_location_of_all()
        for j in range(len(s)):
            s[j] = s[j] ** 2 * ((self.axWorld.get_window_extent().width  / (2 * W_BOUND + 1.) * 72. / self.fig.dpi) ** 2)
        self.axWorld.scatter(x, y, c=c, s=s, alpha=0.8, linewidths=0, cmap=self.cmap, norm=self.norm)
        self.axWorld.set_xlim(-W_BOUND, W_BOUND)
        self.axWorld.set_ylim(-W_BOUND, W_BOUND)
        self.axWorld.axis("off")

        self.axGraph.cla()
        self.population_graph['days'].append(i)
        for value in self.population_graph['values']:
            value['data'].append(self.world.count_people_based_on_status(value['designator']))
            self.axGraph.plot(self.population_graph['days'], value['data'], label=value['designator'], c=value['color'])
        #self.axGraph.legend()
        self.axGraph.set_ylim(0, self.world.population())

    def field_update(self, i):
        self.plot_update(i)

        if not self.world.count_people_based_on_status('I'):
            print(f'Stopping the simulation\nRemoved: {self.world.count_people_based_on_status("R")}, Susceptible: {self.world.count_people_based_on_status("S")}')
            sim.event_source.stop()
        else:
            if i % 5 == 0:
                print (
                    f'update no: {i * DAY}, updates took: {int(time.time() - self.last_time)}s, Day since T0: {i}, R0: {self.world.calculate_R0()}'
                )
                self.last_time = time.time()
        for _ in range(DAY):
            self.world.update()


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


class World():
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

    def population(self):
        return len(self.people)
    
    def get_location_of_all(self):
        return (
            [p.location.x for p in self.people],
            [p.location.y for p in self.people], 
            [COLORS[p.status]['id'] for p in self.people],
            [p.infection_radius for p in self.people]
        )

    def calculate_R0(self):
        # how to calculate: https://web.stanford.edu/~jhj1/teachingdocs/Jones-on-R0.pdf
        c_bar = sum(person.came_in_contact for person in self.get_people_based_on_status("I")) / self.count_people_based_on_status("I")
        for person in self.get_people_based_on_status("I"):
            person.came_in_contact = 0
        return round(self.people[0].infection_probability * c_bar * DURATION / DAY, 2)
    
    def update(self):
        for person in self.people:
            if person.is_infected():
                for prey in self.people:
                    if prey.is_healthy() and prey != person and person.distance_to(prey) <= person.infection_radius:
                        if rnd.random(1) <= person.infection_probability:
                            person.came_in_contact += 1
                            prey.status = "I"
        for person in self.people:
            person.update()


class Person():
    """ self.CONFIG = {
        'normal': {
            'infection_radius': 10,
            'infection_probability': 0.2
        },
        'in_central': {
            'infection_radius': 10,
            'infection_probability': 0.2
        },
        'at_home': {
            'infection_radius': 10,
            'infection_probability': 0.01
        }
    } """

    def __init__(self):
        self.center = Coordinates(0, 0)
        self.bound = Coordinates(P_BOUND, P_BOUND)
        self.max_speed = MAX_SPEED

        self.location = Coordinates()
        self.location.set_random_within_bound(self.bound)
        
        self.status = "S"
        self.sickness_duration = DURATION
        self.infection_radius = 2
        self.infection_probability = 0.2
        #self.change_config('normal')

        self.came_in_contact = 0
        
        self.travel_probability = 0.0005
        
        self.change_mind()

        self.central_location = False
        self.will_to_go = 0.05

    def change_mind(self):
        if rnd.random(1) < self.travel_probability:
            self.location.set_random_within_bound(self.bound)
        self.heading = rand_degrees()
        self.speed = rand_float_in_range(0, self.max_speed)
        self.change_holdoff = rnd.randint(1, 10)

    """ def change_config(self, mode):
        self.infection_radius = self.CONFIG[mode]['infection_radius']
        self.infection_probability = self.CONFIG[mode]['infection_probability'] """
              
    def update(self):
        if self.change_holdoff > 0:
            self.change_holdoff -= 1
            if self.change_holdoff == 0:
                self.change_mind()

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
        if self.status == "S":
            return True
        return False
    
    def is_infected(self):
        if self.status == "I":
            return True
        return False

    def distance_to(self, to):
        return math.sqrt((self.location.x - to.location.x) ** 2 + (self.location.y - to.location.y) ** 2)


def rand_float_in_range(lower, upper):
    return (rnd.random(1) * (upper - lower)) + lower

def rand_degrees():
    return rnd.randint(0, 360)


# has to keep local reference, it will get GCed otherwise
sim = Simulation()

if EXPORT:
    import os.path
    import glob
    export_name = f'run_P{sim.world.population()}_S{MAX_SPEED}_B{P_BOUND}(*).mp4'
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'exports', export_name)
    file_index = 1
    for file_name in glob.glob(path):
        # won't work for numbers > 9 of course...
        file_index = int(file_name[-6]) + 1
    sim.save(path.replace('*', str(file_index)), writer="ffmpeg", fps=10)

plt.show()