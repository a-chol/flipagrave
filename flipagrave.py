import sqlite3, json, shutil, os, urllib, argparse, datetime
from moviepy.editor import *
from moviepy.video.fx import *

def find_file(mediaDirs, filename):
  for dir in mediaDirs:
    for root, dirs, files in os.walk(dir):
      for file in files:
        if file==filename:
          return os.path.join(root, file)
  return ""

def restore_video(database, projectId, mediaDirs, outputFile, preview):
  conn = sqlite3.connect(database)
  c = conn.cursor()
  c.execute("SELECT payload_obj FROM creation_flipagram LIMIT 1 OFFSET "+str(projectId-1))

  project = json.loads(c.fetchone()[0])

  moments = project['moments']
  videoclips = []
  for moment in moments:
    fixedPath = find_file(mediaDirs, os.path.basename(urllib.unquote(moment['mediaItem']['sourceUri']).decode('utf8')))
    
    if not os.path.isfile(fixedPath):
        print(fixedPath, ' -> NOK (', urllib.unquote(moment['mediaItem']['sourceUri']).decode('utf8'), ')')
        return

    ext = os.path.splitext(fixedPath)[1]
    print "processing " + os.path.basename(fixedPath)
    if ext.lower() == '.mp4':
      clip = VideoFileClip(fixedPath)
      if moment['naturalRotation'] != 0:
        clip = all.rotate(clip, -moment['naturalRotation'])
        
      clip = all.crop(clip, x1=moment['cropRect']['left']*moment['intrinsicWidth'], y1=moment['cropRect']['top']*moment['intrinsicHeight'],x2=moment['cropRect']['right']*moment['intrinsicWidth'], y2=moment['cropRect']['bottom']*moment['intrinsicHeight'])
      
      
      seqs = moment['mediaItem']['clips']
      startSeq = seqs[0]['start']
      curSeq = seqs[0]['start']
      seqs = seqs[1:]
      for start in seqs:
        
        if start['start'] != curSeq+1:
          # save current sequence as clip
          videoclips.append(clip.subclip(startSeq, curSeq+1))
          startSeq=start['start']
          curSeq=startSeq
        else:
          curSeq = start['start']
      
      videoclips.append(clip.subclip(startSeq, curSeq+1))
    elif ext.lower() == '.jpg':
      clip = ImageClip(fixedPath).set_duration(moment['durationMillis']/1000.)
      clip = crop.crop(clip, x1=moment['cropRect']['left']*moment['intrinsicWidth'], y1=moment['cropRect']['top']*moment['intrinsicHeight'],x2=moment['cropRect']['right']*moment['intrinsicWidth'], y2=moment['cropRect']['bottom']*moment['intrinsicHeight'])
      videoclips.append(clip)
    else:
      print(fixedPath, ': not used', ext)
      
    # if len(videoclips)>2:
      # break
    # if os.path.isfile(fixedPath):
      # print(os.path.basename(fixedPath), ' -> OK')

  print(len(moments), ' fragments')
  if len(videoclips) <= 0:
    print("empty clip sequence")
    quit()
  final = concatenate_videoclips(videoclips)
  final = resize.resize(final, 0.25)

  # add audio
  if len(project['audioInfo']['path'])>0:
    fixedPath = find_file(mediaDirs, os.path.basename(urllib.unquote(project['audioInfo']['path']).decode('utf8')))
    print fixedPath
    if not os.path.isfile(fixedPath):
      print(fixedPath, ' -> NOK (', urllib.unquote(moment['mediaItem']['sourceUri']).decode('utf8'), ')')
      return
    music = AudioFileClip(fixedPath)
    music.set_duration(final.duration)
    soundComp = [music]
    if final.audio!=None:
      soundComp.append(final.audio)
    final_audio = CompositeAudioClip(soundComp)
    final.audio = final_audio

  if preview:
    final.preview(fps=10)
  else:
    final.write_videofile(outputFile, fps=24)
  
def list_projects(dbPath):
  conn = sqlite3.connect(dbPath)
  c = conn.cursor()
  c.execute("SELECT payload_obj, is_current, created_ts, updated_ts FROM creation_flipagram")
  projNumber = 0
  for project in c.fetchall():
    moments = json.loads(project[0])['moments']
    # print projNumber+1, ' : ', len(moments), " elements, ", "current project, " if project[1] else "", "created on ", project[2], ", last edited on ", project[3]
    print projNumber+1, ' : ', len(moments), " elements, ", "current projet, " if project[1] else "", "created on ", datetime.datetime.fromtimestamp(project[2]/1000).strftime('%Y-%m-%d %H:%M:%S'), ", last edited on ", datetime.datetime.fromtimestamp(project[3]/1000).strftime('%Y-%m-%d %H:%M:%S')
    projNumber+=1
  
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--backupDir", help="backup folder for flipagram", action="store")
  parser.add_argument("--projects", help="list projects from database", action="store_true")
  parser.add_argument("--export", help="create video for project number", action="store", type=int)
  parser.add_argument('--mediaDirs', metavar='N', nargs='+', help='list of folders to get media from', default=".")
  parser.add_argument('--output', help='output video file', action="store")
  parser.add_argument('--preview', help='preview video file', action="store_true")
  args = parser.parse_args()
  
  if not os.path.isdir(args.backupDir):
    print "Could not get backup directory (use --backupDir to point to the apps dir extracted from adb backup)"
    quit()
  else:
    dbPath = os.path.join(args.backupDir, 'com.cheerfulinc.flipagram/db/slideshow.db')
    
  if args.projects:
    list_projects(dbPath)
  elif args.export:
    restore_video(dbPath, args.export, args.mediaDirs, args.output, args.preview)
  
    
