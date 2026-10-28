import pygame
import sys
import traceback
from grid import Grid
from algorithms import bfs_steps, dijkstra_steps, a_star_steps
from visualizer import Visualizer
from settings import *


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pathfinding Visualizer")
        self.clock = pygame.time.Clock()
        
        self.grid = Grid(GRID_ROWS, GRID_COLS)
        self.visualizer = Visualizer(self.screen, self.grid)
        
        self.running = True
        self.algorithm = 1
        self.state = 'IDLE'
        
        self.generator = None
        self.current_step = None
        
        self.stats = {
            'Algorithm': 'BFS',
            'Visited': 0,
            'Path length': 0,
            'Path cost': 0,
            'Steps': 0,
            'Status': 'Idle'
        }
        
        self.step_timer = 0.0
        self.step_interval = 1.0 / STEPS_PER_SECOND
        
        self.mouse_dragging = False
        self.mouse_button = 0
        self.modifiers = {'s': False, 'g': False, 'w': False}
        
        # Убедимся, что START и GOAL в пределах сетки
        start_row, start_col = 5, 5
        goal_row, goal_col = 20, min(35, GRID_COLS - 1)
        
        self.grid.base[start_row][start_col] = 'START'
        self.grid.start = (start_row, start_col)
        self.grid.base[goal_row][goal_col] = 'GOAL'
        self.grid.goal = (goal_row, goal_col)
        
        self.error_message = None
    
    def get_cell_from_mouse(self, pos):
        x, y = pos
        col = (x - self.visualizer.grid_offset_x) // self.visualizer.cell_size
        row = (y - self.visualizer.grid_offset_y) // self.visualizer.cell_size
        
        if 0 <= row < self.grid.rows and 0 <= col < self.grid.cols:
            return row, col
        return None
    
    def handle_mouse(self, pos, button, modifiers):
        cell = self.get_cell_from_mouse(pos)
        if cell is None:
            return
        
        row, col = cell
        
        if button == 1:
            if modifiers['s']:
                if self.grid.base[row][col] != 'GOAL':
                    if self.grid.start:
                        old_row, old_col = self.grid.start
                        self.grid.base[old_row][old_col] = 'EMPTY'
                    self.grid.base[row][col] = 'START'
                    self.grid.start = (row, col)
            elif modifiers['g']:
                if self.grid.base[row][col] != 'START':
                    if self.grid.goal:
                        old_row, old_col = self.grid.goal
                        self.grid.base[old_row][old_col] = 'EMPTY'
                    self.grid.base[row][col] = 'GOAL'
                    self.grid.goal = (row, col)
            elif modifiers['w']:
                if self.grid.base[row][col] not in ('START', 'GOAL'):
                    self.grid.base[row][col] = 'WEIGHTED'
            else:
                if self.grid.base[row][col] not in ('START', 'GOAL'):
                    self.grid.base[row][col] = 'WALL'
        
        elif button == 3:
            if self.grid.base[row][col] not in ('START', 'GOAL'):
                self.grid.base[row][col] = 'EMPTY'
    
    def start_algorithm(self):
        if self.state not in ('IDLE', 'PAUSED'):
            return
        
        if not self.grid.start or not self.grid.goal:
            self.stats['Status'] = 'Set START and GOAL'
            return
        
        try:
            self.grid.reset_search()
            self.stats['Visited'] = 0
            self.stats['Path length'] = 0
            self.stats['Path cost'] = 0
            self.stats['Steps'] = 0
            
            if self.algorithm == 1:
                self.generator = bfs_steps(self.grid, self.grid.start, self.grid.goal)
                self.stats['Algorithm'] = 'BFS'
            elif self.algorithm == 2:
                self.generator = dijkstra_steps(self.grid, self.grid.start, self.grid.goal)
                self.stats['Algorithm'] = 'Dijkstra'
            elif self.algorithm == 3:
                self.generator = a_star_steps(self.grid, self.grid.start, self.grid.goal)
                self.stats['Algorithm'] = 'A*'
            
            self.state = 'RUNNING'
            self.stats['Status'] = 'Searching'
            self.error_message = None
            
        except Exception as e:
            self.error_message = f"Error starting: {e}"
            print(f"ERROR in start_algorithm: {e}")
            traceback.print_exc()
    
    def next_step(self):
        if self.generator is None:
            return
        
        try:
            self.current_step = next(self.generator)
            self.stats['Steps'] += 1
            
            step_type = self.current_step.get('type')
            
            if step_type == 'visit':
                self.stats['Visited'] += 1
                node = self.current_step['node']
                state = self.current_step['state']
                self.grid.search[node[0]][node[1]] = state
            
            elif step_type == 'path':
                node = self.current_step['node']
                self.grid.search[node[0]][node[1]] = 'PATH'
                self.stats['Path length'] += 1
            
            elif step_type == 'found':
                path = self.current_step.get('path', [])
                self.stats['Path length'] = len(path)
                self.stats['Path cost'] = self.current_step.get('cost', 0)
                self.stats['Status'] = 'Found'
                self.state = 'FINISHED'
            
            elif step_type == 'not_found':
                self.stats['Status'] = 'Not found'
                self.state = 'FINISHED'
        
        except StopIteration:
            self.state = 'FINISHED'
            self.stats['Status'] = 'Finished'
        except Exception as e:
            self.error_message = f"Error: {e}"
            print(f"ERROR in next_step: {e}")
            traceback.print_exc()
            self.state = 'FINISHED'
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_1:
                    self.algorithm = 1
                    self.state = 'IDLE'
                    self.grid.reset_search()
                    self.stats['Algorithm'] = 'BFS'
                    self.stats['Status'] = 'Idle'
                    self.error_message = None
                
                elif event.key == pygame.K_2:
                    self.algorithm = 2
                    self.state = 'IDLE'
                    self.grid.reset_search()
                    self.stats['Algorithm'] = 'Dijkstra'
                    self.stats['Status'] = 'Idle'
                    self.error_message = None
                
                elif event.key == pygame.K_3:
                    self.algorithm = 3
                    self.state = 'IDLE'
                    self.grid.reset_search()
                    self.stats['Algorithm'] = 'A*'
                    self.stats['Status'] = 'Idle'
                    self.error_message = None
                
                elif event.key == pygame.K_SPACE:
                    if self.state == 'IDLE':
                        self.start_algorithm()
                    elif self.state == 'RUNNING':
                        self.state = 'PAUSED'
                        self.stats['Status'] = 'Paused'
                    elif self.state == 'PAUSED':
                        self.state = 'RUNNING'
                        self.stats['Status'] = 'Searching'
                
                elif event.key == pygame.K_n:
                    if self.state in ('RUNNING', 'PAUSED'):
                        self.next_step()
                
                elif event.key == pygame.K_r:
                    self.grid.reset_search()
                    self.state = 'IDLE'
                    self.stats['Status'] = 'Idle'
                    self.stats['Visited'] = 0
                    self.stats['Path length'] = 0
                    self.stats['Path cost'] = 0
                    self.stats['Steps'] = 0
                    self.error_message = None
                
                elif event.key == pygame.K_c:
                    self.grid.clear()
                    self.state = 'IDLE'
                    s_row, s_col = 5, 5
                    g_row, g_col = 20, min(35, GRID_COLS - 1)
                    self.grid.base[s_row][s_col] = 'START'
                    self.grid.start = (s_row, s_col)
                    self.grid.base[g_row][g_col] = 'GOAL'
                    self.grid.goal = (g_row, g_col)
                    self.stats['Status'] = 'Idle'
                    self.error_message = None
                
                elif event.key == pygame.K_UP:
                    self.step_interval = max(0.01, self.step_interval - 0.02)
                
                elif event.key == pygame.K_DOWN:
                    self.step_interval = min(1.0, self.step_interval + 0.02)
                
                elif event.key == pygame.K_s:
                    self.modifiers['s'] = True
                elif event.key == pygame.K_g:
                    self.modifiers['g'] = True
                elif event.key == pygame.K_w:
                    self.modifiers['w'] = True
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_s:
                    self.modifiers['s'] = False
                elif event.key == pygame.K_g:
                    self.modifiers['g'] = False
                elif event.key == pygame.K_w:
                    self.modifiers['w'] = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 3):
                    self.mouse_dragging = True
                    self.mouse_button = event.button
                    self.handle_mouse(event.pos, event.button, self.modifiers)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_dragging:
                    self.handle_mouse(event.pos, self.mouse_button, self.modifiers)
    
    def update(self, dt):
        if self.state == 'RUNNING':
            self.step_timer += dt
            if self.step_timer >= self.step_interval:
                self.step_timer = 0.0
                self.next_step()
    
    def draw(self):
        self.visualizer.draw_background()
        self.visualizer.draw_grid()
        
        algorithm_name = ALGORITHM_NAMES.get(self.algorithm, 'Unknown')
        self.visualizer.draw_panel(algorithm_name, self.state, self.stats)
        
        # Показываем ошибку на экране, если она есть
        if self.error_message:
            error_font = pygame.font.Font(None, 24)
            error_text = error_font.render(self.error_message, True, (200, 50, 50))
            self.screen.blit(error_text, (60, WINDOW_HEIGHT - 30))
        
        pygame.display.flip()
    
    def run(self):
        try:
            while self.running:
                dt = self.clock.tick(FPS) / 1000.0
                
                self.handle_events()
                self.update(dt)
                self.draw()
        
        except Exception as e:
            print(f"FATAL ERROR: {e}")
            traceback.print_exc()
            input("Press Enter to exit...")
        finally:
            pygame.quit()
            sys.exit()


def main():
    app = App()
    app.run()


if __name__ == '__main__':
    main()