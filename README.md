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

### Beschreibung

Der DLA Kachelgenerator generiert DeepZoomImages aus allen Dateien in einem übergebenen Verzeichnis, bzw. allen Dateien in spezifischen Unterverzeichnissen. Zusätzlich wird eine JSON-Datei im `tiles`-Ordner erzeugt, die die komplette Dateiliste zur Verwendung mit z. B. [OpenSeadragon](https://openseadragon.github.io/) enthält. Die JSON-Datei ist nach dem übergeordneten Verzeichnis benannt.

#### Hilfe

```bash
kachelgenerator.py -h
```

```
usage: kachelgenerator.py [-h] 
                          [--recursive [RECURSIVE [RECURSIVE ...]]]
                          [--extensions [EXTENSIONS [EXTENSIONS ...]]] 
                          [-l]
                          [-n] 
                          [-w [WORKER]]
                          [paths [paths ...]]

DeepZoomImages-Generator

positional arguments:
  paths                 Pfade, die die Digitalisate enthalten.

optional arguments:
  -h, --help            show this help message and exit
  --recursive [RECURSIVE [RECURSIVE ...]]
                        Ordner, die die Digitalisate enthalten (absteigende Präferenz)
  --extensions [EXTENSIONS [EXTENSIONS ...]]
                        Mögliche Dateiendungen der Digitalisate (default: tiff, tif, jpg, jpeg)
  -l                    Erstellt Logfile (kachelgenerator.log).
  -n                    Erstellt Networker Direktive (tiles-Ordner werden vom Backup ausgeschlossen).
  -w [WORKER]           Anzahl Worker (default 4).
```

#### Beispiele

* im aktivem Verzeichnis
`./kachelgenerator.py`

* in den übergebenen Verzeichnissen
`./kachelgenerator.py /pfad/1 /pfad/2`

* in den Ordnern "org" und "max" innerhalb der übergebenen Verzeichnisse
`./kachelgenerator.py /pfad/1 /pfad/2 --recursive org max`

* nur Dateien mit der Endung "tiff"
`./kachelgenerator.py --extensions .tiff`

* ohne Multiprocessing
`./kachelgenerator.py -w 1`

* mit 8 parallelen Prozessen
`./kachelgenerator.py -w 8`

* erzeuge Logdatei in aktivem Verzeichnis (kachelgenerator.log)
`./kachelgenerator.py -l`

* erzeuge Networker Direktive (Ausschluss vom Backup)
`./kachelgenerator.py -n`

* volles Programm
`./kachelgenerator.py /pfad/1 /pfad/2 --recursive org max  --extensions .tiff -l —n -w 8`