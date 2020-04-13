from iso.gfx.map import TileMap
from typing import Callable, Tuple, Dict, List
import math
from collections import defaultdict
Point = Tuple[int, int]

def default_heuristic(map: TileMap, goal: Point) -> Callable:
    # for now just distance
    gx, gy = goal
    def h(start: Point) -> float:
        nonlocal gx, gy
        sx, sy = start
        return abs(gx-sx) + abs(gy-sy)
    return h

def trivial_d(current: Point, neighbor: Point) -> float:
    return 1

def reconstruct_path(came_from: Dict[Point, Point], current: Point):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path

def neighborhood(at: Point) -> List[Point]:
    x, y = at
    return (
        (x-1,y-1), (x, y-1), (x+1, y-1),
        (x-1,y), (x+1,y),
        (x-1,y+1), (x, y+1), (x+1, y+1)
    )
    pass

def a_star(start: Point, goal: Point, 
            h: Callable[[Point], float],
            d: Callable[[Point, Point], float]):
    """ Find path from start to goal. 
        h(x) is a heuristic that estimates cost from x to the goal
        d(x, y) is the cost to go from x to neighbor y
    """
    start = tuple(start); goal = tuple(goal)
    open_set = set([start]) # TODO should be a priority queue or something

    # came_from[x] -> point preceding x on the path
    came_from: Dict[Point, Point] = {}

    # g_score[x] is score of cheapest path known from start to x
    g_score = defaultdict(lambda: math.inf)
    g_score[start] = 0

    # f_score[n] = g_score[n] + h(n)
    # represents best guess of path from start -> n -> goal
    f_score = defaultdict(lambda: math.inf)
    f_score[start] = h(start)

    while open_set:
        current = sorted(open_set, key=lambda x: f_score[x])[0]
        if current == goal:
            return reconstruct_path(came_from, current)

        open_set.remove(current)
        for neighbor in neighborhood(current):
            tentative_g = g_score[current] + d(current, neighbor)
            if tentative_g < g_score[neighbor]:
                # path to neighbor is better
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = g_score[neighbor] + h(neighbor)
                if neighbor not in open_set:
                    open_set.add(neighbor)

    # failure
    return False
    

