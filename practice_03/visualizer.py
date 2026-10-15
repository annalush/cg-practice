import pygame
from settings import *


class Visualizer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 36)

        self.viz_area = pygame.Rect(50, 100, 1000, 420)

    def draw_background(self):
        self.screen.fill(COLOR_BG)

    def draw_header(self, algorithm_name, state_text):
        title = self.title_font.render(algorithm_name, True, COLOR_TEXT)
        self.screen.blit(title, (50, 15))

        state = self.font.render(state_text, True, COLOR_TEXT_LIGHT)
        self.screen.blit(state, (50, 55))

    def draw_array(self, values, step=None, algorithm=None):
        n = len(values)
        if n == 0:
            return

        bar_width = self.viz_area.width / n
        max_value = max(values) if values else 100
        max_bar_height = self.viz_area.height - 20

        highlight_indices = set()
        swap_indices = set()
        sorted_indices = set()
        search_left = None
        search_right = None
        search_mid = None
        found_index = None
        excluded_indices = set()
        min_index = None

        if step:
            step_type = step.get("type")

            if step_type == "compare":
                indices = step.get("indices", ())
                highlight_indices.update(indices)
                if "current_min" in step:
                    min_index = step["current_min"]

            elif step_type == "swap":
                swap_indices.update(step.get("indices", ()))

            elif step_type == "new_min":
                min_index = step.get("indices", (None,))[0]

            elif step_type == "pass_end":
                sorted_idx = step.get("sorted_index")
                if sorted_idx is not None:
                    sorted_indices.update(range(sorted_idx, len(values)))

            elif step_type == "check":
                search_left = step.get("left")
                search_right = step.get("right")
                search_mid = step.get("mid")

                if search_left is not None and search_right is not None:
                    for i in range(n):
                        if i < search_left or i > search_right:
                            excluded_indices.add(i)

            elif step_type == "found":
                found_index = step.get("index")

            elif step_type == "finished":
                sorted_indices.update(range(n))

        for i, value in enumerate(values):
            bar_height = (value / max_value) * max_bar_height
            x = self.viz_area.x + i * bar_width
            y = self.viz_area.y + self.viz_area.height - 10 - bar_height

            color = self._get_bar_color(
                i, highlight_indices, swap_indices, sorted_indices,
                search_left, search_right, search_mid, found_index,
                excluded_indices, min_index
            )

            pygame.draw.rect(
                self.screen, color,
                (x, y, max(1, bar_width - 1), bar_height)
            )

            if n <= 40 and bar_width >= 18:
                value_text = self.small_font.render(str(value), True, COLOR_TEXT)
                text_x = x + (bar_width - value_text.get_width()) / 2
                text_y = y - 15
                self.screen.blit(value_text, (text_x, text_y))

    def _get_bar_color(self, i, highlight, swap, sorted_,
                       search_left, search_right, search_mid,
                       found, excluded, min_idx):
        if found is not None and i == found:
            return COLOR_BAR_FOUND
        if i in swap:
            return COLOR_BAR_SWAP
        if min_idx is not None and i == min_idx:
            return COLOR_BAR_MIN
        if search_mid is not None and i == search_mid:
            return COLOR_BAR_MID
        if i in highlight:
            return COLOR_BAR_COMPARE
        if i in sorted_:
            return COLOR_BAR_SORTED
        if search_left is not None and search_right is not None:
            if search_left <= i <= search_right:
                return COLOR_BAR_SEARCH
        if i in excluded:
            return COLOR_BAR_EXCLUDED
        return COLOR_BAR_DEFAULT

    def draw_stats(self, stats):
        y = 540
        x = 50

        for key, value in stats.items():
            text = self.font.render(f"{key}: {value}", True, COLOR_TEXT)
            self.screen.blit(text, (x, y))
            y += 24

    def draw_legend(self):
        legend_items = [
            ("Обычный", COLOR_BAR_DEFAULT),
            ("Сравнение", COLOR_BAR_COMPARE),
            ("Обмен", COLOR_BAR_SWAP),
            ("Минимум", COLOR_BAR_MIN),
            ("Отсортирован", COLOR_BAR_SORTED),
            ("Поиск", COLOR_BAR_SEARCH),
            ("Mid", COLOR_BAR_MID),
            ("Найден", COLOR_BAR_FOUND),
            ("Исключён", COLOR_BAR_EXCLUDED),
        ]

        x = 50
        y = 660

        for name, color in legend_items:
            pygame.draw.rect(self.screen, color, (x, y, 12, 12))
            text = self.small_font.render(name, True, COLOR_TEXT_LIGHT)
            self.screen.blit(text, (x + 16, y))
            x += 95

    def draw_controls(self):
        controls = [
            "1-Bubble Sort",
            "2-Selection Sort",
            "3-Binary Search",
            "SPACE-Start/Pause",
            "N-Next step",
            "R-New array",
            "T-Set target",
            "ESC-Exit"
        ]

        y = 685
        x = 50

        for control in controls:
            text = self.small_font.render(control, True, COLOR_TEXT_LIGHT)
            self.screen.blit(text, (x, y))
            x += 130

    def draw_target_input(self, current_input):
        text = self.font.render(f"Enter target: {current_input}", True, COLOR_TEXT)
        self.screen.blit(text, (50, 75))

    def draw_result_message(self, message):
        text = self.font.render(message, True, (40, 120, 40))
        self.screen.blit(text, (50, 530))