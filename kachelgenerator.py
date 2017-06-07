#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Skript zum generieren von DeepZoomImages
# Stand: 07.07.2017

# Mögliche Dateiendungen der zu konvertierenden Dateien
dateiendungen = ('.tiff', '.tif', '.jpg', '.jpeg')

###############################################################################

# Importieren allgemeiner Bibliotheken
import argparse, errno, json, logging, os, shutil, sys
from time import time
from multiprocessing import Pool

###############################################################################

# Parsen der Programmparameter
parser = argparse.ArgumentParser(description='DeepZoomImages-Generator')
# Ordner, die die zu konvertierenden Dateien enthalten
parser.add_argument('paths', nargs='*', default=[os.path.curdir], help='Pfade, die die Digitalisate enthalten.')
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

# Testen, welches Tool installiert ist:

# Globale Variable
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

# Skript ggfls. terminieren
if tool == 0:
  sys.exit('Kein Tool gefunden/installiert! Bitte VIPS oder DeepZoom installieren.')

###############################################################################

# Globale Variablen

# Zählen von Verarbeitungsdauer, Dateien, Fehlern
bm_time = time()
bm_files = 0
bm_errors = 0

# Dateiliste eines zu verarbeitenden Ordners
filelist = []

###############################################################################

# Kacheln generieren
def generate_tile(task):

  global bm_errors

  # expand tuple
  filename, filein, fileout = task

  # 1. VIPS Python-Bindings
  if tool == 1:
    try:
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

# Schleife über die verschiedenen Pfade
for path in args.paths:

  # Rekursives Durchsuchen der Pfade
  for rootpath, dirnames, filenames in os.walk(path):

    # Bestimmung des 'tiles'-Ordners im übergeordneten Ordner
    tilesfolder = os.path.join(os.path.abspath(os.path.join(rootpath, os.pardir)), 'tiles')

    # Löschen des 'tiles'-Ordners und ggfls. Unterordner
    if os.path.exists(tilesfolder):
      try:
        shutil.rmtree(tilesfolder, ignore_errors=True)
      except OSError, e:
        logger.error('Fehler beim Löschen: ' + str(e.args))
      except:
        raise

    # Erstellen des 'tiles'-Ordners und ggfls. Unterordner
    try:
      os.makedirs(tilesfolder)
    except OSError, e:
      # Für alle Fehler, außer dass der Ordner existiert, zum nächsten Ordner gehen
      if not e.errno == errno.EEXIST:
        logger.error('Fehler beim Erstellen ' + str(e.args))
        continue
    except:
      raise

    # Zurücksetzen der Listen
    del filelist[:]
    tasklist = []
    
    # Verarbeiten aller Dateien
    for filename in filenames:

      # Beschränkung auf Dateiendungen
      if filename.endswith(dateiendungen):

        # Datei in Listen speichern
        filelist.append(filename)
        tasklist.append((filename, os.path.join(rootpath, filename), os.path.join(tilesfolder, filename[:filename.rindex('.')])))
        bm_files += 1

    # Generieren von DeepZoomImages auslagern in Workers
    p = Pool(args.worker)
    p.map(generate_tile, tasklist)

    # Dateiendungen in .dzi ändern
    for filename in filelist:
      filename = filename[:filename.rindex('.')] + '.dzi'

    # Speichern der Dateiliste in einer JSON-Datei
    with open(os.path.join(tilesfolder, filename[:filename.rindex('_')] + '.json'), 'w') as jsonfile:
      json.dump({'files': filelist}, jsonfile)

    # Erstellen der Networker Direktive
    if args.networker:
      if not os.path.exists(os.path.join(tilesfolder[:tilesfolder.rindex('tiles')], 'tiles', '.nsr')):
        with open(os.path.join(tilesfolder[:tilesfolder.rindex('tiles')], 'tiles', '.nsr'), 'w') as networkerfile:
          networkerfile.write('+skip: *')
          logger.info('Networker Direktive erstellt: ' + os.path.join(tilesfolder[:tilesfolder.rindex('tiles')], 'tiles', '.nsr'))
          
    # Rekursives Durchsuchen der Ordner verhindern 
    break

###############################################################################

# Stats ausgeben
print '{} Sekunden für {} Dateien mit {} Fehlern.'.format(time() - bm_time, bm_files, bm_errors)