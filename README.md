# SCIM-based User Deletion for Stack Overflow for Teams
A SCIM API script for Stack Overflow for Teams that can delete all deactivated users or a list of specific users.


## Requirements
* Stack Overflow Enterprise
* Python 3.8 or higher ([download](https://www.python.org/downloads/))
* Operating system: Linux, MacOS, or Windows

## Setup

[Download](https://github.com/jklick-so/so4t_scim_user_deletion/archive/refs/heads/main.zip) and unpack the contents of this repository

**Installing Dependencies**

* Open a terminal window (or, for Windows, a command prompt)
* Navigate to the directory where you unpacked the files
* Install the dependencies: `python3 -m pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org`

> NOTE: Depending on your installation of Python, you may need to use `python` or `py` instead of `python3` in the command above. If `python3` is not a recognized command, you can check which command to use by running `python --version` or `py --version` in your terminal and seeing which responds with the installed Python version.

**Enabling and Authenticating SCIM**

To use the SCIM API for deleting users:

* First, enable SCIM in the admin settings ([documentation](https://support.stackenterprise.co/support/solutions/articles/22000236123-system-for-cross-domain-identity-management-scim-2-0-support)). If this has not been enabled before, you'll need to contact whoever manages your identity provider configuration (aka SSO/SAML) to have them configure/provide a SCIM token.
* If SCIM is already enabled and configured, you can obtain the SCIM token from the admin settings, by selecting "Show Password" and copying the token to your clipboard.
* Lastly, you'll need to contact Stack Overflow support (support@stackoveflow.com) to help you enable SCIM-based user deletion. Before enabling this functionality, the support team will want to confirm you understand that once a user is deleted, it cannot be restored, and the next time a deleted user attempts to login, they'll be prompted to create a new account.

## Usage

**Deleting specific users**

If you'd like to delete specific users, create a file named `users.csv` in the same directory as the script. Each line of the file should contain the email address of a user you'd like to delete. You can find a template [here](https://github.com/jklick-so/so4t_scim_user_deletion/blob/main/Templates/users.csv).

In a terminal window, navigate to the directory where you unpacked the script. Run the script with the `--csv` flag, replacing the URL, token, and CSV file name with your own:
`python3 so4t_scim_user_deletion.py --url "https://SUBDOMAIN.stackenterprise.co" --token "YOUR_TOKEN" --csv "CSV_FILE_NAME.csv"`

**Deleting all deactivated users**

If you'd like to delete all deactivated users, run the script with the `--deactivated` flag (instead of the `--csv` flag). In a terminal window, navigate to the directory where you unpacked the script and use the following command, replacing the URL and token with your own:
* For Enterprise: `python3 so4t_scim_user_deletion.py --url "https://SUBDOMAIN.stackenterprise.co" --token "YOUR_TOKEN" --deactivated`


## Support, security, and legal
Disclaimer: the creator of this project works at Stack Overflow, but it is a labor of love that comes with no formal support from Stack Overflow. 

If you run into issues using the script, please [open an issue](https://github.com/jklick-so/so4t_scim_user_deletion/issues). You are also welcome to edit the script to suit your needs, steal the code, or do whatever you want with it. It is provided as-is, with no warranty or guarantee of any kind. If the creator wasn't so lazy, there would likely be an MIT license file included.
