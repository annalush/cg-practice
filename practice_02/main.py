import pygame
import sys
from pathlib import Path

pygame.init()

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 650
FPS = 60

COLOR_BG = (245, 240, 230)
COLOR_COUNTER = (170, 110, 70)
COLOR_CASHIER = (130, 90, 60)
COLOR_PICKUP = (120, 160, 100)
COLOR_ENTRANCE = (180, 140, 120)
COLOR_TEXT = (30, 30, 30)
COLOR_INTERACTION = (60, 170, 90)
COLOR_MENU_BG = (250, 245, 240)
COLOR_MENU_BORDER = (100, 80, 60)
COLOR_MENU_HIGHLIGHT = (200, 180, 160)
COLOR_PROGRESS_BG = (210, 210, 210)
COLOR_PROGRESS_FILL = (70, 170, 90)

CLIENT_COLORS = [
    (70, 130, 220),
    (60, 180, 110),
    (220, 90, 80),
    (230, 175, 60),
]

NO_ORDER = "NO_ORDER"
WAITING = "WAITING"
READY = "READY"
DONE = "DONE"


class BakerySimulator:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Bakery Simulator - Stage 1")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        self.client_pos = pygame.Vector2(80, WINDOW_HEIGHT // 2)
        self.client_radius = 24
        self.client_speed = 240.0
        self.client_color_index = 0
        
        self.setup_zones()
        
        self.products = [
            {"name": "Хлеб", "price": 70, "stock": 3, "cook_time": 0.0, "key": "1"},
            {"name": "Булочка", "price": 90, "stock": 4, "cook_time": 0.0, "key": "2"},
            {"name": "Сэндвич", "price": 180, "stock": 2, "cook_time": 5.0, "key": "3"},
            {"name": "Кофе", "price": 140, "stock": 5, "cook_time": 3.0, "key": "4"},
        ]
        
        self.money = 420
        self.current_order = None
        self.order_state = NO_ORDER
        self.cooking_time_left = 0.0
        self.total_cook_time = 0.0
        self.message = ""
        self.message_timer = 0.0
        
        self.menu_open = False
        self.running = True
        
    def setup_zones(self):
        self.counter_rect = pygame.Rect(350, 120, 420, 100)
        self.cashier_rect = pygame.Rect(780, 300, 140, 100)
        self.pickup_rect = pygame.Rect(600, 470, 260, 100)
        self.interaction_rect = pygame.Rect(380, 225, 360, 70)
        self.entrance_rect = pygame.Rect(20, 250, 120, 150)
        self.obstacles = [self.counter_rect, self.cashier_rect]
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.menu_open:
                    if event.key == pygame.K_ESCAPE:
                        self.menu_open = False
                    elif event.key == pygame.K_1:
                        self.try_order_product(0)
                    elif event.key == pygame.K_2:
                        self.try_order_product(1)
                    elif event.key == pygame.K_3:
                        self.try_order_product(2)
                    elif event.key == pygame.K_4:
                        self.try_order_product(3)
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    
                    elif event.key == pygame.K_SPACE:
                        self.client_color_index = (
                            self.client_color_index + 1
                        ) % len(CLIENT_COLORS)
                    
                    elif event.key == pygame.K_e:
                        if self.order_state == READY:
                            self.try_pickup_order()
                        else:
                            client_rect = pygame.Rect(
                                0, 0,
                                self.client_radius * 2,
                                self.client_radius * 2
                            )
                            client_rect.center = (
                                round(self.client_pos.x),
                                round(self.client_pos.y)
                            )
                            
                            if client_rect.colliderect(self.interaction_rect):
                                self.menu_open = True
    
    def try_order_product(self, product_index):
        product = self.products[product_index]
        
        if product["stock"] <= 0:
            self.show_message("Товар закончился")
            return
        
        if self.money < product["price"]:
            self.show_message("Недостаточно денег")
            return
        
        self.money -= product["price"]
        product["stock"] -= 1
        self.current_order = product.copy()
        self.menu_open = False
        
        if product["cook_time"] > 0:
            self.order_state = WAITING
            self.cooking_time_left = product["cook_time"]
            self.total_cook_time = product["cook_time"]
        else:
            self.order_state = READY
        
        self.show_message("Заказ принят")
    
    def try_pickup_order(self):
        client_rect = pygame.Rect(
            0, 0,
            self.client_radius * 2,
            self.client_radius * 2
        )
        client_rect.center = (
            round(self.client_pos.x),
            round(self.client_pos.y)
        )
        
        if client_rect.colliderect(self.pickup_rect):
            self.order_state = DONE
            self.show_message("Заказ получен")
            self.current_order = None
            self.cooking_time_left = 0.0
    
    def handle_movement(self, dt):
        if self.menu_open:
            return
        
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)
        
        if keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_s]:
            direction.y += 1
        if keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_d]:
            direction.x += 1
        
        if direction.length_squared() > 0:
            direction = direction.normalize()
        
        next_position = self.client_pos + direction * self.client_speed * dt
        
        next_position.x = max(
            self.client_radius,
            min(WINDOW_WIDTH - self.client_radius, next_position.x)
        )
        next_position.y = max(
            self.client_radius,
            min(WINDOW_HEIGHT - self.client_radius, next_position.y)
        )
        
        next_rect = pygame.Rect(
            0, 0,
            self.client_radius * 2,
            self.client_radius * 2
        )
        next_rect.center = (
            round(next_position.x),
            round(next_position.y)
        )
        
        blocked = False
        for obstacle in self.obstacles:
            if next_rect.colliderect(obstacle):
                blocked = True
                break
        
        if not blocked:
            self.client_pos = next_position
    
    def update_order(self, dt):
        if self.order_state == WAITING:
            self.cooking_time_left -= dt
            
            if self.cooking_time_left <= 0:
                self.cooking_time_left = 0
                self.order_state = READY
                self.show_message("Заказ готов!")
    
    def update_message(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
    
    def show_message(self, text):
        self.message = text
        self.message_timer = 3.0
    
    def draw_scene(self):
        self.screen.fill(COLOR_BG)
        
        pygame.draw.rect(
            self.screen, COLOR_ENTRANCE,
            self.entrance_rect,
            border_radius=8
        )
        entrance_label = self.small_font.render("Вход", True, COLOR_TEXT)
        self.screen.blit(
            entrance_label,
            (self.entrance_rect.centerx - entrance_label.get_width() // 2,
             self.entrance_rect.centery - 10)
        )
        
        pygame.draw.rect(
            self.screen, COLOR_COUNTER,
            self.counter_rect,
            border_radius=8
        )
        counter_label = self.font.render("ПРИЛАВОК", True, (255, 255, 255))
        self.screen.blit(
            counter_label,
            (self.counter_rect.centerx - counter_label.get_width() // 2,
             self.counter_rect.centery - 10)
        )
        
        pygame.draw.rect(
            self.screen, COLOR_CASHIER,
            self.cashier_rect,
            border_radius=8
        )
        cashier_label = self.small_font.render("КАССА", True, (255, 255, 255))
        self.screen.blit(
            cashier_label,
            (self.cashier_rect.centerx - cashier_label.get_width() // 2,
             self.cashier_rect.centery - 10)
        )
        
        pickup_color = COLOR_PICKUP
        if self.order_state == READY:
            pickup_color = (100, 200, 80)
        
        pygame.draw.rect(
            self.screen, pickup_color,
            self.pickup_rect,
            border_radius=8
        )
        pickup_label = self.small_font.render("ВЫДАЧА", True, COLOR_TEXT)
        self.screen.blit(
            pickup_label,
            (self.pickup_rect.centerx - pickup_label.get_width() // 2,
             self.pickup_rect.centery - 10)
        )
        
        client_rect = pygame.Rect(
            0, 0,
            self.client_radius * 2,
            self.client_radius * 2
        )
        client_rect.center = (
            round(self.client_pos.x),
            round(self.client_pos.y)
        )
        
        can_interact = client_rect.colliderect(self.interaction_rect)
        
        if can_interact and not self.menu_open and self.order_state != READY:
            pygame.draw.rect(
                self.screen, COLOR_INTERACTION,
                self.interaction_rect,
                width=3,
                border_radius=8
            )
        
        pygame.draw.circle(
            self.screen,
            CLIENT_COLORS[self.client_color_index],
            (round(self.client_pos.x), round(self.client_pos.y)),
            self.client_radius,
        )
        
        if can_interact and not self.menu_open and self.order_state != READY:
            hint = self.font.render("E — сделать заказ", True, COLOR_INTERACTION)
            self.screen.blit(hint, (380, 200))
        
        if self.order_state == READY:
            pickup_client_rect = pygame.Rect(
                0, 0,
                self.client_radius * 2,
                self.client_radius * 2
            )
            pickup_client_rect.center = (
                round(self.client_pos.x),
                round(self.client_pos.y)
            )
            
            if pickup_client_rect.colliderect(self.pickup_rect):
                hint = self.font.render("E — получить заказ", True, (40, 120, 40))
                self.screen.blit(hint, (600, 450))
    
    def draw_menu(self):
        if not self.menu_open:
            return
        
        menu_rect = pygame.Rect(200, 100, 600, 400)
        pygame.draw.rect(
            self.screen, COLOR_MENU_BG,
            menu_rect,
            border_radius=12
        )
        pygame.draw.rect(
            self.screen, COLOR_MENU_BORDER,
            menu_rect,
            width=3,
            border_radius=12
        )
        
        title = self.title_font.render("МЕНЮ ЗАКАЗА", True, COLOR_TEXT)
        self.screen.blit(
            title,
            (menu_rect.centerx - title.get_width() // 2, 120)
        )
        
        for i, product in enumerate(self.products):
            y = 180 + i * 50
            
            keys = pygame.key.get_pressed()
            if keys[getattr(pygame, f"K_{i+1}")]:
                pygame.draw.rect(
                    self.screen, COLOR_MENU_HIGHLIGHT,
                    (menu_rect.x + 10, y - 5, menu_rect.width - 20, 45),
                    border_radius=6
                )
            
            stock_color = (30, 30, 30) if product["stock"] > 0 else (150, 30, 30)
            
            text = (
                f"{product['key']}. {product['name']:12} "
                f"{product['price']:3} ₽ "
                f"(ост: {product['stock']})"
            )
            
            if product["cook_time"] > 0:
                text += f" [{product['cook_time']}с]"
            
            label = self.font.render(text, True, stock_color)
            self.screen.blit(label, (menu_rect.x + 20, y))
        
        hint = self.small_font.render(
            "Выберите товар клавишами 1-4 | ESC — закрыть",
            True, (80, 80, 80)
        )
        self.screen.blit(
            hint,
            (menu_rect.centerx - hint.get_width() // 2, 520)
        )
    
    def draw_ui(self):
        y_offset = 20
        
        money_text = self.font.render(f"Money: {self.money} ₽", True, COLOR_TEXT)
        self.screen.blit(money_text, (20, y_offset))
        y_offset += 35
        
        if self.current_order:
            order_text = self.font.render(
                f"Order: {self.current_order['name']}",
                True, COLOR_TEXT
            )
            self.screen.blit(order_text, (20, y_offset))
            y_offset += 35
            
            state_text = self.font.render(
                f"State: {self.order_state}",
                True, COLOR_TEXT
            )
            self.screen.blit(state_text, (20, y_offset))
            y_offset += 35
            
            if self.order_state == WAITING:
                cooking_text = self.font.render(
                    f"Cooking: {self.cooking_time_left:.1f} s",
                    True, COLOR_TEXT
                )
                self.screen.blit(cooking_text, (20, y_offset))
                y_offset += 35
                
                bar_x, bar_y = 20, y_offset
                bar_width, bar_height = 240, 20
                
                pygame.draw.rect(
                    self.screen, COLOR_PROGRESS_BG,
                    (bar_x, bar_y, bar_width, bar_height),
                    border_radius=4
                )
                
                if self.total_cook_time > 0:
                    progress = 1.0 - self.cooking_time_left / self.total_cook_time
                    progress = max(0.0, min(1.0, progress))
                    filled_width = int(bar_width * progress)
                    
                    pygame.draw.rect(
                        self.screen, COLOR_PROGRESS_FILL,
                        (bar_x, bar_y, filled_width, bar_height),
                        border_radius=4
                    )
                
                y_offset += 30
        
        y_offset += 10
        
        fps_text = self.small_font.render(
            f"FPS: {self.clock.get_fps():.0f}",
            True, (70, 70, 70)
        )
        self.screen.blit(fps_text, (20, y_offset))
        
        if self.message:
            msg_surface = self.title_font.render(
                self.message, True, (40, 120, 40)
            )
            self.screen.blit(
                msg_surface,
                (WINDOW_WIDTH // 2 - msg_surface.get_width() // 2,
                 WINDOW_HEIGHT - 80)
            )
        
        controls = (
            "WASD — движение | SPACE — цвет | E — действие | ESC — выход"
        )
        controls_text = self.small_font.render(controls, True, (70, 70, 70))
        self.screen.blit(
            controls_text,
            (20, WINDOW_HEIGHT - 30)
        )
    
    def run(self):
        try:
            while self.running:
                dt = self.clock.tick(FPS) / 1000.0
                
                self.handle_events()
                self.handle_movement(dt)
                self.update_order(dt)
                self.update_message(dt)
                
                self.draw_scene()
                self.draw_menu()
                self.draw_ui()
                
                pygame.display.flip()
        
        finally:
            pygame.quit()
            sys.exit()


def main():
    simulator = BakerySimulator()
    simulator.run()


if __name__ == "__main__":
    main()