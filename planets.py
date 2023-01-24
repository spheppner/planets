import math
import pygame
import random

class World:
    entities = {}

    star_density = 1414090  # kg/m3
    moon_density = 334.502  # kg/m3
    planet_density = 5513.26  # kg/m3

    @classmethod
    def calculate_single_body_acceleration(self, bodies, body_index):
        G_const = 6.67408e-11  # m3 kg-1 s-2
        acceleration = Vector(0, 0, 0)
        target_body = bodies[body_index]
        for index, external_body in bodies.items():
            if index != body_index:
                r = (target_body.pos.x - external_body.pos.x) ** 2 + (target_body.pos.y - external_body.pos.y) ** 2 + (target_body.pos.z - external_body.pos.z) ** 2
                r = math.sqrt(r)
                tmp = G_const * external_body.mass / r ** 3
                acceleration.x += tmp * (external_body.pos.x - target_body.pos.x)
                acceleration.y += tmp * (external_body.pos.y - target_body.pos.y)
                acceleration.z += tmp * (external_body.pos.z - target_body.pos.z)

        return acceleration

    @classmethod
    def compute_velocity(self, bodies, time_step=1):
        for body_index, target_body in bodies.items():
            acceleration = self.calculate_single_body_acceleration(bodies, body_index)

            target_body.velocity.x += acceleration.x * time_step
            target_body.velocity.y += acceleration.y * time_step
            target_body.velocity.z += acceleration.z * time_step

    @classmethod
    def update_location(self, bodies, time_step=1):
        for target_body in bodies.values():
            target_body.pos.x += target_body.velocity.x * time_step
            target_body.pos.y += target_body.velocity.y * time_step
            target_body.pos.z += target_body.velocity.z * time_step

    @classmethod
    def compute_system(self, time_step=1):
        bodies = {k: e for k,e in World.entities.items() if e.mass != 0}
        self.compute_velocity(bodies, time_step=time_step)
        self.update_location(bodies, time_step=time_step)

    @classmethod
    def volumeofball(self, r):
        return 4 / 3 * math.pi * r ** 3

    @classmethod
    def randomcolor(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Vector({self.x}, {self.y}, {self.z})"

    def __getitem__(self, item):
        if item <= 2:
            items = [self.x, self.y, self.z]
            return items[item]
        else:
            return None

class Entity:
    number = 0
    def __init__(self, pos, mass, radius, velocity, temperature=0, name=None, color=World.randomcolor()):
        self.number = Entity.number
        Entity.number += 1

        self.pos = pos # Vector
        self.mass = mass # [kg]
        self.radius = radius # [m]
        self.velocity = velocity # Vector
        self.temperature = temperature
        self.name = name if name else f"Entity {self.number+1}"
        self.color = color

        World.entities[self.number] = self

class Star(Entity):
    def __init__(self, pos, mass=None, velocity=None, temperature=5778, name=None, color=World.randomcolor()):
        mass = 2e30 if mass is None else mass
        radius = ((mass * 3)/(4 * math.pi * World.star_density)) ** (1 / 3)
        velocity = Vector(0, 0, 0) if velocity is None else velocity
        super().__init__(pos, mass, radius, velocity, temperature, name, color)

class Planet(Entity):
    def __init__(self, pos, mass=None, velocity=None, name=None, color=World.randomcolor()):
        mass = 6e24 if mass is None else mass
        radius = ((mass * 3) / (4 * math.pi * World.planet_density)) ** (1 / 3)
        velocity = Vector(0, 30000, 0) if velocity is None else velocity
        super().__init__(pos, mass, radius, velocity, name=name, color=color)

class Moon(Entity):
    def __init__(self, pos, mass=None, velocity=None, name=None, color=World.randomcolor()):
        mass = 7e22 if mass is None else mass
        radius = ((mass * 3) / (4 * math.pi * World.moon_density)) ** (1 / 3)
        velocity = Vector(0, 31023, 0) if velocity is None else velocity
        super().__init__(pos, mass, radius, velocity, name=name, color=color)

class StablePlanet:
    def __init__(self, r_dist, mass, center_pos, center_mass, negative_velocity=False, name=None, color=World.randomcolor()):
        radius = ((mass * 3) / (4 * math.pi * World.planet_density)) ** (1 / 3)
        G_const = 6.67408e-11
        pos = Vector(center_pos.x+r_dist, center_pos.y, center_pos.z)
        v = ((G_const*center_mass)/abs(r_dist)) ** 0.5
        if negative_velocity: v = -v
        Entity(pos, mass, radius, Vector(0, v, 0), name=name, color=color)

class BinaryStarSystem:
    def __init__(self, r_dist, m1, m2, temperature=5778, name=None, color=World.randomcolor(), negative_velocity=False):
        r1 = ((m1 * 3) / (4 * math.pi * World.star_density)) ** (1 / 3)
        r2 = ((m2 * 3) / (4 * math.pi * World.star_density)) ** (1 / 3)

        G_const = 6.67408e-11

        if m1 == m2:
            d1 = -r_dist
            d2 = r_dist

            v1 = ((G_const * m1) / (4 * r_dist)) ** 0.5
            v2 = -v1

        elif max(m1, m2) == m1:
            d1 = -r_dist
            d2 = (m1/m2)*r_dist

            x = m1 / m2
            v1 = ((G_const * m2)/(r_dist*((x+1)**2))) ** 0.5
            v2 = ((G_const * m2 * x**2)/(r_dist*((x+1)**2))) ** 0.5
            v2 = -v2

        elif max(m1, m2) == m2:
            d1 = (m2/m1)*r_dist
            d2 = -r_dist

            x = m2 / m1
            v2 = ((G_const * m1) / (r_dist * ((x + 1) ** 2))) ** 0.5
            v1 = ((G_const * m1 * x ** 2) / (r_dist * ((x + 1) ** 2))) ** 0.5
            v1 = -v1
        if negative_velocity:
            v2 = -v2
            v1 = -v1

        Entity(Vector(d1, 0, 0), m1, r1, Vector(0, v1, 0), temperature, name=f"{name} 1", color=color)
        Entity(Vector(d2, 0, 0), m2, r2, Vector(0, v2, 0), temperature, name=f"{name} 2", color=color)


class Viewer:
    width = 0
    height = 0
    background_color = (0, 0, 0)
    font = None

    def __init__(self, width=800, height=600):
        Viewer.width = width
        Viewer.height = height

        # ---- pygame init
        pygame.init()
        pygame.mixer.init(11025)  # raises exception on fail
        # Viewer.font = pygame.font.Font(os.path.join("data", "FreeMonoBold.otf"),26)
        # fontfile = os.path.join("data", "fonts", "DejaVuSans.ttf")
        # --- font ----
        # if you have your own font:
        # Viewer.font = pygame.freetype.Font(os.path.join("data","fonts","INSERT_YOUR_FONTFILENAME.ttf"))
        # otherwise:
        fontname = pygame.freetype.get_default_font()
        Viewer.font = pygame.freetype.SysFont(fontname, 64)

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.playtime = 0.0
        self.paused = False
        self.time_step = 1
        self.zoom = -2
        self.fov = Vector(0,0,0)

        self.setup()
        self.run()

    def setup(self):
        """call this to restart a game"""
        self.background = pygame.Surface((Viewer.width, Viewer.height))
        self.background.fill(Viewer.background_color)

        AU = 1.5e11
        moon_to_sun = 1.5e11 + 350000000

        # Earth
        e_pos = Vector(AU, 0, 0)
        e_mass = 5.972e24
        e_radius = 6.371e6
        e_velocity = Vector(0, 29300, 0)
        #earth = Entity(e_pos, e_mass, e_radius, e_velocity)

        # Sun
        s_pos = Vector(0, 0, 0)
        s_mass = 2.0e30
        s_radius_real = 696.340e6
        s_radius = 69.6340e6
        s_velocity = Vector(0, 0, 0)
        #sun = Entity(s_pos, s_mass, s_radius, s_velocity)

        Entity(Vector(0,0,0), 0, 3e6, Vector(0,0,0), name="0,0", color=(255,255,255)) # 0,0 Marker

        #M1 = 2e30
        #BinaryStarSystem(AU, 5*M1, M1)

        planets = {"mercury": {"location": Vector(0, 5.7e10, 0), "mass": 3.285e23, "velocity": Vector(47000, 0, 0)},
        "venus": {"location": Vector(0, 1.1e11, 0), "mass": 4.8e24, "velocity": Vector(35000, 0, 0)},
        "earth": {"location": Vector(0, 1.5e11, 0), "mass": 6e24, "velocity": Vector(30000, 0, 0)},
        "mars": {"location": Vector(0, 2.2e11, 0), "mass": 2.4e24, "velocity": Vector(24000, 0, 0)},
        "jupiter": {"location": Vector(0, 7.7e11, 0), "mass": 1e28, "velocity": Vector(13000, 0, 0)},
        "saturn": {"location": Vector(0, 1.4e12, 0), "mass": 5.7e26, "velocity": Vector(9000, 0, 0)},
        "uranus": {"location": Vector(0, 2.8e12, 0), "mass": 8.7e25, "velocity": Vector(6835, 0, 0)},
        "neptune": {"location": Vector(0, 4.5e12, 0), "mass": 1e26, "velocity": Vector(5477, 0, 0)},
        "pluto": {"location": Vector(0, 3.7e12, 0), "mass": 1.3e22, "velocity": Vector(4748, 0, 0)}}

        Star(Vector(0,0,0), name="Sun", color=(255,255,0))
        for name, planet in planets.items():
            Planet(Vector(planet["location"].y, 0, 0), planet["mass"], Vector(0,planet["velocity"].x,0), name=name, color=(0,200,0))

        #Star(Vector(0,0,0), mass=2e30, velocity=Vector(0, 0, 0), name="Sun", color=(255,255,0))
        #StablePlanet(AU, 6e24, Vector(0,0,0), 2e30, name="Earth", color=(0,200,0))

    def run(self):
        running = True
        # --------------------------- main loop --------------------------
        while running:
            if not self.paused:
                World.compute_system(self.time_step)

            # ------- update viewer ---------
            milliseconds = self.clock.tick(self.fps)
            seconds = milliseconds / 1000
            self.playtime += seconds
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if event.key == pygame.K_p:
                        self.paused = False if self.paused else True

            # ------------ pressed keys ------
            pressed_keys = pygame.key.get_pressed()

            if pressed_keys[pygame.K_z]:
                self.zoom += 0.02

            if pressed_keys[pygame.K_u]:
                self.zoom -= 0.02

            if pressed_keys[pygame.K_PLUS]:
                self.time_step += 2000

            if pressed_keys[pygame.K_MINUS]:
                if self.time_step > 200:
                    self.time_step -= 2000

            if pressed_keys[pygame.K_UP]:
                self.fov.y += 20*10**-self.zoom

            elif pressed_keys[pygame.K_DOWN]:
                self.fov.y -= 20*10**-self.zoom

            elif pressed_keys[pygame.K_LEFT]:
                self.fov.x += 20*10**-self.zoom

            elif pressed_keys[pygame.K_RIGHT]:
                self.fov.x -= 20*10**-self.zoom

            # ------ mouse handler ------
            left, middle, right = pygame.mouse.get_pressed()

            oldleft, oldmiddle, oldright = left, middle, right
            # ----------- collision detection ------------

            # ---------- clear all --------------
            pygame.display.set_caption(f"FPS: {self.clock.get_fps():.2f} | {self.time_step} | {self.zoom} | {'PAUSED' if self.paused else 'RUNNING'}")
            self.screen.blit(self.background, (0, 0))

            # --------- update all sprites ----------------
            sprite_radius_scale = -4.5
            sprite_pos_scale = -7

            for entity in World.entities.values():
                sprite_pos = (entity.pos.x*10**(self.zoom+sprite_pos_scale)+self.width//2+self.fov.x*10**self.zoom, entity.pos.y*10**(self.zoom+sprite_pos_scale)+self.height//2+self.fov.y*10**self.zoom)
                pygame.draw.circle(self.screen, entity.color, center=sprite_pos, radius=entity.radius*10**(self.zoom+sprite_radius_scale))

            # ---------- blit all sprites --------------
            pygame.display.flip()
            # -----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()


if __name__ == "__main__":
    viewer = Viewer(width=800, height=800)
    viewer.run()
