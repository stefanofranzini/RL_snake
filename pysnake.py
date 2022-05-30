#!/usr/bin/python3

import pygame as pg
import time
import numpy as np
import os
import gym

############################################################################################
# global definitions #######################################################################
############################################################################################

#### gym environment for the critters brain

env = gym.make("gym_tag:tag-v0",n=23).env
q_table = np.load("custom_environments/q_table_tag.npy")[0]

#### size of stuff

snake_block  = 40

dis_width    = 25 * snake_block
dis_height   = 22 * snake_block

arena_width  = 23 * snake_block
arena_height = 20 * snake_block

#### initialize game environment

pg.init()
pg.mixer.init()

dis = pg.display.set_mode((dis_width, dis_height))
pg.display.update()
pg.display.set_caption("pysnake game by SF")
game_over = False

#### initialize colors

white       = (255, 255, 255)
black       = (0, 0, 0)
red         = (255, 0, 0)
pur         = (255, 0, 255)
blue        = (50, 153, 213)
yellow      = (255, 255, 102)
green       = (0, 255, 0)
rusty       = (184, 77, 0)
deep_purple = (90, 77, 163)
deep_cyan   = (20, 80, 100)
golden      = (255, 179, 0)

snake_colors = [black, red, deep_purple, blue, rusty, golden, deep_cyan]

#### load images for each section of the game

# TITLE SCREEN

title_screen = pg.image.load("other_icons/title_screen.jpg")
height = dis_width * title_screen.get_height() / title_screen.get_width()
title_screen = pg.transform.scale(title_screen, (dis_width, height))

title = pg.image.load("other_icons/snake_title.png")
height = round(dis_width * 0.6) * title.get_height() / title.get_width()
title = pg.transform.scale(title, (round(0.6 * dis_width), height))

# ARENA

background = pg.image.load("other_icons/grass.png")
background = pg.transform.scale(background, (dis_width, dis_height))

# GAME OVER

game_over_screen = pg.image.load("other_icons/game_over.png")
height = dis_width * game_over_screen.get_height() / game_over_screen.get_width()
game_over_screen = pg.transform.scale(game_over_screen, (dis_width, height))

#### load images to use as icons during the game

snake_cursor = pg.image.load("other_icons/snake.png")
snake_cursor = pg.transform.scale(snake_cursor, (120, 120))

berries = []

for i in range(1, 20):
    berry_icon = pg.image.load("berries/berry%d.png" % i).convert_alpha()
    berry_icon = pg.transform.scale(berry_icon, (snake_block * 1.5, snake_block * 1.5))
    berries += [berry_icon]

critters = []

for i in range(1, 15):
    critter_icon = pg.image.load("critters/critter%d.png" % i).convert_alpha()
    critter_icon = pg.transform.scale(
        critter_icon, (snake_block * 2.0, snake_block * 2.0)
    )

    if i in [1, 3, 9]:
        critter_icon_up = critter_icon
        critter_icon_dw = pg.transform.rotate(critter_icon, 180)
        critter_icon_sx = pg.transform.rotate(critter_icon, 90)
        critter_icon_dx = pg.transform.rotate(critter_icon, -90)
    else:
        critter_icon_up = critter_icon
        critter_icon_dw = pg.transform.flip(critter_icon, True, False)
        critter_icon_sx = critter_icon
        critter_icon_dx = pg.transform.flip(critter_icon, True, False)

    critters += [
        [
            critter_icon,
            critter_icon_up,
            critter_icon_dx,
            critter_icon_dw,
            critter_icon_sx
        ]
    ]
    
#### load sounds

critter_sounds = []

for i in range(1, 15):
    critter_sound = pg.mixer.Sound("sfx/critter_sound_%d.mp3" % i)
    critter_sounds += [critter_sound]

chomp_sound = pg.mixer.Sound("sfx/chomp.mp3")
rattle_sound = pg.mixer.Sound("sfx/rattle.mp3")
pain_sound = pg.mixer.Sound("sfx/pain.mp3")
poof_sound = pg.mixer.Sound("sfx/appear.mp3")

