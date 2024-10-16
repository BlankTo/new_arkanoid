import sys
import time
import math
import pygame
import pickle
import numpy as np
from datetime import datetime

refresh_rate = 0.05
grid_width, grid_height = 121, 71
screen_width, screen_height = grid_width * 10, grid_height * 10

# 0 empty
# 1 ball
# 2 paddle_left
# 3 paddle_center
# 4 paddle_right
# 5 wall_left
# 6 wall_right
# 7 wall_top
# 8 wall_bottom
# 9:34 bricks

class Game:

    def __init__(self):

        self.init_grid()

        self.elements = {}
        self.event_log = {}

        self.init_walls()

        self.first_brick = 11, 10
        self.brick_nrow, self.brick_ncol = 3, 8
        self.brick_distance = 14, 10
        self.brick_halfwidth, self.brick_halfheight = 5, 2

        self.init_bricks()

        self.paddle_x, self.paddle_y = 60, 60
        self.paddle_halfwidth, self.paddle_halfheight = 5, 1
        self.paddle_base_speed = 2

        self.init_paddle()

        self.ball_x, self.ball_y = 45, 40
        self.ball_radius = 1
        self.ball_speed_x, self.ball_speed_y = 1, 1

        self.init_ball()

        self.event_pending = []


    def init_grid(self):

        self.grid = np.zeros((grid_width, grid_height), dtype= int)
        self.r = np.zeros((grid_width, grid_height), dtype= int)
        self.g = np.zeros((grid_width, grid_height), dtype= int)
        self.b = np.zeros((grid_width, grid_height), dtype= int)


    def init_walls(self):

        self.grid[0:3, 3:grid_height - 3] = 5 # left wall
        self.r[0:3, 3:grid_height - 3] = 0
        self.g[0:3, 3:grid_height - 3] = 255
        self.b[0:3, 3:grid_height - 3] = 50

        self.elements['wall_left'] = {
            'id': 5,
            'pos': (1, math.floor(grid_height / 2)),
            'shape': (1, math.floor(grid_height / 2)),
            'hitbox': ((0, 3), (2, grid_height - 4)),
            'color': (0, 255, 50)
        }

        self.grid[grid_width - 3:grid_width, 3:grid_height - 3] = 6 # right wall
        self.r[grid_width - 3:grid_width, 3:grid_height - 3] = 0
        self.g[grid_width - 3:grid_width, 3:grid_height - 3] = 255
        self.b[grid_width - 3:grid_width, 3:grid_height - 3] = 100

        self.elements['wall_right'] = {
            'id': 6,
            'pos': (grid_width - 2, math.floor(grid_height / 2)),
            'shape': (1, math.floor(grid_height / 2)),
            'hitbox': ((grid_width - 3, 3), (grid_width - 1, grid_height - 4)),
            'color': (0, 255, 100)
        }

        self.grid[3:grid_width - 3, 0:3] = 7 # top wall
        self.r[3:grid_width - 3, 0:3] = 0
        self.g[3:grid_width - 3, 0:3] = 255
        self.b[3:grid_width - 3, 0:3] = 150

        self.elements['wall_top'] = {
            'id': 7,
            'pos': (math.floor(grid_width / 2), 1),
            'shape': (math.floor(grid_width / 2), 1),
            'hitbox': ((3, 0), (grid_width - 4, 2)),
            'color': (0, 255, 150)
        }

        self.grid[3:grid_width - 3, grid_height - 3:grid_height] = 8 # bottom wall
        self.r[3:grid_width - 3, grid_height - 3:grid_height] = 0
        self.g[3:grid_width - 3, grid_height - 3:grid_height] = 255
        self.b[3:grid_width - 3, grid_height - 3:grid_height] = 200

        self.elements['wall_bottom'] = {
            'id': 8,
            'pos': (math.floor(grid_width / 2), grid_height - 2),
            'shape': (math.floor(grid_width / 2), 1),
            'hitbox': ((3, grid_height - 3), (grid_width - 4, grid_height - 1)),
            'color': (0, 255, 150)
        }


    def init_bricks(self):

        self.brick_positions = [(self.first_brick[0] + j * self.brick_distance[0], self.first_brick[1] + i * self.brick_distance[1]) for j in range(self.brick_ncol) for i in range(self.brick_nrow)]
        self.bricks_alive = len(self.brick_positions)

        for i, brick_pos in enumerate(self.brick_positions):

            self.grid[brick_pos[0] - self.brick_halfwidth:brick_pos[0] + self.brick_halfwidth + 1, brick_pos[1] - self.brick_halfheight:brick_pos[1] + self.brick_halfheight + 1] = i + 9
            self.r[brick_pos[0] - self.brick_halfwidth:brick_pos[0] + self.brick_halfwidth + 1, brick_pos[1] - self.brick_halfheight:brick_pos[1] + self.brick_halfheight + 1] = 255
            self.g[brick_pos[0] - self.brick_halfwidth:brick_pos[0] + self.brick_halfwidth + 1, brick_pos[1] - self.brick_halfheight:brick_pos[1] + self.brick_halfheight + 1] = 255
            self.b[brick_pos[0] - self.brick_halfwidth:brick_pos[0] + self.brick_halfwidth + 1, brick_pos[1] - self.brick_halfheight:brick_pos[1] + self.brick_halfheight + 1] = 255
            
            self.elements[f'brick_{i}'] = {
                'id': i + 9,
                'pos': brick_pos,
                'shape': (self.brick_halfwidth, self.brick_halfheight),
                'hitbox': ((brick_pos[0] - self.brick_halfwidth, brick_pos[1] - self.brick_halfheight), (brick_pos[0] + self.brick_halfwidth, brick_pos[1] + self.brick_halfheight)),
                'color': (255, 255, 255)
            }


    def del_brick(self, id):

        brick_id = id - 9
        brick_pos = self.brick_positions[brick_id]
        
        self.grid[brick_pos[0] - self.brick_halfwidth:brick_pos[0] + self.brick_halfwidth + 1, brick_pos[1] - self.brick_halfheight:brick_pos[1] + self.brick_halfheight + 1] = 0
        self.r[brick_pos[0] - self.brick_halfwidth:brick_pos[0] + self.brick_halfwidth + 1, brick_pos[1] - self.brick_halfheight:brick_pos[1] + self.brick_halfheight + 1] = 0
        self.g[brick_pos[0] - self.brick_halfwidth:brick_pos[0] + self.brick_halfwidth + 1, brick_pos[1] - self.brick_halfheight:brick_pos[1] + self.brick_halfheight + 1] = 0
        self.b[brick_pos[0] - self.brick_halfwidth:brick_pos[0] + self.brick_halfwidth + 1, brick_pos[1] - self.brick_halfheight:brick_pos[1] + self.brick_halfheight + 1] = 0
        
        self.elements[f'brick_{brick_id}']['alive'] = False
        self.event_log['disappearance'] = {
            'subject': id,
        }
        self.bricks_alive -= 1


    def init_paddle(self):
        
        self.paddle_speed = 0
        self.paddle_old_x, self.paddle_old_y = self.paddle_x, self.paddle_y
        self.draw_paddle()
        self.elements['paddle_center'] = {
            'id': 3,
            'pos': (self.paddle_x, self.paddle_y),
            'shape': (self.paddle_halfwidth, self.paddle_halfheight),
            'hitbox': ((self.paddle_x - self.paddle_halfwidth, self.paddle_y - self.paddle_halfheight), (self.paddle_x + self.paddle_halfwidth, self.paddle_y + self.paddle_halfheight)),
            'color': (0, 0, 255)
        }


    def set_paddle_speed(self, value):
        self.paddle_speed = value * self.paddle_base_speed


    def update_paddle(self):

        if self.paddle_speed != 0:
        
            if (self.paddle_x - self.paddle_halfwidth + self.paddle_speed > 2) and (self.paddle_x + self.paddle_halfwidth + self.paddle_speed < grid_width - 3):
                if (self.ball_y + self.ball_radius > self.paddle_y - self.paddle_halfheight - 1 and self.ball_y - self.ball_radius < self.paddle_y + self.paddle_halfheight + 1) and (self.ball_x + self.ball_radius > self.paddle_x - self.paddle_halfwidth + self.paddle_speed and self.ball_x - self.ball_radius < self.paddle_x + self.paddle_halfwidth + self.paddle_speed):
                    
                    #self.ball_speed_x = -self.ball_speed_x

                    #self.event_log.append(('collision', 1, 3))

                    pass

                else:
                    self.paddle_old_x = self.paddle_x
                    self.paddle_x += self.paddle_speed

            self.elements['paddle_center']['pos'] = (self.paddle_x, self.paddle_y)
            self.elements['paddle_center']['hitbox'] = ((self.paddle_x - self.paddle_halfwidth, self.paddle_y - self.paddle_halfheight), (self.paddle_x + self.paddle_halfwidth, self.paddle_y + self.paddle_halfheight))

    def draw_paddle(self):

        self.grid[self.paddle_old_x - self.paddle_halfwidth:self.paddle_old_x + self.paddle_halfwidth + 1, self.paddle_old_y - self.paddle_halfheight:self.paddle_old_y + self.paddle_halfheight + 1] = 0
