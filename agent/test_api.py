import requests
import pandas as pd

resp = requests.post(
    "http://127.0.0.1:3000/query",
    json={"sql": "UPDATE orders SET order_id=10;"}
)
body = resp.json()

print(body)