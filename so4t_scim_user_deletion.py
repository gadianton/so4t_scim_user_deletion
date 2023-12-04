'''
This Python script is a labor of love and has no formal support from Stack Overflow. 
If you run into difficulties, reach out to the person who provided you with this script.
Or, open an issue here: https://github.com/jklick-so/so4t_scim_user_deletion/issues
'''

# Standard Python libraries
import argparse

# Local libraries
from so4t_scim import ScimClient


def main():

    args = get_args()
    client = ScimClient(args.token, args.url)

    # Get all users via API
    all_users = client.get_all_users()

    # Create, format, and validate list of users to delete
    if args.deactivated:
        users_to_delete = [user for user in all_users if not user["active"]]
    elif args.csv:
        csv_users_to_delete = get_users_from_csv(args.csv)
        users_to_delete = []
        for user in csv_users_to_delete:
            scim_user = scim_user_lookup(all_users, email=user)
            if scim_user: # if user_lookup returns None, skip this user
                users_to_delete.append(scim_user)
    else:
        print("Please provide an argument for which users to delete.")
        return

    # Delete users
    for user in users_to_delete:
        print("**********")
        print(f"Deleting user {user['id']} with email {user['emails'][0]['value']}")
        client.delete_user(user["id"])


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

    # parser.add_argument(
    #     "--json",
    #     type=str,
    #     help="A JSON file with a list of users to delete."
    # )

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
        for line in f:
            users_to_delete.append(line.strip())

    return users_to_delete


# def get_users_from_json(json_file):
    
#         with open(json_file, 'r') as f:
#             users_to_delete = json.load(f)
    
#         return users_to_delete


def scim_user_lookup(users, email):

    print("**********")
    print(f"Finding account ID for user with email {email}...")
    for user in users:
        try:
            if user["emails"][0]["value"] == email:
                print(f"Account ID is {user['id']}")
                return user
        except KeyError:
            # print(f"Found SCIM user with no email address:")
            # print(user)
            continue
    
    print(f"User with email {email} not found. Skipping deletion for this user.")
    return None


if __name__ == "__main__":
    main()