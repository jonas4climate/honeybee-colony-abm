
class Node:
    """
    A node class for A* Pathfinding
    """

    def __init__(self, route, position=None, f=0, g=0):
        self.route = route + [position]
        self.position = position

        self.f = f
        self.g = g

    def __eq__(self, other):
        return self.position == other.position


WIDTH = 50
HEIGHT = 50
MOORE_NEIGHBOURS = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]


def astar(maze, start, end):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze
    """

    start_node = Node([], start)
    end_0, end_1 = end

    open_list = [start_node]
    closed_set = set()
    seen = set()

    i = 0

    while len(open_list) > 0:
        i += 1

        current_f = open_list[0].f
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_f:
                current_f = item.f
                current_index = index

        current_node = open_list.pop(current_index)
        closed_set.add(current_node.position)

        curr_x, curr_y = current_node.position

        g = current_node.g + 1

        for new_position in MOORE_NEIGHBOURS:

            node_position = (curr_x + new_position[0], curr_y + new_position[1])

            if node_position == end:
                return current_node.route + [end]

            if node_position in closed_set:
                continue

            n0, n1 = node_position

            if 0 <= n0 < 50 and 0 <= n1 < 50:
                if maze[n0][n1] == 0:

                    h = ((n0 - end_0) ** 2) + ((n1 - end_1) ** 2)
                    f = g + h

                    if node_position not in seen:
                        seen.add(node_position)
                        open_list.append(Node(current_node.route, node_position, f, g))
