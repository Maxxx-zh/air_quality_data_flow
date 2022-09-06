set -e

echo "$PWD"

cd python_files

echo "Air Quality ingestion pipeline starts"
python3 air_quality_parsing.py


