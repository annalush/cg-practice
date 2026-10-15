import pygame
import sys
from algorithms import generate_array, bubble_sort_steps, selection_sort_steps, binary_search_steps
from visualizer import Visualizer
from settings import *


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Algorithm Visualizer")
        self.clock = pygame.time.Clock()
        self.visualizer = Visualizer(self.screen)

        self.running = True
        self.algorithm = 1
        self.state = "IDLE"
        self.values = generate_array()
        self.generator = None
        self.current_step = None

        self.stats = {
            "Comparisons": 0,
            "Swaps": 0,
            "Pass": 0,
            "Steps": 0,
        }

        self.step_timer = 0.0
        self.step_interval = 1.0 / STEPS_PER_SECOND

        self.target = None
        self.target_input = ""
        self.input_mode = False

        self.result_message = None

    def reset_state(self):
        self.state = "IDLE"
        self.generator = None
        self.current_step = None
        self.stats = {
            "Comparisons": 0,
            "Swaps": 0,
            "Pass": 0,
            "Steps": 0,
        }
        self.step_timer = 0.0
        self.result_message = None

    def generate_new_array(self):
        if self.state not in ("IDLE", "FINISHED"):
            return
        self.values = generate_array()
        self.reset_state()

    def start_algorithm(self):
        if self.state not in ("IDLE", "PAUSED"):
            return

        if self.algorithm == 1:
            self.generator = bubble_sort_steps(self.values)
        elif self.algorithm == 2:
            self.generator = selection_sort_steps(self.values)
        elif self.algorithm == 3:
            if self.target is None:
                self.result_message = "Set target first (press T)"
                return
            self.values = sorted(self.values)
            self.generator = binary_search_steps(self.values, self.target)

        self.state = "RUNNING"

    def next_step(self):
        if self.generator is None:
            return

        try:
            self.current_step = next(self.generator)
            self.stats["Steps"] += 1

            step_type = self.current_step.get("type")

            if step_type == "compare":
                self.stats["Comparisons"] += 1
            elif step_type == "swap":
                self.stats["Swaps"] += 1
            elif step_type == "pass_end":
                self.stats["Pass"] += 1
            elif step_type == "check":
                self.stats["Comparisons"] += 1
            elif step_type == "found":
                idx = self.current_step.get("index")
                self.result_message = f"Element found: index {idx}"
                self.state = "FINISHED"
            elif step_type == "not_found":
                self.result_message = "Element not found"
                self.state = "FINISHED"
            elif step_type == "finished":
                self.state = "FINISHED"

        except StopIteration:
            self.state = "FINISHED"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif self.input_mode:
                    if event.key == pygame.K_RETURN:
                        if self.target_input:
                            self.target = int(self.target_input)
                        self.input_mode = False
                        self.target_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.target_input = self.target_input[:-1]
                    elif event.unicode.isdigit():
                        self.target_input += event.unicode

                elif event.key == pygame.K_1:
                    self.algorithm = 1
                    self.reset_state()

                elif event.key == pygame.K_2:
                    self.algorithm = 2
                    self.reset_state()

                elif event.key == pygame.K_3:
                    self.algorithm = 3
                    self.reset_state()

                elif event.key == pygame.K_SPACE:
                    if self.state == "IDLE":
                        self.start_algorithm()
                    elif self.state == "RUNNING":
                        self.state = "PAUSED"
                    elif self.state == "PAUSED":
                        self.state = "RUNNING"

                elif event.key == pygame.K_n:
                    if self.state in ("RUNNING", "PAUSED"):
                        self.next_step()

                elif event.key == pygame.K_r:
                    self.generate_new_array()

                elif event.key == pygame.K_t and self.algorithm == 3:
                    self.input_mode = True
                    self.target_input = ""

    def update(self, dt):
        if self.state == "RUNNING":
            self.step_timer += dt
            if self.step_timer >= self.step_interval:
                self.step_timer = 0.0
                self.next_step()

    def draw(self):
        self.visualizer.draw_background()

        algorithm_name = ALGORITHM_NAMES.get(self.algorithm, "Unknown")
        state_text = f"State: {self.state}"
        if self.target is not None:
            state_text += f" | Target: {self.target}"

        self.visualizer.draw_header(algorithm_name, state_text)
        self.visualizer.draw_array(self.values, self.current_step, self.algorithm)
        
        if self.result_message:
            self.visualizer.draw_result_message(self.result_message)
        
        self.visualizer.draw_stats(self.stats)
        self.visualizer.draw_legend()
        self.visualizer.draw_controls()

        if self.input_mode:
            self.visualizer.draw_target_input(self.target_input)

        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                dt = self.clock.tick(FPS) / 1000.0

                self.handle_events()
                self.update(dt)
                self.draw()

        finally:
            pygame.quit()
            sys.exit()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()