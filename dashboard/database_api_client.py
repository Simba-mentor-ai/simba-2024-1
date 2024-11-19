import pandas as pd
import requests
import json
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_data(self,
                 endpoint='conversations', 
                 limit=1000,
                 api_key='default'):
        
        headers = {
            'X-API-Key': api_key
        }
        response = requests.get(f'{self.base_url}/{endpoint}', headers=headers)

        if response.status_code != 200:
            print('Failed to fetch data:', response.status_code)
            return None
        
        if not response.json():
            print('No data returned')
            return None
        
        if 'total' not in response.json():
            print('No total key in response')
            return None
        else:
            total_conversations = response.json()['total']
            print(f'Total conversations: {total_conversations}')
        
        if total_conversations > 1000:
            print('There are more than 1000 conversations, fetching them in chunks of 1000')
            offset = 0
            response_data = []
            while offset < total_conversations:
                response = requests.get(f'{self.base_url}/{endpoint}?offset={offset}&limit={limit}', headers=headers)
                offset += 1000
                response_data += response.json()['data']
                print(f'Fetched {offset} conversations')
        else:
            response_data = response.json()['data']

        return response_data
    
    