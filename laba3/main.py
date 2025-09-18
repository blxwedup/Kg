import matplotlib.pyplot as plt


def bresenham_line(x0, y0, x1, y1):
    """
Определение ошибки:
    Ошибка – это накопленное отклонение
    между идеальной (вещественной) прямой и выбранными целочисленными пикселями.
Геометрический смысл:
    Геометрически ошибка отражает, насколько выбранный пиксель «отстоит» от истинной линии.
    Если ошибка становится достаточно большой, значит,
    текущий выбор пикселя слишком далёк от идеальной линии и требуется корректировка (смещение по другой оси).

    """
    dx = abs(x1 - x0)  # 7
    dy = abs(y1 - y0)  # 9
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy  # -2

    points = []
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= -dy:
            err -= dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return points


# Пример использования:


def bresenham_circle(cx, cy, r):
    """ошибка величина, которая определяет, насколько точка,
    выбранная на шаге, отклоняется от идеальной окружности
    Эти формулы получены из анализа разности между значением функции окружности
    и значением в середине между двумя возможными пиксельными координатами."""

    x = 0
    y = r
    d = 3 - 2 * r
    points = []

    while x <= y:
        points += [(cx + x, cy + y), (cx - x, cy + y),
                   (cx + x, cy - y), (cx - x, cy - y),
                   (cx + y, cy + x), (cx - y, cy + x),
                   (cx + y, cy - x), (cx - y, cy - x)]
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1
    return points


def plot_results(x1, y1, x2, y2, cx, cy, r, mode):
    """Рисует либо отрезок, либо окружность с узлами алгоритма Брезенхема."""
    fig, ax = plt.subplots(figsize=(6, 6))

    # Параметры сетки
    grid_min = min(x1, x2, cx - r) - 2
    grid_max = max(x1, x2, cx + r) + 2
    grid_miny = min(y1, y2, cy - r) - 2
    grid_maxy = max(y1, y2, cy + r) + 2
    ax.set_xticks(range(grid_min, grid_max + 2))
    ax.set_yticks(range(grid_miny, grid_maxy + 2))
    ax.grid(True, which='both')
    ax.set_xlim([grid_min, grid_max])
    ax.set_ylim([grid_min, grid_max])
    ax.set_aspect('equal')

    if mode == "line":
        # Рисуем стандартный отрезок
        ax.plot([x1, x2], [y1, y2], 'g-', label="Стандартный отрезок")

        # Отображаем узлы алгоритма Брезенхема
        line_points = bresenham_line(x1, y1, x2, y2)
        x_line, y_line = zip(*line_points)
        ax.scatter(x_line, y_line, color='red', marker='s', label="Узлы Брезенхема (отрезок)")

    elif mode == "circle":
        # Рисуем стандартную окружность
        circle = plt.Circle((cx, cy), r, color='g', fill=False, linestyle='dashed', label="Стандартная окружность")
        ax.add_patch(circle)

        # Отображаем узлы алгоритма Брезенхема
        circle_points = bresenham_circle(cx, cy, r)
        x_circle, y_circle = zip(*circle_points)
        ax.scatter(x_circle, y_circle, color='blue', marker='s', label="Узлы Брезенхема (окружность)")

    ax.legend()
    plt.show()


x1, y1, x2, y2 = 1, 1, 8, 10  # Координаты концов отрезка
cx, cy, r = 0, 0, 3  # Координаты центра и радиус окружности

# Выберите режим: "line" - рисовать отрезок, "circle" - рисовать окружность
ans = int(input())
if ans == 1:
    mode = "line"
else:
    mode = "circle"
plot_results(x1, y1, x2, y2, cx, cy, r, mode)