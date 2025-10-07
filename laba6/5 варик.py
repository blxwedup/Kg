import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def cross_product(O, A, B):
    """Векторное произведение: > 0 если B слева от OA, < 0 если справа"""
    return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])


# Глобальные переменные для визуализации
visualization_steps = []
step_counter = [0]


def convex_hull_divide_conquer(points):
    """
    Строит выпуклую оболочку методом разделяй и властвуй
    Возвращает упорядоченный список индексов точек оболочки
    """
    global visualization_steps, step_counter
    visualization_steps = []
    step_counter[0] = 0

    points = np.array(points)
    n = len(points)

    # Создаём список индексов для отслеживания
    indices = list(range(n))

    # Сортируем точки по X, затем по Y
    sorted_indices = sorted(indices, key=lambda i: (points[i][0], points[i][1]))

    print("=" * 70)
    print("АЛГОРИТМ РАЗДЕЛЯЙ И ВЛАСТВУЙ")
    print("=" * 70)
    print(f"Всего точек: {n}")
    print(f"Принцип: рекурсивно делим на две части, строим оболочки,")
    print(f"         затем объединяем их через верхнюю и нижнюю касательные")
    print("=" * 70)

    # Сохраняем начальный шаг
    visualization_steps.append({
        'type': 'start',
        'all_points': sorted_indices,
        'message': 'Сортировка точек по X-координате'
    })

    # Рекурсивный алгоритм
    hull_indices = divide_and_conquer_recursive(points, sorted_indices, depth=0)

    print(f"\n{'=' * 70}")
    print(f"ПОСТРОЕНИЕ ЗАВЕРШЕНО!")
    print(f"Точек в оболочке: {len(hull_indices)}")
    print(f"{'=' * 70}\n")

    # Финальный шаг
    visualization_steps.append({
        'type': 'final',
        'hull': hull_indices
    })

    return hull_indices, visualization_steps, points


def divide_and_conquer_recursive(points, indices, depth=0):
    """Рекурсивная функция разделяй и властвуй"""
    global visualization_steps, step_counter

    n = len(indices)
    indent = "  " * depth

    # Базовый случай: 1-3 точки
    if n <= 3:
        hull = convex_hull_base_case(points, indices)

        step_counter[0] += 1
        print(f"\n{indent}[Шаг {step_counter[0]}] Базовый случай: {n} точки")
        print(f"{indent}Точки: {[f'P{i}' for i in indices]}")
        print(f"{indent}Оболочка: {[f'P{i}' for i in hull]}")

        visualization_steps.append({
            'type': 'base_case',
            'indices': indices,
            'hull': hull,
            'depth': depth,
            'step': step_counter[0]
        })

        return hull

    # Разделяем пополам
    mid = n // 2
    left_indices = indices[:mid]
    right_indices = indices[mid:]

    step_counter[0] += 1
    print(f"\n{indent}[Шаг {step_counter[0]}] РАЗДЕЛЕНИЕ на уровне {depth}")
    print(f"{indent}Всего точек: {n}")
    print(f"{indent}Левая часть ({len(left_indices)}): {[f'P{i}' for i in left_indices]}")
    print(f"{indent}Правая часть ({len(right_indices)}): {[f'P{i}' for i in right_indices]}")

    visualization_steps.append({
        'type': 'divide',
        'left': left_indices,
        'right': right_indices,
        'depth': depth,
        'step': step_counter[0]
    })

    # Рекурсивно строим оболочки
    left_hull = divide_and_conquer_recursive(points, left_indices, depth + 1)
    right_hull = divide_and_conquer_recursive(points, right_indices, depth + 1)

    # Объединяем оболочки
    step_counter[0] += 1
    print(f"\n{indent}[Шаг {step_counter[0]}] ОБЪЕДИНЕНИЕ на уровне {depth}")
    print(f"{indent}Левая оболочка ({len(left_hull)}): {[f'P{i}' for i in left_hull]}")
    print(f"{indent}Правая оболочка ({len(right_hull)}): {[f'P{i}' for i in right_hull]}")

    merged_hull = merge_hulls(points, left_hull, right_hull, depth)

    print(f"{indent}Результат объединения ({len(merged_hull)}): {[f'P{i}' for i in merged_hull]}")

    return merged_hull


