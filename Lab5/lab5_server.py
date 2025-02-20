"""Server code for Lab 5.

Author: Liam Gugliotta
Class: CSI-275-01
Assignment: Lab 5 -- Sorting Server
Due Date: February 20, 2025, 11:59 PM

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

HOST = "localhost"
PORT = 20000
MAX_BYTES = 4096


class SortServer:
    """Don't forget your docstring."""

    server: socket
    server_addr: tuple[str, int]

    def __init__(self, host, port):
        """Init SortServer."""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_addr = host, port
        self.server.bind(self.server_addr)
        print(f"Server binded to {self.server_addr}")

    def __del__(self):
        """Deconstructor for SortServer."""
        print("Closing server socket")
        self.server.close()

    def run_server(self):
        """Start Server."""
        self.server.listen(20)

        while True:
            print("Waiting for connection")
            connection, recv_addr = self.server.accept()
            print(f"Server found connection from: {recv_addr}")

            while True:
                msg_arr: list = []
                msg_recv = connection.recv(MAX_BYTES)
                byte_length = len(msg_recv)
                if not msg_recv:
                    break
                msg_recv = msg_recv.decode("ascii")
                msg_arr.extend(msg_recv.split(' '))

                if byte_length == MAX_BYTES:
                    continue

                response: list[int | float | str] | None = \
                    self.__parse_packet(msg_arr)

                self.__respond_client_error(connection) if response is None \
                    else self.__respond_client_success(connection, response)

            print("Disconnected")
            connection.close()

    def __parse_packet(self, unparsed_list: list) -> list | None:
        """
        Parse recieved list into response.

        Returns list if packet is valid, otherwise returns None
        """
        if len(unparsed_list) == 1:
            return None
        parsed_list: list[int, float] = []
        sort_method: str = 'a'
        possible_sorts: list[str] = ['a', 'd', 's']
        for idx, ele in enumerate(unparsed_list):
            if idx == 0:
                if ele != "LIST":
                    return None
                continue
            if idx == len(unparsed_list) - 1:
                if '|' in ele:
                    result = ele.split('|')
                    if result[1] not in possible_sorts:
                        return None
                    sort_method = result[1]
                    ele = result[0]

            char: int | float | None = self.__check_int_float(ele)
            if char is None:
                return None
            parsed_list.append(char)

        if sort_method == 'a':
            parsed_list.sort()
        elif sort_method == 'd':
            parsed_list.sort(reverse=True)
        elif sort_method == 's':
            parsed_list = sorted([str(ele) for ele in parsed_list])

        return parsed_list

    def __respond_client_success(self, connection, response: str):
        msg_send = "SORTED "
        msg_send += " ".join(map(str, response))

        connection.sendall(msg_send.encode("ascii"))

    def __respond_client_error(self, connection) -> None:
        connection.sendall("ERROR".encode("ascii"))

    def __check_int_float(self, char: str) -> int | float | None:
        """Check if character is an int or float."""
        try:
            return int(char)
        except ValueError:
            try:
                return float(char)
            except ValueError:
                return None


if __name__ == "__main__":
    server = SortServer(HOST, PORT)
    server.run_server()
