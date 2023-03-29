@echo off
echo AWS Sync...
aws s3 sync s3://cibic21-viz-website/photos _outputs/photos
aws s3 sync s3://cibic21-viz-website/cache _exports/pickle_jar