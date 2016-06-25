# flipagrave

My girlfriend made a quite long video on flipagram but was unable to export it due to a bug that wasn't fixed through a number of updates, having the export process stuck at some point. This problem seems to have hit a number of users, reading through the app's store page comments.

In order to avoid doing it all over again, I managed to recover the app cache, read the database and create a script to re-generate the whole resulting video based on what was done inside the app.

## steps

Here are the steps to export the video

1. Get the app cache from android using adb

  * Install adb, either from the android sdk or from any other source
  * Having enable USB debugging in your device settings, connect the USB cable
  * in a command prompt, backup the application cache in a file : adb backup -f data.ab -noapk com.cheerfulinc.flipagram
  * use Android Backup Extractor (https://sourceforge.net/projects/adbextractor/) to get a readable archive of the file : java -jar abe.jar unpack data.ab data.tar
  * use 7zip to unarchive the data
  
2. Read the list of projects in the cache

  * In python 2.7, run 'python flipagrave.py --backupDir apps --projects '
    This gives you a numbered list of the projects in cache. Identify which project you want to export either using the creation date, the fact that it is the current project, or the number of elements (photos and videos) in it.
    In this example, we will assume the project number 2 is the one we want to export
    
3. Get all the media files used in the project in a local folder

4. Export the video

  * run 'python flipagrave.py --backupDir apps --export 2 --output video.mp4
  This could take a while. During the first run, the script might download a few additional dependencies (used by moviepy). At the end of the process, if all went well, you should have a playable video file 'video.mp4'
  
## Features

This script is quite simple and for now supports:
* Image files
* Video files
* Cropping videos
* mixing music
* rotated videos

If there is a feature missing that you would really like to have, or the exported video has some error, don't hesitate to file an issue in the tracker.