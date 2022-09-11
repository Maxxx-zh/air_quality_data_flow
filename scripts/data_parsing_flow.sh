set -e

echo "$PWD"

cd python_files

echo "Air Quality ingestion pipeline starts"
python3 data_parsing.py