#        self.r[self.paddle_old_x - self.paddle_halfwidth:self.paddle_old_x + self.paddle_halfwidth + 1, self.paddle_old_y - self.paddle_halfheight:self.paddle_old_y + self.paddle_halfheight + 1] = 0
#        self.g[self.paddle_old_x - self.paddle_halfwidth:self.paddle_old_x + self.paddle_halfwidth + 1, self.paddle_old_y - self.paddle_halfheight:self.paddle_old_y + self.paddle_halfheight + 1] = 0
        self.b[self.paddle_old_x - self.paddle_halfwidth:self.paddle_old_x + self.paddle_halfwidth + 1, self.paddle_old_y - self.paddle_halfheight:self.paddle_old_y + self.paddle_halfheight + 1] = 0

        self.grid[self.paddle_x - self.paddle_halfwidth:self.paddle_x + self.paddle_halfwidth + 1, self.paddle_y - self.paddle_halfheight:self.paddle_y + self.paddle_halfheight + 1] = 3
#        self.r[self.paddle_x - self.paddle_halfwidth:self.paddle_x + self.paddle_halfwidth + 1, self.paddle_y - self.paddle_halfheight:self.paddle_y + self.paddle_halfheight + 1] = 0
#        self.g[self.paddle_x - self.paddle_halfwidth:self.paddle_x + self.paddle_halfwidth + 1, self.paddle_y - self.paddle_halfheight:self.paddle_y + self.paddle_halfheight + 1] = 0
        self.b[self.paddle_x - self.paddle_halfwidth:self.paddle_x + self.paddle_halfwidth + 1, self.paddle_y - self.paddle_halfheight:self.paddle_y + self.paddle_halfheight + 1] = 255


    def init_ball(self):
        
        self.ball_old_x, self.ball_old_y = self.ball_x, self.ball_y
        self.draw_ball()
        self.elements['ball'] = {
            'id': 1,
            'pos': (self.ball_x, self.ball_y),
            'shape': (self.ball_radius, self.ball_radius),
            'hitbox': ((self.ball_x - self.ball_radius, self.ball_y - self.ball_radius), (self.ball_x + self.ball_radius, self.ball_y + self.ball_radius)),
            'color': (255, 0, 0)
        }


    def update_ball(self):
        
        invert_speed_x = False
        invert_speed_y = False

        collisions = []
        
        ball_new_x = self.ball_x + self.ball_speed_x
        ball_new_y = self.ball_y + self.ball_speed_y


        if np.any(self.grid[ball_new_x - self.ball_radius: ball_new_x + self.ball_radius + 1, self.ball_y - self.ball_radius:self.ball_y + self.ball_radius + 1] != 0):
            invert_speed_x = True
            collisions.extend(set(list(self.grid[ball_new_x - self.ball_radius: ball_new_x + self.ball_radius + 1, self.ball_y - self.ball_radius:self.ball_y + self.ball_radius + 1].ravel())))

        if np.any(self.grid[self.ball_x - self.ball_radius: self.ball_x + self.ball_radius + 1, ball_new_y - self.ball_radius:ball_new_y + self.ball_radius + 1] != 0):
            invert_speed_y = True
            collisions.extend(set(list(self.grid[self.ball_x - self.ball_radius: self.ball_x + self.ball_radius + 1, ball_new_y - self.ball_radius:ball_new_y + self.ball_radius + 1].ravel())))

        if (not invert_speed_x) and (not invert_speed_y):
            if np.any(self.grid[ball_new_x - self.ball_radius: ball_new_x + self.ball_radius + 1, ball_new_y - self.ball_radius:ball_new_y + self.ball_radius + 1] != 0):
                invert_speed_x = True
                invert_speed_y = True
                collisions.extend(set(list(self.grid[ball_new_x - self.ball_radius: ball_new_x + self.ball_radius + 1, ball_new_y - self.ball_radius:ball_new_y + self.ball_radius + 1].ravel())))


        ## qui si ha la collisione, si puo mettere "no movimento" e "disappearance del brick" in coda come eventi nel prossimo frame
        
        #if invert_speed_x: self.ball_speed_x = -self.ball_speed_x
        #if invert_speed_y: self.ball_speed_y = -self.ball_speed_y

        if invert_speed_x or invert_speed_y:
            if invert_speed_x: self.event_pending.append((self.bounce_x, None))
            if invert_speed_y: self.event_pending.append((self.bounce_y, None))

        else:
            self.ball_old_x = self.ball_x
            self.ball_old_y = self.ball_y

            self.ball_x += self.ball_speed_x
            self.ball_y += self.ball_speed_y
        
        for collision_id in collisions:
            if collision_id != 0:
                self.event_log['collision'] = {
                    'subject': 1,
                    'object': collision_id,
                }
                self.event_log['collision'] = {
                    'subject': collision_id,
                    'object': 1,
                }
                if collision_id >= 9:
                    self.event_pending.append((self.del_brick, collision_id))

        ######

        self.elements['ball']['pos'] = (self.ball_x, self.ball_y)
        self.elements['ball']['hitbox'] = ((self.ball_x - self.ball_radius, self.ball_y - self.ball_radius), (self.ball_x + self.ball_radius, self.ball_y + self.ball_radius))

    def draw_ball(self):

        #self.grid[self.ball_old_x - self.ball_radius:self.ball_old_x + self.ball_radius + 1, self.ball_old_y - self.ball_radius:self.ball_old_y + self.ball_radius] = 0
        self.r[self.ball_old_x - self.ball_radius:self.ball_old_x + self.ball_radius + 1, self.ball_old_y - self.ball_radius:self.ball_old_y + self.ball_radius + 1] = 0
