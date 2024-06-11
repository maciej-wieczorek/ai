import mlflow
from ludwig.api import LudwigModel
from ludwig.contribs.mlflow import MlflowCallback
import pandas as pd
import os

# Define paths
config_file = 'config.yaml'
data_dir = 'chest_xray_augmented/train'
csv_path = 'data.csv'

def prepare_data_csv(data_dir, csv_path):
    data = []
    for category in ['NORMAL', 'PNEUMONIA']:
        category_dir = os.path.join(data_dir, category)
        for img_name in os.listdir(category_dir):
            data.append({
                'image_path': os.path.join(category_dir, img_name),
                'label': category
            })
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)

prepare_data_csv(data_dir, csv_path)

mlflow_callback = MlflowCallback()
model = LudwigModel(config=config_file, callbacks=[mlflow_callback])
results = model.train(dataset=csv_path)
mlflow_callback.on_train_end()
