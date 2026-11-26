from collections import deque
import heapq
from settings import NORMAL_COST, WEIGHTED_COST


def heuristic(a, b):
    # Складываем разницы строк и столбцов: диагональные шаги недоступны.
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(came_from, start, goal):
    """Восстанавливает путь от start до goal"""
    path = []
    current = goal
    # Идём от цели по сохранённым предкам, затем разворачиваем путь.
    while current != start:
        path.append(current)
        if current not in came_from:
            # Если цепочка предков оборвалась, восстановить путь нельзя.
            return []
        current = came_from[current]
    path.append(start)
    # До этого момента клетки записывались от цели к началу.
    path.reverse()
    return path


def bfs_steps(grid, start, goal):
    """BFS — поиск в ширину"""
    # Очередь обеспечивает обход по возрастанию числа переходов.
    queue = deque([start])
    # visited хранит уже обнаруженные клетки, came_from — их предков.
    visited = {start}
    came_from = {}
    
    yield {'type': 'visit', 'node': start, 'state': 'OPEN'}
    
    while queue:
        # Берём клетку, которая раньше остальных попала в очередь.
        current = queue.popleft()
        
        # CLOSED означает, что клетка извлечена для обработки.
        yield {'type': 'visit', 'node': current, 'state': 'CLOSED'}
        
        if current == goal:
            # После достижения цели отдельно показываем каждую клетку пути.
            path = reconstruct_path(came_from, start, goal)
            for node in path:
                yield {'type': 'path', 'node': node}
            yield {'type': 'found', 'path': path,
                   'cost': sum(grid.get_cost(*node) for node in path[1:])}
            return
        
        for neighbor in grid.get_neighbors(*current):
            if neighbor not in visited:
                # Отмечаем клетку при добавлении, чтобы не поставить её в очередь дважды.
                visited.add(neighbor)
                # Предок понадобится, чтобы восстановить маршрут в конце.
                came_from[neighbor] = current
                queue.append(neighbor)
                yield {'type': 'visit', 'node': neighbor, 'state': 'OPEN'}
    
    # Очередь опустела, а цель так и не встретилась.
    yield {'type': 'not_found'}


def dijkstra_steps(grid, start, goal):
    """Dijkstra — поиск кратчайшего пути с учётом весов"""
    # В куче храним стоимость пути и координаты клетки.
    frontier = [(0, start)]
    # Для каждой клетки сохраняем лучшую известную стоимость пути от начала.
    cost_so_far = {start: 0}
    came_from = {}
    
    yield {'type': 'visit', 'node': start, 'state': 'OPEN', 'cost': 0}
    
    while frontier:
        # В куче могут оставаться устаревшие записи с большей стоимостью.
        current_cost, current = heapq.heappop(frontier)
        # Если позже нашли более дешёвый путь, старую запись пропускаем.
        if current_cost != cost_so_far[current]:
            continue
        
        yield {'type': 'visit', 'node': current, 'state': 'CLOSED', 'cost': current_cost}
        
        if current == goal:
            # Текущая стоимость уже включает цену входа в целевую клетку.
            path = reconstruct_path(came_from, start, goal)
            for node in path:
                yield {'type': 'path', 'node': node}
            yield {'type': 'found', 'path': path, 'cost': current_cost}
            return
        
        for neighbor in grid.get_neighbors(*current):
            # Стоимость перехода определяется клеткой, в которую входим.
            new_cost = cost_so_far[current] + grid.get_cost(*neighbor)
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                # Сохраняем улучшенную стоимость и добавляем новую запись в кучу.
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(frontier, (new_cost, neighbor))
                yield {'type': 'visit', 'node': neighbor, 'state': 'OPEN', 'cost': new_cost}
    
    yield {'type': 'not_found'}


def a_star_steps(grid, start, goal):
    """A* — поиск с эвристикой"""
    # Элементы кучи: оценка полной стоимости, пройденная стоимость и клетка.
    frontier = [(heuristic(start, goal), 0, start)]
    # Эвристика влияет на порядок обхода, но не добавляется к стоимости пути.
    cost_so_far = {start: 0}
    came_from = {}
    
    yield {'type': 'visit', 'node': start, 'state': 'OPEN', 'cost': 0}
    
    while frontier:
        _, current_cost, current = heapq.heappop(frontier)
        if current_cost != cost_so_far[current]:
            continue
        
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
                # Приоритет A*: пройденная стоимость плюс оценка до цели.
                priority = new_cost + heuristic(neighbor, goal)
                heapq.heappush(frontier, (priority, new_cost, neighbor))
                yield {'type': 'visit', 'node': neighbor, 'state': 'OPEN', 'cost': new_cost, 'priority': priority}
    
    yield {'type': 'not_found'}