#        self.g[self.ball_old_x - self.ball_radius:self.ball_old_x + self.ball_radius + 1, self.ball_old_y - self.ball_radius:self.ball_old_y + self.ball_radius + 1] = 0
#        self.b[self.ball_old_x - self.ball_radius:self.ball_old_x + self.ball_radius + 1, self.ball_old_y - self.ball_radius:self.ball_old_y + self.ball_radius + 1] = 0

        #self.grid[self.ball_x - self.ball_radius:self.ball_x + self.ball_radius + 1, self.ball_y - self.ball_radius:self.ball_y + self.ball_radius] = 1
        self.r[self.ball_x - self.ball_radius:self.ball_x + self.ball_radius + 1, self.ball_y - self.ball_radius:self.ball_y + self.ball_radius + 1] = 255
#        self.g[self.ball_x - self.ball_radius:self.ball_x + self.ball_radius + 1, self.ball_y - self.ball_radius:self.ball_y + self.ball_radius + 1] = 0
#        self.b[self.ball_x - self.ball_radius:self.ball_x + self.ball_radius + 1, self.ball_y - self.ball_radius:self.ball_y + self.ball_radius + 1] = 0

    def bounce_x(self):
        self.ball_speed_x = - self.ball_speed_x
        self.event_log['bounce'] = {
            'subject': 1,
        }

    def bounce_y(self):
        self.ball_speed_y = - self.ball_speed_y
        self.event_log['bounce'] = {
            'subject': 1,
        }

    def resolve_pending(self):
        for event, param in self.event_pending:
            if param is None: event()
            else: event(param)
        
        self.event_pending = []

    def update(self):
        self.resolve_pending()
        self.update_paddle()
        self.draw_paddle()
        self.update_ball()
        self.draw_ball()

        event_log = self.event_log
        self.event_log = {}

        return self.elements, event_log, (self.bricks_alive == 0)
    
    def get_log(self): return self.elements, self.event_log
    
    def get_grid(self):
        return np.transpose(np.stack([self.r, self.g, self.b]), (1, 2, 0))


