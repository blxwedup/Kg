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


def compute_code(x, y, x_min, y_min, x_max, y_max):
    """Вычисление регионного кода для точки (x, y)"""
    # Каждый бит кода указывает положение точки относительно одной из границ
    code = 0b0000
    if x < x_min:
        code |= 0b0001  # Лево
    elif x > x_max:
        code |= 0b0010  # Право
    if y < y_min:
        code |= 0b0100  # Низ
    elif y > y_max:
        code |= 0b1000  # Верх
    # Если точка внутри прямоугольника, код будет 0000
    return code


def sutherland_cohen_clip(rect, p1, p2):
    """Алгоритм отсечения Сазерленда-Коэна"""
    x_min, y_min, x_max, y_max = rect
    x1, y1 = p1
    x2, y2 = p2

    code1 = compute_code(x1, y1, x_min, y_min, x_max, y_max)
    code2 = compute_code(x2, y2, x_min, y_min, x_max, y_max)
    accept = False
    intersection_points = []  # Все точки пересечения

    while True:
        # Если оба кода 0000 - отрезок полностью видимый
        if code1 == 0 and code2 == 0:
            accept = True
            break
        # Если побитовое И кодов не равно 0 - отрезок полностью невидимый
        elif code1 & code2 != 0:
            break
        else:
            # Выбираем точку вне прямоугольника
            code_out = code1 if code1 != 0 else code2
            x, y = 0, 0

            # Находим точку пересечения
            if code_out & 0b1000:  # Верх
                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max
            elif code_out & 0b0100:  # Низ
                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min
            elif code_out & 0b0010:  # Право
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x = x_max
            elif code_out & 0b0001:  # Лево
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x = x_min

            # Сохраняем точку пересечения
            intersection_points.append((x, y))

            # Заменяем точку вне прямоугольника на точку пересечения
            if code_out == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1, x_min, y_min, x_max, y_max)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2, x_min, y_min, x_max, y_max)

    if accept:
        return ((x1, y1), (x2, y2)), intersection_points
    else:
        return None, intersection_points


def plot_clipping(rect, original_segment, clipped_segment, intersection_points):
    """Визуализация отсечения"""
    x_min, y_min, x_max, y_max = rect
    fig, ax = plt.subplots(figsize=(10, 8))

    # Рисуем прямоугольник (окно отсечения)
    rect_poly = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
    rect_poly = np.array(rect_poly)
    ax.plot(*rect_poly.T, 'b-', linewidth=1, label='Окно отсечения')
    ax.plot([rect_poly[-1][0], rect_poly[0][0]], [rect_poly[-1][1], rect_poly[0][1]], 'b-')

    # Рисуем исходный отрезок
    if original_segment:
        p1, p2 = original_segment
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'g--', label='Исходный отрезок')

    # Рисуем отсеченный отрезок
    if clipped_segment:
        p1, p2 = clipped_segment
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'y-', linewidth=2, label='Видимая часть')

    # Рисуем точки пересечения
    if intersection_points:
        for i, (x, y) in enumerate(intersection_points):
            point_label = f'Точка {i + 1}: ({x:.2f}, {y:.2f})'
            ax.plot(x, y, 'ro', markersize=5, label=point_label)
            ax.text(x, y, f' {i + 1}', fontsize=12, va='bottom', ha='left')

    # Настройки графика
    ax.legend()
    ax.grid(True)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Алгоритм Сазерленда-Коэна для отсечения отрезка')

    # Подключаем обработчик скролла
    fig.canvas.mpl_connect('scroll_event', on_scroll)

    plt.show()


# Пример использования
if __name__ == "__main__":
    # Прямоугольник отсечения (x_min, y_min, x_max, y_max)
    rectangle = (2, 2, 8, 6)

    # Отрезок для отсечения (p1, p2)
    segment = ((1, 2), (9, 8))

    # Выполняем отсечение
    clipped_segment, intersections = sutherland_cohen_clip(rectangle, *segment)

    # Визуализируем результат
    plot_clipping(rectangle, segment, clipped_segment, intersections)