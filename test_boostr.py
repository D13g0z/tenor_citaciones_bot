import requests

patente = "JRCL48"
url = f"https://api.boostr.cl/vehicle/{patente}.json"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnQiOiJEaWVnbyBaw7rDsWlnYSBHb21leiIsInBsYW4iOiJmcmVlIiwiYWRkb25zIjoiIiwiZXhjbHVkZXMiOiIiLCJyYXRlIjoiNXgxMCIsImN1c3RvbSI6eyJkb2N1bWVudF9udW1iZXJfZGFpbHlfbGltaXQiOiI1IiwicGxhdGVzX2RhaWx5X2xpbWl0IjoiNSJ9LCJpYXQiOjE3NTI5MDAxOTYsImV4cCI6MTc1NTQ5MjE5Nn0.qTFTe7oBRV5OgMidAUrOB0mQRGG4I0VSJRquC5xMueo"
}

response = requests.get(url, headers=headers)

print("Código de respuesta:", response.status_code)
print("Contenido bruto:")
print(response.text)