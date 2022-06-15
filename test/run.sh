
export MONGODB_URI=mongodb+srv://aescobar:Tks12345@cluster0.iz5q7.mongodb.net/test
export SQLALCHEMY_URI=postgresql://admin:p0o9q2w3@123.123.123.123:5432/cake_cms
echo "MONGODB_URI=$MONGODB_URI"
pytest -v --cov /api-run/test/

echo "Testting Done"