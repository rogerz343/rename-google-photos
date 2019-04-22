# google-photos-tool
scripts that modify files downloaded from google photos

## some background
When you upload an image to Google Photos, you can edit metadata such as
location, date/time taken, etc. However, this information is not modified in
the original source file. Instead, all images uploaded to Google Photos have a
corresponding .json file, which contains information such as GPS coordinates,
a timestamp of when the photo was taken, etc. Thus, when you download your
images from Google Photos, you get the original image files (without any manual
adjustments to metadata).

## getting your photos and information
Google has a service called "Takeout"
(https://takeout.google.com/settings/takeout) which you can use to download a
lot of information that Google has about you, most notably your photos and the
corresponding data (modified time taken, description, etc.) about them.

## photo directory format
It will be assumed that (after downloading your photos with Takeout), you will
have a folder called "Google Photos". In it are many folders (most of them
correspond to dates). In those folders are the actual image files and the
corresponding metadata. For any photo with filename *x*, there should be a file
(with the metadata) called *x.json* in the same directory.

## rename_photos.py
### Usage
1. Set the `input_dir` and `output_dir` variables at the top of the file to
point to the correct/valid directories.
2. To start, simply do `python rename_photos.py`. I also recommend saving the
standard out stream to see if anything went wrong, for example
`python rename_photos.py > log.txt`.

### High level explanation
This script will iterate through the files in the input directory (the directory
of google photos/albums). For each photo/video, it will rename the file to be a
timestamp of when the photo was taken, and it will also potentially modify the
"date taken" metadata of the photo if the current metadata is missing or
incorrect. All changes are not done in place, i.e. we first copy the file to the
specified output directory and then change that one.

### More detailed explanation
First, we need to understand the "Date Taken" tag that Windows puts on files
when you view a file's properties. Supposedly, the value in this field is taken
from the photo's exif metadata tags, in the following order (i.e. Windows will
use the first of the following whose value is not missing).

1. `EXIF:DateTimeOriginal`
2. `IPTC:DateCreated + IPTC:TimeCreated`
3. `XMP:CreateDate`
4. `EXIF:CreateDate`
5. `XMP:DateTimeOriginal`

For this script, we'll just use EXIF:DateTimeOriginal and not care about
date modified, date created, etc.

This script will go through every file and will do the following:
If the file is recognized as a photo with exifdata: the script will first
compare the "photoTakenTime" field in the .json file to the DateTimeOriginal
field in the photo's exif metadata. If the DateTimeOriginal exif tag is missing,
or if the timestamps (the "photoTakenTime" and DateTimeOriginal) are not within
12 hours of each other, then we'll consider the "photoTakenTime" to be the
"true" datetime. Otherwise, we'll consider the exif data as the "true" datetime.
Note that:
- "photoTakenTime" from the google photos .json document uses UTC with no offset
- the exif metadata does not have a timezone associated with it, so we'll
consider it local time.

The script will always output local times (with no associated timezone). Since
most photos do have exif metadata and since this metadata uses local time
("local" to whenever/wherever the photo was taken), most photos will have
accurate filename timestamps. However, if the exif data is missing (in this
case, we rely on google photos's datetime), the resulting timestamp might be off
by up to a few hours. Oh well.

*Note*: EXIF tags do actually include a timezone offset in case you want to
compute the time in UTC, but using that is way too much work for this small
project.

For each photo, the script will
1. Rename the file to be a timestamp of when the photo was taken, in the format
YYYYMMDD_hhmmss_X, where X is a number given to the photo (to resolve conflicts
where more than 1 photo was taken in the same second).
2. Potentially edit the "date taken" exif metadata to be the "true" date, if
needed.

All of the above applies to recognized image formats with exif metadata.
Recognized video formats (or image formats without exif data, such as .png
files) will simply be copied over with the Google Photos timestamp (the
"photoTakenTime" field in the .json file) as the filename.

If the file is not recognized as an image, video, or .json file, then the
script skips it (and prints a "\[skipping\]" warning).

All edits are done on copies of the file, which will be output in the specified
output directory.