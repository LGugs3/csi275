"""Don't forget your docstring."""

import socket

HOST = "localhost"
PORT = 45000


class Connection:
    """Individual TCP connection with client."""

    connection: socket
    addr: tuple[str, int]
    msg_length: int

    def __init__(self, connection: socket, addr: tuple[str, int]):
        """Construct Connection class."""
        self.connection = connection
        self.addr = addr
        self.msg_length = -1

    def __del__(self):
        """Deconstruct Connection class."""
        print(f"Closing connection from {self.addr}")
        self.connection.close()

    def __eq__(self, value):
        """Check if self and value are the same object."""
        if isinstance(value, Connection):
            return self.addr == value.addr
        return False

    def __set_packet_length(self) -> None:
        self.msg_length = int.from_bytes(self.connection.recv(4), "big")

    def __recv_all(self) -> bytes | None:
        data = b""
        while len(data) < self.msg_length:
            more = self.connection.recv(self.msg_length - len(data))
            if not more:
                return None
            data += more
        return data

    def __respond_success(self) -> None:
        success_msg = f"I recieved {self.msg_length} bytes."
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
        self.msg_length = 4096
        self.active_connections: list[Connection] = []
        print(f"Server binded to {self.server_addr}")

    def __del__(self):
        """Deconstructor for LengthServer."""
        self.server.close()
        print("Closed socket.")

    def __add_connection(self, connection, recv_addr) -> Connection | None:
        print(f"Recieved connection from {recv_addr}")
        # check for duplicate connections
        for connect in self.active_connections:
            if connect.addr == recv_addr:
                return None

        return Connection(connection, recv_addr)

    def __interact_clients(self):
        for connection in self.active_connections:
            if connection is None:
                continue
            connection.calc_length()

    def run_server(self):
        """Start Server."""
        self.server.listen(16)
        while True:
            print("Waiting for connection.")
            self.active_connections.append(
                self.__add_connection(*self.server.accept()))

            self.__interact_clients()
            del self.active_connections[:]


if __name__ == "__main__":
    server = LengthServer(HOST, PORT)
    server.run_server()
