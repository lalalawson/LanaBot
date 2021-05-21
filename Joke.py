import requests

def random_joke():
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    joke = response.json()
    return joke['setup'], joke['punchline']