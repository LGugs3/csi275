"""Server code for Lab 10.

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

import threading
import socket
import random

# Global list of 8-Ball answers
ANSWER_LIST = ["It is certain.",
               "It is decidedly so.",
               "Without a doubt.",
               "Yes - definitely.",
               "You may rely on it.",
               "As I see it, yes.",
               "Most likely.",
               "Outlook good.",
               "Yes.",
               "Signs point to yes.",
               "Reply hazy, ask again.",
               "Ask again later.",
               "Better not tell you now.",
               "Cannot predict now.",
               "Concentrate and ask again.",
               "Don't count on it.",
               "My reply is no.",
               "My sources say no.",
               "Outlook not so good.",
               "Very doubtful."]

# Server host/port information
HOST = "localhost"
SERVER_PORT = 7000

# Maximum amount of data to read in one function call
MAX_BYTES = 1024


class EightBallServer:
    """TODO Don't forget your docstrings."""

    def __init__(self, host, port):
        """Create the initial listening socket and start our threads."""
        self.srv_sock = self.create_server_socket(host, port)

        self.start_threads(self.srv_sock)

    def create_server_socket(self, host, port) -> socket:
        """Set up the 8-Ball server socket.

        Should go through the create/bind/listen steps and return
        the created listening socket.
        """
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((host, port))
        server_sock.listen(16)
        return server_sock

    # TODO Write this function!
    def accept_8ball_connections(self, listener: socket):
        """Answer questions with Magic 8-Ball responses.

        This function should:
            - accept a connection from the listener socket
              (within our usual infinite while loop)
            - Use recv_until_delimiter() to grab questions from the client
              until it closes the socket ('?' will be the delimiter)
            - Provide a random response drawn from our 8-Ball answer set
              (see answer_list above) for each question
            - Send all of the answers as a single string back to the client,
            - and close the socket.
        """
        while True:
            client_sock, _ = listener.accept()
            recv_buffer = b""
            answer_list = ""
            data = b"boilerplate"
            while True:
                data, recv_buffer = self.recv_until_delimiter(client_sock,
                                                              b'?',
                                                              recv_buffer)

                if not data:
                    break
                answer_list += ANSWER_LIST[random.randrange(len(ANSWER_LIST))]
            client_sock.sendall(answer_list.encode("ascii"))
            client_sock.close()

    def recv_until_delimiter(self, sock, byte_delim, storage):
        """Receive data until it sees a specified delimiter.

        This function returns two parameters: A complete message,
        and any extra data we currently have after the message (i.e.,
        what you should store in a buffer!)

        The delimiter should be passed to this function as a byte string.
        """
        # Initialize an empty buffer
        data = b""

        # For ease of use later
        delim_char = byte_delim.decode("ascii")
        index = 0

        # See if the message is already there
        for c in storage.decode("ascii"):
            if c != delim_char:  # No delimiter found yet
                data += c.encode("ascii")
                index += 1
            else:  # Delimiter found!
                # Put everything after the delimiter back into storage
                temp = storage[index+1:]
                storage = temp
                # Return the data and the current storage buffer
                return data, storage

        # If we get here, no delimiter yet
        delim_found = False
        while not delim_found:
            try:
                # Query the socket for more data
                more = sock.recv(MAX_BYTES)
            except ConnectionResetError:
                return b"", b""
            if not more:  # No more data to parse
                return b"", b""
            test = more.decode("ascii")
            index = 0
            for c in test:
                if c != delim_char:  # No delimiter found yet
                    data += c.encode("ascii")
                    index += 1
                else:  # Delimiter found!
                    # Put everything after the delimiter into storage
                    temp = test[index + 1:]
                    storage = temp.encode("ascii")
                    # Return the data and the current storage buffer
                    return data, storage

    def accept_connections_forever(self, sock):
        """Converse with a client over `sock` until they are done talking."""
        try:
            self.accept_8ball_connections(sock)
        except EOFError:
            print('Client socket has closed')
        except ConnectionResetError as e:
            print('Connection reset.\ncause: ', e)
        finally:
            sock.close()

    def start_threads(self, listener: socket, workers=4):
        """Kick off the threads needed to serve 8-ball requests.

        Each thread should call accept_connections_forever() as its
        starting function.
        """
        active_threads = []
        thread_args = (listener,)
        for i in range(workers):
            new_thread = threading.Thread(target=self.accept_connections_forever,
                                          args=thread_args)
            new_thread.start()
            active_threads.append(new_thread)


if __name__ == "__main__":
    eight_ball = EightBallServer(HOST, SERVER_PORT)
