import numpy as np
import matplotlib.pyplot as plt


def on_scroll(event):
    """Обработчик масштабирования колесом мыши"""
    ax = plt.gca()
    zoom_factor = 1.1
    if event.button == 'up':
        ax.set_xlim([x / zoom_factor for x in ax.get_xlim()])
        ax.set_ylim([y / zoom_factor for y in ax.get_ylim()])
    elif event.button == 'down':
        ax.set_xlim([x * zoom_factor for x in ax.get_xlim()])
        ax.set_ylim([y * zoom_factor for y in ax.get_ylim()])
    plt.draw()


def compute_code(x, y, x_min, y_min, x_max, y_max):
    """Вычисление регионного кода точки"""
    code = 0b0000
    if x < x_min: code |= 0b0001  # Лево
    if x > x_max: code |= 0b0010  # Право
    if y < y_min: code |= 0b0100  # Низ
    if y > y_max: code |= 0b1000  # Верх
    return code


def midpoint_clip(rect, p1, p2, eps=1e-5):
    """Алгоритм средней точки для отсечения отрезка"""
    x_min, y_min, x_max, y_max = rect
    x1, y1 = p1
    x2, y2 = p2

    code1 = compute_code(x1, y1, x_min, y_min, x_max, y_max)
    code2 = compute_code(x2, y2, x_min, y_min, x_max, y_max)
    intersection_points = []
    visible_segments = []

    def is_close(a, b):
        return abs(a - b) < eps

    stack = [(x1, y1, x2, y2)]
    while stack:
        x1, y1, x2, y2 = stack.pop()
        code1, code2 = (compute_code(x1, y1, x_min, y_min, x_max, y_max),
                        compute_code(x2, y2, x_min, y_min, x_max, y_max))

        if code1 == 0 and code2 == 0:
            visible_segments.append(((x1, y1), (x2, y2)))
            continue

        if code1 & code2 != 0:
            continue

        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        intersection_points.append((mx, my))

        if is_close(x1, x2) and is_close(y1, y2):
            continue

        stack.append((mx, my, x2, y2))
        stack.append((x1, y1, mx, my))

    return visible_segments, intersection_points


def plot_results(rect, original_segment, visible_segments, intersection_points):
    """Визуализация результатов отсечения"""
    x_min, y_min, x_max, y_max = rect
    fig, ax = plt.subplots(figsize=(10, 8))

    rect_poly = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max), (x_min, y_min)]
    rect_poly = np.array(rect_poly)
    ax.plot(*rect_poly.T, 'b-', linewidth=2, label='Окно отсечения')

    p1, p2 = original_segment
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'g--', label='Исходный отрезок')

    first_segment = True
    for segment in visible_segments:
        (x1, y1), (x2, y2) = segment
        if first_segment:
            ax.plot([x1, x2], [y1, y2], 'y--', linewidth=3, label='Видимая часть отрезка')
            first_segment = False
        else:
            ax.plot([x1, x2], [y1, y2], 'y-', linewidth=3)

    if intersection_points:
        x_pts, y_pts = zip(*intersection_points)
        ax.scatter(x_pts, y_pts, c='black', marker='o', label='Точки деления')

    ax.legend()
    ax.grid(True)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Алгоритм средней точки для отсечения отрезка')
    plt.tight_layout()
    fig.canvas.mpl_connect('scroll_event', on_scroll)
    plt.show()


if __name__ == "__main__":
    rectangle = (2, 2, 8, 6)
    segment = ((1, 1), (9, 7))
    visible_segments, intersections = midpoint_clip(rectangle, *segment)
    plot_results(rectangle, segment, visible_segments, intersections)

