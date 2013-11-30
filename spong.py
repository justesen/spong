#!/usr/bin/env python3
"""spong - a simple Pong clone

Usage: spong [options]

It's just a simple Pong clone. You win a point by hitting the opposite
back wall.

Controls:
  Exit   ESC
  Pause  SPACE or PAUSE

  Left paddle:
    Up    W
    Down  S

  Right paddle:
    Up    UP ARROW
    Down  DOWN ARROW

Option(s):
  -h --help          Display this information
  -v --version       Display program name and version number
  --ai <level>       The left paddle is controlled by the computer - difficulty
                     level 1-4, where 1 is the easiest (slower AI reaction)
  --nosound          Disable sound
  --height <pixels>  Set the height of the game window
  --width <pixels>   Set the width of the game window

For developers:
  Class(es):
    Game    - holds game info
    Display - game window and net
    Ball
    Paddle

  Function(s):
    main    - game loop
    pause   - pause game
    help    - display this (docstring)
    version - display program name and version number
    warning - print warning

"""


import pygame
import random
import sys


PRG_NAME = 'spong'
VERSION  = 0.1

WIN_WIDTH  = 560
WIN_HEIGHT = 320

NET_WIDTH  = 4
NET_HEIGHT = 20

BALL_WIDTH   = 10
BALL_HEIGHT  = BALL_WIDTH
BALL_SPEED_X = 2
BALL_SPEED_Y = BALL_SPEED_X

PADDLE_HEIGHT = 60
PADDLE_WIDTH  = BALL_WIDTH
PADDLE_SPEED  = BALL_SPEED_X
PADDLE_OFFSET = 30

AI_LVL_DEF = 2
AI_LVL_MAX = 4

BG_COLOR = (0, 0, 0)
FG_COLOR = (255, 255, 255)


class Game:
    """Dummy class for game options.

    Attributes:
     points (left paddle's score, right paddle's score - integer tuple)
     serve_left (should the left paddle serve? - boolean)
     ai (should the left paddle be controlled by the computer? - boolean)
     nosound (do not play game sounds - boolean)

    """
    pass


class Display:
    """Display class for spong.

    Method(s):
     __init__

    """
    def __init__(self):
        """Create Display object.

        Attribute(s):
         surf (pygame.Surface)
         draw_net (draw the net to the display)
         _net (marks the middle of the display with line segments)

        """
        self.surf = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.net = self._net()

    def draw_net(self):
        """Draw the net to the display."""
        for net in self.net:
            pygame.draw.rect(self.surf, FG_COLOR, net, 0)

    def _net(self):
        """Return a list of rectangles forming a net."""
        net = []
        idx = 1

        while idx * NET_HEIGHT / 2 <= WIN_HEIGHT:
            net.append(pygame.Rect(WIN_WIDTH / 2 - NET_WIDTH / 2,
                                   idx * (NET_HEIGHT / 2),
                                   NET_WIDTH,
                                   NET_HEIGHT))

            idx += 4

        return net


class Ball:
    """Ball class for spong.

    Method(s):
     __init__
     move (move ball)
     collide_paddle (ball collision with paddle)
     collide_wall (ball collision with walls)
     collide_end (ball collision with end walls)
     incspeed (increase horisontal speed)

    """
    def __init__(self, x, y, speed_x, speed_y, nosound=False):
        """Creates Ball object.

        Argument(s):
         x (beginning x-coordinate - integer)
         y (beginning y-coordinate - integer)
         speed_x (beginning horisontal speed - integer)
         speed_y (beginning vertical speed - integer)
         nosound (do not play sound - boolean)

        Attribute(s):
         rect (pygame.Rect)
         speed (vertical speed, horizontal speed - dictionary)
         sound (played when wall is hit - pygame.mixer.Sound)

        """
        self.rect = pygame.Rect(x, y, BALL_WIDTH, BALL_HEIGHT)
        self.speed = {'x': speed_x, 'y': speed_y}
        self.sound = pygame.mixer.Sound('sfx/wall_bounce.wav')

        if nosound:
            self.sound.set_volume(0.0)

    def move(self):
        """Move ball."""
        self.rect = self.rect.move(self.speed['x'], self.speed['y'])

    def collide_wall(self):
        """Change vertical speed if ball collides with paddle."""
        if self.rect.top < 0 or self.rect.bottom > WIN_HEIGHT:
            self.speed['y'] = -self.speed['y']
            self.sound.play()

    def collide_end(self, L_pad, R_pad):
        """Change scores if the ball collides with an end wall.

        Argument(s):
         L_pad (left most paddle Paddle)
         R_pad (right most paddle Paddle)

        """
        if self.rect.left < 0:
            R_pad.score += 1
        elif self.rect.right > WIN_WIDTH:
            L_pad.score += 1

    def incspeed(self):
        """Increase horisontal speed."""
        inc = 0.2

        if self.speed['x'] > 0:
            self.speed['x'] += inc
        else:
            self.speed['x'] -= inc


