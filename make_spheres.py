import math
import numpy as np
from pykdtree.kdtree import KDTree

import numba
from readwrite.algebra_numba import norm, dot, equal, compute_radius, cos_angle

class MASB(object):

    def __init__(self, datadict, max_r, k, idx, denoise_absmin=None, denoise_delta=None, 
                    denoise_min=None, detect_planar=None):
        self.D = datadict

        self.pykdtree = KDTree(self.D['coords'])

        self.m, self.n = datadict['coords'].shape
        self.D['ma_coords_in'] = np.empty( (self.m,self.n), dtype=np.float32 )
        self.D['ma_coords_in'][:] = np.nan
        self.D['ma_q_in'] = np.zeros( (self.m), dtype=np.uint32 )
        self.D['ma_q_in'][:] = np.nan_to_num(self.D['ma_q_in'][:])

        self.SuperR = max_r
        self.delta_convergence = 0.001
        self.iteration_limit = 30
        self.k = k
        self.id = idx

    def compute_ball(self):
        inst_centre, inst_radius = self.compute_balls_oneside()

        return inst_centre,  inst_radius

    def compute_balls_oneside(self, flag=True):
        """Balls shrinking algorithm."""

        p, n = self.D['coords'][self.id], self.D['normals'][self.id]
        
        #-- r represents the ball radius found in the current iteration (i.e. of the while loop below)
        r = None
        
        # iterate till a maximal sphere is formed
        #while r == None:
        #-- q will represent the second point that defines a ball together with p and n
        q = None 
        #-- q_i is the index of q
        q_i = None
        #r = None
        #-- r_previous represents the ball radius found in the previous iteration
        r_previous=self.SuperR
        #-- c is the ball's center point in the current iteration
        c = None
        #-- c_previous is the ball's center point in the previous iteration
        c_previous = None
        j = -1
        
        while True:
            # set r to last found radius if this isn't the first iteration
            j+=1

            if j>0:
                r_previous = r

            # compute ball center
            c = p - n*r_previous
            
            # keep track of this for denoising purpose
            q_i_previous = q_i


            ### FINDING NEAREST NEIGHBOR OF c

            # find closest point to c and assign to q

            dists, indices = self.pykdtree.query(np.array([c]), k=self.k)

            try:
                candidate_c = self.D['coords'][indices]
            except IndexError as detail:
                #raise ValueError(detail)
                pass

            q = candidate_c[0][0]
            q_i = indices[0][0]
            
            # What to do if closest point is p itself?
            if equal(q,p):
                # 1) if r_previous==SuperR, apparantly no other points on the halfspace spanned by -n => that's an infinite ball
                if r_previous == self.SuperR:
                    r = r_previous
                    break
                # 2) otherwise just pick the second closest point
                else: 
                    q = candidate_c[0][1]
                    q_i = indices[0][1]

            # compute new candidate radius r
            while flag:
                try:
                    r = compute_radius(p,n,q)
                    flag = False
                except ZeroDivisionError:
                    continue

            ### EXCEPTIONAL CASES

            # if r < 0 closest point was on the wrong side of plane with normal n => start over with SuperRadius on the right side of that plane
            if r < 0: 
                r = self.SuperR
            # if r > SuperR, stop now because otherwise in case of planar surface point configuration, we end up in an infinite loop
            elif r > self.SuperR:
                r = self.SuperR
                break

            ### END EXCEPTIONAL CASES

            # # stop iteration if r has converged
            if abs(r_previous - r) < self.delta_convergence:
                break

            # stop iteration if this looks like an infinite loop:
            if j > self.iteration_limit:
                break
        
        if r >= self.SuperR:
            pass
        else:
            self.D['ma_coords_in'][self.id] = c
            self.D['ma_q_in'][self.id] = q_i

        return c, r