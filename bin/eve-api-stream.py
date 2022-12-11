import requests
import sys
import os
import logging
import json

# set up logging suitable for splunkd consumption
logging.root
logging.root.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s %(message)s')
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(formatter)
logging.root.addHandler(handler)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from splunklib.modularinput import *

ESI_BASE_URL = 'https://esi.evetech.net/latest'

class EveApiStream(Script):
    def get_scheme(self):
        scheme = Scheme("EVE API")
        scheme.description = "Streams in data from the EVE Swagger API"
        scheme.use_external_validation = False

        endpoint_arg = Argument("endpoint")
        endpoint_arg.data_type = Argument.data_type_string
        endpoint_arg.description = "Endpoint on the API to be accessed: https://esi.evetech.net/latest{?}"
        endpoint_arg.required_on_create = True

        scheme.add_argument(endpoint_arg)

        return scheme

    def stream_events(self, inputs: InputDefinition, ew: EventWriter):
        for input_name, input_item in inputs.inputs.items():
            endpoint = input_item["endpoint"]
            data = get_api_data(endpoint)
            if data is None:
                return

            pages = data.headers.get('X-Pages')
            out = data.json()

            if isinstance(out, list):
                write_item_list(ew, input_name, out)
            else:
                write_item(ew, input_name, out)


            if pages is not None and int(pages) > 1:
                for page in range(2, int(pages)):
                    paged_endpoint = f'{endpoint}?page={page}'
                    data = get_api_data(paged_endpoint)
                    if data is None:
                        return
                    out = data.json()
                    write_item_list(ew, input_name, out)


def get_api_data(endpoint):
    res = requests.get(ESI_BASE_URL + endpoint)
    if res.status_code >= 300:
        logging.error(f'request to {endpoint} returned non-200 status: {res.status_code}')
        return None
    return res


def write_item_list(ew: EventWriter, input_name, items):
    if not isinstance(items, list):
        logging.error(f'Item received is not a list')
        return

    for item in items:
        write_item(ew, input_name, item)

def write_item(ew: EventWriter, input_name, item):
    event = Event()
    event.sourceType = "eve_api"
    event.stanza = input_name
    event.data = json.dumps(item)
    ew.write_event(event)
    

if __name__ == "__main__":
    sys.exit(EveApiStream().run(sys.argv))