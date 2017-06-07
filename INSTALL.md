# Kachelgenerator
## 1. Installation eines DeepZoomImage-Generators
Es gibt zwei Tools, die verwendet werden können: VIPS und DeepZoom. Trotz relativ aufwändiger Installation lautet die klare Empfehlung VIPS, das mehr als doppelt so schnell als DeepZoom ist. Hier gibt es zwei weitere Möglichkeiten, einmal die Nutzung als Subprozess (vermutlich ausreichend) oder mit Python-Bindings (volle Kontrolle und Feedback mit VIPS aus Python heraus, z. B. Fortschrittsanzeige möglich). Das Skript überprüft die Verfügbarkeit aller genannten Tools.
### 1.1: VIPS
[http://www.vips.ecs.soton.ac.uk/](http://www.vips.ecs.soton.ac.uk/)
Den neuesten Source Code findet man unter [http://www.vips.ecs.soton.ac.uk/supported/current/](http://www.vips.ecs.soton.ac.uk/supported/current/).
#### 1.1.1: Installation mit Python-Bindings
```
# Abhängigkeiten installieren
sudo zypper in pkg-config glib2 glib2-devel libxml2 libxml2-devel libgsf libgsf-devel libtiff-devel ImageMagick-devel python-devel python-cairo-devel cairo cairo-devel  libexif-devel libjpeg-turbo gettext-runtime libpng16-devel orc fftw3-devel pango-devel libpoppler-glib-devel librsvg-devel orc

# Installation von gobject-introspection für Python-Bindings (>=1.39.0)
wget http://ftp.gnome.org/pub/GNOME/sources/gobject-introspection/1.39/gobject-introspection-1.39.90.tar.xz
tar xf gobject-introspection-1.39.90.tar.xz
cd gobject-introspection-1.39.90
./configure
make && sudo make install
cd ..

# Installation von pygobject für Python-Bindings (>=3.14.0)
wget http://ftp.gnome.org/pub/GNOME/sources/pygobject/3.14/pygobject-3.14.0.tar.xz
tar xf pygobject-3.14.0.tar.xz
cd pygobject-3.14.0
./configure --with-python=python
make && sudo make install
cd ..

# Installation von VIPS
wget http://www.vips.ecs.soton.ac.uk/supported/current/vips-8.4.2.tar.gz
tar xvf vips-8.4.2.tar.gz
cd vips-8.4.2
./configure --prefix=/usr
make && sudo make install
sudo ldconfig

# Nacharbeiten
export GI_TYPELIB_PATH="/usr/lib64/girepository-1.0"
sudo cp /usr/lib64/python2.7/site-packages/gi/overrides/Vips.* /usr/local/lib64/python2.7/site-packages/gi/overrides
```
#### 1.1.2: Installation als Python-Subprozess
```
# Abhängigkeiten installieren
sudo zypper in pkg-config glib2 glib2-devel libxml2 libxml2-devel libtiff-devel ImageMagick-devel python-devel libexif-devel libjpeg-turbo libpng16-devel

# Installation von VIPS
wget http://www.vips.ecs.soton.ac.uk/supported/current/vips-8.4.2.tar.gz
tar xvf vips-8.4.2.tar.gz
cd vips-8.4.2
./configure --prefix=/usr
make && sudo make install
sudo ldconfig
```

### 1.2 DeepZoom
[https://github.com/openzoom/deepzoom.py](https://github.com/openzoom/deepzoom.py)
```
# Installieren der Abhängigkeiten
sudo zypper in python-imaging

# Installation
git clone https://github.com/openzoom/deepzoom.py.git
cd deepzoom.py
sudo python setup.py install
```
## 2. Skript zur Erzeugung von rekursiven Erzeugung von Kacheln
Das Skript `kachelgenerator.py` prüft nacheinander die Verfügbarkeit von
1. VIPS mit Python-Bindings
2. VIPS als Python-Subprozess (Shell)
3. DeepZoom

und generiert die Kacheln mit dem zuerst gefundenen Tool.

### 2.1 Benutzung
#### 2.1.1 Hilfe
`kachelgenerator.py -h`:
```
usage: kachelgenerator_v3.py [-h] [-l] [-n] [-w [WORKER]] [paths [paths ...]]

DeepZoomImages-Generator

positional arguments:
  paths        Pfade in denen nach Digitalisaten gesucht wird.

optional arguments:
  -h, --help   show this help message and exit
  -l           Erstellt Logfile (kachelgenerator.log).
  -n           Erstellt Networker Direktive (tiles-Ordner werden vom Backup ausgeschlossen).
  -w [WORKER]  Anzahl Worker (default 4).
```
#### 2.1.2 Beispiele
* in aktivem Verzeichnis und allen Unterverzeichnissen
`./kachelgenerator.py`
* in übergebenen Verzeichnissen und deren Unterverzeichnissen
`./kachelgenerator.py /pfad/1 /pfad/2`
* ohne Multiprocessing
`./kachelgenerator.py -w 1`
* mit 8 parallelen Prozessen
`./kachelgenerator.py -w 8`
* erzeuge Logdatei in aktivem Verzeichnis (kachelgenerator.log)
`./kachelgenerator.py -l`
* erzeuge Networker Direktive
`./kachelgenerator.py -n`
* volles Programm
`./kachelgenerator.py -l —n -w 8 /pfad/1 /pfad/2`
### 2.2 Konfiguration
Im Skript können zwei Variablen angepasst werden:
#### 2.2.1 Ordnernamen
`ordnernamen = ('max', 'dpi300-jpg')`
Liste aller Ordner, die die jeweilig höchste Auflösung beinhalten (als Tuple)
#### 2.2.2 Dateiendungen
`dateiendungen = ('.jpg', '.jpeg')`
Liste der Dateiendungen für die zu konvertierenden Digitalisate (als Tuple)