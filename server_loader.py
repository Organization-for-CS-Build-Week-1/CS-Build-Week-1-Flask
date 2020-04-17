import os
import requests
import json

main_url = 'https://safe-reef-80226.herokuapp.com/'

def make_request(dir, params=None, headers=None):
    url = main_url + dir
    response = requests.request('GET', url, params=params, headers=headers)
    return response.json()

def register_request(username, password1, password2):
    params =  {'username':username, 'password1':password1, 'password2':password2}
    return make_request('/api/registration/', params=params)

def load_request(Authorization):
    headers = {'Authorization':Authorization}
    return make_request('/api/debug/load/', headers=headers)

auth = register_request("XXXXXXXXX", "NNNNNNNNN", "NNNNNNNNN")['key']

load_request(auth)
