@echo off
echo Post-render script...
aws s3 sync _outputs/ s3://cibic-renderings
aws s3 sync _exports/pickle_jar s3://cibic-cache