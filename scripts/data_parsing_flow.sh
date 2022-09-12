set -e

echo "$PWD"

cd python_files

echo "Air Quality ingestion pipeline starts"
jupyter nbconvert --to notebook --execute 2_feature_pipeline.ipynb

