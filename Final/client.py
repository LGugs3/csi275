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

import socket
import threading
import constants
import json
import weakref


class Client:
    """Docstring."""

    send_thread: threading.Thread
    recv_thread: threading.Thread
    client_name: str
    send_socket: socket.socket
    recv_socket: socket.socket
    verify_num: int
    is_verified: bool

    def __init__(self):
        """Init Client."""
        self.client_name = ""
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_thread = threading.Thread(target=self.__handle_send)
        self.recv_thread = threading.Thread(target=self.__handle_recv)
        self.is_verified = False
        self.verify_num = -1
        self.__start_client()

    def __del__(self):
        """Destructor."""
        self.send_socket.close()
        self.recv_socket.close()
        if self.recv_thread is not threading.current_thread():
            self.recv_thread.join()
        if self.send_thread.is_alive():
            if self.send_thread is not threading.current_thread():
                self.send_thread.join()

    def __start_client(self):
        """Start client."""
        pot_cl_name = ""
        while not pot_cl_name.isalpha():
            pot_cl_name = input("Enter your display name: ")
            if not pot_cl_name.isalpha():
                print("Display name must be alphabetical characters only.")
        self.client_name = pot_cl_name

        self.recv_thread.start()

    def __recv_all(self, sock: socket.socket, size: int) -> bytes:
        """Receive all data from socket."""
        data = b""
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                break
            data += packet
        return data

    def __handle_send(self):
        """Handle send thread."""
        # wait until verify number is set
        while self.verify_num == -1:
            pass
        self.send_socket.connect(constants.SERVER_READ_ADDR)
        # send verification number
        msg_send = (json.dumps(["VERIFY", self.verify_num])).encode("utf-8")
        msg_len = len(msg_send).to_bytes(4, byteorder="big")
        self.send_socket.sendall(msg_len + msg_send)

        # recv response from server
        return_len = self.send_socket.recv(4)
        return_msg = self.__recv_all(self.send_socket,
                                     int.from_bytes(return_len, byteorder="big"
                                                    ))
        return_msg = json.loads(return_msg.decode("utf-8"))
        if return_msg[0] == "START":
            self.is_verified = True
            self.__print_message("You are now connected to the server.")
        elif return_msg[0] == "ERROR":
            self.__print_error(f"Error code {return_msg[1]}")
            if return_msg[2]:
                self.__del__()
                return

        # wait for user input
        try:
            while True:
                user_input = input()
                did_send_msg = self.__parse_user_input(user_input)
                if did_send_msg:
                    msg_len = self.send_socket.recv(4)
                    msg = self.__recv_all(self.send_socket,
                                          int.from_bytes(msg_len, byteorder="big"))
                    msg = json.loads(msg.decode("utf-8"))
                    self.__parse_server_response(msg)
                else:
                    self.__send_message(json.dumps(["EXIT", self.client_name]))
                    self.__del__()
                    return
        except RuntimeError:
            pass

    def __parse_user_input(self, user_input: str) -> bool:
        if user_input == "!exit":
            self.__send_message(json.dumps(["EXIT", self.client_name]))
            self.__print_message("Exiting...")
            self.__del__()
        if user_input[0] == '@':
            # private message
            user_input = user_input[1:]
            split_msg = user_input.split(" ", 1)
            if not split_msg[0].isalpha():
                self.__print_error("Invalid client name.")
                return False
            msg_send = json.dumps(["PRIVATE", self.client_name, split_msg[1],
                                  split_msg[0]])
            self.__send_message(msg_send)
        else:
            msg_send = json.dumps(["BROADCAST", self.client_name, user_input])
            self.__send_message(msg_send)
        return True

    def __parse_server_response(self, msg: str) -> None:
        """Parse server response.

        Arguments
        ---------
        msg: str
            message to parse
        """
        try:
            if msg[0] == "OK":
                return
            elif msg[0] == "ERROR":
                self.__print_error(f"Error code {msg[1]}")
                if msg[2]:
                    self.__print_error("Client is shutting down.")
                    self.__del__()

        except IndexError:
            print("Received broken message from server.")

    def __print_error(self, msg: str) -> None:
        """Print error message."""
        print(f"Error: {msg}")

    def __print_message(self, msg: str) -> None:
        """Print message."""
        print(msg)

    def __handle_recv(self):
        """Handle receive thread."""
        try:
            self.recv_socket.connect(constants.SERVER_WRITE_ADDR)
        except ConnectionRefusedError:
            self.__print_error("Server is not running.")
            self.__del__()
            return
        # send start
        msg = json.dumps(["START", self.client_name]).encode("utf-8")
        msg_len = len(msg).to_bytes(4, byteorder="big")
        self.recv_socket.sendall(msg_len + msg)
        # get verification number
        return_len = self.recv_socket.recv(4)
        return_msg = self.__recv_all(self.recv_socket,
                                     int.from_bytes(return_len, byteorder="big"
                                                    ))
        return_msg = json.loads(return_msg.decode("utf-8"))
        if return_msg[0] != "VERIFY":
            raise ValueError("Invalid message type")
        self.verify_num = return_msg[1]
        self.send_thread.start()

        # wait until verified
        while not self.is_verified:
            pass
        while True:
            # recv messages from server
            try:
                return_len = self.recv_socket.recv(4)
            except (ConnectionAbortedError, ConnectionResetError):
                return
            return_msg = self.__recv_all(self.recv_socket,
                                         int.from_bytes(return_len,
                                                        byteorder="big"))
            return_msg = json.loads(return_msg.decode("utf-8"))
            self.__parse_server_msg(return_msg)

    def __parse_server_msg(self, msg: str) -> None:
        """Parse server message.

        Arguments
        ---------
        msg: str
            message to parse
        """
        try:
            if msg[0] != "MESSAGE":
                if msg[0] == "EXIT":
                    return
                print("Received broken message from server.")
                print(msg)
            else:
                if msg[3]:
                    self.__print_message(f"{msg[1]} (private): {msg[2]}")
                else:
                    if msg[2] != self.client_name:
                        self.__print_message(f"{msg[2]}: {msg[1]}")
        except IndexError:
            print("Received broken message from server.")
            print(msg)

    def __send_message(self, message: str) -> None:
        """Send message to server."""
        if not self.is_verified:
            return

        message = message.encode("utf-8")
        msg_len = len(message).to_bytes(4, byteorder="big")
        self.send_socket.sendall(msg_len + message)


if __name__ == "__main__":
    client = Client()
    weak_ref = weakref.ref(client, lambda ref: exit(0))
