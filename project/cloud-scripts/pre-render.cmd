@echo off

cd python

echo Fetching rew rides...
 
python fetch_caches.py

echo Render WebViz GEOJSON...

python web_viz_render_geojson.py

cd ../