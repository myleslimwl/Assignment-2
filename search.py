#---------------------Function to visit all treasures-----------------------#
def find_best_treasure_path(start_pos, treasures):
    best_path = []
    min_total_cost = float('inf')

    for order in permutations(treasures):
        current_pos = start_pos
        total_path = []
        total_cost = 0
        valid = True

        for target in order:
            path_segment, cost = ucs(current_pos, target)
            if not path_segment:
                valid = False
                break
            total_path += path_segment
            total_cost += cost
            current_pos = target

        if valid and total_cost < min_total_cost:
            min_total_cost = total_cost
            best_path = total_path

    return best_path

#-------------------------------Uniform-Cost Search Algorithm----------------------------#
def ucs(start, goal):
    #(cost, position)
    open_set = [(0, start)]
    came_from = {}
    cost_so_far = {start: 0}

    while open_set:
        current_cost, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path, cost_so_far[goal]
        
        for neighbor in get_neighbors(*current):
            tile = grid[neighbor[0]][neighbor[1]]
            #Base minmax cost
            step_cost = 1.0

            if tile == 'X1' or tile == 'X2':
                step_cost *= 2
            elif tile == 'R1' or tile == 'R2':
                step_cost *= 0.5

            new_cost = current_cost + step_cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(open_set, (new_cost, neighbor))

    return [], float('inf')
