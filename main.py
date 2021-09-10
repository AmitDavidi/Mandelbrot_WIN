import pygame
from ctypes import *
import numpy as np
import os
import math
from time import *


# import time
# get C Functions
cwd = os.getcwd()
path = os.path.join(cwd + "\myf.dll")

# c_funcs = WinDLL("C:\\Users\\amitd\\PProjects\\New_mandlebrot\\myf.dll")
c_funcs = WinDLL(path)
c_funcs.map_num.argtypes = [c_double, c_double, c_double, c_double]
c_funcs.does_converge.argtypes = [c_double, c_double, c_int]
c_funcs.does_converge.restype = c_double
c_funcs.map_num.restype = c_double

pygame.init()
consts = {
    "WIDTH": 360,
    'HEIGHT': 360,
    'MAX_ITERATIONS': 1000}


def draw_screen(win, screen_matrix):
    pygame.pixelcopy.array_to_surface(win, screen_matrix)



def main(constants, win, data):
    colors = [(66, 30, 15),
              (25, 7, 26),
              (9, 1, 47),
              (4, 4, 73),
              (0, 7, 100),
              (12, 44, 138),
              (24, 82, 177),
              (57, 125, 209),
              (134, 181, 229),
              (211, 236, 248),
              (241, 233, 191),
              (248, 201, 95),
              (255, 170, 0),
              (204, 128, 0),
              (153, 87, 0),
              (106, 52, 3)

              ]
    BLACK = (0, 0, 0)
    len1 = len(colors)

    # better names for constants
    width = constants['WIDTH']
    height = constants['HEIGHT']
    max_iterations = constants['MAX_ITERATIONS']

    # starting ranges for the Mandelbrot
    x_range = [-2, 2]
    y_range = [-2, 2]
    last_x_range = []
    last_y_range = []

    # display calculations
    screen_matrix = np.zeros((width, height, 3), dtype=np.uint8)
    flag = 1
    # zoom variables
    zoom_counter = 1
    diff = 30
    diff_width = 2 * diff

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        # draw rectangle around mouse

        pygame.pixelcopy.array_to_surface(win, screen_matrix)
        current_rect = pygame.Rect(mx - diff, my - diff, diff_width, diff_width)
        pygame.draw.rect(win, (230, 230, 230), current_rect, 1)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_SPACE:
                    x_range = [-2, 2]
                    y_range = [-2, 2]
                    flag = 1
                    zoom_counter = 1
                    max_iterations = consts['MAX_ITERATIONS']

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed(3)[0]:
                    mapped_x1 = c_funcs.map_num(mx - diff, width, x_range[0], x_range[1])
                    mapped_x2 = c_funcs.map_num(mx + diff, width, x_range[0], x_range[1])
                    mapped_y1 = c_funcs.map_num(my - diff, height, y_range[0], y_range[1])
                    mapped_y2 = c_funcs.map_num(my + diff, height, y_range[0], y_range[1])
                    last_x_range.append(x_range)
                    last_y_range.append(y_range)
                    zoom_counter += 1
                    x_range = [mapped_x1, mapped_x2]
                    y_range = [mapped_y1, mapped_y2]
                    flag = 1
                if pygame.mouse.get_pressed(3)[2]:
                    if zoom_counter != 1:
                        x_range = last_x_range.pop(-1)
                        y_range = last_y_range.pop(-1)
                        zoom_counter = max(zoom_counter - 1, 1)
                        flag = 1
                max_iterations = zoom_counter * consts['MAX_ITERATIONS']

        if flag:  # draw the picture
            # start = time.time()
            x = 0
            while x < width:
                mapped_x = c_funcs.map_num(x, width, x_range[0], x_range[1])
                y = 0
                while y < height:
                    mapped_y = c_funcs.map_num(y, height, y_range[0], y_range[1])

                    try:
                        Smoothed_iters = data[(mapped_x, mapped_y)]

                    except KeyError:
                        Smoothed_iters = c_funcs.does_converge(mapped_x, mapped_y, max_iterations)

                        data[(mapped_x, mapped_y)] = Smoothed_iters
                    if Smoothed_iters != -1:  # if not black

                        # Color_mod_17 - the index of the color in the color array
                        Color_mod_17 = Smoothed_iters % len1

                        # how close and how far to the next color - 0 to 1
                        how_close = Color_mod_17 % 1
                        how_far = 1 - how_close

                        # most efficient way to round Smoothed_iters to an integer
                        Smoothed_iters = math.floor(Color_mod_17)
                        # most efficient - currently known to me to round Smoothed_iters + 1 to be in range
                        ColorPlus1_Mod_len = (Smoothed_iters + 1) % len1

                        Color = (how_far * colors[Smoothed_iters][0] + how_close * colors[ColorPlus1_Mod_len][0],
                                 how_far * colors[Smoothed_iters][1] + how_close * colors[ColorPlus1_Mod_len][1],
                                 how_far * colors[Smoothed_iters][2] + how_close * colors[ColorPlus1_Mod_len][2])
                    else:
                        Color = BLACK
                    screen_matrix[x, y] = Color

                    y += 1
                x += 1
            # print(time.time() - start)
            flag = 0
    return data


datadict = {}
# with open('C:\\Users\\amitd\\source\\repos\\Project21\\Project21\\data.txt','r') as data:
# with open('data.txt', 'r') as data:
#    for line in data.readlines():
#        x, y, val = line.strip().replace('\x00', '').split(',')
#        valD = int(val)
#        xD = double(x)
#        yD = double(y)
#        datadict[(xD, yD)] = valD
#
# print(datadict)


WIN = pygame.display.set_mode((consts['WIDTH'], consts['HEIGHT']))
pygame.display.set_caption('The Mandelbrot set - A Glimpse Into Infinity')
main(consts, WIN, datadict)
