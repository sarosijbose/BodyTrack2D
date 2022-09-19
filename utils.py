import numpy as np
import pandas as pd
import math
import os
import tqdm
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from collections import defaultdict

from readwrite import io_npy, io_ply

def disp_args(args):

    print("---CONFIGS---")
    s = "==========================================\n"
    for arg, content in args.__dict__.items():
        s += "{}:{}\n".format(arg, content)
    print(s)

def check_duplicates(data):

    if len(data['coords']['xn']) != len(set(data['coords']['xn'])) and len(data['coords']['yn']) != len(set(data['coords']['yn'])):
        print('Duplicates present in x and y coords')
        x_temp, y_temp = data['coords']['xn'], data['coords']['yn']

        for idx, (x, y) in enumerate(zip(data['coords']['xn'], data['coords']['yn'])):
            for idx2, (x2, y2) in enumerate(zip(data['coords']['xn'][idx+1:], data['coords']['yn'][idx+1:])):
                if x == x2 and y == y2:
                    x_temp.remove(x)
                    y_temp.remove(y)
                    data['normals']['xn'].remove(data['normals']['xn'][idx])
                    data['normals']['yn'].remove(data['normals']['yn'][idx])

        data['coords']['xn'], data['coords']['yn'] = x_temp, y_temp

    return data

def get_dist(line, point):

    if line!= []:
        num = abs(line[0]*point[0]+line[1]*point[1]+line[2])
        deno = np.sqrt(line[0]**2 + line[1]**2)
        return (num/deno)
    else:
        return -1

def plot2D(args, data, ball_info, pill_info, save_name, centre=None, radius=None, plot_path='./plots/'):

    if not os.path.exists(plot_path):
        os.mkdir(plot_path)

    x, y = data['coords']['xn'], data['coords']['yn']
    x, y = pd.Series(x), pd.Series(y)
    
    _, axes = plt.subplots()

    #figure(figsize=(8, 6))
    axes.scatter(x,y)

    if args.render_normals:
        soa = np.empty((len(data['normals']['xn']), 4))
        for x_n, y_n in zip(data['normals']['xn'], data['normals']['yn']):
            ea = np.array([0, 0, x_n, y_n])
            np.append(soa, ea)
        X, Y, U, V = zip(*soa)
        axes.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1)

    if args.pill_disp:

        for idx, (_, value) in tqdm.tqdm(enumerate(pill_info.items())):

            centre1, centre2 = ball_info[value['ball1']]['c'], ball_info[value['ball2']]['c']
            plt.plot(centre1, centre2, 'ro-')
            radius1, radius2 = ball_info[value['ball1']]['r'], ball_info[value['ball2']]['r']
            #axes.scatter(float(centre1[0]) , float(centre1[1]) , s=radius1 ,  facecolors='none', edgecolors='red')
            #axes.scatter(float(centre2[0]) , float(centre2[1]) , s=radius2 ,  facecolors='none', edgecolors='red')

    plt.title(f'Generated 2D {args.shape} Figure')
    plt.savefig(os.path.join(plot_path, save_name))

def load_dict(args, data, load_furthest=False, datadict = defaultdict(int)):

    pts_arr = np.empty((len(data['coords']['xn']), 2))
    normal_arr = np.empty((len(data['normals']['xn']), 2))

    for idx, (x_c, y_c, x_n, y_n) in enumerate(zip(data['coords']['xn'], data['coords']['yn'], data['normals']['xn'], data['normals']['yn'])):
        pts_arr[idx] = [x_c, y_c]
        normal_arr[idx] = [x_n, y_n]

    datadict['coords'] = pts_arr
    datadict['normals'] = normal_arr

    return datadict

def save_file(args, init_x, init_y, neighbours, norm_path='./inputs/furthest_normals.txt'):

    pts_arr = np.empty((args.k+1,2))

    for id, (x, y) in enumerate(neighbours):
        pts_arr[id] = [x, y]
    
    furthest_datadict = {'coords': pts_arr}
    pt_datadict = {'coords': [[init_x, init_y]]}

    return furthest_datadict, pt_datadict

    # if args.render_normals:
    #     length = 0.01
    #     for x0, y0, x_n, y_n in zip(data['coords']['xn'], data['coords']['yn'], data['normals']['xn'], data['normals']['yn']):
    #         dx, dy = -(1/x_n), -(1/y_n)
    #         print(math.hypot(dx, dy))
    #         norm = math.hypot(dx, dy) * 1/length
    #         dx /= norm
    #         dy /= norm
        
    #         axes.plot((x0, x0-dy), (y0, y0+dx))