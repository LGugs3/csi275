"""Client code for Lab 9.

Author: Liam Gugliotta
Class: CSI-275-01
Assignment: Lab 9 - JSON Client/Server

Certification of Authenticity:
I certify that this is entirely my own work, except where I have given
fully-documented references to the work of others. I understand the definition
and consequences of plagiarism and acknowledge that the assessor of this
assignment may, for the purpose of assessing this assignment:
- Reproduce this assignment and provide a copy to another member of academic
- staff; and/or Communicate a copy of this assignment to a plagiarism checking
- service (which may then retain a copy of this assignment on its database for
- the purpose of future plagiarism checking)
"""


import socket
import json
import zlib


def build_list():
    """Collect input from the user and return it as a list.

    Only numeric input will be included; strings are rejected.
    """
    # Create a list to store our numbers
    unsorted_list = []

    # Create a variable for input
    user_input = ""
    inputted_sort_type: bool = False

    while user_input != "done":
        # Prompt the user for input
        user_input = input("Please enter a number, or 'done' to stop.")

        if not inputted_sort_type and user_input.isalpha():
            unsorted_list.append(user_input)
            inputted_sort_type = True
            continue
        else:
            inputted_sort_type = True

        # Validate our input, and add it to out list
        # if it's a number
        try:
            # Were we given an integer?
            unsorted_list.append(int(user_input))
        except ValueError:
            try:
                # Were we given a floating-point number?
                unsorted_list.append(float(user_input))
            except ValueError:
                # Non-numeric input - if it's not "done",
                # reject it and move on
                if (user_input != "done"):
                    print("ERROR: Non-numeric input provided.")
                continue

    # Once we get here, we're done - return the list
    return unsorted_list


def sort_list(unsorted_list):
    """Put your docstring here."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = "localhost", 7778
    sock.connect(server_addr)

    json_list = json.dumps(unsorted_list)
    encoded_json = json_list.encode("utf-8")
    print(f"uncompressed length of list sent: {len(encoded_json)}")
    compressed_json = zlib.compress(encoded_json)

    print(f"compressed length of list sent: {len(compressed_json)}")
    sock.sendall(compressed_json)

    # -------------------------------------------------------------------

    data_recv = sock.recv(4096)
    print(f"msg len recieved before decompress: {len(data_recv)}")
    decompress_json = zlib.decompress(data_recv)

    readable_json = decompress_json.decode("utf-8")
    print(f"msg len recieved after decompress: {len(readable_json)}")
    json_data = json.loads(readable_json)
    sock.close()

    print(json_data)


def main():
    """Call the build_list and sort_list functions, and print the result."""
    number_list = build_list()
    sort_list(number_list)


if __name__ == "__main__":
    main()
