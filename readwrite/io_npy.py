import os
import numpy as np

def write_npy(args, datadict, in_write, keys=[], dir = './outputs/', save_name='furthest_body_'):

	if in_write:
		dir = './inputs/'

	if not os.path.exists(dir):
	    os.makedirs(dir)
	elif not os.path.exists(dir+args.coords_dir):
		os.makedirs(dir+args.coords_dir)

	for key,val in datadict.items():
		if key in keys or len(keys)==0:
			if len(datadict) == 2:
				if key == 'normals':
					fname = os.path.join(dir,save_name+'normals')
					np.save(fname, val)
					np.savetxt(fname+'.txt', val)
				else:
					fname = os.path.join(dir,save_name+'points')
					np.save(fname, val)
					np.savetxt(fname+'.txt', val)
				
			else:
				fname = os.path.join(dir+args.coords_dir,key)
				np.save(fname, val)
				np.savetxt(fname+'.txt', val)

def read_npy(dir, keys, in_write):
	assert os.path.exists(dir)

	if len(keys)==0:
		keys = inspect_npy(dir)

	datadict = {}	
	for key in keys:
		if in_write == False:
			fname = os.path.join(dir,key+'.npy')
		else:
			fname = dir
		if os.path.exists(fname):
			datadict[key] = np.load(fname)
	return datadict

def inspect_npy(dir):
	from glob import glob
	dir = os.path.join(dir,'*')
	return [os.path.split(f)[-1].split('.')[0] for f in glob(dir)]