class Paddle:
    """Paddle class.

    Method(s):
     __init__ (create a paddle)
     move (move the paddle)
     collide_ball (bounce ball when it hits a paddle)
     print_score (return a surface of the score)

    """
    def __init__(self, x, y, points=0, nosound=False):
        """Creater Paddle object.

        Argument(s):
         x (beginning x-coordinate - integer)
         y (beginning y-coordinate - integer)
         points (paddle's score - integer)
         nosound (do not play sound - boolean)

        Attribute(s)
         rect (pygame.Rect)
         score (number of balls the paddle has won - integer)
         speed (vertical speed, horizontal speed - list of integers)
         is_left (is the paddle the left one? - boolean)
         is_moving (is the paddle moving? - boolean)
         sound (played when ball is hit - pygame.mixer.Sound)

        """
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.score = points
        self.speed = PADDLE_SPEED
        self.is_left = self.rect.left == PADDLE_OFFSET
        self.is_moving = False
        self.sound = pygame.mixer.Sound('sfx/paddle_bounce.wav')

        if nosound:
            self.sound.set_volume(0.0)

    def move(self, ball, game):
        """Move the paddle.

        The leftmost bat is moved with the keys W and S.
        The rightmost bat is moved with the up and down arrows.
        If the paddle is ai-controlled it should move, so the center of the
        paddle is in line with the ball.

        """
        self.is_moving = False

        if game.ai and self.is_left:
            if self.rect.top > 0:
                if (self.rect.centery > ball.rect.centery and
                    ball.rect.centerx < WIN_WIDTH * game.ai_lvl / AI_LVL_MAX):
                    self.speed = -abs(self.speed)
                    self.is_moving = True

            if self.rect.bottom < WIN_HEIGHT:
                if (self.rect.centery < ball.rect.centery and
                    ball.rect.centerx < WIN_WIDTH * game.ai_lvl / AI_LVL_MAX):
                    self.speed = abs(self.speed)
                    self.is_moving = True
        else:
            if self.is_left:
                key_up = pygame.K_w
                key_dn = pygame.K_s
            else:
                key_up = pygame.K_UP
                key_dn = pygame.K_DOWN

            if self.rect.top > 0:
                if pygame.key.get_pressed()[key_up]:
                    self.speed = -abs(self.speed)
                    self.is_moving = True

            if self.rect.bottom < WIN_HEIGHT:
                if pygame.key.get_pressed()[key_dn]:
                    self.speed = abs(self.speed)
                    self.is_moving = True

        if self.is_moving:
            self.rect = self.rect.move([0, self.speed])

    def collide_ball(self, ball):
        """If the ball hits the top or bottom of the paddle change
        vertical direction, otherwise spin the ball and change
        horisontal direction.

        Argument(s):
         ball

        """
        if self.rect.colliderect(ball.rect.move(ball.speed['x'],
                                                ball.speed['y'])):
            self.sound.play()
            ball.incspeed()

            if ((self.is_left and ball.rect.left < self.rect.right) or
                (not self.is_left and ball.rect.right > self.rect.left)):
                ball.speed['y'] = -ball.speed['y']
            else:
                if self.is_moving: # Spin the ball
                    if (self.speed < 0 and ball.speed['y'] <= 0 or
                        self.speed < 0 and ball.speed['y'] >= 0):
                        ball.speed['y'] += 1

                        if ball.speed['y'] == 0: # Make ball not fly straight
                            ball.speed['y'] -= 1
                    else:
                        ball.speed['y'] -= 1

                        if ball.speed['y'] == 0: # Make ball not fly straight
                            ball.speed['y'] += 1

                ball.speed['x'] = -ball.speed['x']

    def print_score(self, screen, font_name='Arial', font_size=24):
        """Draw the score to the display.

        Write the score to screen.

        Argument(s):
         screen (Display)
         font_name (name of font - string)
         font_size (size of font - integer)

        """
        font = pygame.font.SysFont(font_name, font_size)
        score_surf = font.render(str(self.score), True, FG_COLOR, BG_COLOR)
        score_rect = score_surf.get_rect()

        if self.is_left:
            score_rect.left = WIN_WIDTH / 3
            score_rect.top = 10
        else:
            score_rect.right = WIN_WIDTH - WIN_WIDTH / 3
            score_rect.top = 10

        screen.surf.blit(score_surf, score_rect)


