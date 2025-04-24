"""Docstring."""

import socket


class ClientInfo:
    """:class:`ClientInfo` class.

    Member Variables
    ----------------
    client_name: str
        display name others see
    verify_num: int
        verification number to associate `recv_socket` with `send_socket`
    is_verified: bool
        Controls if `recv_sock` is connected to a `send_sock`
    recv_socket: socket
        | Client socket that initializes the connection to the server
        | and receives messages from the server.
    recv_addr: tuple[str, int]
        address and port of client's `recv_socket`
    send_socket: socket
        | client socket that sends messages to be displayed to
        | other clients
    send_addr: tuple[str, int]
        address and port of client's `send_socket`
    """

    client_name: str
    verify_num: int
    is_verified: bool
    recv_socket: socket.socket
    recv_addr: tuple[str, int]
    send_socket: socket.socket
    send_addr: tuple[str, int]

    def __init__(self, client_name, recv_sock, recv_addr, verify_num):
        """Initialize :class:`ClientInfo` class."""
        self.client_name = client_name
        self.recv_socket = recv_sock
        self.recv_addr = recv_addr
        self.verify_num = verify_num
        self.is_verified = False

    def __del__(self):
        """Deconstruct :class:`ClientInfo` class."""
        self.recv_socket.close()
        self.send_socket.close()

    def verify_client(self, send_sock, verify_num):
        """Compare verify numbers.

        Returns
        -------
        bool:
            False if no matching verification num
        ClientInfo:
            If matching verification number found

        """
        if self.is_verified:
            return False
        if self.verify_num == verify_num:
            self.send_socket = send_sock
            self.is_verified = True
            return self
        return False
