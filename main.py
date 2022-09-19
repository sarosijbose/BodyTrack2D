import numpy as np
import argparse
import tqdm
import sys
import random
from collections import defaultdict
from multiprocessing import Pool

from get_pointsets import scan_keypoints
from utils import plot2D, load_dict, save_file, disp_args, check_duplicates
from furthest_pt import brute_pts
from gen_normals import get_normals
from logger import Logging

from make_spheres import MASB
from readwrite import io_npy, io_ply
from readwrite.algebra_numba import compute_radius

from pillconstruct import PillConstruct, project_furthestpt

def pill_decompose(args, ball_info = {}, pill_info = {}, ball_count = 0, pill_count = 0, furthest_ball_id=0):
    
    raw_data = scan_keypoints(args)

    data = check_duplicates(raw_data)
    datadict = load_dict(args, data)

    args.init_point = random.randint(0, len(data))

    print('Starting point->', args.init_point)

    init_x, init_y = data['coords']['xn'][args.init_point], data['coords']['yn'][args.init_point]
    init_xn, init_yn = data['normals']['xn'][args.init_point], data['normals']['yn'][args.init_point]

    if args.init_point == 0:
        p_x, p_y = data['coords']['xn'][args.init_point+1], data['coords']['yn'][args.init_point+1]
        args.init_r = compute_radius(np.array([init_x, init_y]), np.array([init_xn, init_yn]), np.array([p_x, p_y]))

    ma = MASB(datadict, max_r=args.init_r, k=args.k, idx=args.init_point)
    init_centre, init_radius = ma.compute_ball()

    io_npy.write_npy(args, datadict, in_write=False)

    #rc_x, rc_y = rc_pts(args, data, init_x, init_y)
    brute_data = brute_pts(args, data, init_x, init_y)

    ma = MASB(datadict, max_r=args.init_r, k=args.k, idx=brute_data['id'])
    furthest_centre, furthest_radius = ma.compute_ball()

    ball_info = {1:{'c': init_centre, 'r':init_radius}, 2:{'c':furthest_centre, 'r':furthest_radius}}
    ball_count+=2

    io_npy.write_npy(args, datadict, in_write=False)

    print('Starting the pill decomposition process....')
    with Pool(processes=args.workers) as p:
        for idx in range(args.iter):
            bar = 1 if idx == 0 else len(pill_info)
            for pill_idx in tqdm.tqdm(range(bar), position=0, leave=True):

                if idx == 0:
                    pill_make = PillConstruct(ball_info, ball1_idx=1, ball2_idx=2)
                    pill = pill_make.pill_make()
                    pill_info[pill_count+1] = pill
                    pill_count+=1

                    print(pill_info[pill_idx+1]['t1'], pill_info[pill_idx+1]['t2'])

                    furthest_info = project_furthestpt(args, data, pill_info[pill_idx+1]['t1'], pill_info[pill_idx+1]['t2'])

                    print('furthest pt->', furthest_info['row_idx'])
                    inst_ma = MASB(datadict, max_r=args.init_r, k=args.k, idx=furthest_info['row_idx'])
                    centre, radius = inst_ma.compute_ball()
                    ball_count+=1
                    print('(iC, iR)->', centre, radius)

                    if (ball_count) not in ball_info:
                        ball_info[ball_count] = {}
                    
                    ball_info[ball_count]['c'] = centre
                    ball_info[ball_count]['r'] = radius
                else:
                    for ball_no in range(2):
                        #pill_make = PillConstruct(ball_info, ball1_idx=pill_info[pill_idx+1][f'ball{ball_no+1}'], ball2_idx=furthest_ball_id)
                        print('parent ball, sibling ball->', parent_pill[f'ball{ball_no+1}'], furthest_ball_id)
                        pill_make = PillConstruct(ball_info, ball1_idx=parent_pill[f'ball{ball_no+1}'], ball2_idx=furthest_ball_id)
                        pill = pill_make.pill_make()
                        pill_info[pill_count+1] = pill

                        pill_count+=1

                        print(pill_info[pill_idx+1]['t1'], pill_info[pill_idx+1]['t2'])
                        furthest_info = project_furthestpt(args, data, pill_info[pill_idx+ball_no+1]['t1'], pill_info[pill_idx+ball_no+1]['t2'])
                        print('pill id, pill_count->', pill_idx+1, pill_count)

                        print('furthest pt->', furthest_info['row_idx'])
                        inst_ma = MASB(datadict, max_r= args.init_r, k=args.k, idx=furthest_info['row_idx'])
                        centre, radius = inst_ma.compute_ball()
                        ball_count+=1
                        print('(C, R)->', centre, radius)

                        if (ball_count) not in ball_info:
                            ball_info[ball_count] = {}
                        
                        ball_info[ball_count]['c'] = centre
                        ball_info[ball_count]['r'] = radius
            furthest_ball_id = ball_count
            parent_pill = pill_info[pill_count]

    print(f'No. of total balls:{len(ball_info)} and pills:{len(pill_info)}')
    
    if args.downsample:
        plot2D(args, data, ball_info, pill_info, save_name=f'{args.shape}_r{args.init_r}_it{args.iter}_ds{args.ds_rate}.png')
    else:
        plot2D(args, data, ball_info, pill_info, save_name=f'{args.shape}_r{args.init_r}_it{args.iter}.png')

def main():

    parser = argparse.ArgumentParser(description='2D Body Track Algorithm')
    parser.add_argument('--shape',help='Type of object',default='human')
    parser.add_argument('--downsample',type=bool, help='Downsample points or not',default=True)
    parser.add_argument('--ds_rate',type=int, help='Downsampling Rate',default=10, choices=[10,50,100])
    parser.add_argument('--render_normals',type=bool, help='Render Normals',default=False)
    parser.add_argument('--pill_disp',type=bool, help='Render Normals',default=True)
    parser.add_argument('--workers',type=int, default=2)
    parser.add_argument('--coords_dir', default='body_points_output4_it1/')
    parser.add_argument('--outfile', help='Output _npy', default='./inputs/furthest_normals')
    parser.add_argument('--init_r', help='Initial sphere radius', default=500, type=int)
    parser.add_argument('--k', help='Number of neighbours to use', default=2, type=int)
    parser.add_argument('--iter', help='Number of iterations', default=10, type=int)
    parser.add_argument('--log_file', type=str, default='human_3')
    #parser.add_argument('--init_point', help='Initial point index', default=0, type=int)

    args = parser.parse_args()

    args.log_dir = './log/' + args.log_file + f'/{args.log_file}.log'
    sys.stdout = Logging(args, args.log_dir)
    disp_args(args)

    pill_decompose(args)

if __name__ == '__main__':
    main()