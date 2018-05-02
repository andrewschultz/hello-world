get_next = False
rows_got = 0
num = 15

txtdir = { 'l': "<", 'r': ">", 'u': "^", 'd': "v" }

def dirtxt(q):
    dist = int(q[0])
    dir = q[1]
    return txtdir[dir] * dist

def sol_show(y, x):
    while 'f' not in board[y][x]:
        str = "{:d}, {:d} {:s} to ".format(x, y, dirtxt(board[y][x]))
        (y, x) = new_square(y, x)
        str += "{:d}, {:d}".format(x, y)
        print(str)
    exit()

def gots():
    retval = 0
    for y in range(height):
        for x in range(width):
            retval += got_yet[y][x]
    return retval

def new_square(y, x):
    z = board[y][x]
    dist = int(z[0])
    dir = z[1]
    if dir == 'l':
        return (y, x - dist)
    if dir == 'r':
        return (y, x + dist)
    if dir == 'u':
        return (y - dist, x)
    if dir == 'd':
        return (y + dist, x)

def first_unfound(g):
    for y in range(height):
        for x in range(width):
            if not g[y][x]: return (y, x)
    return (-1, -1)

width = 6
height = 7

board = [[''] * width for i in range(height)]
got_yet = [[False] * width for i in range(height)]

fx = -1
fy = -1

with open("m15.txt") as file:
    for line in file:
        if 'PROB' + str(num) in line:
            get_next = True
            continue
        if not get_next: continue
        board[rows_got] = line.lower().strip().split(',')
        print(board[rows_got], len(board[rows_got]))
        for x in range(width):
            if 'f' in board[rows_got][x]:
                if fx > -1:
                    print("Uh-oh, two finishes.", fx, fy, "vs", x, rows_got)
                    exit()
                got_yet[rows_got][x] = True
                fx = x
                fy = rows_got
                last_x = fx
                last_y = fy
        rows_got += 1
        if rows_got == 7: break

so_far = 1;
print(board)

while (gots() < 42):
    (y, x) = first_unfound(got_yet)
    temp_y = y
    temp_x = x
    while not got_yet[y][x]:
        got_yet[y][x] = True
        (y, x) = new_square(y, x)
    if y != last_y or x != last_x: print("Boom! Error", y, x, "should be", last_y, last_x)
    last_y = temp_y
    last_x = temp_x
    if gots() == 42:
        print("We have a soluton!")
        sol_show(y, x)
        exit()
    else:
        print(gots(), "tagged so far.")