"""Implemented using the Rotating Calipers Algorithm
https://en.wikipedia.org/wiki/Rotating_calipers"""

import numpy as np

def dist(p1, p2):
	
	x0 = p1[0] - p2[0]
	y0 = p1[1] - p2[1]
	return x0 * x0 + y0 * y0

def rc_pts(args, data, init_x, init_y):

    # Compute edges (x2-x1,y2-y1)
    edges = np.zeros( (len(data['cords'])-1,2) ) # empty 2 column np.array
    for i in range( len(edges) ):
        edge_x = data['cords'][i+1,0] - data['cords'][i,0]
        edge_y = data['cords'][i+1,1] - data['cords'][i,1]
        edges[i] = [edge_x,edge_y]
    #print "Edges: \n", edges

    # Calculate edge angles   atan2(y/x)
    edge_angles = np.zeros( (len(edges)) ) # empty 1 column np.array
    for i in range( len(edge_angles) ):
        edge_angles[i] = math.atan2( edges[i,1], edges[i,0] )
    #print "Edge angles: \n", edge_angles

    # Check for angles in 1st quadrant
    for i in range( len(edge_angles) ):
        edge_angles[i] = abs( edge_angles[i] % (math.pi/2) ) # want strictly positive answers
    #print "Edge angles in 1st Quadrant: \n", edge_angles

    # Remove duplicate angles
    edge_angles = unique(edge_angles)
    #print "Unique edge angles: \n", edge_angles

    # Test each angle to find bounding box with smallest area
    min_bbox = (0, sys.maxint, 0, 0, 0, 0, 0, 0) # rot_angle, area, width, height, min_x, max_x, min_y, max_y
    print("Testing", len(edge_angles), "possible rotations for bounding box... \n")
    for i in range( len(edge_angles) ):

        # Create rotation matrix to shift points to baseline
        # R = [ cos(theta)      , cos(theta-PI/2)
        #       cos(theta+PI/2) , cos(theta)     ]
        R = np.np.array([ [ math.cos(edge_angles[i]), math.cos(edge_angles[i]-(math.pi/2)) ], [ math.cos(edge_angles[i]+(math.pi/2)), math.cos(edge_angles[i]) ] ])
        #print "Rotation matrix for ", edge_angles[i], " is \n", R

        # Apply this rotation to convex hull points
        rot_points = np.dot(R, transpose(data['cords']) ) # 2x2 * 2xn
        #print "Rotated hull points are \n", rot_points

        # Find min/max x,y points
        min_x = np.nanmin(rot_points[0], axis=0)
        max_x = np.nanmax(rot_points[0], axis=0)
        min_y = np.nanmin(rot_points[1], axis=0)
        max_y = np.nanmax(rot_points[1], axis=0)
        #print "Min x:", min_x, " Max x: ", max_x, "   Min y:", min_y, " Max y: ", max_y

        # Calculate height/width/area of this bounding rectangle
        width = max_x - min_x
        height = max_y - min_y
        area = width*height
        #print "Potential bounding box ", i, ":  width: ", width, " height: ", height, "  area: ", area 

        # Store the smallest rect found first (a simple convex hull might have 2 answers with same area)
        if (area < min_bbox[1]):
            min_bbox = ( edge_angles[i], area, width, height, min_x, max_x, min_y, max_y )
        # Bypass, return the last found rect
        #min_bbox = ( edge_angles[i], area, width, height, min_x, max_x, min_y, max_y )

    # Re-create rotation matrix for smallest rect
    angle = min_bbox[0]   
    R = np.array([ [ math.cos(angle), math.cos(angle-(math.pi/2)) ], [ math.cos(angle+(math.pi/2)), math.cos(angle) ] ])
    #print "Projection matrix: \n", R

    # Project convex hull points onto rotated frame
    proj_points = np.dot(R, transpose(data['cords']) ) # 2x2 * 2xn
    #print "Project hull points are \n", proj_points

    # min/max x,y points are against baseline
    min_x = min_bbox[4]
    max_x = min_bbox[5]
    min_y = min_bbox[6]
    max_y = min_bbox[7]

    # Calculate center point and project onto rotated frame
    center_x = (min_x + max_x)/2
    center_y = (min_y + max_y)/2
    center_point = np.dot( [ center_x, center_y ], R )
    #print "Bounding box center point: \n", center_point

    # Calculate corner points and project onto rotated frame
    corner_points = np.zeros( (4,2) ) # empty 2 column np.np.array
    corner_points[0] = np.dot( [ max_x, min_y ], R )
    corner_points[1] = np.dot( [ min_x, min_y ], R )
    corner_points[2] = np.dot( [ min_x, max_y ], R )
    corner_points[3] = np.dot( [ max_x, max_y ], R )
    #print "Bounding box corner points: \n", corner_points

    #print "Angle of rotation: ", angle, "rad  ", angle * (180/math.pi), "deg"

    return (corner_points[0], corner_points[1])

def brute_pts(args, data, init_x, init_y, dmax=0, brute_x=None, brute_y=None, max_id=0):

    neighbours = []
    for row_idx, (x, y) in enumerate(zip(data['coords']['xn'], data['coords']['yn'])):

        if init_x != x and init_y != y:
            d = dist([init_x, init_y], [x, y])
            if d >= dmax:
                dmax = d
                max_id = row_idx
                brute_x, brute_y = x, y


    brute_x_normal, brute_y_normal = data['normals']['xn'][max_id], data['normals']['yn'][max_id]

    # if args.k+1 == 1:
    #     neighbours.append((init_x, init_y))
    # else:
    #     for idx, (x, y) in enumerate(zip(data['coords']['xn'], data['coords']['yn'])):
    #         if max_id-(args.k/2-1) <= idx <= max_id+(args.k/2):
    #             neighbours.append((x,y))

    brute_data = {'bx': brute_x, 'by':brute_y, 'bxn':brute_x_normal, 'byn':brute_y_normal, 'id':max_id}

    return brute_data