import MySQLdb

try:
    db = MySQLdb.connect(
        host="interchange.proxy.rlwy.net",
        user="root",
        passwd="AFSoanivFRVyQhpJqtBqRbrkYXykkJYm",
        db="railway",
        port=23332
    )
    print("✅ Connected to MySQL successfully!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