def convex_hull_base_case(points, indices):
    """Обработка базового случая: 1-3 точки"""
    n = len(indices)

    if n == 1:
        return indices
    elif n == 2:
        return indices
    else:  # n == 3
        # Упорядочиваем против часовой стрелки
        i0, i1, i2 = indices
        cross = cross_product(points[i0], points[i1], points[i2])
        if cross > 0:  # Против часовой
            return [i0, i1, i2]
        else:  # По часовой - разворачиваем
            return [i0, i2, i1]


def merge_hulls(points, left_hull, right_hull, depth):
    """Объединяет две выпуклые оболочки"""
    global visualization_steps, step_counter

    # Находим верхнюю касательную
    upper_left, upper_right = find_upper_tangent(points, left_hull, right_hull)

    step_counter[0] += 1
    print(f"{'  ' * depth}  → Верхняя касательная: P{upper_left} -- P{upper_right}")

    visualization_steps.append({
        'type': 'upper_tangent',
        'left_hull': left_hull,
        'right_hull': right_hull,
        'tangent': (upper_left, upper_right),
        'depth': depth,
        'step': step_counter[0]
    })

    # Находим нижнюю касательную
    lower_left, lower_right = find_lower_tangent(points, left_hull, right_hull)

    step_counter[0] += 1
    print(f"{'  ' * depth}  → Нижняя касательная: P{lower_left} -- P{lower_right}")

    visualization_steps.append({
        'type': 'lower_tangent',
        'left_hull': left_hull,
        'right_hull': right_hull,
        'upper_tangent': (upper_left, upper_right),
        'lower_tangent': (lower_left, lower_right),
        'depth': depth,
        'step': step_counter[0]
    })

    # Строим объединённую оболочку
    merged = []

    # Начинаем с верхней касательной на левой оболочке
    idx = left_hull.index(upper_left)
    while True:
        current = left_hull[idx]
        merged.append(current)
        if current == lower_left:
            break
        idx = (idx + 1) % len(left_hull)

    # Продолжаем по правой оболочке
    idx = right_hull.index(lower_right)
    while True:
        current = right_hull[idx]
        merged.append(current)
        if current == upper_right:
            break
        idx = (idx + 1) % len(right_hull)

    step_counter[0] += 1
    visualization_steps.append({
        'type': 'merge_complete',
        'merged_hull': merged,
        'depth': depth,
        'step': step_counter[0]
    })

    return merged


def find_upper_tangent(points, left_hull, right_hull):
    """Находит верхнюю касательную между двумя оболочками"""
    # Начинаем с самой правой точки левой оболочки и самой левой правой
    left_idx = max(range(len(left_hull)), key=lambda i: points[left_hull[i]][0])
    right_idx = min(range(len(right_hull)), key=lambda i: points[right_hull[i]][0])

    n_left = len(left_hull)
    n_right = len(right_hull)

    changed = True
    while changed:
        changed = False

        # Двигаем левую точку вверх
        while True:
            next_left = (left_idx - 1) % n_left
            if cross_product(points[left_hull[left_idx]],
                             points[right_hull[right_idx]],
                             points[left_hull[next_left]]) <= 0:
                left_idx = next_left
                changed = True
            else:
                break

        # Двигаем правую точку вверх
        while True:
            next_right = (right_idx + 1) % n_right
            if cross_product(points[right_hull[right_idx]],
                             points[left_hull[left_idx]],
                             points[right_hull[next_right]]) >= 0:
                right_idx = next_right
                changed = True
            else:
                break

    return left_hull[left_idx], right_hull[right_idx]


def find_lower_tangent(points, left_hull, right_hull):
    """Находит нижнюю касательную между двумя оболочками"""
    # Начинаем с самой правой точки левой оболочки и самой левой правой
    left_idx = max(range(len(left_hull)), key=lambda i: points[left_hull[i]][0])
    right_idx = min(range(len(right_hull)), key=lambda i: points[right_hull[i]][0])

    n_left = len(left_hull)
    n_right = len(right_hull)

    changed = True
    while changed:
        changed = False

        # Двигаем левую точку вниз
        while True:
            next_left = (left_idx + 1) % n_left
            if cross_product(points[left_hull[left_idx]],
                             points[right_hull[right_idx]],
                             points[left_hull[next_left]]) >= 0:
                left_idx = next_left
                changed = True
            else:
                break

        # Двигаем правую точку вниз
        while True:
            next_right = (right_idx - 1) % n_right
            if cross_product(points[right_hull[right_idx]],
                             points[left_hull[left_idx]],
                             points[right_hull[next_right]]) <= 0:
                right_idx = next_right
                changed = True
            else:
                break

    return left_hull[left_idx], right_hull[right_idx]


