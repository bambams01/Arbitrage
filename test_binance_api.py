import httpx

API_KEY = "kKnKn9OwGnfqLxca9JHU6AGzTYjpFxCBO5gb3ECt2qV5nSDANFtcfZAMhMbyBpxw"
SECRET_KEY = "SsqvNouLmBHzMKaNWc6NO7NZKzQC8IDKq5UtFtdfNPc62UBZ5p0O1nOBniuNaE4X"

headers = {
    "X-MBX-APIKEY": API_KEY
}

url = "https://api.binance.com/api/v3/account"

with httpx.Client(verify=False) as client:
    response = client.get(url, headers=headers)
    print("Status Code:", response.status_code)
    print("Response:", response.text)