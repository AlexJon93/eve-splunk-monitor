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
            out = data.json()

            if isinstance(out, list):
                for item in out:
                    event = Event()
                    event.sourceType = "eve_api"
                    event.stanza = input_name
                    event.data = json.dumps(item)
                    ew.write_event(event)
            else:
                event = Event()
                event.sourceType = "eve_api"
                event.stanza = input_name
                event.data = json.dumps(out)
                ew.write_event(event)

def get_api_data(endpoint):
    response = requests.get(ESI_BASE_URL + endpoint)
    return response
    

if __name__ == "__main__":
    sys.exit(EveApiStream().run(sys.argv))