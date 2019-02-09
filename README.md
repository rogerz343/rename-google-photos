# google-photos-tool
scripts that modify files downloaded from google photos

## some background
Uploading images to Google Photos provides many benefits, such as automatic face
recognition, location tagging, and object tagging. You can also change
information about when and where the photo was taken, and add a description to
each photo. However, modifying these fields doesn't change the metadata that is
found in the originally uploaded photo. Thus, downloading all of your google
photos by simply adding them to your Google Drive won't preserve
some of the new information. The scripts in this repo should help fix that.

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
called *x.json* in the same directory.

## the scripts
*rename_photos.py*: this will go through every photo and rename the file to be
a timestamp of when the photo was taken. Note that it will NOT use the photo's
"date taken" metadata information, but instead will use the "photoTakenTime"
field which is located in the corresponding .json file. In addition, this script
will also edit the "date taken" exif metadata on the actual image file. None of
these edits are done in-place; all files will be copied to the specified output
directory. Also, note that the current implementation saves times in UTC-5:00.