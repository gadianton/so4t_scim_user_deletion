'''
This Python script is a labor of love and has no formal support from Stack Overflow. 
If you run into difficulties, reach out to the person who provided you with this script.
Or, open an issue here: https://github.com/jklick-so/so4t_scim_user_deletion/issues
'''

# Standard Python libraries
import argparse
import csv
import datetime
import logging
import json

# Local libraries
from so4t_scim import ScimClient


def main():

    args = get_args()
    client = ScimClient(args.token, args.url)

    # Get all users via SCIM API and write to a JSON file
    all_users = client.get_all_users()
    write_json(all_users, 'all_users')

    failed_deletions = []
    if args.deactivated and args.csv: # if both --deactivated and --csv flags are provided, print help message
        logging.info("Please provide only one argument for which users to delete.")
        logging.info("Use --deactivated to delete deactivated users.")
        logging.info("Use --csv to delete users from a CSV file.")
        logging.info("See README for more information.")
        return

    elif args.deactivated: # if --deactivated flag is provided, delete deactivated users
        users_to_delete = [user for user in all_users if not user["active"]]
        for user in users_to_delete:
            deletion_result = client.delete_user(user["id"])
            if deletion_result['status'] != 'success':
                failed_deletions.append(deletion_result)

    elif args.csv: # if a CSV file is provided, delete users from the CSV file
        csv_users_to_delete = get_users_from_csv(args.csv)
        for user in csv_users_to_delete:
            scim_user = scim_user_lookup(all_users, email=user)
            if scim_user is None: # if user_lookup returns None, skip this user
                deletion_result = {
                    'email': user,
                    'status': 'failed',
                    'message': 'User email address not found via SCIM API'
                }
                failed_deletions.append(deletion_result)
            else: # if user_lookup returns a user, attempt to delete the user
                deletion_result = client.delete_user(scim_user["id"])
                deletion_result['email'] = user
                if deletion_result['status'] != 'success':
                    failed_deletions.append(deletion_result)

    else: # if no arguments are provided, print help message
        logging.info("Please provide an argument for which users to delete.")
        logging.info("Use --deactivated to delete deactivated users.")
        logging.info("Use --csv to delete users from a CSV file.")
        logging.info("See README for more information.")
        return
    
    # get date and time of report generation to add to the filename
    # this ensures that previous reports are not overwritten when script is run multiple times
    report_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if len(failed_deletions) == 0:
        logging.info("All users deleted successfully.")
        failed_deletions = {
            'status': 'success',
            'message': 'All selected users were deleted successfully.'
        }
    else:
        logging.warning("Some users were not deleted successfully.")
        logging.warning("Please review 'failed_deletions.json' for any users that were not deleted successfully.")

    write_json(failed_deletions, f"failed_deletions_{report_date}") # write failed deletions to a JSON file


def get_args():

    parser = argparse.ArgumentParser(
        description="Delete users from Stack Overflow for Teams."
    )

    parser.add_argument(
        "--token",
        type=str,
        required=True,
        help="The SCIM token for your Stack Overflow for Teams site."
    )

    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="The base URL for your Stack Overflow for Teams site."
    )

    parser.add_argument(
        "--csv",
        type=str,
        help="A CSV file with a list of users to delete."
    )

    parser.add_argument(
        "--deactivated",
        action="store_true",
        help="Delete deactivated users."
    )

    args = parser.parse_args()

    return args


def get_users_from_csv(csv_file):

    users_to_delete = []

    with open(csv_file, 'r') as f:
        csv_reader = csv.reader(f)
        for line in csv_reader:
            users_to_delete.append(line[0])

    return users_to_delete


def scim_user_lookup(users, email):

    logging.debug("**********")
    logging.debug(f"Finding account ID for user with email {email}...")
    for user in users:
        try:
            if user["emails"][0]["value"].lower() == email.lower():
                logging.debug(f"Account ID is {user['id']}")
                return user
        except KeyError: # if SCIM user does not have an email address, skip this user
            continue

    return None


def write_json(data, file_name):

    file_path = file_name+'.json'

    with open(file_path, 'w') as f:
        f.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    main()