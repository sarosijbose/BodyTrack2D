import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from matplotlib.pyplot import figure
from collections import defaultdict

from utils import plot2D, get_dist

class PillConstruct(object):

    def __init__(self, ball_info, ball1_idx, ball2_idx):

        self.ball_info = ball_info
        self.ball1_idx = ball1_idx
        self.ball2_idx = ball2_idx
        self.no_balls = len(ball_info)
        self.ball_list = list(ball_info.items())
        self.ball1_centre = self.ball_list[ball1_idx-1][1]['c']
        self.ball1_radius = self.ball_list[ball1_idx-1][1]['r']
        self.ball2_centre = self.ball_list[ball2_idx-1][1]['c']
        self.ball2_radius = self.ball_list[ball2_idx-1][1]['r']

        self.pill_distance = self.pill_length(ball_info)
   
    def pill_make(self, inf = float('inf'), NaN = float('NaN'), pill = defaultdict(int), skipped_count=0):

        alpha_n = self.ball1_radius*float(self.ball2_centre[0]) - self.ball2_radius*float(self.ball1_centre[0])
        deno = self.ball1_radius - self.ball2_radius
        deno = deno if deno > 0 else -deno
        if deno != 0:

            alpha = alpha_n/deno
            beta_n = self.ball1_radius*float(self.ball2_centre[1]) - self.ball2_radius*float(self.ball1_centre[1])
            beta = beta_n/deno

            m_b = -2*(float(self.ball1_centre[0]) - alpha)*(beta - self.ball1_centre[1])
            a = (self.ball1_centre[0] - alpha)**2 - self.ball1_radius**2
            c = (beta - self.ball1_centre[1])**2 - self.ball1_radius**2
            dis = np.sqrt(m_b**2 - 4*a*c)

            slope1 = (m_b + dis)/2*a
            slope2 = (m_b - dis)/2*a

            tangent1 = [slope1, -1, beta - (slope1*alpha)]
            tangent2 = [slope2, -1, beta - (slope2*alpha)]

        else:

            slope1 = (self.ball2_centre[1] - self.ball1_centre[1])/(self.ball2_centre[0] - self.ball1_centre[0])
            slope2 = slope1

            slope_normal = -(1/slope1)
            normal = [slope_normal, -1, self.ball1_centre[1] - (slope_normal*self.ball1_centre[0])]

            a = 1 + slope_normal**2
            b = 2*slope_normal*(self.ball1_centre[1]-(slope_normal*self.ball1_centre[0]))-2*self.ball1_centre[0]-2*slope_normal*self.ball1_centre[1]
            c = self.ball1_centre[0]**2 - self.ball1_centre[1]**2 + (self.ball1_centre[1]-(slope_normal*self.ball1_centre[0]))**2 + 2*slope_normal*self.ball1_centre[0]*self.ball1_centre[1] - self.ball1_radius**2
            coeff = [a, b, c]

            if inf or NaN in coeff:
                tangent1 = tangent2 = []
                pass
            else:
                roots = np.roots(coeff)

                y1 = slope_normal*float(roots[0]) + self.ball1_centre[1] - slope_normal*self.ball1_centre[0]
                y2 = slope_normal*float(roots[1]) + self.ball1_centre[1] - slope_normal*self.ball1_centre[0]

                tangent1 = [slope1, -1, y1-(slope1*float(roots[0]))]
                tangent2 = [slope2, -1, y2-(slope2*float(roots[1]))]

        pill = {'t1': tangent1, 't2': tangent2, 'ball1': self.ball1_idx, 'ball2': self.ball2_idx}
        
        return pill

    def pill_length(self, ball_info):

        return 100

def project_furthestpt(args, data, tangent1, tangent2, max_dist = 0, t_info = defaultdict(int)):
    
    for row_idx, (x, y) in enumerate(zip(data['coords']['xn'], data['coords']['yn'])):
        
        t1_dist = get_dist(tangent1, [x, y])
        t2_dist = get_dist(tangent2, [x, y])

        if t1_dist != -1 and t2_dist != -1:
            if t1_dist > max_dist or t2_dist > max_dist:
                if t1_dist > t2_dist:
                    max_dist = t1_dist
                    t_info = {'no':0, 'row_idx': row_idx}
                else:
                    max_dist = t2_dist
                    t_info = {'no':1, 'row_idx': row_idx}
        elif t1_dist == -1:
            if t2_dist > max_dist:
                max_dist = t2_dist
                t_info = {'no':1, 'row_idx': row_idx}
        elif t2_dist == -1:
            if t1_dist > max_dist:
                max_dist = t1_dist
                t_info = {'no':0, 'row_idx': row_idx}
        else:
            pass

    return t_info