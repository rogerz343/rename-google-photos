import os

from datetime import datetime
from datetime import timedelta
import json
import piexif
import shutil

# the 'Google Photos' folder, used as input to this script
input_dir = 'C:\\Users\\roger\\Downloads\\Takeout\\Google Photos\\'

# the output directory, where all files will be written to
output_dir = 'C:\\Users\\roger\\Downloads\\Takeout\\output\\'

# local time offset, in hours. this will be subtracted from the UTC time
# for reference, EST (winter) is UTC-5
#                EDT (summer) is UTC-4
offset = 4

# tolerance: if google photos's timestamp ('photoTakenTime') and the photo's
# exif metadata timestamp ('DateTimeOriginal') differ by more than this, then
# we consider the google timestamp to be the 'correct' one. measured in hours.
tolerance = 12

photo_extensions = [
    '.jpg', '.jpeg', '.jpe', '.jfif', '.bmp', '.dib', '.gif',
    '.png', '.tif', '.tiff', '.heic', '.mp4', '.avi', '.wmv',
    '.flv',
]

video_extensions = [
    '.mp4', '.m4a', '.m4p', '.m4v', '.f4v', '.f4a', '.m4b', '.m4r', '.f4b',
    '.mov', '.3gp', '.3gp2', '.3g2', '.3gpp', '.3gpp2', '.ogg', '.oga', '.ogv',
    '.ogx', '.wmv', '.wma', '.asf', '.webm', '.flv', '.avi', '.gif', '.qt',
    '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.m2v'
]

for f in os.listdir(input_dir):
    subdir_path = os.path.join(input_dir, f)
    if not os.path.isdir(subdir_path):
        continue
    subdir_files = os.listdir(subdir_path)
    print('[status] processing directory: '
        + f
        + ' with '
        + str(len(subdir_files))
        + ' files.'
    )
    for filename in subdir_files:
        source_filepath = os.path.join(subdir_path, filename)
        root, ext = os.path.splitext(filename)
        if ext.lower() not in photo_extensions \
            and ext.lower() not in video_extensions:
            if ext.lower() != '.json':
                print('[skipping] unrecognized file format: ' + str(source_filepath))
        try:
            with open(os.path.join(source_filepath + '.json')) as data:
                d = json.load(data)
                google_dt = datetime.utcfromtimestamp(int(d['photoTakenTime']['timestamp']))
                google_dt = google_dt - timedelta(hours=offset)

                # will be overridden by exif datetime if not missing
                true_dt_str = google_dt

                # files with no exif data, e.g. videos or .png files
                if ext.lower() in video_extensions \
                    or ext.lower() == '.png':
                    # resolve filename conflicts by appending with a numeric id
                    counter = 1
                    true_dt_str = true_dt.strftime('%Y%m%d_%H%M%S')
                    new_filepath = os.path.join(output_dir, true_dt_str + '_' + str(counter) + ext)
                    while os.path.isfile(new_filepath):
                        counter += 1
                        new_filepath = os.path.join(output_dir, true_dt_str + '_' + str(counter) + ext)
                    shutil.copyfile(source_filepath, new_filepath)
                    continue

                try:
                    exif_dict = piexif.load(source_filepath)
                    try:
                        # 36867 is the exif tag for DateTimeOriginal
                        exif_dt_str = exif_dict['Exif'][36867].decode('utf-8')
                        exif_dt = datetime.strptime(exif_dt_str, '%Y:%m:%d %H:%M:%S')
                    except KeyError:
                        exif_dt = -1
                    
                    if exif_dt == -1 \
                        or google_dt - exif_dt > timedelta(hours=tolerance) \
                        or exif_dt - google_dt > timedelta(hours=tolerance):
                        true_dt = google_dt
                    else:
                        true_dt = exif_dt
                except piexif._exceptions.InvalidImageDataError:
                    print('[skipping] bad/no exif data: ' + source_filepath)

                # resolve filename conflicts by appending with a numeric id
                counter = 1
                true_dt_str = true_dt.strftime('%Y%m%d_%H%M%S')
                new_filepath = os.path.join(output_dir, true_dt_str + '_' + str(counter) + ext)
                while os.path.isfile(new_filepath):
                    counter += 1
                    new_filepath = os.path.join(output_dir, true_dt_str + '_' + str(counter) + ext)
                
                # copy file, rename file, edit exif metadata
                shutil.copyfile(source_filepath, new_filepath)
                if true_dt != exif_dt:
                    exif_dt_str = true_dt.strftime('%Y:%m:%d %H:%M:%S')
                    exif_dict = piexif.load(new_filepath)
                    exif_dict['Exif'][36867] = exif_dt_str
                    exif_bytes = piexif.dump(exif_dict)
                    piexif.insert(exif_bytes, new_filepath)

                    print('[note] changed metadata for: ' + source_filepath)
        except FileNotFoundError:
            pass