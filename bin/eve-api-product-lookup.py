import requests
import sys
import csv
import json

ESI_ID_URL = 'https://esi.evetech.net/latest/universe/names/'

def fetch_name(id):
    res = requests.post(ESI_ID_URL, data=[id])
    if res.status_code >= 300:
        return "Error Status"

    data = res.json()
    return json.dumps(data)

def main():
    idColumn = sys.argv[1]
    prodName = sys.argv[2]

    outfile = sys.stdout

    r = csv.DictReader(sys.stdin)
    w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
    w.writeheader()

    for result in r:
        if result[idColumn] and result[prodName]:
            w.writerow(result)

        elif result[idColumn]:
            result[prodName] = fetch_name(result[idColumn])
            w.writerow(result)

        else:
            result[idColumn] = 'Error'
            w.writerow(result)