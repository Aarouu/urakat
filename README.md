# urakat
Ihmiset voivat postata alustalle urakkahommia, jotka tulisi toteuttaa esim. kattoremontti. Johon kaikki tämän toteuttamiseen kykenevät voivat tarjota hinnan josta toteuttavat tämän. 

## Sovelluksen toiminnot

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan omia tarjolla olevia urakoita esim. kattoremontti.
* Käyttäjä näkee sovellukseen lisätyt ilmoitukset.
* Käyttäjä pystyy etsimään muiden julkaisemia urakoita.
* Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja käyttäjien historiasta .
* Käyttäjä pystyy valitsemaan urakan ilmoitukselle milloin, millä hinnalla, missä paikassa ja kuinka nopeasti tulisi saada valmiiksi.
* Käyttäjä pystyy tarjoutua tekemään toisten postaaman urakan omalla hinnalla ja ehdoillaan.

## Sovelluksen asennus

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut ja lisää alkutiedot:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```