clock = pg.time.Clock()

#### define the fonts

font_style = pg.font.Font("fonts/impact.ttf", 60)
score_font = pg.font.Font("fonts/impact.ttf", 35)
title_font = pg.font.Font("fonts/impact.ttf", 100)
name_font = pg.font.Font("fonts/impact.ttf", 70)

############################################################################################
# functions ################################################################################
############################################################################################

def probe(delta):

    alpha = 1.0 / (5 * snake_block)
    return 0.5 * (1 + np.sign(delta - 1)) * (np.exp(-alpha * delta) + 1)

def encode(xf,yf,xh,yh,xt,yt):
    
    state = [ 1, 1, 1, 1, 1 ]
    
    # 1) transform coordinates
    
    xh = xh//snake_block - 1
    yh = yh//snake_block - 1
    xf = xf//snake_block - 1
    yf = yf//snake_block - 1
    xt = xt//snake_block - 1
    yt = yt//snake_block - 1
    
    width = arena_width//snake_block
    height= arena_height//snake_block
    
    fdist = 0
    hdist = 0

    diff_x = (xh - xf) % width
    x_diff = (xf - xh) % width
    
    if diff_x != 0:
        if diff_x < x_diff:
            state[0] = 0
            fdist += diff_x
        else:
            state[0] = 2
            fdist += x_diff

    diff_y = (yh - yf) % height 
    y_diff = (yf - yh) % height 
    
    if diff_y != 0:
        if diff_y < y_diff:
            state[1] = 0
            fdist += diff_y
        else:
            state[1] = 2
            fdist += y_diff
    
    diff_x = (xh - xt) % width 
    x_diff = (xt - xh) % width 
    
    if diff_x != 0:
        if diff_x < x_diff:
            state[2] = 0
            hdist += diff_x
        else:
            state[2] = 2
            hdist += x_diff

    diff_y = (yh - yt) % height 
    y_diff = (yt - yh) % height 
    
    if diff_y != 0:
        if diff_y < y_diff:
            state[3] = 0
            hdist += diff_y
        else:
            state[3] = 2
            hdist += y_diff

    if fdist > hdist:
        state[4] = 0
    elif fdist < hdist:
        state[4] = 2

    return np.ravel_multi_index(state,(3,3,3,3,3))

def decode(action):
    
    probability = [ 0 ] * 5
    probability[action] = 1
    return probability

def pick_action(state,q_table):
    
    my_qs = q_table[state]
    
    epsilon = 0.00
    
    return np.argmax(my_qs)

def critter_brain(xc, yc, xs, ys, foodx, foody):

    state = encode(foodx,foody,xs,ys,xc,yc)
    
    action = pick_action(state,q_table)
    
    return decode(action)


def update_gobble(indexes):

    i = 0

    while i < len(indexes):
        indexes[i] -= 1
        if indexes[i] < 0:
            del indexes[i]
        else:
            i += 1

    return indexes


def print_score(score):
    value = score_font.render("Your Score: " + str(score), True, black)
    dis.blit(value, [0, 0])


def color_surface(surface, color):
    arr = pg.surfarray.pixels3d(surface)
    arr[:, :, 0] = color[0]
    arr[:, :, 1] = color[1]
    arr[:, :, 2] = color[2]


