from pathlib import Path
from PIL import Image, UnidentifiedImageError
import numpy as np
import matplotlib.pyplot as plt


def load_image(path: str) -> Image.Image:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Файл не найден: {path.resolve()}")
    try:
        with Image.open(path) as img:
            img.load()
            return img.convert("RGB")
    except UnidentifiedImageError:
        raise ValueError(f"Файл не является поддерживаемым изображением: {path}")


def explore_image(image: Image.Image, filepath: str) -> np.ndarray:
    print("ЗАДАНИЕ 1")
    print(f"Файл: {filepath}")
    print(f"Формат: {image.format}")
    print(f"Размер: {image.size}")
    print(f"Режим: {image.mode}")
    print(f"Ширина: {image.width}, Высота: {image.height}")
    
    array = np.asarray(image)
    print(f"NumPy shape: {array.shape}")
    print(f"NumPy dtype: {array.dtype}")
    print(f"Min: {array.min()}, Max: {array.max()}")
    print(f"Каналов: {array.shape[2] if len(array.shape) == 3 else 1}")
    
    for x, y in [(0, 0), (image.width//2, image.height//2), (image.width-1, image.height-1)]:
        print(f"Пиксель [{x}, {y}]: {array[y, x]}")
    
    return array


def extract_channels(array: np.ndarray) -> tuple:
    print("\nЗАДАНИЕ 2")
    red, green, blue = array[:, :, 0], array[:, :, 1], array[:, :, 2]
    
    for name, ch in [("R", red), ("G", green), ("B", blue)]:
        print(f"{name}: min={ch.min()}, max={ch.max()}, mean={ch.mean():.2f}")
    
    return red, green, blue


def save_channels(red: np.ndarray, green: np.ndarray, blue: np.ndarray, output_dir: Path):
    zeros = np.zeros_like(red)
    Image.fromarray(np.stack([red, zeros, zeros], axis=2)).save(output_dir / "red_channel.png")
    Image.fromarray(np.stack([zeros, green, zeros], axis=2)).save(output_dir / "green_channel.png")
    Image.fromarray(np.stack([zeros, zeros, blue], axis=2)).save(output_dir / "blue_channel.png")
    print("Сохранено: red_channel.png, green_channel.png, blue_channel.png")


def change_brightness(image_array: np.ndarray, delta: int) -> np.ndarray:
    data = image_array.astype(np.int16)
    data = np.clip(data + delta, 0, 255)
    return data.astype(np.uint8)


def process_brightness(image: Image.Image, output_dir: Path):
    print("\nЗАДАНИЕ 3")
    array = np.asarray(image)
    
    darker = Image.fromarray(change_brightness(array, -50))
    darker.save(output_dir / "darker.png")
    print(f"Затемнение (delta=-50): сохранено darker.png")
    
    brighter = Image.fromarray(change_brightness(array, 50))
    brighter.save(output_dir / "brighter.png")
    print(f"Осветление (delta=+50): сохранено brighter.png")
    
    return darker, brighter


def resize_image(image: Image.Image, factor: float) -> Image.Image:
    new_width = max(1, int(image.width * factor))
    new_height = max(1, int(image.height * factor))
    return image.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)


def resize_keep_aspect(image: Image.Image, new_width: int) -> Image.Image:
    if new_width <= 0:
        raise ValueError("Ширина должна быть положительным числом")
    scale = new_width / image.width
    new_height = max(1, int(image.height * scale))
    return image.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)


def process_resizing(image: Image.Image, output_dir: Path):
    print("\nЗАДАНИЕ 4")
    
    resized_50 = resize_image(image, 0.5)
    resized_50.save(output_dir / "resized_50.png")
    print(f"50%: {resized_50.size} -> сохранено resized_50.png")
    
    resized_150 = resize_image(image, 1.5)
    resized_150.save(output_dir / "resized_150.png")
    print(f"150%: {resized_150.size} -> сохранено resized_150.png")
    
    resized_custom = resize_keep_aspect(image, 300)
    print(f"Ширина 300px: {resized_custom.size}")
    
    return resized_50, resized_150


def rotate_image(image: Image.Image, angle: float, expand: bool = True) -> Image.Image:
    if not isinstance(angle, (int, float)):
        raise ValueError("Угол должен быть числом")
    return image.rotate(angle, resample=Image.Resampling.BICUBIC, expand=expand, fillcolor=(255, 255, 255))


