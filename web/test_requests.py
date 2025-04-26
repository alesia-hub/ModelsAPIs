import requests

base_url = 'http://192.168.0.26:5000'

request_type = base_url+'/register'

body = {
            'username': 'Mark Twain',
            'password': 'Cat123',
            'tokens': 14
        }

session = requests.Session()
session.headers = {"content-type": "application/json"}

post_request = session.post(request_type, body)
response_data = post_request.json()
print(response_data)
