# dla_kachelgenerator
Script to generate tiles (DeepZoomImages)
Skript zur Erzeugung von Kacheln (DeepZoomImages)

### Tools

Das Skript `kachelgenerator.py` prüft nacheinander die Verfügbarkeit von
1. [http://www.vips.ecs.soton.ac.uk/](VIPS) mit Python-Bindings
2. [http://www.vips.ecs.soton.ac.uk/](VIPS) als Python-Subprozess (Shell)
3. [https://github.com/openzoom/deepzoom.py](DeepZoom)

und generiert die Kacheln mit dem zuerst gefundenen Tool.

### Installation

Siehe `INSTALL.md`.

### Benutzung

#### Hilfe

```bash
kachelgenerator.py -h
```

```
usage: kachelgenerator_v3.py [-h] [-l] [-n] [-w [WORKER]] [paths [paths ...]]

DeepZoomImages-Generator

positional arguments:
  paths        Pfade, die die Digitalisate enthalten.

optional arguments:
  -h, --help   show this help message and exit
  -l           Erstellt Logfile (kachelgenerator.log).
  -n           Erstellt Networker Direktive (tiles-Ordner werden vom Backup ausgeschlossen).
  -w [WORKER]  Anzahl Worker (default 4).
```

#### Beispiele

* im aktivem Verzeichnis
`./kachelgenerator.py`

* in den übergebenen Verzeichnissen
`./kachelgenerator.py /pfad/1 /pfad/2`

* ohne Multiprocessing
`./kachelgenerator.py -w 1`

* mit 8 parallelen Prozessen
`./kachelgenerator.py -w 8`

* erzeuge Logdatei in aktivem Verzeichnis (kachelgenerator.log)
`./kachelgenerator.py -l`

* erzeuge Networker Direktive (Ausschluss vom Backup)
`./kachelgenerator.py -n`

* volles Programm
`./kachelgenerator.py -l —n -w 8 /pfad/1 /pfad/2`

### Konfiguration

Das Skript konvertiert standardmässig folgende Dateiendungen:

`dateiendungen = ('.tiff', '.tif', '.jpg', '.jpeg')`

Dise Liste wird als Tuple angegeben und kann entsprechend angepasst werden.