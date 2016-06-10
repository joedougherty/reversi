def north(position):
    return (position[0]-1, position[1])

def south(position):
    return (position[0]+1, position[1])

def east(position):
    return (position[0], position[1]-1)

def west(position):
    return (position[0], position[1]+1)

def northwest(position):
    return north(west(position))

def southwest(position):
    return south(west(position))

def northeast(position):
    return north(east(position))

def southeast(position):
    return south(east(position))

