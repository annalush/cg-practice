import pygame
from settings import *


class Visualizer:
    def __init__(self, screen, grid):
        self.screen = screen
        self.grid = grid
        self.font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 28)
        self.header_font = pygame.font.Font(None, 20)
        
        # Сетка слева, панель справа
        grid_area_width = WINDOW_WIDTH - PANEL_WIDTH - 40
        grid_area_height = WINDOW_HEIGHT - 40
        
        self.cell_size = min(
            grid_area_width // grid.cols,
            grid_area_height // grid.rows
        )
        
        self.grid_offset_x = 20
        self.grid_offset_y = 20
        
        self.panel_x = WINDOW_WIDTH - PANEL_WIDTH + 10
        self.panel_y = 20
    
    def draw_background(self):
        self.screen.fill(COLOR_BG)
        
        pygame.draw.line(
            self.screen, COLOR_GRID_BORDER,
            (self.panel_x - 5, 10),
            (self.panel_x - 5, WINDOW_HEIGHT - 10),
            2
        )
    
    def draw_grid(self):
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                x = self.grid_offset_x + col * self.cell_size
                y = self.grid_offset_y + row * self.cell_size
                
                base_state = self.grid.base[row][col]
                search_state = self.grid.search[row][col]
                
                color = self._get_cell_color(base_state, search_state)
                
                pygame.draw.rect(
                    self.screen, color,
                    (x, y, self.cell_size, self.cell_size)
                )
                pygame.draw.rect(
                    self.screen, COLOR_GRID_BORDER,
                    (x, y, self.cell_size, self.cell_size), 1
                )
                
                if base_state == 'START':
                    text = self.font.render('S', True, (255, 255, 255))
                    self.screen.blit(text, (x + 4, y + 2))
                elif base_state == 'GOAL':
                    text = self.font.render('G', True, (255, 255, 255))
                    self.screen.blit(text, (x + 4, y + 2))
    
    def _get_cell_color(self, base_state, search_state):
        if search_state == 'PATH':
            return COLOR_PATH
        if search_state == 'CLOSED':
            return COLOR_CLOSED
        if search_state == 'OPEN':
            return COLOR_OPEN
        
        if base_state == 'WALL':
            return COLOR_WALL
        if base_state == 'START':
            return COLOR_START
        if base_state == 'GOAL':
            return COLOR_GOAL
        if base_state == 'WEIGHTED':
            return COLOR_WEIGHTED
        
        return COLOR_EMPTY
    
    def draw_panel(self, algorithm_name, state, stats):
        x = self.panel_x
        y = self.panel_y
        
        title = self.title_font.render(algorithm_name, True, COLOR_TEXT)
        self.screen.blit(title, (x, y))
        y += 35
        
        state_text = self.font.render(f"State: {state}", True, COLOR_TEXT)
        self.screen.blit(state_text, (x, y))
        y += 30
  
        pygame.draw.line(
            self.screen, COLOR_GRID_BORDER,
            (x, y), (x + PANEL_WIDTH - 30, y), 1
        )
        y += 15

        stat_header = self.header_font.render("STATISTICS", True, COLOR_TEXT_LIGHT)
        self.screen.blit(stat_header, (x, y))
        y += 25
        
        for key, value in stats.items():
            text = self.font.render(f"{key}: {value}", True, COLOR_TEXT)
            self.screen.blit(text, (x, y))
            y += 22
        
        y += 15
        
        pygame.draw.line(
            self.screen, COLOR_GRID_BORDER,
            (x, y), (x + PANEL_WIDTH - 30, y), 1
        )
        y += 15
        
        legend_header = self.header_font.render("LEGEND", True, COLOR_TEXT_LIGHT)
        self.screen.blit(legend_header, (x, y))
        y += 25
        
        legend_items = [
            ('Empty', COLOR_EMPTY),
            ('Wall', COLOR_WALL),
            ('Start', COLOR_START),
            ('Goal', COLOR_GOAL),
            ('Weighted', COLOR_WEIGHTED),
            ('Open', COLOR_OPEN),
            ('Closed', COLOR_CLOSED),
            ('Path', COLOR_PATH),
        ]
        
        for name, color in legend_items:
            pygame.draw.rect(self.screen, color, (x, y, 14, 14))
            pygame.draw.rect(self.screen, COLOR_GRID_BORDER, (x, y, 14, 14), 1)
            text = self.small_font.render(name, True, COLOR_TEXT)
            self.screen.blit(text, (x + 20, y))
            y += 20
        
        y += 10

        pygame.draw.line(
            self.screen, COLOR_GRID_BORDER,
            (x, y), (x + PANEL_WIDTH - 30, y), 1
        )
        y += 15
        
        # Подсказки управления
        controls_header = self.header_font.render("CONTROLS", True, COLOR_TEXT_LIGHT)
        self.screen.blit(controls_header, (x, y))
        y += 25
        
        controls = [
            "LMB - Wall",
            "RMB - Clear",
            "S+LMB - Start",
            "G+LMB - Goal",
            "W+LMB - Weighted",
            "1 - BFS",
            "2 - Dijkstra",
            "3 - A*",
            "SPACE - Start/Pause",
            "N - Next step",
            "R - Reset",
            "C - Clear map",
            "Up/Down - Speed",
            "Esc - Exit",
        ]
        
        for control in controls:
            text = self.small_font.render(control, True, COLOR_TEXT_LIGHT)
            self.screen.blit(text, (x, y))
            y += 18