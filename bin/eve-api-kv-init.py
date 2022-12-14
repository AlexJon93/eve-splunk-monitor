import yaml
import requests
import sys

SPLUNK_KV_URL = 'https://localhost:8089/servicesNS/admin/eve-online-monitor/storage/collections/kvstorecoll/batch_save'

def save_to_kv(out):
    res = requests.post(SPLUNK_KV_URL, json=out)
    if res.status_code >= 300:
        print('API returned code: ', res.status_code)
        sys.exit(1)

def run():
    with open('./data/typeIDs.yaml') as file:
        print('Loading typeID yaml...')
        data = yaml.load(file, Loader=yaml.CFullLoader)
        out = []
        for k, v in data.items():
            out.append({k: v['name']['en']})

    print('Saving to KV store')
    


if __name__ == "__main__":
    run()