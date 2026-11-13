# Data sources

## airports.csv / runways.csv / countries.csv / regions.csv
- Source: OurAirports open data — https://davidmegginson.github.io/ourairports-data/
- License: public domain.

## airlines.dat (added 2026-10-29)
- Source: OpenFlights Airline Database, snapshot from the official GitHub repo
  https://github.com/jpatokal/openflights (file: data/airlines.dat)
  Downloaded from: https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat
  on 2026-10-29.
- License: Open Database License (ODbL) + Database Contents License, per
  https://openflights.org/data.php — use requires attribution to OpenFlights
  and share-alike licensing of publicly distributed derived databases.
  Airline pages on this site carry an "Data: OpenFlights" attribution.
- Fields: Airline ID, Name, Alias, IATA code, ICAO code, Callsign, Country, Active (Y/N).
  `\N` in the file means "no value".
- Filter used by generate.py for published pages: Active = "Y" AND IATA code is a
  valid 2-character code ([A-Z0-9]{2}). That yields 1,003 airlines over 984 unique
  IATA codes (19 IATA codes are legitimately shared by 2–3 carriers; those get one
  shared code page listing all of them).
- Known quality caveats: the OpenFlights snapshot is aging and its Active flag is
  imperfect (e.g. Ansett Australia, defunct since 2002, is still flagged "Y");
  156 of the filtered airlines have no ICAO code and 234 have no callsign in the
  source, so those fields are simply omitted on their pages. No alliance data
  exists in airlines.dat, so no alliance field is published.