def main(game):
    """Start game.

    Change game object's score and serve right, when a point is won.
    Exit if ESC or close button is pressed.
    Pause if SPACE or PAUSE is pressed.

    Argument(s):
     game

    """
    screen = Display()

    if game.serve_left:
        tmp = -BALL_SPEED_X
    else:
        tmp = BALL_SPEED_X

    random.seed()

    ball = Ball(WIN_WIDTH / 2 - BALL_WIDTH / 2,
                WIN_HEIGHT / 2 - BALL_HEIGHT / 2,
                tmp,
                [-2, -1, 1, 2][random.randint(0, 3)],
                game.nosound)

    L_pad = Paddle(PADDLE_OFFSET,
                   WIN_HEIGHT / 2 - PADDLE_HEIGHT / 2,
                   game.points[0],
                   game.nosound)

    R_pad = Paddle(WIN_WIDTH - PADDLE_WIDTH - PADDLE_OFFSET,
                   WIN_HEIGHT / 2 - PADDLE_HEIGHT / 2,
                   game.points[1],
                   game.nosound)

    while True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or
                (event.type == pygame.KEYDOWN and
                 event.key == pygame.K_ESCAPE)):
                sys.exit()
            elif (event.type == pygame.KEYDOWN and
                  (event.key == pygame.K_SPACE or
                   event.key == pygame.K_PAUSE)):
                pause([pygame.K_SPACE, pygame.K_PAUSE], [pygame.K_ESCAPE])

        ball.move()
        ball.collide_wall()
        ball.collide_end(L_pad, R_pad)

        if game.points != (L_pad.score, R_pad.score):
            game.points = (L_pad.score, R_pad.score)
            game.serve_left = not game.serve_left

            return

        L_pad.move(ball, game)
        L_pad.collide_ball(ball)
        R_pad.move(ball, game)
        R_pad.collide_ball(ball)

        screen.surf.fill(BG_COLOR)
        screen.draw_net()
        R_pad.print_score(screen)
        L_pad.print_score(screen)
        pygame.draw.rect(screen.surf, FG_COLOR, ball.rect, 0)
        pygame.draw.rect(screen.surf, FG_COLOR, L_pad.rect, 0)
        pygame.draw.rect(screen.surf, FG_COLOR, R_pad.rect, 0)
        pygame.display.flip()

        pygame.time.wait(10)


def pause(unpause_keys, exit_keys):
    """Pause the game.

    Unpause the game when one of the unpause_keys is pressed.
    Exit the game when one of the exit_keys or close button is pressed.

    Argument(s):
     unpause_keys (list of pygame keyboard constants)
     exit_keys (list of pygame keyboard constants)

    """
    while True:
        event = pygame.event.wait()

        if event.type == pygame.KEYDOWN:
            for u in unpause_keys:
                if event.key == u:
                    return

            for e in exit_keys:
                if event.key == e:
                    sys.exit()
        elif event.type == pygame.QUIT:
            sys.exit()


def help():
    """Print usage message and module information.

    Print docstring stripped from trailing whitespace.

    """
    print(__doc__.rstrip())
    sys.exit()


def version():
    print(PRG_NAME, VERSION)
    print("""
For license and copyright information see the LICENSE file, which should have
been distributed with the software.""")
    sys.exit()


def warning(*args):
    print(PRG_NAME, ": warning: ", sep='', end='')

    for arg in args:
        print(arg, end='')

    print()


def parse_args(options, game):
    for idx, opt in enumerate(options):
        if opt == '-h' or opt == '--help':
            help()
        elif opt == '-v' or opt == '--version':
            version()
        elif opt == '--ai':
            game.ai = True

            try:
                game.ai_lvl = int(options[idx + 1])

                if game.ai_lvl < 1 or game.ai_lvl > AI_LVL_MAX:
                    game.ai_lvl = AI_LVL_DEF
            except (ValueError, IndexError):
                warning("ai difficulty was not set - using default level ",
                        AI_LVL_DEF, " of ", AI_LVL_MAX)
        elif opt == '--nosound':
            game.nosound = True
        elif opt == '--height':
            try:
                WIN_HEIGHT = int(options[idx + 1])
            except (ValueError, IndexError):
                warning("--height was not be followed by a number ",
                        "- using default ", WIN_HEIGHT)
        elif opt == '--width':
            try:
                WIN_WIDTH = int(options[idx + 1])
            except (ValueError, IndexError):
                warning("--width was not be followed by a number ",
                        "- using default ", WIN_WIDTH)
        else:
            if not options[idx - 1] in ['--ai',
                                        '--nosound',
                                        '--height',
                                        '--width']:
                warning("unknown argument ", opt)


if __name__ == '__main__':
    game = Game()
    game.points = (0, 0)
    game.serve_left = False
    game.ai = False
    game.ai_lvl = AI_LVL_DEF
    game.nosound = False

    parse_args(sys.argv[1:], game)

    pygame.mixer.pre_init(buffer=1024) # Sounds plays instantly
    pygame.init()
    pygame.display.set_caption('spong')
    pygame.display.set_icon(pygame.image.load('img/icon.png'))
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])

    while True:
        main(game)
        pygame.time.wait(1000)

