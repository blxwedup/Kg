import numpy as np
import matplotlib.pyplot as plt


def on_scroll(event):
    ax = plt.gca()
    current_xlim = ax.get_xlim()
    current_ylim = ax.get_ylim()

    zoom_factor = 1.1  # Множитель зума
    if event.button == 'up':  # Колесо мыши вверх
        ax.set_xlim([x / zoom_factor for x in current_xlim])
        ax.set_ylim([y / zoom_factor for y in current_ylim])
    elif event.button == 'down':  # Колесо мыши вниз
        ax.set_xlim([x * zoom_factor for x in current_xlim])
        ax.set_ylim([y * zoom_factor for y in current_ylim])

    plt.draw()


def dot(v1, v2):
    return np.dot(v1, v2)


def cyrus_beck_clip(polygon, p1, p2):
    n = len(polygon)
    d = np.array(p2) - np.array(p1)  # направляющий вектор отрезка
    tE, tL = 0, 1  # начальные параметры входа и выхода
    entry_points, exit_points = [], []  # списки точек пересечения

    for i in range(n):
        edge_start = np.array(polygon[i])
        edge_end = np.array(polygon[(i + 1) % n])
        edge = edge_end - edge_start  # вектор стороны многоугольника
        normal = np.array([-edge[1], edge[0]])  # Нормаль к стороне

        w = np.array(p1) - edge_start  # вектор от начала стороны к началу отрезка

        num = np.dot(normal, w)  # числитель для вычисления t
        den = np.dot(normal, d)  # знаменатель

        # Проверка параллельности
        if den == 0:
            if num < 0:  # Отрезок полностью вне
                return None, (p1, p2), entry_points, exit_points
            else:
                continue  # Параллелен и внутри/на границе

        t = -num / den  # параметр пересечения

        # Все точки пересечения добавляются в списки
        intersection_point = p1 + t * d
        if den > 0:  # Входная точка
            tE = max(tE, t)
            entry_points.append(intersection_point)
        else:  # Выходная точка
            tL = min(tL, t)
            exit_points.append(intersection_point)

    if tE > tL:  # Нет видимой части
        return None, (p1, p2), entry_points, exit_points

    # Вычисляем конечные точки видимого отрезка
    clipped_segment = (p1 + tE * d, p1 + tL * d)
    return clipped_segment, (p1, p2), entry_points, exit_points


def plot_clipping(polygon, original_segment, clipped_segment, entry_points, exit_points):
    polygon = np.array(polygon)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot(*polygon.T, 'b-', label='Polygon')
    ax.plot([polygon[-1][0], polygon[0][0]], [polygon[-1][1], polygon[0][1]], 'b-')

    if original_segment:
        ax.plot([original_segment[0][0], original_segment[1][0]], [original_segment[0][1], original_segment[1][1]],
                'g--', label='Original Segment')

    if clipped_segment:
        ax.plot([clipped_segment[0][0], clipped_segment[1][0]], [clipped_segment[0][1], clipped_segment[1][1]], 'y-',
                linewidth=2, label='Clipped Segment')

    for pt in entry_points:
        ax.plot(pt[0], pt[1], 'ro', label=f'Entry Point ({pt[0]:.2f}, {pt[1]:.2f})')

    for pt in exit_points:
        ax.plot(pt[0], pt[1], 'go', label=f'Exit Point ({pt[0]:.2f}, {pt[1]:.2f})')

    ax.legend()
    ax.grid()
    ax.set_xlim(min(polygon[:, 0]) - 1, max(polygon[:, 0]) + 1)
    ax.set_ylim(min(polygon[:, 1]) - 1, max(polygon[:, 1]) + 1)

    fig.canvas.mpl_connect('scroll_event', on_scroll)
    plt.show()


# Пример использования
polygon = [(1, 1), (5, 1), (6, 3), (5, 5), (2, 5), (1, 3)]
p1, p2 = (0, 0), (9, 6)
clipped, original, entries, exits = cyrus_beck_clip(polygon, p1, p2)
plot_clipping(polygon, original, clipped, entries, exits)
