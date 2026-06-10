# Home map geometry — provenance + how to regenerate

The `.metro-outline` SVG on the homepage (760×430 viewBox) uses two kinds of
geometry, both derived from OpenStreetMap:

1. **Municipal outlines** (`.metro-area`, `.metro-area-context`) — simplified
   from OSM/Nominatim boundary relations (pre-2026-06; original script lost).
2. **Water** (`.mw-strait`, `.mw-bay`, `.mw-river`, `.mw-lake`) — added
   2026-06-09 from real OSM geometry. Bays/lakes via Nominatim
   `polygon_geojson=1`; Fraser/Pitt riverbank polygons via Overpass
   (`natural=water` + `water=river` in bbox). Drawn ON TOP of the land tints
   because municipal boundaries legally extend into water. The strait along
   the west edge is the one hand-built path (hugs the real coast edges).

## Projection (equirectangular, fitted to the existing outlines)

    x = 501.7365 * lon + 61966.19
    y = -767.1709 * lat + 37987.15

Recovered by least-squares fit of Nominatim city bounding boxes against the
in-file path bboxes (3–7 px residual per city; y/x scale ratio = 1/cos 49.2°).
Inverse, for the viewport bbox: lon = (x − 61966.19) / 501.7365,
lat = (y − 37987.15) / −767.1709 → viewport ≈ (48.955, −123.50) to
(49.516, −121.988) (S,W,N,E).

## To add/refresh a water or boundary feature

1. Fetch GeoJSON: `https://nominatim.openstreetmap.org/search?q=<name>&format=json&limit=1&polygon_geojson=1`
   (send a User-Agent). For riverbanks use Overpass `natural=water` polygons.
2. Project every (lon,lat) with the constants above.
3. Clip to (−8,−8)–(768,438), Douglas-Peucker simplify at ~1 px tolerance,
   drop fragments with bbox area < 70 px², round to 1 decimal.
4. Emit `M x y L x y … Z` and append inside `<g class="metro-water-over">`
   (bays/rivers/lakes) or before the context group (backdrop layers).

Gotchas: Nominatim free-text matches can be wrong ("Howe Sound" → a paper
mill; "Mission" → a street address) — always check `display_name` before
using a result. After any home CSS/markup change, regenerate city pages
(`python3 _generate_city_pages.py`) — they embed the home `<style>` block and
scrape the map pins for per-city market data.
