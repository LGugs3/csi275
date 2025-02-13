"""Student code for Lab 4.

Author: Liam Gugliotta
Class: CSI-275-01
Assignment: Lab4 -- UDP Sockets
Certification of Authenticity:
I certify that this is entirely my own work, except where I have given
fully-documented references to the work of others. I understand the definition
and consequences of plagiarism and acknowledge that the assessor of this
assignment may, for the purpose of assessing this assignment:
- Reproduce this assignment and provide a copy to another member of academic
- staff; and/or Communicate a copy of this assignment to a plagiarism checking
- service (which may then retain a copy of this assignment on its database for
- the purpose of future plagiarism checking)

Champlain College CSI-235, Spring 2019
The following code was written by Joshua Auerbach (jauerbach@champlain.edu)
"""

import socket
from functools import partial
import random
import constants


class TimeOutError(Exception):
    """Custom exception for UDP packet timout."""

    pass


class UDPClient:
    """UDPClient Docstring."""

    def __init__(self, host_ip: str, port: int, use_msg_id: bool = False):
        """Initialize class."""
        self.server_addr = host_ip, port
        self.use_msg_id = use_msg_id

        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_send = self.udp_sock.sendto
        # use lambda b/c sendto does not have keyword args
        self.send_msg_server = partial(lambda data, addr: udp_send(data, addr),
                                       addr=self.server_addr)

        self.udp_sock.settimeout(constants.INITIAL_TIMEOUT)

    def __del__(self):
        """Deconstructor method."""
        self.udp_sock.close()

    def send_message_by_character(self, msg: str) -> str:
        """Send msg to sever with each packet containing one character."""
        full_response: str = ""
        for char in msg:
            if self.use_msg_id:
                next_id = random.randint(0, constants.MAX_ID)
            result: bool | str = True
            curr_wait_time = self.__reset_timeout()

            while not type(result) is str:  # until a string is returned
                if not self.use_msg_id:
                    result = self.__send_msg(char)
                else:
                    # format msg to standard
                    msg = (str(next_id) + '|' + char)
                    result = self.__send_msg_with_id(msg, next_id)

                # recvfrom() timed out
                if type(result) is bool and not result:
                    curr_wait_time *= 2
                    self.udp_sock.settimeout(curr_wait_time)
                    if curr_wait_time >= constants.MAX_TIMEOUT:
                        raise TimeOutError("Maximum Timeout Time reached")
                elif type(result) is str:
                    full_response += result

        return full_response

    def __send_msg_with_id(self, msg: str, id: int) -> bool | str:
        """
        Send message to server and recieve response.

        Usecase only for ids
        Returns:
            Boolean:
                True if response recieved but ids do not match,
                false if socket timed out
            String:
                character that was recieved with correct ID

        """
        try:
            self.send_msg_server(msg.encode("ascii"))
            response, response_addr = \
                self.udp_sock.recvfrom(constants.MAX_BYTES)
        except socket.timeout:
            return False
        msg_parts = response.decode("ascii").split('|')
        return msg_parts[1] if int(msg_parts[0]) == id else True

    def __send_msg(self, msg: str) -> bool | str:
        """
        Send UDP packet to server without ID.

        Returns false if timeout otherwise returns packet recieved.
        """
        try:
            self.send_msg_server(msg.encode("ascii"))
            response, response_addr = \
                self.udp_sock.recvfrom(constants.MAX_BYTES)
        except socket.timeout:
            return False
        else:
            return response.decode("ascii")

    def __reset_timeout(self) -> float:
        self.udp_sock.settimeout(constants.INITIAL_TIMEOUT)
        return constants.INITIAL_TIMEOUT


def main():
    """Run some basic tests on the required functionality.

    for more extensive tests run the autograder!
    """
    client = UDPClient(constants.HOST, constants.ECHO_PORT)
    print(client.send_message_by_character("hello world"))

    client = UDPClient(constants.HOST, constants.REQUEST_ID_PORT, True)
    print(client.send_message_by_character("hello world"))


if __name__ == "__main__":
    main()