def process_rotation(image: Image.Image, output_dir: Path):
    print("\nЗАДАНИЕ 5")
    
    rotated_45 = rotate_image(image, 45)
    rotated_45.save(output_dir / "rotated_45.png")
    print(f"45°: {rotated_45.size} -> сохранено rotated_45.png")
    
    rotated_90 = rotate_image(image, 90)
    print(f"90°: {rotated_90.size}")
    
    rotated_custom = rotate_image(image, 30)
    rotated_custom.save(output_dir / "rotated_custom.png")
    print(f"30°: {rotated_custom.size} -> сохранено rotated_custom.png")
    
    rotated_no_expand = rotate_image(image, 45, expand=False)
    print(f"expand=False: {rotated_no_expand.size}, expand=True: {rotated_45.size}")
    
    return rotated_45, rotated_custom


def to_grayscale_pillow(image: Image.Image) -> Image.Image:
    return image.convert("L")


def to_grayscale_numpy(image: Image.Image) -> Image.Image:
    array = np.asarray(image)
    gray = 0.299 * array[:, :, 0] + 0.587 * array[:, :, 1] + 0.114 * array[:, :, 2]
    return Image.fromarray(np.clip(gray, 0, 255).astype(np.uint8))


def process_grayscale(image: Image.Image, output_dir: Path):
    print("\nЗАДАНИЕ 6")
    
    gray_pillow = to_grayscale_pillow(image)
    gray_pillow.save(output_dir / "grayscale_pillow.png")
    print(f"Pillow: {gray_pillow.mode}, {gray_pillow.size} -> сохранено grayscale_pillow.png")
    
    gray_numpy = to_grayscale_numpy(image)
    gray_numpy.save(output_dir / "grayscale_numpy.png")
    print(f"NumPy: {gray_numpy.mode}, {gray_numpy.size} -> сохранено grayscale_numpy.png")
    
    return gray_pillow, gray_numpy


def process_region(image: Image.Image, output_dir: Path) -> Image.Image:
    print("\nЗАДАНИЕ 7")
    
    array = np.asarray(image).copy()
    h, w = array.shape[:2]
    
    x1, y1 = w // 3, h // 3
    x2, y2 = 2 * w // 3, 2 * h // 3
    
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    
    if x1 >= x2 or y1 >= y2:
        raise ValueError("Координаты области выходят за пределы изображения")
    
    region = array[y1:y2, x1:x2]
    gray_region = 0.299 * region[:, :, 0] + 0.587 * region[:, :, 1] + 0.114 * region[:, :, 2]
    gray_region = np.clip(gray_region, 0, 255).astype(np.uint8)
    
    array[y1:y2, x1:x2, 0] = gray_region
    array[y1:y2, x1:x2, 1] = gray_region
    array[y1:y2, x1:x2, 2] = gray_region
    
    result = Image.fromarray(array)
    result.save(output_dir / "region_processed.png")
    print(f"Область: x[{x1}:{x2}], y[{y1}:{y2}] -> сохранено region_processed.png")
    
    return result


def create_composition(images: dict, output_dir: Path):
    print("\nЗАДАНИЕ 8")
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flat
    
    titles = {
        'original': 'Исходное',
        'resized': 'Уменьшенное (50%)',
        'rotated': 'Поворот 45°',
        'grayscale': 'Grayscale',
        'brightness': 'Яркость +50',
        'region': 'Обработанная область'
    }
    
    for idx, (key, title) in enumerate(titles.items()):
        if idx < len(axes) and key in images:
            img = images[key]
            # ИСПРАВЛЕНИЕ: Явно указываем cmap='gray' для черно-белых изображений,
            # чтобы Matplotlib не применял желто-зеленую цветовую карту по умолчанию
            if img.mode == 'L':
                axes[idx].imshow(img, cmap='gray')
            else:
                axes[idx].imshow(img)
            
            axes[idx].set_title(title, fontsize=12, fontweight='bold')
            axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_dir / "result.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("Композиция из 6 изображений -> сохранено result.png")


def save_result(image: Image.Image, path: Path):
    image.save(path)


def main():
    print("ПРАКТИЧЕСКАЯ РАБОТА №1")
    
    image_path = "images/1.jpg"
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        image = load_image(image_path)
        array = explore_image(image, image_path)
        
        red, green, blue = extract_channels(array)
        save_channels(red, green, blue, output_dir)
        
        darker, brighter = process_brightness(image, output_dir)
        
        resized_50, resized_150 = process_resizing(image, output_dir)
        
        rotated_45, rotated_custom = process_rotation(image, output_dir)
        
        gray_pillow, gray_numpy = process_grayscale(image, output_dir)
        
        region_processed = process_region(image, output_dir)
        
        composition = {
            'original': image,
            'resized': resized_50,
            'rotated': rotated_45,
            'grayscale': gray_pillow,
            'brightness': brighter,
            'region': region_processed
        }
        create_composition(composition, output_dir)
        
        
    except FileNotFoundError as e:
        print(f"ОШИБКА: {e}")
    except ValueError as e:
        print(f"ОШИБКА: {e}")
    except Exception as e:
        print(f"ОШИБКА: {e}")


if __name__ == "__main__":
    main()