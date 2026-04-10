import requests
import logging
import json
from config import SS_API_KEY

class APIError(Exception):
    pass

class SuperSend:
    def __init__(self):
        self.api_key = SS_API_KEY
        self.base_url = 'https://api.supersend.io/v2'
        self.headers = {'Authorization': 'Bearer {}'.format(self.api_key),
                        'Content-Type': 'application/json'}
        self.team_id = '1523d91c-eb2c-400a-b97d-37ca8247a0e6'

    def make_request(self, endpoint: str, method:str = 'get', json_var:dict = None, params_value:dict = None) -> dict:
        try:
            functions = {'get' : requests.get,
                         'post' : requests.post,
                         'patch': requests.patch,
                         'delete': requests.delete}
            
            func = functions.get(method)
            response = func(f"{self.base_url}/{endpoint}", headers=self.headers, json=json_var, params=params_value)
            
            # Check for HTTP errors (non-2xx status codes)
            # response.raise_for_status() # this line does not let me see the error message on the api response

            # Error Handling
            error_codes = [400, 401, 403, 404, 409, 422, 429, 500, 503]
            if response.status_code in error_codes:
                raise APIError(f"API returned error code {response.status_code}: {response.json()['error']['message']}")
            
            data = response.json()
            return data

        except requests.exceptions.HTTPError as http_err:
            # Handle HTTP-specific errors (e.g., 404, 500)
            logging.error(f"HTTP error occurred: {http_err}")
            raise APIError(f"HTTP error occurred: {http_err}")

        except requests.exceptions.RequestException as req_err:
            # Handle non-HTTP specific issues (e.g., connection errors)
            logging.error(f"Request error occurred: {req_err}")
            raise APIError(f"Request error occurred: {req_err}")

        except APIError as api_err:
            # Handle custom API error
            logging.error(f"API-specific error occurred: {api_err}")
            raise api_err

        except Exception as err:
            # Catch other unexpected errors
            logging.error(f"An unexpected error occurred: {err}")
            raise Exception(f"An unexpected error occurred: {err}")

    # CONTACTS ENDPOINT
    def list_contacts_by_team(self, team_id: str = None, params_value:dict = None) -> dict:
        if not team_id:
            team_id = self.team_id
        endpoint = "contacts?TeamId={}".format(team_id)
        try:
            data = self.make_request(endpoint, params_value=params_value)
            return data
        except APIError as err:
            print(f"API error: {err}")

    def get_contact(self, contact_id: str) -> dict:
        endpoint = "contacts/{}".format(contact_id)
        try:
            data = self.make_request(endpoint)
            return data
        except APIError as err:
            print(f"API error: {err}")

    def update_contact(self, contact_id: str, payload: dict) -> dict:
        
        endpoint = "contacts/{}".format(contact_id)
        try:
            data = self.make_request(endpoint, method='patch', json_var=payload)
            return data
        except APIError as err:
            print(f"API error: {err}")

    # check: need to mark bad email as is_active = 0
    def bulk_create_contacts(self, contacts: list[dict], campaign_id:str, team_id: str = "1523d91c-eb2c-400a-b97d-37ca8247a0e6") -> dict:
        """
        Sends a list of dictionaries of contacts to create
        contacts on SuperSend.io

        :param contacts: Example: \n
            contacts = {
            "contacts": [
                {
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "company_name": "Acme Corp"
                }
            ],
            "TeamId": "{team_id}",
            "CampaignId": "{campaign_id}"
            }
        :type contacts: list[dict]
        :return: API call response
        :rtype: dict
        """

        # CHECK: Need to add all
        valid_payload_keys = ["email","first_name","last_name","company_name"]
        sent = 0
        index = 0
        counter = 1
        while not sent:

            if index:
                contacts.pop(int(index))

            payload = {
                "contacts": contacts,
                "TeamId": "{}".format(team_id),
                "CampaignId": "{}".format(campaign_id),
                "validate_emails": "true"
                }

            endpoint = 'contacts/bulk'

            try:
                data = self.make_request(endpoint=endpoint, json_var=payload, method='post')
                return data
            except APIError as err:
                logging.warning(f"API error: {err}")
                err = str(err)
                index = err.split('contacts[')[1]
                index = index.split(']')[0]
                logging.warning(f"Failed index: {index}")
                logging.info('trying again... loop {}'.format(counter))
                counter += 1




    def delete_contact_by_id(self, contact_id: str) -> dict:
        endpoint = 'contacts/{}'.format(contact_id)

        try:
            data = self.make_request(endpoint=endpoint, method='delete')
            return data
        except APIError as err:
            print(f"API error: {err}")

    # SENDERS ENDPOINT
    # CHECK:  theres more params to pass, add them in the future
    def list_senders(self, limit:int = 100, offset:int = 0) -> list:
        """
        List all senders on SuperSend.io
        
        :param limit: max 100
        :type limit: int
        :param offset: offset to manage pagination
        :type offset: int
        :return: a list of dictionaries with each sender's information
        :rtype: list
        """
        try:
            endpoint = 'senders?TeamId={0}&limit={1}&offset={2}'.format(self.team_id, limit, offset)
            has_more = True
            data_final = []
            loop = 1
            while has_more:
                print('Entering loop {}...'.format(loop))
                data = self.make_request(endpoint)
                data_final.extend(data['data'])
                has_more = data['pagination']['has_more']
                offset += limit
                endpoint = 'senders?TeamId={0}&limit={1}&offset={2}'.format(self.team_id, limit, offset)
                print('loop {} finshed!\n'.format(loop))
                loop += 1
            return data_final
        except APIError as err:
            print(f"API error: {err}")

    def update_sender(self, sender_id:str) -> dict:
        endpoint = 'senders/{}'.format(sender_id)
        # payload = {
        #     "send_as": "Updated Name <sales@example.com>",
        #     "reply_to": "support@example.com",
        #     "signature": "<p>New signature</p>",
        #     "forward_to": "admin@example.com",
        #     "disabled": false,
        #     "warm": true,
        #     "max_per_day": 75,
        #     "global_max_per_day": 150,
        #     "max_warm_per_day": 30,
        #     "warm_email_ramp": 45,
        #     "mail_warm_minimum": 10,
        #     "SenderProfileId": "profile-uuid"
        # }
        payload = {'global_max_per_day':42}
        try:
            data = self.make_request(endpoint=endpoint, method='patch', json_var=payload)
            return data
        except APIError as err:
            print(f"API error: {err}")

# if __name__ == "__main__":

#     api_client = SuperSend()
#     data = api_client.list_senders()
#     print(data)

#     api_client = APIClient("https://api.supersend.io/v2")
#     try:

#         data = api_client.list_senders()
#         for sender in data:
#             email = sender['email']
#             print('Updating {}...'.format(email))
#             sender_id = sender['id']
#             data_1 = api_client.update_sender(sender_id)
#             print('success: ', data_1['success'])
#             print('')

#     except APIError as err:
#         print(f"API error: {err}")

