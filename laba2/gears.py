import pygame
import numpy as np
import math
import time

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Взаимосвязанные вращающиеся шестерни")

CENTER = np.array([WIDTH // 2, HEIGHT // 2])
clock = pygame.time.Clock()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Функции трансформации из main.py
def to_matrix(points):
    """Функция для создания матрицы 1×3 для хранения координат"""
    return np.array([[x, -y, 1] for x, y in points]).T

def transform(points, matrix):
    """Применяет матрицу трансформации к точкам"""
    return (matrix @ points).astype(int)

def translate(dx, dy):
    """Создает матрицу перемещения"""
    return np.array([[1, 0, dx], [0, 1, -dy], [0, 0, 1]])

def scale(sx, sy, px=0, py=0):
    """Создает матрицу масштабирования"""
    return np.array([[sx, 0, px * (1 - sx)], [0, sy, -py * (1 - sy)], [0, 0, 1]])

def rotate(angle, px=0, py=0):
    """Создает матрицу поворота"""
    rad = math.radians(angle)
    translation_to_origin = np.array([[1, 0, -px], [0, 1, -py], [0, 0, 1]])
    rotation_matrix = np.array([
        [math.cos(rad), -math.sin(rad), 0],
        [math.sin(rad), math.cos(rad), 0],
        [0, 0, 1]
    ])
    translation_back = np.array([[1, 0, px], [0, 1, py], [0, 0, 1]])
    
    return translation_back @ rotation_matrix @ translation_to_origin

class Gear:
    def __init__(self, center_x, center_y, radius, teeth_count, color=BLACK, name=""):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.teeth_count = teeth_count
        self.color = color
        self.name = name
        self.angle = 0
        self.tooth_height = radius * 0.3  # Высота зубца
        self.inner_radius = radius * 0.6  # Внутренний радиус
        self.angular_velocity = 0  # Угловая скорость
        
        # Создаем точки шестерни и преобразуем в матричную форму
        gear_points = self._generate_gear_points()
        self.points_matrix = to_matrix(gear_points)
        
        # Матрица трансформации (изначально единичная)
        self.transform_matrix = np.eye(3)
        
    def _generate_gear_points(self):
        """Генерирует точки для отрисовки шестерни с зубцами"""
        points = []
        angle_per_tooth = 2 * math.pi / self.teeth_count
        
        for i in range(self.teeth_count):
            # Базовый угол для этого зубца
            base_angle = i * angle_per_tooth
            
            # Создаем зубец (трапециевидной формы)
            # 1. Начало зубца (на основном радиусе)
            angle_start = base_angle - angle_per_tooth * 0.15
            x_start = self.radius * math.cos(angle_start)
            y_start = self.radius * math.sin(angle_start)
            points.append((x_start, y_start))
            
            # 2. Левый край зубца (внешний радиус)
            angle_left = base_angle - angle_per_tooth * 0.08
            x_left = (self.radius + self.tooth_height) * math.cos(angle_left)
            y_left = (self.radius + self.tooth_height) * math.sin(angle_left)
            points.append((x_left, y_left))
            
            # 3. Правый край зубца (внешний радиус)
            angle_right = base_angle + angle_per_tooth * 0.08
            x_right = (self.radius + self.tooth_height) * math.cos(angle_right)
            y_right = (self.radius + self.tooth_height) * math.sin(angle_right)
            points.append((x_right, y_right))
            
            # 4. Конец зубца (на основном радиусе)
            angle_end = base_angle + angle_per_tooth * 0.15
            x_end = self.radius * math.cos(angle_end)
            y_end = self.radius * math.sin(angle_end)
            points.append((x_end, y_end))
            
        return points
    
    def set_angular_velocity(self, velocity):
        """Устанавливает угловую скорость"""
        self.angular_velocity = velocity
    
    def update(self, dt):
        """Обновляет угол поворота шестерни и матрицу трансформации"""
        self.angle += self.angular_velocity * dt
        
        # Обновляем матрицу трансформации: сначала поворот, затем перемещение
        rotation_matrix = rotate(math.degrees(self.angle), 0, 0)
        translation_matrix = translate(self.center_x, self.center_y)
        self.transform_matrix = translation_matrix @ rotation_matrix
        
    def get_transformed_points(self):
        """Возвращает точки шестерни, преобразованные с помощью матрицы трансформации"""
        # Применяем матрицу трансформации к точкам шестерни
        transformed_points_matrix = transform(self.points_matrix, self.transform_matrix)
        
        # Преобразуем обратно в список кортежей
        points_list = []
        for i in range(transformed_points_matrix.shape[1]):
            x = transformed_points_matrix[0, i]
            y = transformed_points_matrix[1, i]
            points_list.append((x, y))
            
        return points_list
    
    def draw(self, screen):
        """Отрисовывает шестерню на экране"""
        points = self.get_transformed_points()
        # Преобразуем координаты для pygame (добавляем смещение к центру экрана)
        screen_points = [(int(x + CENTER[0]), int(y + CENTER[1])) for x, y in points]
        
        # Рисуем зубцы
        if len(screen_points) > 2:
            pygame.draw.polygon(screen, self.color, screen_points, 2)
        
        # Получаем преобразованные координаты центра
        center_matrix = to_matrix([(0, 0)])  # Центр шестерни в локальных координатах
        transformed_center = transform(center_matrix, self.transform_matrix)
        center_screen = (int(transformed_center[0, 0] + CENTER[0]), int(transformed_center[1, 0] + CENTER[1]))
        
        # Рисуем основную окружность
        pygame.draw.circle(screen, self.color, center_screen, int(self.radius), 2)
        
        # Рисуем внутреннюю окружность (ось)
        pygame.draw.circle(screen, self.color, center_screen, int(self.inner_radius), 2)
        
        # Рисуем центральную точку
        pygame.draw.circle(screen, self.color, center_screen, 3)
        
        # Подписываем шестерню
        if self.name:
            font = pygame.font.Font(None, 24)
            text = font.render(self.name, True, self.color)
            text_rect = text.get_rect(center=(center_screen[0], center_screen[1] + self.radius + 20))
            screen.blit(text, text_rect)

def calculate_gear_ratios(gear1, gear2, gear3):
    """
    Рассчитывает соотношения угловых скоростей для взаимосвязанных шестерен
    gear1 - ведущая шестерня (задаем ей базовую скорость)
    gear2 и gear3 - ведомые шестерни
    """
    base_speed = 1.0  # Базовая угловая скорость для gear1
    
    # Для зубчатых передач: w1 * r1 = w2 * r2
    # где w - угловая скорость, r - радиус шестерни
    
    # gear1 вращается по часовой стрелке
    gear1.set_angular_velocity(base_speed)
    
    # gear2 соединена с gear1, вращается против часовой стрелки
    # Расстояние между центрами должно быть равно сумме радиусов для правильного зацепления
    gear2_speed = -base_speed * (gear1.radius + gear1.tooth_height) / (gear2.radius + gear2.tooth_height)
    gear2.set_angular_velocity(gear2_speed)
    
    # gear3 соединена с gear1, вращается против часовой стрелки
    gear3_speed = -base_speed * (gear1.radius + gear1.tooth_height) / (gear3.radius + gear3.tooth_height)
    gear3.set_angular_velocity(gear3_speed)

def draw_connections(screen, gear1, gear2, gear3):
    """Рисует линии соединения между шестернями"""
    # Получаем преобразованные координаты центров шестерен
    center_matrix1 = to_matrix([(0, 0)])
    center_matrix2 = to_matrix([(0, 0)])
    center_matrix3 = to_matrix([(0, 0)])
    
    transformed_center1 = transform(center_matrix1, gear1.transform_matrix)
    transformed_center2 = transform(center_matrix2, gear2.transform_matrix)
    transformed_center3 = transform(center_matrix3, gear3.transform_matrix)
    
    center1 = (int(transformed_center1[0, 0] + CENTER[0]), int(transformed_center1[1, 0] + CENTER[1]))
    center2 = (int(transformed_center2[0, 0] + CENTER[0]), int(transformed_center2[1, 0] + CENTER[1]))
    center3 = (int(transformed_center3[0, 0] + CENTER[0]), int(transformed_center3[1, 0] + CENTER[1]))
    
    # Рисуем пунктирные линии соединения
    pygame.draw.line(screen, GRAY, center1, center2, 1)
    pygame.draw.line(screen, GRAY, center1, center3, 1)

def main():
    # Создаем три взаимосвязанные шестерни
    # Позиционируем их так, чтобы они правильно зацеплялись
    gear1 = Gear(0, 0, 80, 24, RED, "Шестерня 1")        # Центральная ведущая
    gear2 = Gear(-180, 0, 60, 18, GREEN, "Шестерня 2")    # Левая ведомая
    gear3 = Gear(90, 140, 50, 15, BLUE, "Шестерня 3")     # Правая верхняя ведомая
    
    # Рассчитываем соотношения скоростей
    calculate_gear_ratios(gear1, gear2, gear3)
    
    running = True
    last_time = time.time()
    
    # Переменные для управления
    paused = False
    speed_multiplier = 1.0
    
    print("Управление:")
    print("SPACE - пауза/воспроизведение")
    print("+ / - - увеличить/уменьшить скорость")
    print("R - сброс анимации")
    print("ESC - выход")
    
    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    print("Пауза" if paused else "Воспроизведение")
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    speed_multiplier += 0.2
                    print(f"Скорость: {speed_multiplier:.1f}x")
                elif event.key == pygame.K_MINUS:
                    speed_multiplier = max(0.1, speed_multiplier - 0.2)
                    print(f"Скорость: {speed_multiplier:.1f}x")
                elif event.key == pygame.K_r:
                    gear1.angle = 0
                    gear2.angle = 0
                    gear3.angle = 0
                    print("Анимация сброшена")
        
        # Обновление анимации
        if not paused:
            # Применяем множитель скорости
            effective_dt = dt * speed_multiplier
            gear1.update(effective_dt)
            gear2.update(effective_dt)
            gear3.update(effective_dt)
        
        # Отрисовка
        screen.fill(WHITE)
        
        # Рисуем координатные оси
        pygame.draw.line(screen, GRAY, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 1)
        pygame.draw.line(screen, GRAY, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 1)
        
        # Рисуем соединения между шестернями
        draw_connections(screen, gear1, gear2, gear3)
        
        # Рисуем шестерни
        gear1.draw(screen)
        gear2.draw(screen)
        gear3.draw(screen)
        
        # Информация на экране
        font = pygame.font.Font(None, 36)
        info_text = f"Скорость: {speed_multiplier:.1f}x"
        if paused:
            info_text += " (ПАУЗА)"
        text_surface = font.render(info_text, True, BLACK)
        screen.blit(text_surface, (10, 10))
        
        # Показываем углы поворота
        angles_text = f"Углы: Ш1={math.degrees(gear1.angle):.1f}° Ш2={math.degrees(gear2.angle):.1f}° Ш3={math.degrees(gear3.angle):.1f}°"
        font_small = pygame.font.Font(None, 24)
        angles_surface = font_small.render(angles_text, True, BLACK)
        screen.blit(angles_surface, (10, 50))
        
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    pygame.quit()

if __name__ == "__main__":
    main()
