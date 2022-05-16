
export MONGODB_URI=$DB_TEST
pytest -v --cov /api-run/test/

echo "Testting Done"