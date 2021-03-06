#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Skript zum generieren von DeepZoomImages
# Stand: 19.09.2017

###############################################################################

# Importieren allgemeiner Bibliotheken
import argparse, errno, json, logging, os, shutil, sys
from time import time
from multiprocessing import Pool
from functools import partial

###############################################################################

# Parsen der Programmparameter
parser = argparse.ArgumentParser(description='DeepZoomImages-Generator')
# Ordner, die die zu konvertierenden Dateien enthalten
parser.add_argument('paths', nargs='*', default=[os.path.curdir], help='Pfade, die die Digitalisate enthalten.')
# Rekursives Durchsuchen der übergebenen Pfade
parser.add_argument('--recursive', nargs='*', type=str, help='Ordner, die die Digitalisate enthalten (absteigende Präferenz)')
# Dateiendungen
parser.add_argument('--extensions', nargs='*', type=str, help='Mögliche Dateiendungen der Digitalisate (default: tiff, tif, jpg, jpeg)')
# Logdatei erstellen
parser.add_argument('-l', dest='logfile', action='store_true', default=False, help='Erstellt Logfile (kachelgenerator.log).')
# Ausschluss vom Networker Backup
parser.add_argument('-n', dest='networker', action='store_true', default=False, help='Erstellt Networker Direktive (tiles-Ordner werden vom Backup ausgeschlossen).')
# Anzahl der Worker/Prozesse
parser.add_argument('-w', dest='worker', nargs='?', type=int, default=4, help='Anzahl Worker (default 4).')
# Parsen
args = parser.parse_args()

###############################################################################

# Logging einrichten
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# formatieren
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# console handler einrichten
ch = logging.StreamHandler()
ch.setLevel(logging.WARN)
ch.setFormatter(formatter)
logger.addHandler(ch)
# file handler einrichten ('-l' Flag)
if args.logfile:
  fh = logging.FileHandler('kachelgenerator.log')
  fh.setLevel(logging.DEBUG)
  fh.setFormatter(formatter)
  logger.addHandler(fh)

###############################################################################
#
# Testen, welches Tool installiert ist
#
###############################################################################

def check_tool():

  tool = 0

  # 1. VIPS mit Python Bindings
  try:
    # Import von VIPS zur Erzeugung der DeepZoomImages
    import gi
    gi.require_version('Vips', '8.0')
    from gi.repository import Vips
    Vips
  except:
    logger.info('VIPS mit Python-Bindings nicht gefunden.')
  else:
    tool = 1
    logger.info('VIPS mit Python-Bindings installiert.')
    # Concurrency mit Python verwalten
    os.environ['VIPS_CONCURRENCY'] = '1'

  # 2. VIPS als Subprozess
  if tool == 0:
    try:
      # Import von subprocess
      import subprocess
      subprocess.check_output('vips')
    except:
      logger.info('VIPS nicht gefunden.')
    else:
      tool = 2
      logger.info('VIPS installiert.')
      # Concurrency mit Python verwalten
      os.environ['VIPS_CONCURRENCY'] = '1'

  # 3. DeepZoom
  if tool == 0:
    try:
      # Import von deepzoom
      import deepzoom
      deepzoom
    except:
      logger.info('DeepZoom nicht gefunden.')
    else:
      tool = 3
      logger.info('DeepZoom installiert.')

  return tool

###############################################################################
#
# Kacheln generieren
#
###############################################################################

