"""Server code for Lab 10.

Author: Liam Gugliotta
Class: CSI-275-01
Assignment: Final Project

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

from client_info import ClientInfo
# import constants
import threading
import socket
import random
import json


class Server:
    """Docstring."""

    __active_threads: list[threading.Thread]
    __active_connections: list[ClientInfo]
    __purgatory_connections: list[tuple[socket.socket, tuple]]
    __read_addr: tuple[str, int]
    __write_addr: tuple[str, int]

    def __init__(self):
        """Initialize :class:`Server` class."""
        self.__active_connections = []
        self.__purgatory_connections = []
        self.__active_threads = []
        self.__read_addr = ("localhost", 8000)
        self.__write_addr = ("localhost", 9000)

    def __del__(self):
        """Deconstruct :class:`Server` class."""
        for connection in self.__active_connections:
            connection.recv_socket.close()
            connection.send_socket.close()
            del connection

    def __recv_all(self, sock: socket.socket, size: int) -> bytes:
        """Receive all bytes from socket.

        Arguments
        ---------
        sock: socket
            socket to receive from
        size: int
            number of bytes to receive

        Returns
        -------
        bytes:
            bytes received from socket
        """
        data = b""
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                break
            data += packet
        return data

    def __handle_client_connections(self):
        """Handle Reading socket tasks."""
        read_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        read_sock.bind(self.__read_addr)
        read_sock.listen(16)

        while True:
            thread_args = read_sock.accept()
            print(f"Client {thread_args[1]} connected.")
            new_client = threading.Thread(target=self.__communicate_client,
                                          args=thread_args)
            new_client.start()
            self.__active_threads.append(new_client)

    def __handle_client_init(self):
        """Handle writing socket tasks."""
        write_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        write_sock.bind(self.__write_addr)
        write_sock.listen(16)

        while True:
            new_client, new_addr = write_sock.accept()
            self.__purgatory_connections.append((new_client, new_addr))

    def __wait_for_client_init(self):
        """Wait for clients in `__purgatory_connections` to send 'START'."""
        while True:
            for sock in self.__purgatory_connections:
                sock[0].setblocking(False)
                try:
                    msg_len = sock[0].recv(4)
                except (BlockingIOError, ConnectionResetError):
                    # no message received
                    continue
                # some message recieved
                if msg_len:
                    # decode and parse json
                    encoded_msg = self.__recv_all(sock[0],
                                                  int.from_bytes(msg_len))
                    if not encoded_msg:
                        continue
                    decoded = encoded_msg.decode("utf-8")
                    msg_data = json.loads(decoded)
                    try:
                        if msg_data[0] != "START":
                            continue
                    except IndexError:
                        # no message received
                        continue

                    # START message received
                    pot_cl_name = msg_data[1]
                    if not pot_cl_name.isalpha():
                        # client name not alphabetical
                        self.__send_client_error(sock[0], 1)
                    # client name already taken]
                    client_exists = False
                    for client in self.__active_connections:
                        client_exists = client.client_name == pot_cl_name
                    if client_exists:
                        self.__send_client_error(sock, 2)

                    # add client to active connections
                    verify_num = random.randint(0, 10000)
                    new_client = ClientInfo(msg_data[1],
                                            sock[0], sock[1], verify_num)
                    send_data = ["VERIFY", verify_num]
                    self.__send_msg_client(sock[0], json.dumps(send_data))
                    self.__active_connections.append(new_client)

    def __communicate_client(self, sock: socket.socket, addr: tuple[str, int]):
        current_client = None
        while True:
            sock.setblocking(True)
            try:
                enc_msg_len = sock.recv(4)
            except ConnectionResetError:
                # client disconnected
                print(f"Client {addr} disconnected.")
                del current_client
                if sock is not None:
                    sock.close()
                break
            if enc_msg_len:
                enc_msg = self.__recv_all(sock, int.from_bytes(enc_msg_len))
                if enc_msg:
                    msg_data = json.loads(enc_msg.decode("utf-8"))
                    print(f"Received message from client {addr}: {msg_data}")
                    return_val = self.__parse_client_msg(sock, msg_data[0],
                                                         msg_data[1:],
                                                         current_client)
                    if return_val == -1:
                        sock.close()
                        break
                    if isinstance(return_val, tuple):
                        if return_val[0] == 0:
                            self.__send_client_ok(sock)
                        else:
                            if return_val[0] == -2:
                                current_client = return_val[1]
                                current_client.send_addr = addr
                            else:
                                # error in parsing message
                                return_val[1](sock, return_val[0])

    def __parse_client_msg(self, sock: socket.socket,
                           command: str, data: list,
                           cl_info: ClientInfo) -> tuple:
        """Parse message received from client.

        Arguments
        ---------
        sock: socket
            socket message was received from
        command: str
            string that appears in `MESSAGE_TYPES` in :file:`constants.py`
        cl_info: ClientInfo
            Information for the current client.

        Returns
        -------
        tuple:
            | First value is return code, non-zero is error.
            | Second value is function to run(maybe remove).
        """
        if cl_info is None and command != "VERIFY":
            # requried to have client info
            return (5, self.__send_client_error)
        match(command):
            case "START":
                # should never happen, client has already been started
                return (4,)  # second arg in tuple is func to run
            case "EXIT":
                if len(data) != 1:
                    # incorrect number of arguments
                    return (5, self.__send_client_error)

                if data[0] != cl_info.client_name:
                    # incorrect client name
                    return (1, self.__send_client_error)

                self.__active_connections.remove(cl_info)
                msg_send = ["EXIT", cl_info.client_name]
                self.__send_msg_client(cl_info.recv_socket,
                                       json.dumps(msg_send))
                del cl_info
                return 0
            case "BROADCAST":
                print(f"Broadcasting message: {data}")
                if len(data) != 2:
                    # incorrect number of arguments
                    return (5, self.__send_client_error)

                msg_send = ["MESSAGE", data[1], data[0], False]
                # incorrect client name
                if data[0] != cl_info.client_name:
                    return (1, self.__send_msg_client)

                self.__broadcast_msg(json.dumps(msg_send))
                return (0, )
            case "PRIVATE":
                if len(data) != 3:
                    # incorrect number of arguments
                    return (5, self.__send_client_error)
                # incorrect client name or client not found
                if data[0] != cl_info.client_name or data[2] not in \
                        map(lambda x: x.client_name,
                            self.__active_connections):
                    return (1, self.__send_client_error)
                # send message to client
                msg_send = json.dumps(["MESSAGE", cl_info.client_name, data[1],
                                       True])
                # find correct client to send msg to
                for active_conn in self.__active_connections:
                    if active_conn.client_name == data[2]:
                        self.__send_msg_client(active_conn.recv_socket,
                                               msg_send)
                        break
                return (0, )
            case "VERIFY":
                for active_conn in self.__active_connections:
                    result = active_conn.verify_client(sock, data[0])
                    if isinstance(result, ClientInfo):
                        # notify client they can start sending messages
                        self.__send_msg_client(sock, json.dumps(["START"]))
                        return (-2, result)
                # no matching verification numbers
                self.__send_client_error(sock, 3, True)
                return -1
            case _:
                return (4,)

    def __send_msg_client(self, sock: socket.socket, json: str):
        """Send `json` message to client `sock`.

        Arguments
        ---------
        sock: socket
            socket to send send to
        json: str
            json string to encode and send
        """
        print(f"Sending message to client: {json}")
        encoded = json.encode("utf-8")
        msg_send = len(encoded).to_bytes(4) + encoded
        try:
            sock.sendall(msg_send)
        except ConnectionResetError:
            return

    def __send_client_ok(self, sock: socket.socket):
        """Send OK message to client.

        Arguments
        ---------
        sock: socket
            socket to send send to
        """
        try:
            self.__send_msg_client(sock, json.dumps(["CONT"]))
        except ConnectionResetError:
            return

    def __broadcast_msg(self, msg: str):
        """Broadcast message to all clients.

        Arguments
        ---------
        msg: str
            message to send to all clients
        """
        for active_conn in self.__active_connections:
            if not active_conn.is_verified:
                continue
            self.__send_msg_client(active_conn.recv_socket, msg)

    def __send_client_error(self, sock, error, is_fatal=False):
        """Send error message to client.

        Arguments
        ---------
        sock: socket
            Socket to send error message to
        error: str
            Error code to send to client
        is_fatal: bool, optional
            | If True, client will be disconnected.
            | Defaults to False.
        """
        try:
            msg_send = ["ERROR", error, is_fatal]
            self.__send_msg_client(sock, json.dumps(msg_send))
        except ConnectionResetError:
            return

    def init_server(self):
        """Start Reading and Writing sockets."""
        read_thread = threading.Thread(target=self.__handle_client_connections)
        write_thread = threading.Thread(target=self.__handle_client_init)
        add_connections = threading.Thread(target=self.__wait_for_client_init)

        read_thread.start()
        write_thread.start()
        add_connections.start()
        self.__active_threads.append(read_thread)
        self.__active_threads.append(write_thread)
        self.__active_threads.append(add_connections)


if __name__ == "__main__":
    server = Server()
    server.init_server()
