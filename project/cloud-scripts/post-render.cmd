@echo off
echo Post-render script...
aws s3 sync _outputs/data s3://cibic21-viz-website/data
aws s3 sync _outputs/photos s3://cibic21-viz-website/photos
aws s3 sync _outputs/renderings s3://cibic21-viz-website/renderings
aws s3 sync _exports/pickle_jar s3://cibic21-viz-website/cache