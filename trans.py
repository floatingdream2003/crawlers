import os
import glob


def rename_images(directory, start_number):
    # 使用 glob 模块查找所有图像文件
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif']
    images = []

    for ext in image_extensions:
        images.extend(glob.glob(os.path.join(directory, ext)))

        # 按数字递增重命名
    for index, image_path in enumerate(images, start=start_number):
        # 获取文件扩展名
        _, ext = os.path.splitext(image_path)
        # 生成新的文件名
        new_name = os.path.join(directory, f"{index}{ext}")
        # 重命名文件
        os.rename(image_path, new_name)

    # 示例用法


directory_path = "./pics6"  # 请将此处替换为你的图片目录
start_number = 4482  # 指定起始数字
rename_images(directory_path, start_number)