def draw_snake(snake_list, gobble_index, snake_icons, snake_tails, snake_color):

    sizes = [snake_block for i in range(len(snake_list))]
    for index in gobble_index:
        sizes[index] = sizes[index] * 1.5

    for i in range(1, len(snake_list) - 1)[::-1]:
        x = snake_list[i]
        offset = (snake_block - sizes[i]) * 0.5
        pg.draw.rect(
            dis, snake_color, [x[0] + offset, x[1] + offset, sizes[i], sizes[i]]
        )

    xh, yh = snake_list[-1]

    dirx = snake_list[-1][0] - snake_list[-2][0]
    diry = snake_list[-1][1] - snake_list[-2][1]

    if diry == snake_block:
        dis.blit(snake_icons[1], (xh, yh))
    elif dirx == -snake_block:
        dis.blit(snake_icons[2], (xh, yh))
    elif dirx == snake_block:
        dis.blit(snake_icons[3], (xh, yh))
    else:
        dis.blit(snake_icons[0], (xh, yh))

    xh, yh = snake_list[0]

    dirx = snake_list[1][0] - snake_list[0][0]
    diry = snake_list[1][1] - snake_list[0][1]

    if diry == snake_block:
        dis.blit(snake_tails[1], (xh, yh))
    elif dirx == -snake_block:
        dis.blit(snake_tails[2], (xh, yh))
    elif dirx == snake_block:
        dis.blit(snake_tails[3], (xh, yh))
    else:
        dis.blit(snake_tails[0], (xh, yh))


def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [0.0, dis_height / 2])


def get_alphanumeric(key):

    letter = pg.key.name(key)
    return letter.upper(), (letter.isalnum() and len(letter) == 1)


############################################################################################
# game loop  ###############################################################################
############################################################################################

