
export MONGODB_URI=mongodb+srv://aescobar:Tks12345@cluster0.iz5q7.mongodb.net/test
echo "MONGODB_URI=$MONGODB_URI"
pytest -v --cov /api-run/test/

echo "Testting Done"