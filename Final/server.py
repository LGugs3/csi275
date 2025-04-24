"""Docstring."""

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

    def __handle_client_connections(self):
        """Handle Reading socket tasks."""
        read_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        read_sock.bind(self.__read_addr)
        read_sock.listen(16)

        while True:
            thread_args = read_sock.accept()
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
                msg_len = sock[0].recv(4)
                # some message recieved
                if msg_len:
                    # decode and parse json
                    encoded_msg = sock[0].recv(int.from_bytes(msg_len))
                    decoded = encoded_msg.decode("utf-8")
                    msg_data = json.loads(decoded)
                    if msg_data[0] != "START":
                        continue
                    pot_cl_name = msg_data[1]

                    # client name already taken
                    if map(lambda client: client.client_name == pot_cl_name,
                           self.__active_connections):
                        self.__send_client_error(sock, 2)
                        continue

                    # add client to active connections
                    verify_num = random.randint(0, 10000)
                    new_client = ClientInfo(msg_data[1],
                                            sock[0], sock[1], verify_num)
                    send_data = ["VERIFY", verify_num]
                    self.__send_msg_client(sock[0], json.dumps(send_data))
                    self.__active_connections.append(new_client)

    def __communicate_client(self, sock: socket.socket, addr: tuple[str, int]):
        while True:
            current_client = None
            sock.setblocking(True)
            enc_msg_len = sock.recv(4)
            if enc_msg_len:
                enc_msg = sock.recv(int.from_bytes(enc_msg_len))
                if enc_msg:
                    msg_data = json.loads(enc_msg.decode("utf-8"))
                    return_val = self.__parse_client_msg(sock, msg_data[0],
                                                         msg_data[1:],
                                                         current_client)
                    if return_val == -1:
                        sock.close()
                        break
                    if return_val is tuple:
                        match return_val[0]:
                            case -2:
                                current_client = return_val[1]

    def __parse_client_msg(self, sock: socket.socket,
                           command: str, data: list,
                           cl_info: ClientInfo = None) -> tuple:
        """Parse message received from client.

        Arguments
        ---------
        sock: socket
            socket message was received from
        command: str
            string that appears in `MESSAGE_TYPES` in :file:`constants.py`
        cl_info: ClientInfo
            | Information for the current client.
            | Defaults to `None`.

        Returns
        -------
        tuple:
            | First value is return code, non-zero is error.
            | Second value is function to run(maybe remove).
        """
        match(command):
            case "START":
                return (4,)  # second arg in tuple is func to run
            case "EXIT":
                self.__active_connections.remove(cl_info)
                del cl_info
                return 0
            case "BROADCAST":
                msg_send = ["MESSAGE", data[0], data[1]]
                for active_conn in self.__active_connections:
                    if not active_conn.is_verified:
                        continue
                    self.__send_msg_client(active_conn.recv_socket,
                                           json.dumps(msg_send))
                return (0, )
            case "PRIVATE":
                return (0, )
            case "VERIFY":
                for active_conn in self.__active_connections:
                    result = active_conn.verify_client(sock, data[0])
                    if result is ClientInfo:
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
        encoded = json.encode("utf-8")
        msg_send = len(encoded).to_bytes(4) + encoded
        sock.sendall(msg_send)

    def __send_client_error(self, sock, error, is_fatal=False):
        self.__send_msg_client(sock, json.dumps(["ERROR", error, is_fatal]))

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
