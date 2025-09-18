import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


def seed_fill_by_lines(polygon, seed_point):
    min_x = min(p[0] for p in polygon)
    max_x = max(p[0] for p in polygon)
    min_y = min(p[1] for p in polygon)
    max_y = max(p[1] for p in polygon)

    width = max_x - min_x + 1
    height = max_y - min_y + 1
    grid = np.zeros((height, width), dtype=bool)

    def point_in_polygon(x, y):
        n = len(polygon)
        inside = False
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]
            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside
        return inside

    stack = [seed_point]
    filled_pixels = []

    while stack:
        x, y = stack.pop()

        if x < min_x or x > max_x or y < min_y or y > max_y:
            continue

        xi = int(x - min_x)
        yi = int(y - min_y)

        if grid[yi, xi] or not point_in_polygon(x, y):
            continue

        # Заполняем текущую точку
        grid[yi, xi] = True
        filled_pixels.append((x, y))

        # Находим левую границу
        left = x
        while left > min_x and point_in_polygon(left - 1, y):
            left -= 1
            xi_left = int(left - min_x)
            if not grid[yi, xi_left]:
                grid[yi, xi_left] = True
                filled_pixels.append((left, y))

        # Находим правую границу
        right = x
        while right < max_x and point_in_polygon(right + 1, y):
            right += 1
            xi_right = int(right - min_x)
            if not grid[yi, xi_right]:
                grid[yi, xi_right] = True
                filled_pixels.append((right, y))

        if y + 1 <= max_y:
            for x_scan in range(left, right + 1):
                if point_in_polygon(x_scan, y + 1):
                    xi_scan = int(x_scan - min_x)
                    yi_scan = int(y + 1 - min_y)
                    if not grid[yi_scan, xi_scan]:
                        stack.append((x_scan, y + 1))

        if y - 1 >= min_y:
            for x_scan in range(left, right + 1):
                if point_in_polygon(x_scan, y - 1):
                    xi_scan = int(x_scan - min_x)
                    yi_scan = int(y - 1 - min_y)
                    if not grid[yi_scan, xi_scan]:
                        stack.append((x_scan, y - 1))

        yield filled_pixels.copy()

polygon = [(0, 0), (400, 10), (200, 60), (150,200),  (200,350), (125,200), (125,350), (100,200),  (75,200), (50,350), (50,200), (-5, 100)]
seed_point = (60, 220)

min_x = min(p[0] for p in polygon)
max_x = max(p[0] for p in polygon)
min_y = min(p[1] for p in polygon)
max_y = max(p[1] for p in polygon)
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(min_x - 5, max_x + 5)
ax.set_ylim(min_y - 5, max_y + 5)
ax.set_aspect('equal')
ax.grid(True)

poly_patch = Polygon(polygon, closed=True, fill=None, edgecolor='blue', linewidth=2)
ax.add_patch(poly_patch)

seed_dot, = ax.plot([seed_point[0]], [seed_point[1]], 'ro', markersize=4)

filled_scatter = ax.scatter([], [], s=1, color='green', alpha=1)


def update(frame):
    if frame == 0:
        # Первый кадр - только многоугольник и точка затравки
        filled_scatter.set_offsets(np.empty((0, 2)))
        return [poly_patch, seed_dot, filled_scatter]

    filled_pixels = frame
    if filled_pixels:
        filled_scatter.set_offsets(filled_pixels)

    return [poly_patch, seed_dot, filled_scatter]


ani = FuncAnimation(fig, update,
                    frames=seed_fill_by_lines(polygon, seed_point),
                    interval=10, blit=True, repeat=False)

plt.title('Алгоритм заполнения с затравкой по отрезкам')
plt.show()