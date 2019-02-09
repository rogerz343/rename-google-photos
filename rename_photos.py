import os

from datetime import datetime
from datetime import timedelta
import json
import shutil

# the "Google Photos" folder, used as input to this script
input_dir = 'C:\\Users\\[name here]\\Desktop\\Takeout\\test set\\'

# the output directory, where all files will be written to
output_dir = 'D:\\[name here]\\Desktop\\output\\'

photo_extensions = [
    ".jpg", ".jpeg", ".jpe", ".jfif", ".bmp", ".dib", ".gif",
    ".png", ".tif", ".tiff", ".heic", ".mp4", ".avi", ".wmv",
    ".flv", ".mpeg"
]

for f in os.listdir(input_dir):
    subdir_path = os.path.join(input_dir, f)
    if not os.path.isdir(subdir_path):
        continue
    for filename in os.listdir(subdir_path):
        root, ext = os.path.splitext(filename)
        if ext.lower() not in photo_extensions:
            continue
        source_filepath = os.path.join(subdir_path, filename)
        with open(os.path.join(source_filepath + ".json")) as data:
            d = json.load(data)
            dt = datetime.utcfromtimestamp(int(d["photoTakenTime"]["timestamp"]))

            # program assumes (for now) UTC-5:00
            dt = dt - timedelta(hours=5)

            counter = 1
            date_time = dt.strftime("%Y%m%d_%H%M%S")
            new_filepath = os.path.join(output_dir, date_time + "_" + str(counter) + ext)
            while os.path.isfile(new_filepath):
                counter += 1
                new_filepath = os.path.join(output_dir, date_time + "_" + str(counter) + ext)
            
            shutil.copyfile(source_filepath, new_filepath)

            # todo: change metadata