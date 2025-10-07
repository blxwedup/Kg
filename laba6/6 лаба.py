import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from matplotlib.patches import Polygon

def main():
    # Входные данные: координаты вершин многоугольника (замкнутый контур)
    # Задаём вершины многоугольника в порядке обхода (последняя точка = первой)
    polygon = np.array([
        [50, 50],    # Вершина 1
        [200, 100],   # Вершина 2
        [150, 200],   # Вершина 3
        [100, 150],   # Вершина 4
        [50, 50]      # Замыкаем многоугольник (совпадает с вершиной 1)
    ])

    # Инициализация изображения (белый фон)
    # width, height - размеры изображения в пикселях
    width, height = 250, 250
    # Создаём массив пикселей (1 = белый, 0 = чёрный)
    image = np.ones((height, width), dtype=np.uint8)

    # Создаём список всех рёбер (исключая горизонтальные)
    edges = []
    # Проходим по всем вершинам многоугольника
    for i in range(len(polygon) - 1):
        x1, y1 = polygon[i]     # Начало ребра
        x2, y2 = polygon[i + 1]  # Конец ребра
        if y1 != y2:  # Игнорируем горизонтальные рёбра
            edges.append((x1, y1, x2, y2))  # Добавляем ребро в список

    # Сортируем рёбра по минимальному Y для последовательной обработки
    edges.sort(key=lambda e: min(e[1], e[3]))

    # Подготовка данных для анимации (сохраняем кадры)
    frames_data = []

    # Шаг 0: Исходный многоугольник
    frames_data.append({
        "title": "Исходный многоугольник",  # Заголовок кадра
        "image": image.copy(),              # Копия изображения
        "current_edge": None,              # Текущее ребро, его ещё  нет
        "current_y": None                  # Текущая строка, её ещё нет
    })

    # Шаги 1..N: Обработка каждого ребра построчно
    for edge_idx, edge in enumerate(edges):
        x1, y1, x2, y2 = edge  # Координаты текущего ребра
        y_min, y_max = min(y1, y2), max(y1, y2)  # Диапазон Y для ребра
        
        # Обрабатываем каждую строку Y в ребре
        for y in range(y_min, y_max):
            if y1 == y2:
                continue  # Горизонтальные рёбра пропускаем
            
            # Вычисляем X-координату на ребре для текущего Y
            # t - параметр интерполяции (0 в начале ребра, 1 в конце)
            t = (y - y1) / (y2 - y1) if y2 != y1 else 0
            # Вычисляем X-координату пересечения ребра с текущей строкой Y
            x_edge = int(x1 + t * (x2 - x1))
            
            # Инвертируем пиксели справа от ребра (XOR)
            for x in range(x_edge, width):
                image[y, x] ^= 1  # XOR: 1→0 (белый→чёрный), 0→1 (чёрный→белый)
            
            # Сохраняем каждый 2-й Y, а также первый и последний Y в ребре
            if y % 2 == 0 or y == y_min or y == y_max:
                frames_data.append({
                    "title": f"Ребро {edge_idx + 1}, Y = {y}",  # Заголовок
                    "image": image.copy(),                       # Текущее изображение
                    "current_edge": edge,                        # Текущее ребро
                    "current_y": y                               # Текущая строка Y
                })

    # Финальный кадр: Готовый результат
    frames_data.append({
        "title": "Результат: Закрашенный многоугольник",
        "image": image.copy(),
        "current_edge": None,
        "current_y": None
    })

    # Создаём анимацию
    fig, ax = plt.subplots(figsize=(8, 8))  # Создаём фигуру 8x8 дюймов
    # Цветовая карта: 0 = чёрный, 1 = белый
    cmap = ListedColormap(['black', 'white'])
    # Создаём отображение изображения
    img_display = ax.imshow(image, cmap=cmap, interpolation='nearest')

    def update(frame):
        # Функция обновления кадра анимации
        data = frames_data[frame]  # Данные текущего кадра
        img_display.set_array(data["image"])  # Обновляем изображение
        ax.clear()  # Очищаем оси
        
        # Отображаем изображение
        ax.imshow(data["image"], cmap=cmap, interpolation='nearest')
        
        # Рисуем границы многоугольника синей линией
        ax.plot(polygon[:, 0], polygon[:, 1], 'b-', linewidth=2)
        
        # Подсвечиваем текущее ребро (если есть)
        if data["current_edge"] is not None:
            x1, y1, x2, y2 = data["current_edge"]
            # Рисуем текущее ребро красной линией
            ax.plot([x1, x2], [y1, y2], 'r-', linewidth=3)
            
            # Подсвечиваем текущую строку Y зелёной пунктирной линией
            ax.axhline(y=data["current_y"], color='green', linestyle='--', alpha=0.5)
            
            # Вычисляем точку пересечения ребра с текущей строкой Y
            t = (data["current_y"] - y1) / (y2 - y1) if y2 != y1 else 0
            x_edge = int(x1 + t * (x2 - x1))
            # Рисуем точку пересечения красным кружком
            ax.plot(x_edge, data["current_y"], 'ro')
        
        # Устанавливаем заголовок
        ax.set_title(data["title"])
        # Устанавливаем границы отображения
        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)  # Ось Y направлена вниз
        return []

    # Запуск анимации
    ani = animation.FuncAnimation(
        fig,                # Фигура для анимации
        update,             # Функция обновления
        frames=len(frames_data),  # Число кадров
        interval=200,       # Интервал между кадрами (мс)
        repeat=False        # Не повторять анимацию
    )
    plt.show()  # Показать анимацию

if __name__ == "__main__":
    main()