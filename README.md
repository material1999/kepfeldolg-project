# Képfeldolgozás haladóknak projektmunka - Snooker

## Téma: 

Videófelvételeken a snooker asztalon mozgó golyók nyomkövetése és a találatok detektálása a lyukba guruló golyók pontértékének (színének) meghatározásával.

## Feladat megvalósítása: 

Python nyelven, az OpenCv, NumPy, Sys és PyQt5 csomagok használatával.

## Használati útmutató:

### Használathoz szükséges nyelvek és csomagok: 

- Python3
- PyQt5
- OpenCV
- NumPy

### A kódbázis használata 

Az alkalmazást futtathatjuk fejlesztői környezetből is, vagy készíthetünk belőle futtatható állományt. Utóbbihoz a szükséges parancsok megtalálhatók a create_exe.txt szövegfájlban Windows és MacOS operációs rendszerekre. 

### A futtatható állomány használata 

Az alkalmazás használatához nem kell mást tennünk, mint a generált mappából kikeresni a SnookerCounter.exe fájlt és futtatni azt. 

Futtatás után egy egyszerű GUI felületet kell lássunk, két gombbal. Az első gomb segítségével kereshetjük ki a fájlkezelőből a vizsgálni kívánt videót, majd a START gomb segítségével indíthatjuk el (illetve szüneteltethetjük is) a feldolgozást. Az eredmény videó a futás végén automatikusan elkészül. 

### Saját, példától eltérő videók

Amennyiben saját videót akarunk használni, szükséges lehet a színmaszkok kódszintű módosítása. Ebben az esetben a maszkok értékének átírása után generáljuk újra a futtatható állományt, nyissuk meg az új videót, és más teendőnk nincs is. 
