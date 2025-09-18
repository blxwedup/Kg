import pygame
import numpy as np
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Компьютерная графика")

CENTER = np.array([WIDTH // 2, HEIGHT // 2])


# Функция для создания матрицы 1×3 для хранения координат
def to_matrix(points):
    return np.array([[x, -y, 1] for x, y in points]).T


def transform(points, matrix):
    return (matrix @ points).astype(int)


# --- Фигура №7 (точная версия) ---
# Квадрат (сторона 200)
square_init = [(-100, -100), (100, -100), (100, 100), (-100, 100)]

# Центральная точка соединения лучей — ближе к верху (70% высоты квадрата)
lines_init = [
    (0, 100),      # верх квадрата
    (0, 70),       # центр соединения (подняли ещё выше)
    (-100, -100),  # левый нижний угол
    (100, -100)    # правый нижний угол
]

# --- Фигура №7 (исправленная версия по твоему описанию) ---
square_init = [(-100, -100), (100, -100), (100, 100), (-100, 100)]

# Линии:
# 1) Левая линия: (-100, -100) -> (-25, 0) -> (0, 100)
# 2) Правая линия: (100, -100) -> (25, 0) -> (0, 100)
lines_left = [(-100, -100), (-25, 0), (0, 100)]
lines_right = [(100, -100), (25, 0), (0, 100)]

# Нижний треугольник (оставляем широким)
small_triangle_init = [(-100, -100), (0, -50), (100, -100)]

# Превращаем в матрицы
square_matrix = to_matrix(square_init)
lines_left_matrix = to_matrix(lines_left)
lines_right_matrix = to_matrix(lines_right)
triangle_matrix = to_matrix(small_triangle_init)



def translate(dx, dy):
    return np.array([[1, 0, dx], [0, 1, -dy], [0, 0, 1]])


def scale(sx, sy, px=0, py=0):
    return np.array([[sx, 0, px * (1 - sx)], [0, sy, -py * (1 - sy)], [0, 0, 1]])


def rotate(angle, px=0, py=0):
    rad = math.radians(angle)
    translation_to_origin = np.array([[1, 0, -px], [0, 1, -py], [0, 0, 1]])
    rotation_matrix = np.array([
        [math.cos(rad), -math.sin(rad), 0],
        [math.sin(rad), math.cos(rad), 0],
        [0, 0, 1]
    ])
    translation_back = np.array([[1, 0, px], [0, 1, py], [0, 0, 1]])

    return translation_back @ rotation_matrix @ translation_to_origin


def reflect_x():
    return np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])


def reflect_y():
    return np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])


def reflect_y_equals_x():
    return np.array([[0, -1, 0], [-1, 0, 0], [0, 0, 1]])


def reset():
    global square_matrix, lines_left_matrix, lines_right_matrix, triangle_matrix, transform_matrix
    square_matrix = to_matrix(square_init)
    lines_matrix = to_matrix(lines_init)
    triangle_matrix = to_matrix(small_triangle_init)
    transform_matrix = np.eye(3)


running = True
transform_matrix = np.eye(3)

while running:
    screen.fill((255, 255, 255))
    pygame.draw.line(screen, (0, 0, 0), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 1)
    pygame.draw.line(screen, (0, 0, 0), (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 1)

    font = pygame.font.Font(None, 23)
    for i in range(-WIDTH // 2, WIDTH // 2, 50):
        text = font.render(str(i), True, (0, 0, 0))
        screen.blit(text, (i + WIDTH // 2, HEIGHT // 2 + 5))
    for i in range(-HEIGHT // 2, HEIGHT // 2, 50):
        if (i != 0):
            text = font.render(str(i), True, (0, 0, 0))
            screen.blit(text, (WIDTH // 2 + 5, HEIGHT // 2 - i))

    # Преобразование точек
    transformed_square = transform(square_matrix, transform_matrix)
    transformed_lines = transform(lines_left_matrix, transform_matrix)
    transformed_lines = transform(lines_right_matrix, transform_matrix)

    pygame.draw.polygon(screen, (0, 0, 0), transform(square_matrix, transform_matrix)[:2].T + CENTER, 2)

    # Рисуем линии
    p_left = transform(lines_left_matrix, transform_matrix)[:2].T + CENTER
    pygame.draw.lines(screen, (0, 0, 0), False, p_left, 2)

    p_right = transform(lines_right_matrix, transform_matrix)[:2].T + CENTER
    pygame.draw.lines(screen, (0, 0, 0), False, p_right, 2)

    # Нижний треугольник
    pygame.draw.polygon(screen, (0, 0, 0), transform(triangle_matrix, transform_matrix)[:2].T + CENTER, 2)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                dx = int(input("Сдвиг по X: "))
                transform_matrix = translate(dx, 0) @ transform_matrix
            elif event.key == pygame.K_LEFT:
                transform_matrix = translate(-10, 0) @ transform_matrix
            elif event.key == pygame.K_UP:
                dy = int(input("Сдвиг по Y: "))
                transform_matrix = translate(0, dy) @ transform_matrix
            elif event.key == pygame.K_DOWN:
                transform_matrix = translate(0, -10) @ transform_matrix
            elif event.key == pygame.K_r:
                angle = int(input("Поворот на угол: "))
                print("Относительно точки:")
                px = int(input("X: "))
                py = int(input("Y: "))
                transform_matrix = rotate(angle, px, -py) @ transform_matrix
            elif event.key == pygame.K_a:
                sx = float(input("Коэффицент масштабирования по X: "))
                transform_matrix = scale(sx, 1, 0, 0) @ transform_matrix
            elif event.key == pygame.K_d:
                sy = float(input("Коэффицент масштабирования по Y: "))
                transform_matrix = scale(1, sy, 0, 0) @ transform_matrix
            elif event.key == pygame.K_x:
                transform_matrix = reflect_x() @ transform_matrix
            elif event.key == pygame.K_y:
                transform_matrix = reflect_y() @ transform_matrix
            elif event.key == pygame.K_m:
                transform_matrix = reflect_y_equals_x() @ transform_matrix
            elif event.key == pygame.K_c:
                reset()

pygame.quit()
