"""
View available API endpoints
"""
from gradio_client import Client

SPACE_URL = "https://ahammadshawki8-cattle-detection-api.hf.space"

print("Checking available API endpoints...")
print(f"Space URL: {SPACE_URL}\n")

try:
    client = Client(SPACE_URL)
    
    print("Available API endpoints:")
    print(client.view_api(return_format="dict"))
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
