import asyncio
import os
import aiohttp
import json
import datetime
import base64
import random
import time
from hashlib import md5
from typing import Optional

from dotenv import load_dotenv, dotenv_values 

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad

load_dotenv()

SEARCHED_LOCATIONS_PATH = "data/searched_locations.json"

# fetch datamall api key from env
API_ENDPOINT = os.getenv("API_ENDPOINT")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")

HEADER_PREFIX = os.getenv("HEADER_PREFIX")

REQUEST_API_VERSION = os.getenv("REQUEST_API_VERSION")
REQUEST_BRAND = os.getenv("REQUEST_BRAND")
REQUEST_OS = os.getenv("REQUEST_OS")
REQUEST_OS_VERSION = os.getenv("REQUEST_OS_VERSION")
REQUEST_SCREEN = os.getenv("REQUEST_SCREEN")
REQUEST_VERSION = os.getenv("REQUEST_VERSION")
REQUEST_VERSION_CODE = os.getenv("REQUEST_VERSION_CODE")
REQUEST_USER_AGENT = os.getenv("REQUEST_USER_AGENT")

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

class Client:
    def __init__(self, token: str = ''):
        super().__init__()

        self.http_session = aiohttp.ClientSession()

        if os.path.exists(SEARCHED_LOCATIONS_PATH):
            with open(SEARCHED_LOCATIONS_PATH, 'r') as f:
                self.searched_locations = set(tuple(x) for x in json.load(f))
        else:
            self.searched_locations = set()

        self.private_rsa_cipher = PKCS1_v1_5.new(RSA.import_key(PRIVATE_KEY))
        self.public_rsa_cipher = PKCS1_v1_5.new(RSA.import_key(PUBLIC_KEY))
        self.token = token

    def save_searched_locations(self):
        with open(SEARCHED_LOCATIONS_PATH, 'w') as f:
            json.dump(list(self.searched_locations), f)


    def decrypt(self, encrypted_key: str, encrypted_data: str):
        ek_bytes = base64.b64decode(encrypted_key)
        sentinel = random.randbytes(16)  # Random sentinel for padding
        aes_key_raw = self.private_rsa_cipher.decrypt(ek_bytes, sentinel=sentinel)
        
        if aes_key_raw == sentinel:
            raise ValueError("Decryption failed. Sentinel was returned.")

        aes_cipher = AES.new(base64.b64decode(aes_key_raw), AES.MODE_ECB)
        ed_bytes = base64.b64decode(encrypted_data)
        decrypted = unpad(aes_cipher.decrypt(ed_bytes), 16)
        return decrypted.decode('utf-8')

    def encrypt(self, message: str):
        bytes_message = message.encode('utf-8')
        current_time_millis = str(int(time.time() * 1000))
        generated_aes_key = os.urandom(16)

        encrypted_aes_key = self.public_rsa_cipher.encrypt(base64.b64encode(generated_aes_key, altchars=None))
        security_key = base64.b64encode(encrypted_aes_key, altchars=None).decode('utf-8')
        aes_cipher = AES.new(generated_aes_key, AES.MODE_ECB)

        deviceId = os.urandom(20).hex().upper()
        nonce = md5((deviceId + current_time_millis).encode()).hexdigest()

        td_elements = [
            self.token,
            deviceId
        ]
        td = base64.b64encode(aes_cipher.encrypt(pad(':'.join(td_elements).encode(), 16)), altchars=None).decode('utf-8')
        headers = {
            HEADER_PREFIX + '-Timestamp': current_time_millis,
            HEADER_PREFIX + '-Nonce': nonce,
            HEADER_PREFIX + '-Security': security_key,
            HEADER_PREFIX + '-td': td,
        }
        if self.token:
            headers[HEADER_PREFIX + '-Token'] = self.token
        encrypted_message = aes_cipher.encrypt(pad(bytes_message, 16))
        encrypted_message = base64.b64encode(encrypted_message, altchars=None).decode('utf-8')

        return encrypted_message, headers

    async def request(self, url: str, payload: dict, *, additional_headers: Optional[dict] = None):
        encrypted_payload, headers = self.encrypt(json.dumps(payload))
        if additional_headers is not None:
            headers.update(additional_headers)

        params = {'d': encrypted_payload}
        headers = {
            **headers,
            HEADER_PREFIX + '-Api-Version': REQUEST_API_VERSION,
            HEADER_PREFIX + '-Brand': REQUEST_BRAND,
            HEADER_PREFIX + '-Channel': '1',
            HEADER_PREFIX + '-Network': '0',
            HEADER_PREFIX + '-OS': REQUEST_OS,
            HEADER_PREFIX + '-OS-Version': REQUEST_VERSION,
            HEADER_PREFIX + '-Screen': REQUEST_SCREEN,
            HEADER_PREFIX + '-Version': REQUEST_VERSION,
            HEADER_PREFIX + '-VersionCode': REQUEST_VERSION_CODE,
            'User-Agent': REQUEST_USER_AGENT
        }
        
        auth = aiohttp.BasicAuth(login=LOGIN, password=PASSWORD)

        async with self.http_session.get(url, params=params, headers=headers, auth=auth) as response:
            response.raise_for_status()
            parsed_response = await response.json()

        decrypted_data = self.decrypt(parsed_response['k'], parsed_response['d'])
        return json.loads(decrypted_data)

    async def get_parking(self, latitude, longitude):
        payload = {
            "lng": longitude,
            "radius": "1000",
            "lat": latitude
        }
        location_str = ','.join([
            str(latitude), str(longitude), '-1', str(int(time.time() * 1000)), '-1'
        ])
        return await self.request(
            API_ENDPOINT, payload,
            additional_headers={HEADER_PREFIX + '-Location': location_str}
        )
    
    async def update_parking(self, latitude, longitude):

        print("hellooooo ")
        response = await self.get_parking(latitude, longitude)
        data = response['data']['area']

        print("we got the data!")

        with open('data/bicycle_parking_locations.json', 'r') as file:
            bicycle_parking_locations = json.load(file)["data"]

        processed_data = []

        insertions = 0

        for location in bicycle_parking_locations:
            processed_item = location
            
            for datum in data:
                if (abs(processed_item['latitude'] - datum['lat']) < 0.0002 and
                    abs(processed_item['longitude'] - datum['lng']) < 0.0002) and 'qr' not in processed_item:
                    processed_item['qr'] = datum['qrCode']
                    insertions += 1

                    self.searched_locations.add((processed_item['latitude'], processed_item['longitude']))
                    data.remove(datum)
                    break
                elif 'qr' in processed_item:
                    self.searched_locations.add((processed_item['latitude'], processed_item['longitude']))
            
            
            processed_data.append(processed_item)

        with open('data/bicycle_parking_locations.json', 'w') as file:
            json.dump({"data": processed_data}, file, indent=2)

        print(f"updated {insertions} parking locations.")

        return insertions

    async def find_next_location(self):
        with open('data/bicycle_parking_locations.json', 'r') as file:
            bicycle_parking_locations = json.load(file)["data"][::-1]

        target_location = None

        for location in bicycle_parking_locations:
            if "qr" not in location and (location['latitude'], location['longitude']) not in self.searched_locations:
                target_location = location
                break
            elif "qr" in location:
                self.searched_locations.add((location['latitude'], location['longitude']))

        print("yay we got a target location:", target_location)
        
        if target_location is None:
            print("No more locations to process.")
            return False
        
        updated = await self.update_parking(
            target_location['latitude'],
            target_location['longitude']
        )

        self.searched_locations.add((target_location['latitude'], target_location['longitude']))
        self.save_searched_locations()

        # sleep for 10s
        print(f"Sleeping for 10 seconds after processing! yay we're repsonsible!")
        await asyncio.sleep(2.5)

        return True
    
if __name__ == '__main__':
    async def main():
        client = Client()

        while True:
            has_next = await client.find_next_location()
            if not has_next:
                break

        await client.http_session.close()

    asyncio.run(main())