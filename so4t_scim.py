'''
This Python script is a labor of love and has no formal support from Stack Overflow. 
If you run into difficulties, open an issue here: 
https://github.com/jklick-so/so4t_scim_user_deletion/issues
'''

# Standard Python libraries
import logging

# Open source libraries
import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential, RetryError

# Set up logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class ScimClient:
    VALID_ROLES = ["Registered", "Moderator", "Admin"]
    MAX_RETRIES = 3

    def __init__(self, token, url, proxy=None):
        self.session = requests.Session()
        self.base_url = url
        self.token = token
        self.headers = {
            'Authorization': f"Bearer {self.token}"
        }
        self.proxies = {'https': proxy} if proxy else {'https': None}
        if "stackoverflowteams.com" in self.base_url: # For Basic and Business tiers
            self.soe = False
            self.scim_url = f"{self.base_url}/auth/scim/v2/users"
        else: # For Enterprise tier
            self.soe = True
            self.scim_url = f"{self.base_url}/api/scim/v2/users"

        self.ssl_verify = self.test_connection()

    
    def test_connection(self):
        ssl_verify = True

        logging.info("Testing SCIM connection...")
        try:
            response = self.session.get(self.scim_url, headers=self.headers, proxies=self.proxies,
                                    verify=ssl_verify)
        except requests.exceptions.SSLError:
            logging.warning(f"Received SSL error when connecting to {self.base_url}.")
            logging.warning("If you're sure the URL is correct (and trusted), you can proceed without SSL "
                          "verification.")
            proceed = input("Proceed without SSL verification? (y/n) ")
            if proceed.lower() == "y":
                requests.packages.urllib3.disable_warnings(
                    requests.packages.urllib3.exceptions.InsecureRequestWarning)
                ssl_verify = False
                response = self.session.get(self.scim_url, headers=self.headers, 
                                        verify=ssl_verify, proxies=self.proxies)
            else:
                logging.info("Exiting...")
                raise SystemExit

        if response.status_code == 200:
            logging.info(f"SCIM connection was successful.")
            return ssl_verify
        else:
            logging.error(f"SCIM connection failed. Please check your token and URL.")
            logging.error(f"Status code: {response.status_code}")
            logging.error(f"Response from server: {response.text}")
            logging.error("Exiting...")
            raise SystemExit


    def get_user(self, account_id):
        scim_user_url = f"{self.scim_url}/{account_id}"
        response = self.session.get(scim_user_url, headers=self.headers)

        if response.status_code == 404:
            logging.info(f"User with account ID {account_id} not found.")
            return None

        elif response.status_code != 200:
            logging.error(f"API call failed with status code: {response.status_code}.")
            logging.error(response.text)
            return None

        else:
            logging.info(f"Retrieved user with account ID {account_id}")
            return response.json()
    

    def get_all_users(self):
        params = {
            "count": 100,
            "startIndex": 1,
        }

        items = []
        while True:
            logging.info(f"Getting 100 users from {self.scim_url} with startIndex of {params['startIndex']}")
            response = self.session.get(self.scim_url, headers=self.headers, params=params, 
                                proxies=self.proxies, verify=self.ssl_verify)
            if response.status_code != 200:
                logging.error(f"API call failed with status code: {response.status_code}.")
                logging.error(response.text)
                logging.error ("Exiting...")
                logging.error ("Please try running the script again. "
                       "If the problem persists, open a GitHub issue.")
                raise SystemExit

            items_data = response.json().get('Resources')
            items += items_data

            params['startIndex'] += params['count']
            if params['startIndex'] > response.json().get('totalResults'):
                break

        return items


    def update_user(self, account_id, active=True, role=None):
        # If no value is set for `active`, the user account will be deactivated

        scim_user_url = f"{self.scim_url}/{account_id}"
        payload = {}

        payload['active'] = active
        if role is not None:
            if role in self.VALID_ROLES:
                payload['userType'] = role
            else:
                logging.warning(f"Invalid role: {role}. Valid roles are: {self.VALID_ROLES}")
                return

        response = self.session.put(scim_user_url, headers=self.headers, json=payload, 
                                proxies=self.proxies, verify=self.ssl_verify)

        if response.status_code == 404:
            logging.warning(f"User with account ID {account_id} not found.")

        elif response.status_code != 200:
            logging.error(f"API call failed with status code: {response.status_code}.")
            logging.error(response.text)

        elif role is not None:
            response_json = response.json()
            try:
                 user_role = response_json['userType']
            except KeyError: # If user is not a moderator/admin, the 'userType' key will not exist
                user_role = "Registered"

            if user_role != role:
                logging.warning(f"Failed to update user with account ID {account_id} to role: "
                                f"{role}")
                logging.warning("Please check that SCIM settings in the Stack Overflow admin "
                              "panel to make sure the ability to change user pemissions is enabled "
                              "(i.e check the boxes).")
            else:
                logging.info(f"Updated user with account ID {account_id} to role: {role}")


    def delete_user(self, account_id):

        scim_user_url = f"{self.scim_url}/{account_id}"
        deletion_result = {
            'account_id': account_id,
            'account_url': f'{self.base_url}/accounts/{account_id}',
            'status': 'success',
            'message': 'User deleted successfully.'
        }

        logging.info(f"Sending DELETE request to {scim_user_url}")
        response = self.session.delete(scim_user_url, headers=self.headers, proxies=self.proxies, 
                                   verify=self.ssl_verify)

        if response.status_code == 400:
            logging.error(f"Failed to delete user with account ID {account_id}")
            logging.error(type(response.json().get('ErrorMessage')))
            logging.error(response.json().get('ErrorMessage'))
            deletion_result['status'] = 'error'
            deletion_result['message'] = response.json().get('ErrorMessage')
            return deletion_result

        elif response.status_code == 404:
            logging.error(f"Delete request for user with account ID {account_id} returned 404.")
            logging.error("This could mean that user deletion for SCIM is not enabled for your site "
                          "or that the user does not exist.")
            logging.error("To enable user deletion for SCIM, open a support ticket with Stack Overflow.")
            deletion_result['status'] = 'error'
            deletion_result['message'] = "User not found."
            return deletion_result

        elif response.status_code == 500:
            error_message = response.json().get('ErrorMessage')

            if "Adjust role to User" in error_message:
                logging.warning(f"User with account ID {account_id} cannot be deleted because they're "
                                "a moderator or admin.")
                
                # logging.warning("Attempting to reduce their role to User...")
                # self.update_user(account_id, role="Registered")
                # logging.warning("Retrying delete...")
                # self.delete_user(account_id)
                

                @retry(retry=retry_if_exception_type(requests.exceptions.RequestException), 
                   stop=stop_after_attempt(self.MAX_RETRIES), 
                   wait=wait_exponential(multiplier=1, min=1, max=10))
                def delete_user_retry():
                    logging.warning("Attempting to reduce their role to Registered...")
                    self.update_user(account_id, role="Registered")
                    logging.warning("Retrying delete...")
                    self.delete_user(account_id)

                try:
                    delete_user_retry()
                except RetryError:
                    logging.error("Max retries reached. Aborting deletion.")
                    deletion_result['status'] = 'error'
                    deletion_result['message'] = f"Attempted to delete {self.MAX_RETRIES} times. " \
                                                    "Max retries reached. Deletion aborted."
                
                return deletion_result
            
            elif "FK_CommunityMemberships_CreationUser" in error_message:
                logging.warning(f"User with account ID {account_id} cannot be deleted because they are "
                                "the creator of a community.")
                logging.warning("Please contact Stack Overflow support for assistance.")
                deletion_result['status'] = 'error'
                deletion_result['message'] = "User cannot be deleted because they are the creator " \
                                                "of a community. Please contact support."
                return deletion_result

            else:
                logging.error(f"Failed to delete user with account ID {account_id}")
                logging.error(error_message)
                deletion_result['status'] = 'error'
                deletion_result['message'] = "Failed to delete user. Error message: " \
                                                f"{error_message}"
                return deletion_result

        elif response.status_code != 204: # any unexpected status code or scenario
            logging.error(f"API call failed with status code: {response.status_code}.")
            logging.error(response.text)
            deletion_result['status'] = 'error'
            deletion_result['message'] = response.text
            return deletion_result

        else:
            logging.info(f"Deleted user with account ID {account_id}")
            return deletion_result
