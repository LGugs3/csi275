"""
User creates a list of integers + floats which is then sorted and printed.

Author: Liam Gugliotta
Class: CSI-275-01
Assignment: Lab 1 -- Sorting With Python

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


class InvalidList(Exception):
    """Custom Exception."""

    pass


class CustomList:
    """Encapsulate list creation and sorting method."""

    def __init__(self):
        """Init fxn."""
        self.unsorted_list: list[int | float] = []
        self.server_addr: tuple[str, int] = "159.203.166.188", 7778

    def build_list(self) -> None:
        """Build unsorted list of ints and floats."""
        exit_keyword = "exit"
        val_to_append = ""

        while val_to_append != exit_keyword:
            val_to_append = input(f"Enter Number({exit_keyword} to stop): ")
            if val_to_append == exit_keyword:
                break

            if (val_to_append.isdigit()):
                self.unsorted_list.append(int(val_to_append))
            else:
                try:
                    val_to_append = float(val_to_append)
                except ValueError:
                    print(f"{val_to_append} is not an integer or float")
                except Exception as e:
                    print(type(e).__name__, ':', e, "\n\nSomething went \
                        critically wrong; How did you do this.")
                else:
                    self.unsorted_list.append(float(val_to_append))

    def sort_list(self) -> str:
        """Send unsorted list to server."""
        buffer_size = 4096
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting to server...")
        server.connect(self.server_addr)
        print("Connected to server")

        data = "LIST "

        for ele in self.unsorted_list:
            data += str(ele) + ' '

        server.sendall(data.encode("ascii"))
        print("Unsorted List sent to server")

        sorted_list: bytearray = bytearray()
        response: bytes = bytes()

        print("Recieving data", end="")
        while True:
            print(".", end="")
            response = server.recv(buffer_size)
            if not response:
                # Client disconnected
                break
            sorted_list += response
            if len(response) < buffer_size:
                # Response size is smaller than max recieve size(no more data)
                break
        server.close()
        print()
        decoded_list = sorted_list.decode("ascii")
        if "SORTED" not in decoded_list:
            raise InvalidList("List submitted to server not formatted \
                              correctly")

        return decoded_list
