# Mars Walk Planner
Browser prototype for planning and rehearsing a safe walk on Mars, using real HiRISE data (Jezero Crater region, 2 km square).

Live site (GitHub Pages): https://vajnak.github.io/mars-walk-planner/
- `index.html` home page, `map.html` map and route planner, `walk.html` first-person 3D view.

Data: NASA/JPL-Caltech/University of Arizona (HiRISE DTM DTEEC_048842_1985_048908_1985_U01 and orthoimage ESP_048842_1985_RED_C_01_ORTHO), distributed by USGS Astrogeology.

Run locally: `python -m http.server 8000` in this folder, then open http://localhost:8000
Rebuild data: put the two raw files next to prep_data.py and run `python prep_data.py` (needs numpy and pillow).