# Main

save_log = True

pygame.init()
window = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Basic Arkanoid")

game = Game()

grid = pygame.surfarray.make_surface(game.get_grid())
screen = pygame.transform.scale(grid, (screen_width, screen_height))
window.blit(screen, (0, 0))

t = time.time()
keys_down = []
keys_up = []
paddle_left = False
paddle_right = False
first_time_run = True
screen_running = True
game_running = False

element_log, event_log = game.get_log()
frame_id = 0
frames = [{
    'frame_id': frame_id,
    'commands': [],
    'elements': element_log,
    'events': {}
}]
frame_id += 1

while screen_running:

    for e in pygame.event.get():

        if e == pygame.QUIT:
            screen_running = False

        if e.type == pygame.KEYDOWN:
            keys_down.append(e.key)
            keydown = True

        if e.type == pygame.KEYUP:
            keys_up.append(e.key)
            keyup = True

    new_t = time.time()
    if new_t - t > refresh_rate:
        
        command_log = []

        if first_time_run:
            if not game_running and len(keys_down) > 0:
                game_running = True

        if pygame.K_q in keys_down:
            screen_running = False

        if pygame.K_s in keys_down:
            game_running = not game_running

        if pygame.K_UP in keys_down:
            refresh_rate -= refresh_rate / 2
            print(refresh_rate)
        if pygame.K_DOWN in keys_down:
            refresh_rate += refresh_rate / 2
            print(refresh_rate)

        if keys_down.count(pygame.K_LEFT) > keys_up.count(pygame.K_LEFT):
            paddle_left = True
        elif keys_down.count(pygame.K_LEFT) < keys_up.count(pygame.K_LEFT):
            paddle_left = False

        if keys_down.count(pygame.K_RIGHT) > keys_up.count(pygame.K_RIGHT):
            paddle_right = True
        elif keys_down.count(pygame.K_RIGHT) < keys_up.count(pygame.K_RIGHT):
            paddle_right = False

        if (not paddle_left and not paddle_right):
            command_log.append(('paddle_stop'))
            game.set_paddle_speed(0)
        elif paddle_left:
            command_log.append(('paddle_left'))
            game.set_paddle_speed(-1)
        elif paddle_right:
            command_log.append(('paddle_right'))
            game.set_paddle_speed(1)
        else:
            command_log.append(('paddle_stop'))
            game.set_paddle_speed(0)

        if game_running:

            element_log, event_log, end_game = game.update()

            if first_time_run:
                event_log['start game'] = {
                    'subject': 0,
                }
                first_time_run = False

            print('----------------------------------')
            print('----------------------------------')
            print(f'frame {frame_id}')
            print(event_log)

            frames.append({
                'frame_id': frame_id,
                'commands': command_log,
                'elements': element_log,
                'events': event_log
                })
            frame_id += 1

            grid = pygame.surfarray.make_surface(game.get_grid())
            screen = pygame.transform.scale(grid, (screen_width, screen_height))
            window.blit(screen, (0, 0))

            if end_game:
                game_running = False
                screen_running = False
    
        t = new_t
        keys_down = []
        keys_up = []

    # Refresh the display
    pygame.display.flip()

if save_log:
    
    with open(f'logs/arkanoid_logs/arkanoid_log_{datetime.now().strftime("_%d_%m_%Y_%H_%M_%S")}.pkl', 'wb') as logfile:
        pickle.dump(frames, logfile)

pygame.quit()
sys.exit()