def game_loop(show_title_screen=True):

    game_over = False
    game_close = False

    pg.mixer.music.load("music/title_screen.mp3")
    pg.mixer.music.set_volume(0.1)
    pg.mixer.music.play(-1, 0, 10000)

    k = 50
    show_cursor = True
    y_cursor = 250

    try:
        ipt = open("saves/custom.game", "r")

        mylist = []

        for line in ipt:
            mylist += [int(line.split()[0])]

        head_index, tail_index, col_index = mylist[:3]
    except:

        head_index, tail_index, col_index = 0, 0, 0

    if not show_title_screen:

        snake_color = snake_colors[col_index]

        snake_icon = pg.image.load("snakes/head_%d.png" % head_index).convert_alpha()
        color_surface(snake_icon, snake_color)
        snake_icon = pg.transform.scale(snake_icon, (snake_block, snake_block))

        snake_icon_up = snake_icon
        snake_icon_dw = pg.transform.rotate(snake_icon, 180)
        snake_icon_dx = pg.transform.rotate(snake_icon, -90)
        snake_icon_sx = pg.transform.flip(snake_icon_dx, True, False)

        snake_tail = pg.image.load("snakes/tail_%d.png" % tail_index).convert_alpha()
        color_surface(snake_tail, snake_color)
        snake_tail = pg.transform.scale(snake_tail, (snake_block, snake_block))

        snake_tail_up = snake_tail
        snake_tail_dw = pg.transform.rotate(snake_tail, 180)
        snake_tail_dx = pg.transform.rotate(snake_tail, -90)
        snake_tail_sx = pg.transform.flip(snake_tail_dx, True, False)

        snake_icons = [snake_icon_up, snake_icon_dw, snake_icon_sx, snake_icon_dx]
        snake_tails = [snake_tail_up, snake_tail_dw, snake_tail_sx, snake_tail_dx]

    while show_title_screen:

        dis.fill(black)
        buffer = round(0.5 * (dis_height - title_screen.get_height()))
        dis.blit(title_screen, (0, buffer))

        buffer = round(0.5 * (dis_width - title.get_width()))
        dis.blit(title, (buffer, 20))

        if show_cursor:
            dis.blit(snake_cursor, (100, y_cursor))

        mesg = title_font.render("new game", True, black)
        dis.blit(mesg, [300, 270])

        mesg = title_font.render("customize", True, black)
        dis.blit(mesg, [300, 420])

        mesg = title_font.render("high scores", True, black)
        dis.blit(mesg, [300, 570])

        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if y_cursor == 250:
                    if event.key == pg.K_DOWN:
                        print
                        y_cursor = 400
                        poof_sound.play()
                    elif event.key == pg.K_RETURN:
                        show_title_screen = False

                        snake_color = snake_colors[col_index]

                        snake_icon = pg.image.load(
                            "snakes/head_%d.png" % head_index
                        ).convert_alpha()
                        color_surface(snake_icon, snake_color)
                        snake_icon = pg.transform.scale(
                            snake_icon, (snake_block, snake_block)
                        )

                        snake_icon_up = snake_icon
                        snake_icon_dw = pg.transform.rotate(snake_icon, 180)
                        snake_icon_dx = pg.transform.rotate(snake_icon, -90)
                        snake_icon_sx = pg.transform.flip(snake_icon_dx, True, False)

                        snake_tail = pg.image.load(
                            "snakes/tail_%d.png" % tail_index
                        ).convert_alpha()
                        color_surface(snake_tail, snake_color)
                        snake_tail = pg.transform.scale(
                            snake_tail, (snake_block, snake_block)
                        )

                        snake_tail_up = snake_tail
                        snake_tail_dw = pg.transform.rotate(snake_tail, 180)
                        snake_tail_dx = pg.transform.rotate(snake_tail, -90)
                        snake_tail_sx = pg.transform.flip(snake_tail_dx, True, False)

                        snake_icons = [
                            snake_icon_up,
                            snake_icon_dw,
                            snake_icon_sx,
                            snake_icon_dx,
                        ]
                        snake_tails = [
                            snake_tail_up,
                            snake_tail_dw,
                            snake_tail_sx,
                            snake_tail_dx,
                        ]

                        poof_sound.play()
                        pg.mixer.music.fadeout(2000)

                elif y_cursor == 400:
                    if event.key == pg.K_UP:
                        y_cursor = 250
                        poof_sound.play()
                    elif event.key == pg.K_DOWN:
                        y_cursor = 550
                        poof_sound.play()
                    elif event.key == pg.K_RETURN:
                        poof_sound.play()

                        custom_screen = True

                        display_color = snake_colors[col_index]

                        display_head = pg.image.load(
                            "snakes/head_%d.png" % head_index
                        ).convert_alpha()
                        color_surface(display_head, display_color)
                        display_head = pg.transform.scale(display_head, (200, 200))

                        display_tail = pg.image.load(
                            "snakes/tail_%d.png" % tail_index
                        ).convert_alpha()
                        color_surface(display_tail, display_color)
                        display_tail = pg.transform.scale(display_tail, (200, 200))

                        x_cursor = 125
                        k = 50

                        while custom_screen:

                            dis.fill(black)
                            buffer = round(
                                0.5 * (dis_height - title_screen.get_height())
                            )
                            dis.blit(title_screen, (0, buffer))

                            mesg = title_font.render("HEAD", True, black)
                            dis.blit(mesg, [100, 170])

                            mesg = title_font.render("TAIL", True, black)
                            dis.blit(mesg, [420, 170])

                            mesg = title_font.render("COLOR", True, black)
                            dis.blit(mesg, [675, 170])

                            dis.blit(display_head, (100, 320))
                            dis.blit(display_tail, (400, 320))
                            pg.draw.rect(dis, display_color, [700, 320, 200, 200])

                            if show_cursor:
                                dis.blit(snake_cursor, (x_cursor, 570))

                            pg.display.update()

                            for event in pg.event.get():
                                if event.type == pg.KEYDOWN:
                                    if x_cursor == 125:
                                        if event.key == pg.K_RIGHT:
                                            x_cursor = 445
                                            poof_sound.play()
                                        if event.key == pg.K_UP and head_index > 0:
                                            head_index -= 1
                                            display_head = pg.image.load(
                                                "snakes/head_%d.png" % head_index
                                            ).convert_alpha()
                                            color_surface(display_head, display_color)
                                            display_head = pg.transform.scale(
                                                display_head, (200, 200)
                                            )
                                            poof_sound.play()
                                        if event.key == pg.K_DOWN and head_index < 6:
                                            head_index += 1
                                            display_head = pg.image.load(
                                                "snakes/head_%d.png" % head_index
                                            ).convert_alpha()
                                            color_surface(display_head, display_color)
                                            display_head = pg.transform.scale(
                                                display_head, (200, 200)
                                            )
                                            poof_sound.play()
                                    elif x_cursor == 445:
                                        if event.key == pg.K_RIGHT:
                                            x_cursor = 725
                                            poof_sound.play()
                                        if event.key == pg.K_LEFT:
                                            x_cursor = 125
                                            poof_sound.play()
                                        if event.key == pg.K_UP and tail_index > 0:
                                            tail_index -= 1
                                            display_tail = pg.image.load(
                                                "snakes/tail_%d.png" % tail_index
                                            ).convert_alpha()
                                            color_surface(display_tail, display_color)
                                            display_tail = pg.transform.scale(
                                                display_tail, (200, 200)
                                            )
                                            poof_sound.play()
                                        if event.key == pg.K_DOWN and tail_index < 6:
                                            tail_index += 1
                                            display_tail = pg.image.load(
                                                "snakes/tail_%d.png" % tail_index
                                            ).convert_alpha()
                                            color_surface(display_tail, display_color)
                                            display_tail = pg.transform.scale(
                                                display_tail, (200, 200)
                                            )
                                            poof_sound.play()
                                    elif x_cursor == 725:
                                        if event.key == pg.K_LEFT:
                                            x_cursor = 445
                                            poof_sound.play()
                                        if event.key == pg.K_UP and col_index > 0:
                                            col_index -= 1
                                            display_color = snake_colors[col_index]
                                            color_surface(display_head, display_color)
                                            color_surface(display_tail, display_color)
                                            poof_sound.play()
                                        if event.key == pg.K_DOWN and col_index < 6:
                                            col_index += 1
                                            display_color = snake_colors[col_index]
                                            color_surface(display_head, display_color)
                                            color_surface(display_tail, display_color)
                                            poof_sound.play()
                                    if event.key == pg.K_RETURN:
                                        poof_sound.play()
                                        custom_screen = False

                                        opt = open("saves/custom.game", "w")

                                        opt.write(
                                            "%d\n%d\n%d"
                                            % (head_index, tail_index, col_index)
                                        )
                                        opt.close()

                                elif event.type == pg.QUIT:
                                    show_title_screen = False
                                    custom_screen = False
                                    game_over = True

                            k -= 1
                            if k < 0:
                                show_cursor = show_cursor ^ True
                                k = 50

                elif y_cursor == 550:
                    if event.key == pg.K_UP:
                        y_cursor = 400
                        poof_sound.play()
                    elif event.key == pg.K_RETURN:
                        poof_sound.play()

                        high_score_screen = True

                        try:

                            ipt = open("saves/save.game", "r")

                            names = []
                            scors = []

                            for line in ipt:
                                flds = line.split()
                                names += [flds[0]]
                                scors += [int(flds[1])]

                            ipt.close()

                            names = names[:3]
                            scors = scors[:3]

                        except:

                            names = []
                            scors = []

                        while high_score_screen:

                            dis.fill(black)
                            buffer = round(
                                0.5 * (dis_height - title_screen.get_height())
                            )
                            dis.blit(title_screen, (0, buffer))

                            mesg = title_font.render("HIGH SCORES", True, black)
                            dis.blit(mesg, [240, 160])

                            for i in range(len(scors)):
                                mesg = font_style.render(
                                    "%d.  %s   :  %04d" % (i + 1, names[i], scors[i]),
                                    True,
                                    black,
                                )
                                dis.blit(mesg, [280, 100 * (i + 3)])

                            for i in range(3 - len(scors)):
                                mesg = font_style.render(
                                    "%d.  %s   :  0000"
                                    % (i + len(scors) + 1, "_ _ _ _ _"),
                                    True,
                                    black,
                                )
                                dis.blit(mesg, [280, 100 * (i + len(scors) + 3)])

                            pg.display.update()

                            for event in pg.event.get():
                                if event.type == pg.KEYDOWN:
                                    high_score_screen = False
                                elif event.type == pg.QUIT:
                                    high_score_screen = False
                                    game_over = True

            if event.type == pg.QUIT:
                show_title_screen = False
                game_over = True

        k -= 1
        if k < 0:
            show_cursor = show_cursor ^ True
            k = 30

    playlist = ["music/song%d.mp3" % i for i in range(1, 6)]
    np.random.shuffle(playlist)
    pg.mixer.music.load(playlist.pop(0))

    pg.mixer.music.set_volume(0.5)
    pg.mixer.music.play()
    pg.mixer.music.queue(playlist.pop(0))

    MUSIC_END = pg.USEREVENT + 1
    pg.mixer.music.set_endevent(MUSIC_END)

    sb = snake_block

    score = 0

    x1 = round(arena_width / (2.0 * snake_block)) * snake_block
    y1 = round(arena_height / (2.0 * snake_block)) * snake_block

    snake_length = 5
    snake_speed = 10
    snake_list = [[x1, y1 + sb * i] for i in range(snake_length)][::-1]

    available = [
        [x * sb, y * sb]
        for x in range(1, round(arena_width / sb + 1))
        for y in range(1, round(arena_height / sb + 1))
        if (x * sb, y * sb) not in snake_list
    ]

    gobble_index = []

    critter_deployed = False
    critter_counter = 5

    mytime = 0

    y1_change = -snake_block
    x1_change = 0

    berry_icon = np.random.choice(berries)
    foodx, foody = available[np.random.choice(range(len(available)))]

    forbidden = [pg.K_DOWN]

    while not game_over:

        while game_close:

            dis.fill(black)
            buffer = round(0.5 * (dis_height - game_over_screen.get_height()))
            dis.blit(game_over_screen, (0, buffer))

            mesg = title_font.render("GAME OVER", True, red)
            dis.blit(mesg, [280, 20])

            high_score = False

            if "***" in names:
                high_score = True
                new_name = []
                new_index = names.index("***")

            while high_score:

                dis.fill(black)
                buffer = round(0.5 * (dis_height - game_over_screen.get_height()))
                dis.blit(game_over_screen, (0, buffer))

                mesg = title_font.render("GAME OVER", True, red)
                dis.blit(mesg, [280, 20])

                screen_name = new_name + ["*"] * (7 - len(new_name))

                mesg = name_font.render("%04d" % scors[new_index], True, red)
                dis.blit(mesg, [450, 550])

                for i in range(7):
                    letter = name_font.render("%s" % screen_name[i], True, red)
                    dis.blit(letter, [200 + 100 * (i), 400])

                if show_message:
                    mesg = score_font.render(
                        "New High Score! Insert your name and press ENTER to save!",
                        True,
                        red,
                    )
                    dis.blit(mesg, [100, dis_height - 100])

                    dis.blit(snake_cursor, (x_cursor, 350))

                pg.display.update()

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        game_over = True
                        game_close = False
                        high_score = False
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_BACKSPACE:
                            if len(new_name) > 0:
                                poof_sound.play()
                                del new_name[-1]

                                x_cursor -= 100

                        elif event.key == pg.K_RETURN and len(new_name) > 0:
                            names[new_index] = "".join(new_name)
                            high_score = False

                            opt = open("saves/save.game", "w")

                            for i in range(len(names)):
                                opt.write("%s\t%d\n" % (names[i], scors[i]))

                            opt.close()

                        else:
                            new_letter, is_valid = get_alphanumeric(event.key)
                            if is_valid and len(new_name) < 7:

                                poof_sound.play()
                                new_name += [new_letter]

                                x_cursor += 100

                k -= 1
                if k < 0:
                    k = 50
                    show_message = show_message ^ True

            for i in range(len(scors)):
                mesg = font_style.render(
                    "%d.  %s   :  %04d" % (i + 1, names[i], scors[i]), True, red
                )
                dis.blit(mesg, [280, 100 * (i + 2)])

            for i in range(3 - len(scors)):
                mesg = font_style.render(
                    "%d.  %s   :  0000" % (i + len(scors) + 1, "_ _ _ _ _"), True, red
                )
                dis.blit(mesg, [280, 100 * (i + len(scors) + 2)])

            if show_message:
                mesg = font_style.render("YOUR SCORE  : %04d" % (score), True, red)
                dis.blit(mesg, [280, 550])

                mesg = score_font.render(
                    "You Lost! Press Q to Quit, ENTER to Play Again!", True, red
                )
                dis.blit(mesg, [200, dis_height - 100])

            pg.display.update()

            k -= 1
            if k < 0:
                k = 50
                show_message = show_message ^ True

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        game_over = False
                        game_close = False
                        show_title_screen = True
                        game_loop(show_title_screen)
                    if event.key == pg.K_RETURN:
                        game_loop(show_title_screen)

        for event in pg.event.get():
            if event.type == MUSIC_END:
                if len(playlist) > 0:
                    pg.mixer.music.queue(playlist.pop(0))
                else:
                    playlist = ["music/song%d.mp3" % i for i in range(1, 6)]
                    np.random.shuffle(playlist)

                    pg.mixer.music.queue(playlist.pop(0))

            if event.type == pg.QUIT:
                game_over = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    pause = True

                    pg.mixer.music.set_volume(0.1)

                    s = pg.Surface((dis_width, dis_height))
                    s.set_alpha(128)
                    s.fill((255, 255, 255))
                    dis.blit(s, [0, 0])

                    mesg = title_font.render("PAUSE", True, snake_color)
                    dis.blit(mesg, [375, 350])

                    while pause:

                        pg.display.update()

                        for event in pg.event.get():
                            if event.type == pg.QUIT:
                                game_over = True
                                pause = False
                            if event.type == pg.KEYDOWN:
                                if event.key == pg.K_SPACE:
                                    pause = False
                                    pg.mixer.music.set_volume(0.5)
                    break

                if event.key not in forbidden:
                    if event.key == pg.K_LEFT:
                        x1_change = -snake_block
                        y1_change = 0
                        forbidden = [pg.K_RIGHT]
                    elif event.key == pg.K_RIGHT:
                        x1_change = snake_block
                        y1_change = 0
                        forbidden = [pg.K_LEFT]
                    elif event.key == pg.K_UP:
                        y1_change = -snake_block
                        x1_change = 0
                        forbidden = [pg.K_DOWN]
                    elif event.key == pg.K_DOWN:
                        y1_change = snake_block
                        x1_change = 0
                        forbidden = [pg.K_UP]
                    break

        x1 += x1_change
        y1 += y1_change
        gobble_index = update_gobble(gobble_index)

        if np.random.uniform(0, 1) < 0.001:
            pg.mixer.Sound.play(rattle_sound)

        if x1 >= arena_width + snake_block:
            x1 = snake_block
        elif x1 < snake_block:
            x1 = arena_width
        elif y1 >= arena_height + snake_block:
            y1 = snake_block
        elif y1 < snake_block:
            y1 = arena_height

        dis.fill(white)
        pg.draw.rect(dis, blue, [snake_block, snake_block, arena_width, arena_height])
        dis.blit(background, (0, 0))

        dis.blit(berry_icon, (foodx - 0.25 * snake_block, foody - 0.25 * snake_block))

        snake_head = []
        snake_head += [x1]
        snake_head += [y1]
        snake_list += [snake_head]
        try:
            available.remove(snake_head)
        except ValueError:
            pass

        if len(snake_list) > snake_length:
            available += [snake_list[0]]
            del snake_list[0]

        if critter_deployed:
            if np.random.uniform(0, 1) < 0.01:
                critter_sfx.play()

            if mytime % 4 == 0:
                if np.random.uniform(0, 1) < 1.0:
                    critter_dir = np.random.choice(
                        range(5), p=critter_brain(x2, y2, x1, y1, foodx, foody)
                    )
                    x2_change, y2_change = [
                        (0,  0),
                        (0,-sb),
                        (sb, 0),
                        (0, sb),
                        (-sb,0)
                        ][critter_dir]

                x2_ = x2 + x2_change
                y2_ = y2 + y2_change

                if x2_ >= arena_width + snake_block:
                    x2_ = snake_block
                elif x2_ < snake_block:
                    x2_ = arena_width
                elif y2_ >= arena_height + snake_block:
                    y2_ = snake_block
                elif y2_ < snake_block:
                    y2_ = arena_height

                if not [x2_, y2_] in snake_list:
                    x2 = x2_
                    y2 = y2_

            dis.blit(
                critter_icons[critter_dir],
                (x2 - 0.5 * snake_block, y2 - 0.5 * snake_block),
            )

        for x in snake_list[:-1]:
            if x == snake_head:
                print("ouch!")
                pain_sound.play()
                game_close = True
                pg.mixer.music.fadeout(3000)
                time.sleep(2)

                pg.mixer.music.load("music/game_over.mp3")
                pg.mixer.music.set_volume(0.2)
                pg.mixer.music.play(-1, 0, 10000)

                show_message = True
                k = 50
                x_cursor = 150

                try:

                    ipt = open("saves/save.game", "r")

                    names = []
                    scors = []

                    for line in ipt:
                        flds = line.split()
                        names += [flds[0]]
                        scors += [int(flds[1])]

                    ipt.close()

                    nscore = len(scors)

                    for n in range(len(scors)):
                        if score > scors[n]:
                            nscore = n
                            break

                    names.insert(nscore, "***")
                    scors.insert(nscore, score)

                    names = names[:3]
                    scors = scors[:3]

                except:

                    names = ["***"]
                    scors = [score]

        draw_snake(snake_list, gobble_index, snake_icons, snake_tails, snake_color)

        if x1 == foodx and y1 == foody:
            pg.mixer.Sound.play(chomp_sound)
            berry_icon = np.random.choice(berries)
            foodx, foody = available[np.random.choice(range(len(available)))]
            gobble_index = [g + 1 for g in gobble_index] + [snake_length]
            snake_length += 1
            score += 1
            critter_counter -= 1
            if critter_counter <= 0:
                if not critter_deployed:
                    critter_deployed = True
                    x2, y2 = available[np.random.choice(range(len(available)))]
                    critter_index = np.random.choice(len(critters))
                    critter_icons = critters[critter_index]
                    critter_dir = np.random.choice(
                        range(5), p=critter_brain(x2, y2, x1, y1, foodx, foody)
                    )
                    x2_change, y2_change = [
                        (0, -sb),
                        (0, sb),
                        (-sb, 0),
                        (sb, 0),
                        (0, 0),
                    ][critter_dir]
                    critter_sound = critter_sounds[critter_index]
                    critter_sfx = pg.mixer.Sound(critter_sound)
                    critter_sfx.play()

                else:
                    critter_counter = 5

        if critter_deployed:

            if x1 == x2 and y1 == y2:
                critter_sfx.fadeout(500)
                pg.mixer.Sound.play(chomp_sound)
                gobble_index = [g + 1 for g in gobble_index] + [snake_length]
                if snake_speed < 15:
                    snake_speed += 1
                snake_length += 1
                score += snake_speed
                critter_deployed = False
                critter_counter = 5

            if x2 == foodx and y2 == foody:
                pg.mixer.Sound.play(chomp_sound)
                berry_icon = np.random.choice(berries)
                foodx, foody = available[np.random.choice(range(len(available)))]

        pg.draw.rect(dis, white, [0, 0, snake_block, dis_height])
        pg.draw.rect(dis, white, [0, 0, dis_width, snake_block])
        pg.draw.rect(
            dis, white, [snake_block + arena_width, 0, snake_block, dis_height]
        )
        pg.draw.rect(
            dis, white, [0, arena_height + snake_block, dis_width, snake_block]
        )

        print_score(score)

        pg.display.update()

        clock.tick(snake_speed)
        mytime += 1
    pg.quit()
    quit()


# pg.mixer.music.play(-1)

# play the game loop

game_loop()