def generate_tile(task, tool):

  global bm_errors

  # expand tuple
  filename, filein, fileout = task

  # 1. VIPS Python-Bindings
  if tool == 1:
    try:
      import gi
      gi.require_version('Vips', '8.0')
      from gi.repository import Vips
      img = Vips.Image.new_from_file(filein)
      # img.dzsave(output_dir, layout='zoomify', suffix='.jpg[Q=100]')
      img.dzsave(fileout)
    except Vips.Error, e:
      logger.error('Fehler bei der Kachelgenerierung für ' + filein + ': ' + str(e.detail))
      filelist.remove(filename)
      bm_errors += 1
    else:
      logger.info('Kacheln für ' + filein + ' generiert.')

  # 2. VIPS Python-Subprozess
  elif tool == 2:
    try:
      result = subprocess.check_output(['vips', 'dzsave', filein, fileout], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
      logger.error('Fehler bei der Kachelgenerierung für ' + filein + ': ' + str(e.output))
      filelist.remove(filename)
      bm_errors += 1
    else:
      logger.info('Kacheln für ' + filein + ' generiert.')

  # 3. DeepZoom
  elif tool == 3:
    try:
      creator = deepzoom.ImageCreator()
      creator.create(filein, fileout + '.dzi')
    except:
      logger.error('Fehler bei der Kachelgenerierung für ' + filein)
      filelist.remove(filename)
      bm_errors += 1
    else:
      logger.info('Kacheln für ' + filein + ' generiert.')

  # Zur Sicherheit terminieren
  else:
    logger.fatal('Kein Tool gefunden/installiert! Bitte VIPS oder DeepZoom installieren.')
    sys.exit()

###############################################################################
#
# Ordner mit den zu konvertierenden Dateien bestimmen
#
###############################################################################

def determine_input_dirs(path_list, dir_list):

  dirs = []

  # Schleife über die verschiedenen Pfade
  for path in path_list:

    # Rekursives Durchsuchen?
    if dir_list:

      # Rekursives Durchsuchen der Pfads
      for rootpath, dirnames, filenames in os.walk(path):

        # Prüfen ob der Pfad einen gesuchten Ordnernamen enthält, aber keine weiteren Unterordner
        for dir in dir_list:

          if rootpath.lower().endswith(dir.lower()) and len(dirnames) == 0:

            dirs.append(rootpath)

    else:

      dirs.append(path)

  return dirs

###############################################################################
#
# Ordner mit den zu konvertierenden Dateien verarbeiten
#
###############################################################################

def convert_images(dir_list, tool, args):

  global bm_files

  # Mögliche Dateiendungen der zu konvertierenden Dateien
  file_extensions = ('.tiff', '.tif', '.jpg', '.jpeg')
  if args.extensions:
    file_extensions = tuple(args.extensions)

  for dir in dir_list:

    # Bestimmung des 'tiles'-Ordners im übergeordneten Ordner
    tilesfolder = os.path.join(os.path.abspath(os.path.join(dir, os.pardir)), 'tiles')

    # Löschen des 'tiles'-Ordners und ggfls. Unterordner
    if os.path.exists(tilesfolder):
      try:
        shutil.rmtree(tilesfolder, ignore_errors=True)
      except OSError, e:
        logger.error('Fehler beim Löschen: ' + str(e.args))
      except:
        raise

    # Erstellen des 'tiles'-Ordners
    try:
      os.makedirs(tilesfolder)
    except OSError, e:
      # Für alle Fehler, außer dass der Ordner existiert, zum nächsten Ordner gehen
      if not e.errno == errno.EEXIST:
        logger.error('Fehler beim Erstellen ' + str(e.args))
        continue
    except:
      raise

    # Erstellen der Networker Direktive
    if args.networker:
      if not os.path.exists(os.path.join(tilesfolder[:tilesfolder.rindex('tiles')], 'tiles', '.nsr')):
        with open(os.path.join(tilesfolder[:tilesfolder.rindex('tiles')], 'tiles', '.nsr'), 'w') as networkerfile:
          networkerfile.write('+skip: *')
          logger.info('Networker Direktive erstellt: ' + os.path.join(tilesfolder[:tilesfolder.rindex('tiles')], 'tiles', '.nsr'))

    # Erstellung einer Datei- und Aufgabenliste
    file_list = []
    task_list = []

    # Bestimmung der Digitalisate im Pfad
    for rootpath, dirnames, filenames in os.walk(dir):

      # Erstellen der Dateiliste
      for filename in filenames:

        # Beschränkung auf Dateiendungen
        if filename.endswith(file_extensions):

          # Datei in Listen speichern
          file_list.append(filename)
          task_list.append((filename, os.path.join(rootpath, filename), os.path.join(tilesfolder, filename[:filename.rindex('.')])))
          bm_files += 1   


      # Wir wollen nur die Digitalisate auf der oberen Ebene
      break

    # Dateiendungen in .dzi ändern
    for f in file_list:
      f = f[:f.rindex('.')] + '.dzi'

    # Speichern der Dateiliste in einer JSON-Datei
    with open(os.path.join(tilesfolder, os.path.basename(os.path.normpath(tilesfolder.rsplit('/',1)[0])) + '.json'), 'w') as jsonfile:
      json.dump({'files': file_list}, jsonfile)

    # Generieren von DeepZoomImages auslagern in Workers
    p = Pool(args.worker)
    p.map(partial(generate_tile, tool=tool), task_list)

###############################################################################

# Zählen von Verarbeitungsdauer, Dateien, Fehlern
bm_time = time()
bm_files = 0
bm_errors = 0

# Tool prüfen und ggfls terminieren
tool = check_tool()
if tool == 0:
  sys.exit('Kein Tool gefunden/installiert! Bitte VIPS oder DeepZoom installieren.')
elif tool == 1:
  import gi
  gi.require_version('Vips', '8.0')
  from gi.repository import Vips
elif tool == 2:
  import subprocess
  subprocess.check_output('vips')
elif tool == 3:
  import deepzoom

# Inputorder bestimmen
input_dirs = determine_input_dirs(args.paths, args.recursive)

# Konvertierung starten
convert_images(input_dirs, tool, args)

# Stats ausgeben
print '{0} Sekunden für {1} Dateien mit {2} Fehlern.'.format(time() - bm_time, bm_files, bm_errors)