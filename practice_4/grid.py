from settings import NORMAL_COST, WEIGHTED_COST


class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.base = [['EMPTY' for _ in range(cols)] for _ in range(rows)]
        self.search = [[None for _ in range(cols)] for _ in range(rows)]
        self.start = None
        self.goal = None
    
    def get_cost(self, row, col):
        if self.base[row][col] == 'WEIGHTED':
            return WEIGHTED_COST
        return NORMAL_COST
    
    def is_passable(self, row, col):
        return self.base[row][col] != 'WALL'
    
    def get_neighbors(self, row, col):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.is_passable(nr, nc):
                    neighbors.append((nr, nc))
        return neighbors
    
    def reset_search(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.search[r][c] = None
    
    def clear(self):
        self.base = [['EMPTY' for _ in range(self.cols)] for _ in range(self.rows)]
        self.search = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None
        self.goal = None