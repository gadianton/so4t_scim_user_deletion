'''
This Python script is a labor of love and has no formal support from Stack Overflow. 
If you run into difficulties, open an issue here: 
https://github.com/jklick-so/so4t_scim_user_deletion/issues
'''

# Open source libraries
import requests




class ScimClient:

    def __init__(self, token, url, proxy=None):
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

        print("Testing SCIM connection...")
        try:
            response = requests.get(self.scim_url, headers=self.headers, proxies=self.proxies,
                                    verify=ssl_verify)
        except requests.exceptions.SSLError:
            print(f"Received SSL error when connecting to {self.base_url}.")
            print("If you're sure the URL is correct (and trusted), you can proceed without SSL "
                  "verification.")
            proceed = input("Proceed without SSL verification? (y/n) ")
            if proceed.lower() == "y":
                # Suppress SSL warnings if user opts to proceed without SSL verification
                requests.packages.urllib3.disable_warnings(
                    requests.packages.urllib3.exceptions.InsecureRequestWarning)
                ssl_verify = False
                response = requests.get(self.scim_url, headers=self.headers, 
                                        verify=ssl_verify, proxies=self.proxies)
            else:
                print("Exiting...")
                raise SystemExit

        if response.status_code == 200:
            print(f"SCIM connection was successful.")
            return ssl_verify
        else:
            print(f"SCIM connection failed. Please check your token and URL.")
            print(f"Status code: {response.status_code}")
            print(f"Response from server: {response.text}")
            print("Exiting...")
            raise SystemExit


    def get_user(self, account_id):
        # Get a single user by account ID

        scim_url = f"{self.scim_url}/{account_id}"
        response = requests.get(scim_url, headers=self.headers)

        if response.status_code == 404:
            print(f"User with account ID {account_id} not found.")
            return None

        elif response.status_code != 200:
            print(f"API call failed with status code: {response.status_code}.")
            print(response.text)
            return None

        else:
            print(f"Retrieved user with account ID {account_id}")
            return response.json()
    

    def get_all_users(self):
        # Get all users via SCIM API

        params = {
            "count": 100,
            "startIndex": 1,
        }

        items = []
        while True: # Keep performing API calls until all items are received
            print(f"Getting 100 users from {self.scim_url} with startIndex of {params['startIndex']}")
            response = requests.get(self.scim_url, headers=self.headers, params=params, 
                                    proxies=self.proxies, verify=self.ssl_verify)
            if response.status_code != 200:
                print(f"API call failed with status code: {response.status_code}.")
                print(response.text)
                print ("Exiting...")
                print ("Please try running the script again. "
                       "If the problem persists, open a GitHub issue.")
                raise SystemExit

            items_data = response.json().get('Resources')
            items += items_data

            params['startIndex'] += params['count']
            if params['startIndex'] > response.json().get('totalResults'):
                break

        return items


    def update_user(self, account_id, active=None, role=None):
        # Update a user's active status or role via SCIM API
        # Role changes require an admin setting to allow SCIM to modify user roles
        # `role` can be one of the following: Registered, Moderator, Admin
        # if another role is passed, it will be ignored (and still report HTTP 200)
        # `active` can be True or False

        valid_roles = ["Registered", "Moderator", "Admin"]

        scim_url = f"{self.scim_url}/{account_id}"
        payload = {}
        if active is not None:
            payload['active'] = active
        if role is not None:
            if role in valid_roles:
                payload['userType'] = role
            else:
                print(f"Invalid role: {role}. Valid roles are: {valid_roles}")
                return

        response = requests.put(scim_url, headers=self.headers, json=payload, 
                                proxies=self.proxies, verify=self.ssl_verify)

        if response.status_code == 404:
            print(f"User with account ID {account_id} not found.")
        elif response.status_code != 200:
            print(f"API call failed with status code: {response.status_code}.")
            print(response.text)
        else:
            print(f"Updated user with account ID {account_id}")


    def delete_user(self, account_id, retries=0):
        # By default, deleting users via SCIM is disabled. To enable it, open a support ticket.
        # If SCIM deletion is not enabled, the API will return a 404 error, which is the same
        # response as if the user doesn't exist.
        # Deleting a user via SCIM requires the user's account ID (not user ID)
        
        scim_url = f"{self.scim_url}/{account_id}"

        print(f"Sending DELETE request to {scim_url}")
        response = requests.delete(scim_url, headers=self.headers, proxies=self.proxies, 
                                   verify=self.ssl_verify)

        if response.status_code == 400:
            # Most common 400 Error response:
                # {"ErrorMessage":"You cannot delete or destroy System Accounts."}
            
            print(f"Failed to delete user with account ID {account_id}")
            print(type(response.json().get('ErrorMessage')))
            print(response.json().get('ErrorMessage'))
            self.pause_script()

        elif response.status_code == 404:
            print(f"Delete request for user with account ID {account_id} returned 404.")
            print("This could mean that user deletion for SCIM is not enabled for your site "
                  "or that the user does not exist.")
            print("To enable user deletion for SCIM, open a support ticket with Stack Overflow.")
            self.pause_script()

        elif response.status_code == 500:
            # 500 Error responses:
                # {"ErrorMessage":"Moderators cannot be deleted - tried to delete <UserName>. 
                    # Adjust role to User."}
                # "SCIM user modification failed - unknown user"
            
            # As of 2024.02.29, a 500 can also be returned if the user is the creator of a 
            # community. This is a known issue that will be fixed in a future release.
                # The lengthy "ErrorMessage" will include the following text:
                    # The DELETE statement conflicted with the REFERENCE constraint 
                    # "FK_CommunityMemberships_CreationUser".
            
            if "Adjust role to User" in response.json().get('ErrorMessage'):
                print(f"User with account ID {account_id} cannot be deleted because they're "
                        "a moderator or admin.")
                print("Reducing their role to User...")
                self.update_user(account_id, role="Registered")
                if retries < 3:
                    print("Retrying delete...")
                    self.delete_user(account_id, retries+1)
                else:
                    print("Max retries reached. Aborting deletion.")

            elif "FK_CommunityMemberships_CreationUser" in response.json().get('ErrorMessage'):
                print(f"User with account ID {account_id} cannot be deleted because they are "
                        "the creator of a community.")
                print("Please contact Stack Overflow support for assistance.")

            else:
                print(f"Failed to delete user with account ID {account_id}")
                print(response.json().get('ErrorMessage'))
            
            self.pause_script()

        elif response.status_code != 204:
            print(f"API call failed with status code: {response.status_code}.")
            print(response.text)
            self.pause_script()

        else:
            print(f"Deleted user with account ID {account_id}")

    def pause_script(self):
        input("Press the Enter or Return key to continue...")
