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
c_funcs.does_converge.argtypes = [c_double, c_double, c_int, c_int, c_int]
c_funcs.does_converge.restype = c_double
c_funcs.map_num.restype = c_double

pygame.init()
consts = {
    "WIDTH": 500,
    'HEIGHT': 500,
    'MAX_ITERATIONS': 1000}

""""
replaced by C- function
def is_converge(x, y, iterations):
    i = 0
    # first gen is x + iy
    z_n_imaginary = y
    z_n_real = x
    while i < iterations:
        # imaginary of next gen = old gen squared + y - imaginary part
        new_z_n_imaginary = 2 * z_n_real * z_n_imaginary + y
        # real of next gen = old gen squared + x - real part
        new_z_n_real = z_n_real * z_n_real - z_n_imaginary * z_n_imaginary + x
        z_n_real = new_z_n_real
        z_n_imaginary = new_z_n_imaginary
        if (z_n_real * z_n_real + z_n_imaginary * 2) > 4:
            # diverges
            color = map2(i, 0, iterations, 10, 250)
            # return color based on iterations
            return color, color, color
        i += 1
    # converge
    return 0, 0, 0
map2(double value, double min, double max, double wanted_min, double wanted_max)
"""


# def c_funcs_map_num(value, Max, wanted_min, wanted_max):
#    x = c_funcs.map_num(value, Max, wanted_min, wanted_max)
#    return x


def draw_screen(win, screen_matrix):
    pygame.pixelcopy.array_to_surface(win, screen_matrix)


def main(constants, win, data):

    colors = [(0, 0, 0),
              (66, 30, 15),
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
              (106, 52, 3)]

    # better names for constants
    width = constants['WIDTH']
    height = constants['HEIGHT']
    max_iterations = constants['MAX_ITERATIONS']
    height_range = range(height)
    width_range = range(width)
    # starting ranges for the Mandelbrot
    x_range = [-2, 2]
    y_range = [-2, 2]
    last_x_range = []
    last_y_range = []

    # display calculations
    screen_matrix = np.zeros((height, width, 3), dtype=np.uint8)
    flag = 1
    # zoom variables
    zoom_counter = 1
    diff = 30
    diff_width = 2 * diff

    # Coloring the set
    max_color = 250
    min_color = 0

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


            start = time()
            for x in width_range:
                mapped_x = c_funcs.map_num(x, width, x_range[0], x_range[1])
                for y in height_range:
                    mapped_y = c_funcs.map_num(y, height, y_range[0], y_range[1])

                    # try:
                    #     iters_before_bail = data[(mapped_x, mapped_y)]
                    #
                    # except KeyError:

                    # how many iterations did it take to bail out is Smoothed iters
                    iters_before_bail = c_funcs.does_converge(mapped_x, mapped_y, max_iterations, min_color, max_color)
                        # data[(mapped_x, mapped_y)] = iters_before_bail

                    # color_index - the index of the color in the color array
                    color_index = iters_before_bail % 17
                    next_color_index = (iters_before_bail + 1) % 17

                    # how close and how far to the next color - 0 to 1
                    how_close = color_index % 1
                    how_far = 1 - how_close

                    next_color = colors[math.floor(next_color_index)]
                    this_color = colors[math.floor(color_index)]

                    Color = (how_far * this_color[0] + how_close * next_color[0],
                             how_far * this_color[1] + how_close * next_color[1],
                             how_far * this_color[2] + how_close * next_color[2])
                    screen_matrix[x, y] = Color

            print(time() - start)
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