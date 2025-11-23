import requests

# Change this to your live server API endpoint
API_URL = "https://giftedlucky.pythonanywhere.com/billing/api/sync/sales/"

def sync_sales():
    try:
        response = requests.post(API_URL, json={})
        if response.status_code == 200:
            print("✅ Sync successful:", response.json())
        else:
            print("❌ Sync failed:", response.status_code, response.text)
    except Exception as e:
        print("⚠️ Error during sync:", str(e))

if __name__ == "__main__":
    sync_sales()
