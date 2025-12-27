#!/usr/bin/env python3
"""
Упрощенный скрипт для генерации базовых PWA иконок
Использует только Pillow без cairosvg
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw

def ensure_dir(path):
    """Создает директорию если не существует"""
    Path(path).mkdir(parents=True, exist_ok=True)

def create_book_icon(size, is_maskable=False):
    """Создает иконку книги"""
    # Создаем изображение с черным фоном
    img = Image.new('RGB', (size, size), color='#000000')
    draw = ImageDraw.Draw(img)

    # Рассчитываем размеры элементов
    if is_maskable:
        # Для maskable добавляем safe area (80% от размера)
        padding = size * 0.2
        book_size = size * 0.6
        offset = (size - book_size) / 2
    else:
        # Для обычных иконок используем больше пространства
        padding = size * 0.15
        book_size = size * 0.7
        offset = (size - book_size) / 2

    # Размеры книги
    book_width = book_size * 0.5
    book_height = book_size * 0.7
    book_x = offset + (book_size - book_width) / 2
    book_y = offset + (book_size - book_height) / 2

    # Рисуем левую страницу
    left_page = [
        (book_x, book_y),
        (book_x, book_y + book_height),
        (book_x + book_width/2, book_y + book_height - book_height*0.1),
        (book_x + book_width/2, book_y)
    ]
    draw.polygon(left_page, fill='#3b82f6', outline='#60a5fa')

    # Рисуем правую страницу
    right_page = [
        (book_x + book_width/2, book_y),
        (book_x + book_width/2, book_y + book_height - book_height*0.1),
        (book_x + book_width, book_y + book_height),
        (book_x + book_width, book_y)
    ]
    draw.polygon(right_page, fill='#1d4ed8', outline='#60a5fa')

    # Рисуем корешок книги (вертикальная линия по центру)
    draw.line(
        [(book_x + book_width/2, book_y),
         (book_x + book_width/2, book_y + book_height - book_height*0.1)],
        fill='#FFFFFF',
        width=max(1, size // 100)
    )

    # Рисуем текстовые линии на левой странице
    line_width = book_width * 0.2
    line_x = book_x + book_width * 0.15
    line_y_start = book_y + book_height * 0.2
    line_spacing = book_height * 0.12

    for i in range(3):
        opacity = int(255 * (0.6 - i * 0.1))
        color = f'#{opacity:02x}{opacity:02x}{opacity:02x}'
        y = line_y_start + i * line_spacing
        draw.line(
            [(line_x, y), (line_x + line_width, y)],
            fill=color,
            width=max(1, size // 80)
        )

    # Рисуем текстовые линии на правой странице
    line_x_right = book_x + book_width * 0.65
    for i in range(3):
        opacity = int(255 * (0.6 - i * 0.1))
        color = f'#{opacity:02x}{opacity:02x}{opacity:02x}'
        y = line_y_start + i * line_spacing
        draw.line(
            [(line_x_right, y), (line_x_right + line_width, y)],
            fill=color,
            width=max(1, size // 80)
        )

    return img

def main():
    """Основная функция генерации иконок"""
    base_dir = Path(__file__).parent
    static_dir = base_dir / 'static'
    icons_dir = static_dir / 'icons'

    ensure_dir(icons_dir)

    print("🎨 Генерация PWA иконок...\n")

    # Размеры для генерации
    icons_to_generate = [
        ('icon-192.png', 192, False),
        ('icon-512.png', 512, False),
        ('icon-maskable-192.png', 192, True),
        ('icon-maskable-512.png', 512, True),
        ('apple-touch-icon.png', 180, False),
        ('favicon-32.png', 32, False),
        ('favicon-16.png', 16, False),
    ]

    for filename, size, is_maskable in icons_to_generate:
        icon_type = "maskable" if is_maskable else "обычная"
        print(f"📦 Создание {icon_type} иконки: {filename} ({size}x{size})")

        img = create_book_icon(size, is_maskable)
        output_path = icons_dir / filename
        img.save(output_path, 'PNG', optimize=True)

        print(f"   ✓ Сохранена: {output_path}")

    print("\n✅ Генерация иконок завершена!")
    print(f"📁 Иконки сохранены в: {icons_dir}")
    print("\n💡 Примечание:")
    print("   Созданы базовые иконки с помощью Pillow.")
    print("   Для лучшего качества рекомендуется использовать:")
    print("   - https://realfavicongenerator.net/ (загрузите favicon.svg)")
    print("   - или установите cairo: brew install cairo (macOS)")

if __name__ == '__main__':
    main()
