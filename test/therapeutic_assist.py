payload = {
    "msg" : "hi there"
}


import requests
url = 'http://127.0.0.1:1337/assist'
headers = {'Content-type': 'application/x-www-form-urlencoded'}
x = requests.post(url, headers=headers, data=payload)
print(x.text)