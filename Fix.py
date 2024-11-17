import asyncio
import websockets
import json
import requests
import random
import string

# Function to generate a random 32-character Chrome extension ID
def generate_random_extension_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

# Shared headers for requests with a dynamic `origin`
def get_headers():
    # Generate a random extension ID each time
    random_extension_id = generate_random_extension_id()
    
    return {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json;charset=UTF-8",
        "origin": f"chrome-extension://{random_extension_id}",  # Use random extension ID
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "x-client-info": "supabase-js-web/2.45.4",
        "x-supabase-api-version": "2024-01-01",
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlra25uZ3JneHV4Z2pocGxicGV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU0MzgxNTAsImV4cCI6MjA0MTAxNDE1MH0.DRAvf8nH1ojnJBc3rD_Nw6t1AV8X_g6gmY_HByG2Mag"  # Ensure this API key is included
    }

# Function to read account info from the file
def read_account_info(file_path):
    with open(file_path, 'r') as file:
        return {line.split('=')[0].strip(): line.split('=')[1].strip() for line in file}

# Login and get access token
def login(email, password):
    url = "https://ikknngrgxuxgjhplbpey.supabase.co/auth/v1/token?grant_type=password"
    payload = {"email": email, "password": password, "gotrue_meta_security": {}}
    response = requests.post(url, headers=get_headers(), json=payload)
    
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print("Access Token:", access_token)
        return access_token
    print("Login failed:", response.status_code, response.text)
    return None

# Get user info using the access token
def get_user_info(access_token):
    url = "https://ikknngrgxuxgjhplbpey.supabase.co/auth/v1/user"
    response = requests.get(url, headers={**get_headers(), "authorization": f"Bearer {access_token}"})
    
    if response.status_code == 200:
        user_id = response.json().get("id")
        print("User ID:", user_id)
        return user_id
    print("Failed to fetch user info:", response.status_code, response.text)
    return None

# Get personal code using the user ID
def get_personal_code(user_id, access_token):
    url = f"https://ikknngrgxuxgjhplbpey.supabase.co/rest/v1/profiles?select=personal_code&id=eq.{user_id}"
    response = requests.get(url, headers={**get_headers(), "authorization": f"Bearer {access_token}"})
    
    if response.status_code == 200:
        personal_code = response.json()[0].get("personal_code")
        print("Personal Code:", personal_code)
        return personal_code
    print("Failed to fetch personal code:", response.status_code, response.text)
    return None

# WebSocket function with periodic PING every 3 seconds
async def connect_to_websocket(user_id):
    url = f"wss://secure.ws.teneo.pro/websocket?userId={user_id}&version=v0.2"
    try:
        async with websockets.connect(url) as websocket:
            print("Connected to WebSocket")
            
            # Wait for the connection success message before sending PING
            message = await websocket.recv()
            response = json.loads(message)
            print(f"Received message: {response}")
            if response.get("message") == "Connected successfully":
                print("Connection established successfully!")

            # Loop to send PING every 3 seconds
            while True:
                ping_message = {"type": "PING"}
                await websocket.send(json.dumps(ping_message))
                print("Sent PING message:", ping_message)
                await asyncio.sleep(3)  # Wait for 3 seconds before sending the next PING
    except Exception as e:
        print(f"Error connecting to WebSocket: {e}")

# Main function
async def main():
    account_info = read_account_info('account.txt')

    # Login and get access token
    access_token = login(account_info.get("email"), account_info.get("password"))

    if access_token:
        user_id = get_user_info(access_token)
        if user_id:
            get_personal_code(user_id, access_token)
            await connect_to_websocket(user_id)  # Connect to WebSocket after retrieving user information

# Run the complete process
asyncio.run(main())
