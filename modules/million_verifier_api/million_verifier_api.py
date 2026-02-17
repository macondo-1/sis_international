import os 
import requests
import logging 
import json
from pathlib import Path


class APIError(Exception):
    pass

class MillionVerifier:
    def __init__(self):
        self.api_key = os.getenv("MV_API_KEY")
        self.base_url = "https://bulkapi.millionverifier.com/bulkapi/v2"

        self.headers = {'Authorization': 'Bearer {}'.format(self.api_key),
                        'Content-Type': 'application/json'}

    def make_request(self, endpoint: str, method:str = 'get', json_var:dict = None, params_value:dict = None, files:tuple = None) -> dict:
        try:
            functions = {'get' : requests.get,
                         'post' : requests.post,
                         'patch': requests.patch,
                         'delete': requests.delete}
            
            func = functions.get(method)
            if method == 'post':
                response = func(f"{self.base_url}/{endpoint}", files=files)
            else:
                response = func(f"{self.base_url}/{endpoint}", headers=self.headers, json=json_var, params=params_value, files=files) # 
            
            # Check for HTTP errors (non-2xx status codes)
            # response.raise_for_status() # this line does not let me see the error message on the api response

            # Error Handling
            # CHECK: this error codes are from another API
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

    def api_credits(self) -> dict:
        """
        Get available credits
        
        :param self: 
        """
        
        endpoint = 'credits?api={}'.format(self.api_key)

        try:
            data = self.make_request(endpoint)
            return data
        except APIError as err:
            print(f"API error: {err}")

    def verify_single_email_address(self, email: str, timeout:str = '20') -> dict:
        """
        Verify an email address in real time as your subscriber signs up to your newsletter.
        Special characters in the email address should be encoded.
        
        :param self: Description
        :param email: Description
        :type email: str
        :param timeout: Description
        :type timeout: str
        :return: Description
        :rtype: dict
        """

        endpoint = "?api={0}&email={1}&timeout=10".format(self.api_key, email)
        try:
            data = self.make_request(endpoint)
            return data
        except APIError as err:
            print(f"API error: {err}")

    def file_upload(self, file_path: str, file_name: str) -> dict:

        """
        example output
        {'file_id': '30258177', 'file_name': 'test', 'status': 'unknown', 'unique_emails': 0, 'updated_at': '2026-02-17 05:38:51', 'createdate': '2026-02-17 05:38:51', 'percent': 0, 'total_rows': 0, 'verified': 0, 'unverified': 0, 'ok': 0, 'catch_all': 0, 'disposable': 0, 'invalid': 0, 'unknown': 0, 'reverify': 0, 'credit': 0, 'estimated_time_sec': 0, 'error': ''}
        """
        
        files=[
        ('file_contents',(file_name,open(file_path,'rb'),'text/plain'))
        ]
        endpoint = "upload?key={}".format(self.api_key)
        try:
            data = self.make_request(endpoint, method='post', files=files)
            return data
        except APIError as err:
            print(f"API error: {err}")

    def file_info(self, file_id: str) -> dict:
        """
        Retrieves a file's information
        
        :param file_id: id of the file on Million Verifier
        :type file_id: str
        :return: Information as a dictionary
        :rtype: dict
        """

        endpoint = "fileinfo?key={0}&file_id={1}".format(self.api_key, file_id)
        try:
            data = self.make_request(endpoint)
            return data
        except APIError as err:
            print(f"API error: {err}")

    # CHECK: there's more options as params
    def files_list(self,
                   offset:str = 0,
                   status:str = 'finished',
                   limit:str = '50',
                   updated_at_from:str = None,
                   createdate_from:str = None,
                   percent_from:str = None,
                   percent_to:str = None,
                   has_error:str = 'False') -> dict:
        """
        Docstring for files_list
        
        :param self: Description
        :param limit: Description
        :param status: options: ["in_progress" "error" "finished" "canceled" "paused" "in_queue_to_start"]
        :param updated_at_from: string <yyyy-MM-dd HH:mm:ss>
        :param updated_at_to: string <yyyy-MM-dd HH:mm:ss>
        :param createdate_from: string <yyyy-MM-dd HH:mm:ss>
        :param has_error: options: ["1" "t" "T" "TRUE" "True" "true" "0" "f" "F" "FALSE" "False" "false"]
        :type limit: str
        :return: Description
        :rtype: dict
        """
        
        endpoint = (
            "filelist?"
            "key={api_key}&"
            "offset={offset}&"
            "limit={limit}&"
            "status={status}&"
            "updated_at_from={updated_at_from}&"
            "percent_from={percent_from}&"
            "percent_to={percent_to}&"
            "has_error={has_error}"
        ).format(
            api_key=self.api_key,
            offset=offset,
            limit=limit,
            status=status,
            updated_at_from=updated_at_from,
            percent_from=percent_from,
            percent_to=percent_to,
            has_error=has_error,
        )
        try:
            data = self.make_request(endpoint)
            return data
        except APIError as err:
            print(f"API error: {err}")

    def save_csv_file(self, data:str, file_name: str) -> None:
        try:
            with open(file_name, 'w') as file:
                file.writelines(data)
        except Exception as e:
            print('Failed saving file. Error: ', e)


    # CHECK: doesn't follow the patter using make_request method, the issue is that make_request parses the response as json, but this yields a string instead
    def download_report(self, file_id:str) -> str:
        url = "https://bulkapi.millionverifier.com/bulkapi/v2/download?key={0}&file_id={1}&filter=all".format(self.api_key, file_id)
        try:
            response = requests.get(url)
            return response.text
        except APIError as err:
            print(f"API error: {err}")