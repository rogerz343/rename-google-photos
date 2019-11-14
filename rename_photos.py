import os
import glob
import pytz

from datetime import datetime
from datetime import timedelta
import json
import piexif
import shutil

# the 'Google Photos' folder, used as input to this script
input_dir = 'C:\\Users\\roger\\Downloads\\Takeout\\Google Photos\\'

# the output directory, where all files will be written to
output_dir = 'C:\\Users\\roger\\Downloads\\Takeout\\output\\'

# this program assumes US eastern time, which is either UTC-4 or UTC-5 depending
# on whether its daylight savings time or not. it determines whether to subtract
# 4 or 5 hours by checking the date (to determine if daylight time or not).

# tolerance: if google photos's timestamp ('photoTakenTime') and the photo's
# exif metadata timestamp ('DateTimeOriginal') differ by more than this, then
# we consider the google timestamp to be the 'correct' one. measured in hours.
tolerance = 24

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
        ext = ext.lower()
        if ext not in photo_extensions \
                and ext not in video_extensions:
            if ext != '.json':
                print('[skipping] unrecognized file format: ' + str(source_filepath))
            continue
        try:
            with open(os.path.join(source_filepath + '.json')) as data:
                d = json.load(data)
                google_dt = datetime.utcfromtimestamp(int(d['photoTakenTime']['timestamp']))

                # convert to US/Eastern time (this auto-detects daylight [savings] time)
                et = pytz.timezone('US/Eastern')
                utc = pytz.utc
                google_dt = google_dt.astimezone(et)

                # will be overridden by exif datetime if not missing
                true_dt_str = google_dt

                # don't try to get exif data for videos or .png files
                if ext not in video_extensions and ext != '.png':
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
                        print('[warning] some error in reading exif data for '
                            + source_filepath + '. using google photos data.')

                # resolve filename conflicts by appending with a numeric id
                counter = 1
                true_dt_str = true_dt.strftime('%Y%m%d_%H%M%S')
                new_filepath_no_ext = os.path.join(output_dir, true_dt_str + '_' + str(counter))
                while len(glob.glob(new_filepath_no_ext + '*')) > 0:
                    counter += 1
                    new_filepath_no_ext = os.path.join(output_dir, true_dt_str + '_' + str(counter))
                new_filepath = new_filepath_no_ext + ext
                
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