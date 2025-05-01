import requests

print(requests.get("http://213.239.221.99:5000/tasks/5").json())