def draw_convex_hull(points, hull_indices):
    """Рисует итоговую выпуклую оболочку"""
    fig, ax = plt.subplots(figsize=(10, 8))

    # Точки
    ax.scatter(points[:, 0], points[:, 1], c='blue', s=150,
               zorder=5, edgecolors='black', linewidth=2)

    # Подписи
    for i, point in enumerate(points):
        ax.annotate(f'P{i}', (point[0], point[1]),
                    xytext=(8, 8), textcoords='offset points',
                    fontsize=12, fontweight='bold')

    # Рёбра оболочки
    n = len(hull_indices)
    for i in range(n):
        j = (i + 1) % n
        ax.plot([points[hull_indices[i], 0], points[hull_indices[j], 0]],
                [points[hull_indices[i], 1], points[hull_indices[j], 1]],
                'r-', linewidth=3, alpha=0.7)

    # Заливка
    hull_coords = points[hull_indices]
    ax.fill(hull_coords[:, 0], hull_coords[:, 1], 'red', alpha=0.1)

    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_title('Выпуклая оболочка (разделяй и властвуй)',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')
    plt.tight_layout()
    plt.show()


def animate_divide_conquer(points, steps, interval=2000):
    """Анимация алгоритма разделяй и властвуй"""
    fig, ax = plt.subplots(figsize=(14, 10))

    def animate(frame):
        if frame >= len(steps):
            return []

        step = steps[frame]
        ax.clear()
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')

        step_type = step['type']

        if step_type == 'start':
            # Начальное состояние
            ax.scatter(points[:, 0], points[:, 1], c='blue', s=150,
                       zorder=5, edgecolors='black', linewidth=2)
            for i in range(len(points)):
                ax.annotate(f'P{i}', (points[i, 0], points[i, 1]),
                            xytext=(8, 8), textcoords='offset points',
                            fontsize=11, fontweight='bold')
            ax.set_title('Начало: сортировка точек по X-координате',
                         fontsize=13, fontweight='bold', color='darkblue')

        elif step_type == 'divide':
            # Показываем разделение
            left = step['left']
            right = step['right']
            depth = step['depth']

            # Все точки
            for i in range(len(points)):
                if i in left:
                    color = 'lightcoral'
                    label = 'Левая'
                elif i in right:
                    color = 'lightgreen'
                    label = 'Правая'
                else:
                    color = 'lightgray'
                    label = ''

                ax.scatter(points[i, 0], points[i, 1], c=color, s=150,
                           zorder=5, edgecolors='black', linewidth=2)
                ax.annotate(f'P{i}', (points[i, 0], points[i, 1]),
                            xytext=(8, 8), textcoords='offset points',
                            fontsize=10, fontweight='bold')

            ax.set_title(f'Шаг {step["step"]}: РАЗДЕЛЕНИЕ (уровень {depth})\n'
                         f'Левая: {len(left)} точек, Правая: {len(right)} точек',
                         fontsize=13, fontweight='bold', color='purple')

        elif step_type == 'base_case':
            # Базовый случай
            indices = step['indices']
            hull = step['hull']

            # Все точки серые
            ax.scatter(points[:, 0], points[:, 1], c='lightgray', s=100,
                       zorder=3, edgecolors='gray', linewidth=1)

            # Текущие точки синие
            for i in indices:
                ax.scatter(points[i, 0], points[i, 1], c='blue', s=180,
                           zorder=5, edgecolors='black', linewidth=2)
                ax.annotate(f'P{i}', (points[i, 0], points[i, 1]),
                            xytext=(8, 8), textcoords='offset points',
                            fontsize=11, fontweight='bold')

            # Оболочка для базового случая
            n = len(hull)
            if n > 1:
                for i in range(n):
                    j = (i + 1) % n
                    ax.plot([points[hull[i], 0], points[hull[j], 0]],
                            [points[hull[i], 1], points[hull[j], 1]],
                            'g-', linewidth=2.5, alpha=0.7, zorder=4)

            ax.set_title(f'Шаг {step["step"]}: БАЗОВЫЙ СЛУЧАЙ\n'
                         f'{len(indices)} точки → оболочка из {len(hull)} точек',
                         fontsize=13, fontweight='bold', color='darkgreen')

        elif step_type == 'upper_tangent':
            # Верхняя касательная
            left_hull = step['left_hull']
            right_hull = step['right_hull']
            tangent = step['tangent']

            # Все точки серые
            ax.scatter(points[:, 0], points[:, 1], c='lightgray', s=100,
                       zorder=3, edgecolors='gray', linewidth=1)

            # Левая оболочка
            for i in range(len(left_hull)):
                j = (i + 1) % len(left_hull)
                ax.plot([points[left_hull[i], 0], points[left_hull[j], 0]],
                        [points[left_hull[i], 1], points[left_hull[j], 1]],
                        'red', linewidth=2, alpha=0.5, zorder=4, linestyle='--')

            for idx in left_hull:
                ax.scatter(points[idx, 0], points[idx, 1], c='lightcoral', s=140,
                           zorder=5, edgecolors='red', linewidth=2)

            # Правая оболочка
            for i in range(len(right_hull)):
                j = (i + 1) % len(right_hull)
                ax.plot([points[right_hull[i], 0], points[right_hull[j], 0]],
                        [points[right_hull[i], 1], points[right_hull[j], 1]],
                        'green', linewidth=2, alpha=0.5, zorder=4, linestyle='--')

            for idx in right_hull:
                ax.scatter(points[idx, 0], points[idx, 1], c='lightgreen', s=140,
                           zorder=5, edgecolors='green', linewidth=2)

            # Верхняя касательная
            ax.plot([points[tangent[0], 0], points[tangent[1], 0]],
                    [points[tangent[0], 1], points[tangent[1], 1]],
                    'blue', linewidth=4, alpha=0.9, zorder=6)

            ax.scatter([points[tangent[0], 0], points[tangent[1], 0]],
                       [points[tangent[0], 1], points[tangent[1], 1]],
                       c='blue', s=200, zorder=7, edgecolors='darkblue', linewidth=2)

            # Подписи
            for i in range(len(points)):
                ax.annotate(f'P{i}', (points[i, 0], points[i, 1]),
                            xytext=(8, 8), textcoords='offset points',
                            fontsize=9, fontweight='bold')

            ax.set_title(f'Шаг {step["step"]}: ВЕРХНЯЯ КАСАТЕЛЬНАЯ\n'
                         f'P{tangent[0]} -- P{tangent[1]}',
                         fontsize=13, fontweight='bold', color='blue')

        elif step_type == 'lower_tangent':
            # Нижняя касательная
            left_hull = step['left_hull']
            right_hull = step['right_hull']
            upper = step['upper_tangent']
            lower = step['lower_tangent']

            # Все точки серые
            ax.scatter(points[:, 0], points[:, 1], c='lightgray', s=100,
                       zorder=3, edgecolors='gray', linewidth=1)

            # Левая оболочка
            for i in range(len(left_hull)):
                j = (i + 1) % len(left_hull)
                ax.plot([points[left_hull[i], 0], points[left_hull[j], 0]],
                        [points[left_hull[i], 1], points[left_hull[j], 1]],
                        'red', linewidth=2, alpha=0.3, zorder=4, linestyle='--')

            # Правая оболочка
            for i in range(len(right_hull)):
                j = (i + 1) % len(right_hull)
                ax.plot([points[right_hull[i], 0], points[right_hull[j], 0]],
                        [points[right_hull[i], 1], points[right_hull[j], 1]],
                        'green', linewidth=2, alpha=0.3, zorder=4, linestyle='--')

            # Верхняя касательная (светлая)
            ax.plot([points[upper[0], 0], points[upper[1], 0]],
                    [points[upper[0], 1], points[upper[1], 1]],
                    'blue', linewidth=3, alpha=0.4, zorder=5)

            # Нижняя касательная (яркая)
            ax.plot([points[lower[0], 0], points[lower[1], 0]],
                    [points[lower[0], 1], points[lower[1], 1]],
                    'orange', linewidth=4, alpha=0.9, zorder=6)

            ax.scatter([points[lower[0], 0], points[lower[1], 0]],
                       [points[lower[0], 1], points[lower[1], 1]],
                       c='orange', s=200, zorder=7, edgecolors='darkorange', linewidth=2)

            # Подписи
            for i in range(len(points)):
                ax.annotate(f'P{i}', (points[i, 0], points[i, 1]),
                            xytext=(8, 8), textcoords='offset points',
                            fontsize=9, fontweight='bold')

            ax.set_title(f'Шаг {step["step"]}: НИЖНЯЯ КАСАТЕЛЬНАЯ\n'
                         f'P{lower[0]} -- P{lower[1]}',
                         fontsize=13, fontweight='bold', color='orange')

        elif step_type == 'merge_complete':
            # Завершение объединения
            merged = step['merged_hull']

            # Все точки серые
            ax.scatter(points[:, 0], points[:, 1], c='lightgray', s=100,
                       zorder=3, edgecolors='gray', linewidth=1)

            # Объединённая оболочка
            n = len(merged)
            for i in range(n):
                j = (i + 1) % n
                ax.plot([points[merged[i], 0], points[merged[j], 0]],
                        [points[merged[i], 1], points[merged[j], 1]],
                        'purple', linewidth=3, alpha=0.7, zorder=5)

            for idx in merged:
                ax.scatter(points[idx, 0], points[idx, 1], c='mediumpurple', s=160,
                           zorder=6, edgecolors='purple', linewidth=2)

            # Заливка
            hull_coords = points[merged]
            ax.fill(hull_coords[:, 0], hull_coords[:, 1], 'purple', alpha=0.15, zorder=2)

            # Подписи
            for i in range(len(points)):
                ax.annotate(f'P{i}', (points[i, 0], points[i, 1]),
                            xytext=(8, 8), textcoords='offset points',
                            fontsize=10, fontweight='bold')

            ax.set_title(f'Шаг {step["step"]}: ОБЪЕДИНЕНИЕ ЗАВЕРШЕНО\n'
                         f'Оболочка из {len(merged)} точек',
                         fontsize=13, fontweight='bold', color='purple')

        elif step_type == 'final':
            # Финальный результат
            hull = step['hull']

            ax.scatter(points[:, 0], points[:, 1], c='blue', s=150,
                       zorder=5, edgecolors='black', linewidth=2)

            # Оболочка
            n = len(hull)
            for i in range(n):
                j = (i + 1) % n
                ax.plot([points[hull[i], 0], points[hull[j], 0]],
                        [points[hull[i], 1], points[hull[j], 1]],
                        'red', linewidth=3.5, alpha=0.8, zorder=4)

            # Заливка
            hull_coords = points[hull]
            ax.fill(hull_coords[:, 0], hull_coords[:, 1], 'red', alpha=0.15, zorder=2)

            # Подписи
            for i in range(len(points)):
                ax.annotate(f'P{i}', (points[i, 0], points[i, 1]),
                            xytext=(8, 8), textcoords='offset points',
                            fontsize=11, fontweight='bold')

            ax.set_title('ВЫПУКЛАЯ ОБОЛОЧКА ПОСТРОЕНА!\n'
                         f'Алгоритм разделяй и властвуй: {len(hull)} точек в оболочке',
                         fontsize=14, fontweight='bold', color='darkgreen')

        plt.tight_layout()
        return []

    anim = FuncAnimation(fig, animate, frames=len(steps),
                         interval=interval, repeat=True, blit=True)
    plt.show()


def main():
    print("\n" + "=" * 70)
    print("  ВЫПУКЛАЯ ОБОЛОЧКА - АЛГОРИТМ РАЗДЕЛЯЙ И ВЛАСТВУЙ")
    print("=" * 70 + "\n")

    # Набор точек
    points = [
        [0, 0],
        [1, 1],
        [2, 0],
        [3, 1],
        [1, 2],
        [2, 3],
        [0, 3],
        [1.5, 1.5]  # внутренняя точка
    ]

    print(f"Исходные точки ({len(points)} шт.):")
    for i, p in enumerate(points):
        print(f"  P{i}: {p}")
    print()

    # Строим оболочку
    hull_indices, steps, points_arr = convex_hull_divide_conquer(points)

    # Визуализация
    print("Показываем анимацию (закройте окно для итогового результата)...\n")
    animate_divide_conquer(points_arr, steps, interval=2000)

    print("Показываем итоговый результат...\n")
    draw_convex_hull(points_arr, hull_indices)


if __name__ == "__main__":
    main()

