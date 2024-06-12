import os
import cv2
import numpy as np
import imgaug.augmenters as iaa
from tqdm import tqdm

def augment_images(input_dir, output_dir, augment_count=3):
    os.makedirs(output_dir, exist_ok=True)
    seq = iaa.Sequential([
        iaa.Affine(rotate=(-25, 25)),
        iaa.Fliplr(0.5),
        iaa.GaussianBlur(sigma=(0.0, 3.0)),
        iaa.AdditiveGaussianNoise(scale=(10, 60)),
    ])

    for category in ['NORMAL', 'PNEUMONIA']:
        input_category_dir = os.path.join(input_dir, category)
        output_category_dir = os.path.join(output_dir, category)
        os.makedirs(output_category_dir, exist_ok=True)

        for img_name in tqdm(os.listdir(input_category_dir)):
            img_path = os.path.join(input_category_dir, img_name)
            image = cv2.imread(img_path)

            for i in range(augment_count):
                augmented_image = seq(image=image)
                output_img_name = f"{os.path.splitext(img_name)[0]}_aug_{i}.jpeg"
                output_img_path = os.path.join(output_category_dir, output_img_name)
                cv2.imwrite(output_img_path, augmented_image)

augment_images('chest_xray', 'chest_xray_augmented')
