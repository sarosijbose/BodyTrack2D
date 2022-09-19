from sklearn.decomposition import PCA
from pykdtree.kdtree import KDTree
from multiprocessing import Pool
from time import time
from readwrite import io_npy
import numpy as np
import sys
import argparse


def compute_normal(neighbours):
	pca = PCA(n_components=2)
	pca.fit(neighbours)
	plane_normal = pca.components_[-1] # this is a normalized normal
	# make all normals point upwards:
	if plane_normal[-1] < 0:
		plane_normal *= -1
	return plane_normal

def get_normals(args, init_x, init_y, max_id=0):
	if args.infile.endswith('ply'):
		from readwrite import io_ply
		datadict = io_ply.read_ply(args.infile)
	elif args.infile.endswith('las'):
		from readwrite import io_las
		datadict = io_las.read_las(args.infile)
	elif args.infile.endswith('npy'):
		datadict = io_npy.read_npy(args.infile, ['coords'], in_write=True)
	
	kd_tree = KDTree( datadict['coords'] )
	neighbours = kd_tree.query( datadict['coords'], args.k+1)[1]
	neighbours = datadict['coords'][neighbours]
	
	p = Pool()
	t1 = time()
	normals = p.map(compute_normal, neighbours)
	t2 = time()
	print("finished normal computation in {} s".format(t2-t1))

	for idx, (x, y) in enumerate(datadict['coords']):
		if x == init_x and y == init_y:
			max_id = idx
			break
	
	datadict['coords'] = np.array([[init_x, init_y]])
	datadict['normals'] = np.array(normals[max_id], dtype=np.float32)

	io_npy.write_npy(args, datadict, in_write=False)