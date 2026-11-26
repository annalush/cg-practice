from settings import NORMAL_COST, WEIGHTED_COST


class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # Тип клетки и состояние поиска хранятся независимо.
        self.base = [['EMPTY' for _ in range(cols)] for _ in range(rows)]
        self.search = [[None for _ in range(cols)] for _ in range(rows)]
        self.start = None
        self.goal = None
    
    def get_cost(self, row, col):
        # Стена не рассматривается как сосед; здесь возвращается цена проходимой клетки.
        if self.base[row][col] == 'WEIGHTED':
            return WEIGHTED_COST
        return NORMAL_COST
    
    def is_passable(self, row, col):
        return self.base[row][col] != 'WALL'
    
    def get_neighbors(self, row, col):
        neighbors = []
        # Диагональные переходы не предусмотрены; стены исключаются.
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            # Сначала проверяем границы, затем доступность клетки.
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.is_passable(nr, nc):
                    neighbors.append((nr, nc))
        return neighbors
    
    def reset_search(self):
        # Очищаем только следы поиска, сохраняя препятствия и точки.
        for r in range(self.rows):
            for c in range(self.cols):
                self.search[r][c] = None
    
    def clear(self):
        # Полная очистка удаляет также начальную и конечную точки.
        self.base = [['EMPTY' for _ in range(self.cols)] for _ in range(self.rows)]
        self.search = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None
        self.goal = None
