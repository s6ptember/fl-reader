#!/usr/bin/env python3
"""
Скрипт для генерации PWA иконок из SVG
Требует: pip install cairosvg pillow
"""

import os
from pathlib import Path

try:
    import cairosvg
    from PIL import Image
    import io
except ImportError:
    print("Установите необходимые зависимости:")
    print("pip install cairosvg pillow")
    exit(1)


def ensure_dir(path):
    """Создает директорию если не существует"""
    Path(path).mkdir(parents=True, exist_ok=True)


def svg_to_png(svg_path, output_path, size):
    """Конвертирует SVG в PNG заданного размера"""
    try:
        # Конвертируем SVG в PNG с помощью cairosvg
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size,
        )

        # Сохраняем PNG
        with open(output_path, 'wb') as f:
            f.write(png_data)

        print(f"✓ Создана иконка: {output_path} ({size}x{size})")
        return True
    except Exception as e:
        print(f"✗ Ошибка при создании {output_path}: {e}")
        return False


def create_maskable_svg(source_svg, output_svg):
    """Создает maskable версию SVG с safe area"""
    # Читаем оригинальный SVG
    with open(source_svg, 'r') as f:
        svg_content = f.read()

    # Создаем версию для maskable (без закругленных углов, с padding)
    maskable_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="bookGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1d4ed8;stop-opacity:1" />
    </linearGradient>
  </defs>

  <!-- Черный фон без закругления для maskable -->
  <rect width="100" height="100" fill="#000000"/>

  <!-- Книга в центре с padding для safe area (80% от размера) -->
  <g transform="translate(20, 20) scale(0.6)">
    <path d="M 30 25 L 30 75 L 50 70 L 70 75 L 70 25 Z"
          fill="url(#bookGradient)"
          stroke="#60a5fa"
          stroke-width="1.5"/>

    <line x1="50" y1="25" x2="50" y2="70"
          stroke="rgba(255,255,255,0.3)"
          stroke-width="1"/>

    <line x1="35" y1="35" x2="45" y2="35"
          stroke="rgba(255,255,255,0.6)"
          stroke-width="1.5"
          stroke-linecap="round"/>
    <line x1="35" y1="42" x2="45" y2="42"
          stroke="rgba(255,255,255,0.5)"
          stroke-width="1.5"
          stroke-linecap="round"/>
    <line x1="35" y1="49" x2="45" y2="49"
          stroke="rgba(255,255,255,0.4)"
          stroke-width="1.5"
          stroke-linecap="round"/>

    <line x1="55" y1="35" x2="65" y2="35"
          stroke="rgba(255,255,255,0.6)"
          stroke-width="1.5"
          stroke-linecap="round"/>
    <line x1="55" y1="42" x2="65" y2="42"
          stroke="rgba(255,255,255,0.5)"
          stroke-width="1.5"
          stroke-linecap="round"/>
    <line x1="55" y1="49" x2="65" y2="49"
          stroke="rgba(255,255,255,0.4)"
          stroke-width="1.5"
          stroke-linecap="round"/>
  </g>
</svg>"""

    with open(output_svg, 'w') as f:
        f.write(maskable_svg)

    print(f"✓ Создан maskable SVG: {output_svg}")


def main():
    """Основная функция генерации иконок"""
    # Пути
    base_dir = Path(__file__).parent
    static_dir = base_dir / 'static'
    icons_dir = static_dir / 'icons'

    # Создаем директорию для иконок
    ensure_dir(icons_dir)

    # Пути к SVG файлам
    favicon_svg = static_dir / 'favicon.svg'
    maskable_svg = icons_dir / 'maskable.svg'

    # Проверяем наличие исходного SVG
    if not favicon_svg.exists():
        print(f"✗ Файл {favicon_svg} не найден!")
        return

    print("🎨 Генерация PWA иконок...\n")

    # Создаем maskable SVG
    create_maskable_svg(favicon_svg, maskable_svg)

    # Размеры иконок для генерации
    sizes = {
        'icon-192.png': 192,
        'icon-512.png': 512,
        'icon-maskable-192.png': 192,
        'icon-maskable-512.png': 512,
        'apple-touch-icon.png': 180,
        'favicon-32.png': 32,
        'favicon-16.png': 16,
    }

    print("\n📦 Генерация обычных иконок:")
    # Генерируем обычные иконки
    for filename in ['icon-192.png', 'icon-512.png', 'apple-touch-icon.png', 'favicon-32.png', 'favicon-16.png']:
        size = sizes[filename]
        output_path = icons_dir / filename
        svg_to_png(favicon_svg, output_path, size)

    print("\n🎭 Генерация maskable иконок:")
    # Генерируем maskable иконки
    for filename in ['icon-maskable-192.png', 'icon-maskable-512.png']:
        size = sizes[filename]
        output_path = icons_dir / filename
        svg_to_png(maskable_svg, output_path, size)

    print("\n✅ Генерация иконок завершена!")
    print(f"📁 Иконки сохранены в: {icons_dir}")
    print("\n📋 Следующие шаги:")
    print("1. Проверьте иконки в директории static/icons/")
    print("2. Обновите base.html для подключения manifest.json")
    print("3. Зарегистрируйте service worker")
    print("4. Протестируйте PWA в Chrome DevTools (Lighthouse)")


if __name__ == '__main__':
    main()
