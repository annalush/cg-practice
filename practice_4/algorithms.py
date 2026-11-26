from collections import deque
import heapq
from settings import NORMAL_COST, WEIGHTED_COST


def heuristic(a, b):
    """Manhattan distance для 4 направлений"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(came_from, start, goal):
    """Восстанавливает путь от start до goal"""
    path = []
    current = goal
    while current != start:
        path.append(current)
        if current not in came_from:
            return []
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path


def bfs_steps(grid, start, goal):
    """BFS — поиск в ширину"""
    queue = deque([start])
    visited = {start}
    came_from = {}
    
    yield {'type': 'visit', 'node': start, 'state': 'OPEN'}
    
    while queue:
        current = queue.popleft()
        
        yield {'type': 'visit', 'node': current, 'state': 'CLOSED'}
        
        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            for node in path:
                yield {'type': 'path', 'node': node}
            yield {'type': 'found', 'path': path}
            return
        
        for neighbor in grid.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)
                yield {'type': 'visit', 'node': neighbor, 'state': 'OPEN'}
    
    yield {'type': 'not_found'}


def dijkstra_steps(grid, start, goal):
    """Dijkstra — поиск кратчайшего пути с учётом весов"""
    frontier = [(0, start)]
    cost_so_far = {start: 0}
    came_from = {}
    
    yield {'type': 'visit', 'node': start, 'state': 'OPEN', 'cost': 0}
    
    while frontier:
        current_cost, current = heapq.heappop(frontier)
        
        yield {'type': 'visit', 'node': current, 'state': 'CLOSED', 'cost': current_cost}
        
        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            for node in path:
                yield {'type': 'path', 'node': node}
            yield {'type': 'found', 'path': path, 'cost': current_cost}
            return
        
        for neighbor in grid.get_neighbors(*current):
            new_cost = cost_so_far[current] + grid.get_cost(*neighbor)
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(frontier, (new_cost, neighbor))
                yield {'type': 'visit', 'node': neighbor, 'state': 'OPEN', 'cost': new_cost}
    
    yield {'type': 'not_found'}


def a_star_steps(grid, start, goal):
    """A* — поиск с эвристикой"""
    frontier = [(0, start)]
    cost_so_far = {start: 0}
    came_from = {}
    
    yield {'type': 'visit', 'node': start, 'state': 'OPEN', 'cost': 0}
    
    while frontier:
        current_cost, current = heapq.heappop(frontier)
        
        yield {'type': 'visit', 'node': current, 'state': 'CLOSED', 'cost': current_cost}
        
        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            for node in path:
                yield {'type': 'path', 'node': node}
            yield {'type': 'found', 'path': path, 'cost': current_cost}
            return
        
        for neighbor in grid.get_neighbors(*current):
            new_cost = cost_so_far[current] + grid.get_cost(*neighbor)
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                priority = new_cost + heuristic(neighbor, goal)
                heapq.heappush(frontier, (priority, neighbor))
                yield {'type': 'visit', 'node': neighbor, 'state': 'OPEN', 'cost': new_cost, 'priority': priority}
    
    yield {'type': 'not_found'}