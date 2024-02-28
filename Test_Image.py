from PIL import Image
import os


def combine_images_in_folder(folder_path, output_tiff):
    """
    Принимает путь к папке и имя выходного TIFF файла. Она комбинирует все изображения из этой папки в один TIFF файл
    Args:
    - folder_path (str): путь к папке, содержащей изображения
    - output_tiff (str): путь к выходному файлу TIFF
    """
    # Получаем список файлов изображений в папке
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

    # Создаем новый пустой файл TIFF
    tiff_image = Image.new('RGB', (1000, 1000))  # Тут меняем размер под необходимый

    # Перебираем файлы изображений и вставляем их в файл TIFF
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        image = Image.open(image_path)
        tiff_image.paste(image, (0, 0))  # Тут, настраиваем координаты вставки

    # Сохраняем объединенный файл TIFF
    tiff_image.save(output_tiff)


def combine_images_from_folders(folder_list, output_tiff):
    """
    Принимает список папок и имя выходного TIFF файла. Она комбинирует изображения из всех папок в один TIFF файл

    Args:
    - folder_list (list): Список путей к папкам
    - output_tiff (str): Путь к выходному файлу TIFF
    """
    # Путь к выходному файлу TIFF
    tiff_image = Image.new('RGB', (1000, 1000))  # Тут меняем размер под необходимый

    # Перебираем пути к папкам и объединяем изображения
    for folder_path in folder_list:
        # Получаем список файлов изображений в папке
        image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

        # Перебираем файлы изображений и вставляем их в файл TIFF
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            image = Image.open(image_path)
            tiff_image.paste(image, (0, 0))  # Тут, настраиваем координаты вставки

    # Сохраняем объединенный файл TIFF
    tiff_image.save(output_tiff)


# Пример использования функций
folder_list = ['1388_12_Наклейки 3-D_3']  # список папок
output_tiff = 'Result.tif'  # имя выходного TIFF файла

combine_images_from_folders(folder_list, output_tiff)
