"""Server code for Lab 6.

Author: Liam Gugliotta
Class: CSI-275-01
Assignment: Lab 6 -- Framing with Length Fields
Due Date: March 3, 2025, 11:59 PM

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
PORT = 45000


class Connection:
    """Individual TCP connection with client."""

    connection: socket
    addr: tuple[str, int]
    msg_length: int
    completed_interactions: bool

    def __init__(self, connection: socket, addr: tuple[str, int]):
        """Construct Connection class."""
        self.connection = connection
        self.addr = addr
        self.msg_length = -1
        self.completed_interactions = False

    def __del__(self):
        """Deconstruct Connection class."""
        print(f"Closing connection from {self.addr}")
        self.connection.close()

    def __eq__(self, value):
        """Check if self and value are the same object."""
        if isinstance(value, Connection):
            return self.addr == value.addr
        return False

    def __bool__(self):
        """Check if interactions have been completed."""
        return self.completed_interactions

    def __set_packet_length(self) -> None:
        self.msg_length = int.from_bytes(self.connection.recv(4), "big")

    def __recv_all(self) -> bytes | None:
        data = b""
        while len(data) < self.msg_length:
            more = self.connection.recv(self.msg_length - len(data))
            if not more:
                self.completed_interactions = True
                return None
            data += more
        return data

    def __respond_success(self) -> None:
        success_msg = f"I received {self.msg_length} bytes."
        self.connection.sendall(len(success_msg).to_bytes(4, byteorder="big") +
                                success_msg.encode("ascii"))

    def __respond_fail(self) -> None:
        fail_msg = "Length Error"
        self.connection.sendall(len(fail_msg).to_bytes(4, byteorder="big") +
                                fail_msg.encode("ascii"))

    def calc_length(self) -> None:
        """Recieve and parse packets from client."""
        self.__set_packet_length()
        response = self.__recv_all()
        if response is None:
            self.__respond_fail()
        else:
            response = response.decode("ascii")
            self.__respond_success() if len(response) == self.msg_length \
                else self.__respond_fail()

        self.completed_interactions = True


class LengthServer:
    """Create a server that return the length of received strings."""

    server: socket
    server_addr: tuple[str, int]
    active_connections: list[Connection]

    def __init__(self, host: str, port: int):
        """Don't forget your docstring."""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_addr = host, port
        self.server.bind(self.server_addr)
        self.active_connections: list[Connection] = []
        print(f"Server binded to {self.server_addr}")

    def __del__(self):
        """Deconstructor for LengthServer."""
        self.server.close()
        print("Closed socket.")

    def __add_connection(self, connection: socket, recv_addr: tuple[str, int])\
            -> Connection | None:
        """Check for duplicate Connections.

        Returns Connection() if the connection is new, otherwise returns None
        """
        print(f"Recieved connection from {recv_addr}")
        existing_addr = any(connect.addr == recv_addr
                            for connect in self.active_connections)
        return None if existing_addr else Connection(connection, recv_addr)

    def __interact_clients(self):
        """Do specified activity with clients."""
        for connection in self.active_connections:
            if connection is None:
                continue
            connection.calc_length()

    def run_server(self):
        """Start Server."""
        self.server.listen(16)
        # I realize that there is never more than one active connection
        # this is really just a proof of concept
        while True:
            print("Waiting for connection.")
            self.active_connections.append(
                self.__add_connection(*self.server.accept()))

            self.__interact_clients()
            # Disconnect from clients that have completed their interactions
            for idx, conn in enumerate(self.active_connections):
                if conn:
                    del self.active_connections[idx]


if __name__ == "__main__":
    server = LengthServer(HOST, PORT)
    server.run_server()
