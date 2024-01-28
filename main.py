import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)


# font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 20


class SnakeGame:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        self.x_vel = 0
        self.y_vel = 0

        self.reset()

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        self._move(action)  # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward -= 10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward += 10
            self._place_food()
        else:
            self.snake.pop()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score

    def get_state(self):
        snake_head_x = self.head.x
        snake_head_y = self.head.y

        food_x = self.food.x
        food_y = self.food.y

        x_vel = self.x_vel
        y_vel = self.y_vel

        danger_right, danger_left, danger_up, danger_down = self.find_danger_in_all_dirs()

        #Number of inputs - 14
        return np.array([danger_left, danger_right, danger_up, danger_down, x_vel, y_vel, food_x < snake_head_x, food_x > snake_head_x, food_y < snake_head_y, food_y > snake_head_y, snake_head_x, snake_head_y, food_x, food_y], dtype=int)
    def find_danger_in_all_dirs(self):
        danger = [0, 0, 0, 0]
        for i in range(4):
            danger[i] = self.find_danger(i)
        return danger[0], danger[1], danger[2], danger[3]

    def find_danger(self, direction):
        if direction == 0:
            x = self.head.x + BLOCK_SIZE
            y = self.head.y
        elif direction == 1:
            x = self.head.x - BLOCK_SIZE
            y = self.head.y
        elif direction == 2:
            x = self.head.x
            y = self.head.y + BLOCK_SIZE
        elif direction == 3:
            x = self.head.x
            y = self.head.y - BLOCK_SIZE
        else:
            print("Error: invalid direction")
            return 0

        if x > self.w - BLOCK_SIZE or x < 0 or y > self.h - BLOCK_SIZE or y < 0:
            return True

        if Point(x, y) in self.snake[1:]:
            return True

        return False

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True
        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, action):
        x = self.head.x
        y = self.head.y

        clockwise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clockwise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clockwise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clockwise[next_idx] # right turn r -> d -> l -> u
        else:
            next_idx = (idx - 1) % 4
            new_dir = clockwise[next_idx]

        self.direction = new_dir

        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
            self.x_vel = 1
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
            self.x_vel = -1
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
            self.y_vel = 1
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            self.y_vel = -1

        self.head = Point(x, y)