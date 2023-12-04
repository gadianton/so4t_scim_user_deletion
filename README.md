# Stack Overflow for Teams SCIM-based User Deletion (soft_scim_user_deletion.py)
A SCIM API script for Stack Overflow for Teams that can delete all deactivated users or a list of specific users.


## Requirements
* A Stack Overflow for Teams instance with SCIM enabled (Basic, Business, or Enterprise)
* Python 3.8 or higher ([download](https://www.python.org/downloads/))
* Operating system: Linux, MacOS, or Windows

## Setup

[Download](https://github.com/jklick-so/soft_scim_user_deletion/archive/refs/heads/main.zip) and unpack the contents of this repository

**Installing Dependencies**

* Open a terminal window (or, for Windows, a command prompt)
* Navigate to the directory where you unpacked the files
* Install the dependencies: `pip3 install -r requirements.txt`

**Enabling and Authenticating SCIM**

To use the SCIM API, you'll first need to enable SCIM in the admin settings. Second, you'll need to generate a SCIM token to authenticate the API calls.
- [SCIM Documentation for Basic and Business](https://stackoverflowteams.help/en/articles/4538506-automated-user-provisioning-scim-overview)
- [SCIM Documentation for Enterprise](https://support.stackenterprise.co/a/solutions/articles/22000236123)

> NOTE: The SCIM token is different from the API token used for Stack Overflow for Teams API. 

## Usage

**Deleting specific users**

If you'd like to delete specific users, create a file named `users.csv` in the same directory as the script. Each line of the file should contain the email address of a user you'd like to delete. You can find a template [here](https://github.com/jklick-so/soft_scim_user_deletion/blob/main/Templates/users.csv).

In a terminal window, navigate to the directory where you unpacked the script. Run the script with the `--csv` flag, replacing the URL, token, and CSV file name with your own:
* For Basic and Business: `python3 soft_scim_user_deletion.py --url "https://stackoverflowteams.com/c/TEAM-NAME" --token "YOUR_TOKEN" --csv users.csv`
* For Enterprise: `python3 soft_scim_user_deletion.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --csv users.csv`

**Deleting all deactivated users**

If you'd like to delete all deactivated users, run the script with the `--deactivated` flag. In a terminal window, navigate to the directory where you unpacked the script and use the following command, replacing the URL and token with your own:
* For Basic and Business: `python3 soft_scim_user_deletion.py --url "https://stackoverflowteams.com/c/TEAM-NAME" --token "YOUR_TOKEN" --deactivated`
* For Enterprise: `python3 soft_scim_user_deletion.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --deactivated`


## Support, security, and legal
Disclaimer: the creator of this project works at Stack Overflow, but it is a labor of love that comes with no formal support from Stack Overflow. 

If you run into issues using the script, please [open an issue](https://github.com/jklick-so/soft_scim_user_deletion/issues). You are also welcome to edit the script to suit your needs, steal the code, or do whatever you want with it. It is provided as-is, with no warranty or guarantee of any kind. If the creator wasn't so lazy, there would likely be an MIT license file included.

All data is handled locally on the device from which the script is run. The script does not transmit data to other parties, such as Stack Overflow. All of the API calls performed are read only, so there is no risk of editing or adding content on your Stack Overflow for Teams instance.
