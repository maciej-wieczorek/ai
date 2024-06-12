import os
import pandas as pd


# Prepare CSV file for Ludwig
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

csv_path = 'data.csv'
data_dir = 'chest_xray'
prepare_data_csv(data_dir, csv_path)
