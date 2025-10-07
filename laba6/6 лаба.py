import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def cross_product(O, A, B):
    """Векторное произведение: > 0 если B слева от OA, < 0 если справа"""
    return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])


def convex_hull_brute_force(points):
    """
    Строит выпуклую оболочку методом полного перебора
    Возвращает: (hull_edges, steps) - рёбра оболочки и шаги для визуализации
    """
    points = np.array(points)
    n = len(points)
    hull_edges = []
    steps = []

    print("=" * 70)
    print("АЛГОРИТМ ПОЛНОГО ПЕРЕБОРА")
    print("=" * 70)
    print(f"Всего точек: {n}")
    print(f"Принцип: ребро в оболочке, если все точки по одну сторону от него")
    print(f"Всего пар для проверки: {n * (n - 1) // 2}")
    print("=" * 70)

    pair_count = 0

    # Перебираем все пары точек
    for i in range(n):
        for j in range(i + 1, n):
            pair_count += 1
            p1, p2 = points[i], points[j]

            # Проверяем положение всех остальных точек
            point_sides = []
            left_count = 0
            right_count = 0

            for k in range(n):
                if k == i or k == j:
                    point_sides.append(0)
                    continue

                cross = cross_product(p1, p2, points[k])

                if abs(cross) < 1e-10:  # Коллинеарные
                    point_sides.append(0)
                elif cross > 0:
                    point_sides.append(1)  # Слева
                    left_count += 1
                else:
                    point_sides.append(-1)  # Справа
                    right_count += 1

            # Ребро валидно, если все точки с одной стороны
            is_valid = (left_count == 0 or right_count == 0)

            # Сохраняем шаг
            steps.append({
                'p1_idx': i, 'p2_idx': j,
                'is_valid': is_valid,
                'point_sides': point_sides,
                'pair_number': pair_count
            })

            print(f"\n[Пара {pair_count}] P{i}{p1} -- P{j}{p2}")
            for k in range(n):
                if k != i and k != j and point_sides[k] != 0:
                    side = "СЛЕВА" if point_sides[k] > 0 else "СПРАВА"
                    print(f"  P{k}: {side}")

            if is_valid:
                hull_edges.append((i, j))
                print(f"  ✓ Часть оболочки")
            else:
                print(f"  ✗ Не часть оболочки")

    print(f"\n{'=' * 70}")
    print(f"Найдено рёбер: {len(hull_edges)}")
    print(f"{'=' * 70}\n")

    return hull_edges, steps, points


def draw_convex_hull(points, hull_edges):
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
    for i, j in hull_edges:
        ax.plot([points[i, 0], points[j, 0]],
                [points[i, 1], points[j, 1]],
                'r-', linewidth=3, alpha=0.7)

    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_title('Выпуклая оболочка (алгоритм полного перебора)',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')
    plt.tight_layout()
    plt.show()


def animate_convex_hull(points, steps, interval=1500):
    """Пошаговая анимация построения оболочки"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    def animate(frame):
        if frame >= len(steps):
            return []

        step = steps[frame]

        # Левый график - текущая проверка
        ax1.clear()
        ax1.set_xlabel('X', fontsize=11)
        ax1.set_ylabel('Y', fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal', adjustable='box')

        # Правый график - накопленный результат
        ax2.clear()
        ax2.set_xlabel('X', fontsize=11)
        ax2.set_ylabel('Y', fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal', adjustable='box')

        p1_idx = step['p1_idx']
        p2_idx = step['p2_idx']

        # Рисуем точки на левом графике с цветовой кодировкой
        for i, point in enumerate(points):
            if i == p1_idx or i == p2_idx:
                color = 'orange'
                size = 200
            else:
                if step['point_sides'][i] > 0:
                    color = 'lightgreen'  # Слева
                elif step['point_sides'][i] < 0:
                    color = 'lightcoral'  # Справа
                else:
                    color = 'lightgray'  # На прямой
                size = 150

            ax1.scatter(point[0], point[1], c=color, s=size,
                        zorder=5, edgecolors='black', linewidth=1.5)
            ax1.annotate(f'P{i}', (point[0], point[1]),
                         xytext=(5, 5), textcoords='offset points',
                         fontsize=10, fontweight='bold')

        # Проверяемое ребро
        p1, p2 = points[p1_idx], points[p2_idx]
        color = 'green' if step['is_valid'] else 'red'
        linestyle = '-' if step['is_valid'] else '--'
        ax1.plot([p1[0], p2[0]], [p1[1], p2[1]],
                 color=color, linewidth=3, linestyle=linestyle, alpha=0.8, zorder=3)

        status = "✓ ЧАСТЬ ОБОЛОЧКИ" if step['is_valid'] else "✗ НЕ ЧАСТЬ ОБОЛОЧКИ"
        ax1.set_title(f"Шаг {step['pair_number']}: P{p1_idx} -- P{p2_idx}\n{status}",
                      fontsize=12, fontweight='bold',
                      color='green' if step['is_valid'] else 'red')

        # Правый график - накопленные рёбра
        ax2.scatter(points[:, 0], points[:, 1], c='blue', s=100,
                    zorder=5, edgecolors='black', linewidth=1)

        for i, point in enumerate(points):
            ax2.annotate(f'P{i}', (point[0], point[1]),
                         xytext=(5, 5), textcoords='offset points',
                         fontsize=10, fontweight='bold')

        # Все найденные рёбра до текущего момента
        edges_so_far = [(s['p1_idx'], s['p2_idx'])
                        for s in steps[:frame + 1] if s['is_valid']]

        for i, j in edges_so_far:
            ax2.plot([points[i, 0], points[j, 0]],
                     [points[i, 1], points[j, 1]],
                     'green', linewidth=2.5, alpha=0.7, zorder=3)

        ax2.set_title(f"Найдено рёбер: {len(edges_so_far)}",
                      fontsize=12, fontweight='bold')

        fig.suptitle('Алгоритм полного перебора',
                     fontsize=14, fontweight='bold')
        plt.tight_layout()

        return []

    anim = FuncAnimation(fig, animate, frames=len(steps),
                         interval=interval, repeat=True, blit=True)
    plt.show()


def main():
    print("\n" + "=" * 70)
    print("  ВЫПУКЛАЯ ОБОЛОЧКА - АЛГОРИТМ ПОЛНОГО ПЕРЕБОРА")
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
    hull_edges, steps, points_arr = convex_hull_brute_force(points)

    # Визуализация
    print("Показываем анимацию (закройте окно для итогового результата)...\n")
    animate_convex_hull(points_arr, steps, interval=1500)

    print("Показываем итоговый результат...\n")
    draw_convex_hull(points_arr, hull_edges)


if __name__ == "__main__":
    main()

