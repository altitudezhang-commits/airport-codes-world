# Airport Codes World

Every airport on Earth gets its own page: a zero-dependency programmatic-SEO generator that builds 5,500+ static pages from public data.

This repository contains the Python generator and source data used to build [Airport Codes World](https://airport-codes-world.pages.dev), a static reference site for airport and airline codes.

## What it generates

- One page for every airport with an IATA code in the bundled OurAirports data
- Airline code pages from the bundled OpenFlights snapshot
- Country and index pages, plus a sitemap
- Pure static HTML with inline CSS — no JavaScript framework, no build dependencies

## Quick start

Requirements: Python 3.10+ (standard library only).

```bash
python3 generate.py --base https://airport-codes-world.pages.dev
```

Generated files are written to `dist/`.

> **Note on `data/airports.csv`:** the file is stored in this repository as four
> sequential parts (`data/airports.csv.part-001` … `part-004`) because of upload
> size limits. Reassemble it once before generating:
>
> ```bash
> sh data/join_airports_csv.sh
> ```

## Data and attribution

- Airport, runway, country, and region data: [OurAirports](https://davidmegginson.github.io/ourairports-data/), released into the public domain.
- Airline data: [OpenFlights Airline Database](https://openflights.org/data.php), used under the Open Database License (ODbL) and Database Contents License. Publicly distributed derived databases must keep the OpenFlights attribution and share-alike terms. See `data/SOURCES.md` for the exact snapshot, filters, and known data caveats.

## Code license

The generator code is released under the MIT License. Data files keep the licenses and attribution terms stated above.
