import numpy

# Open the keypoint files and return them as tuples.
def scan_keypoints(args, root='./noisy/'):

    x_cords = []
    y_cords = []
    cords = []
    x_normals = []
    y_normals = []

    if args.shape == 'human':
        file_points = open(root + 'body_points.txt', 'r');
        file_normals = open(root + 'body_normals.txt', 'r');
    elif args.shape == 'giraffe':
        file_points = open(root + f'{args.shape}_points.txt', 'r');
        file_normals = open(root + f'{args.shape}_normals.txt', 'r');
    elif args.shape == 'octopus':
        file_points = open(root + f'{args.shape}_points.txt', 'r');
        file_normals = open(root + f'{args.shape}_normals.txt', 'r');
    elif args.shape == 'statue':
        file_points = open(root + f'{args.shape}_points.txt', 'r');
        file_normals = open(root + f'{args.shape}_normals.txt', 'r');
    else:
        file_points = open(root + f'{args.shape}_points.txt', 'r');
        file_normals = open(root + f'{args.shape}_normals.txt', 'r');

    for i, (coords, normals) in enumerate(zip(file_points, file_normals)):

        if args.downsample:
            if (i+1)%args.ds_rate == 0:
                x_cords.append(int(coords.split(' ')[0]))
                y_cords.append(int(coords.split(' ')[1]))
                cords.append([int(coords.split(' ')[0]), int(coords.split(' ')[1])])
                x_normals.append(float(normals.split(' ')[0]))
                y_normals.append(float(normals.split(' ')[1]))

        else:
            x_cords.append(int(coords.split(' ')[0]))
            y_cords.append(int(coords.split(' ')[1]))
            cords.append([int(coords.split(' ')[0]), int(coords.split(' ')[1])])
            x_normals.append(float(normals.split(' ')[0]))
            y_normals.append(float(normals.split(' ')[1]))
        
    data = {'coords':{'xn':x_cords, 'yn':y_cords}, 'normals':{'xn':x_normals, 'yn':y_normals}, 'cords':cords}

    return data

if __name__ == '__main__':
    scan_keypoints()