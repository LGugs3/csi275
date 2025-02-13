"""Don't forget your docstring."""

import socket

HOST = "127.0.0.1"
PORT = 20000
MAX_BYTES = 4096


class SortServer:
    """Don't forget your docstring."""

    server: socket
    server_addr: tuple[str, int]

    def __init__(self, host, port):
        """Don't forget your docstring."""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_addr = host, port
        self.server.bind(self.server_addr)

    def run_server(self):
        """Don't forget your docstring."""
        self.server.listen(20)

        while True:
            connection, recv_addr = self.server.accept()

            msg_arr: list = []
            while True:
                msg_recv = connection.recv(MAX_BYTES)
                byte_length = len(msg_recv)
                if not msg_recv:
                    break
                msg_recv = msg_recv.decode("ascii")
                msg_arr.extend(msg_recv.split(' '))

                if byte_length == MAX_BYTES:
                    continue

                response: list[int | float] | bool = \
                    self.__parse_packet(msg_arr)

                self.__respond_client_error(connection) if not response else \
                    self.__respond_client_success(connection, response)
                break

    def __parse_packet(self, unparsed_list: list) -> list | bool:
        """Parse recieved list into response."""
        parsed_list: list[int, float] = []
        sort_method: str = 'a'
        possible_sorts: list[str] = ['a', 'd', 's']
        for idx, ele in enumerate(unparsed_list):
            if idx == 0 and ele != "LIST":
                return False
            if idx == len(unparsed_list) - 1:
                if '|' in ele:
                    result = ele.split('|')
                    if result[1] not in possible_sorts:
                        return False
                    sort_method = result[1]
                    ele = result[0]
            else:
                char: int | float | bool = self.__check_int_float(ele)
                if not char:
                    return False
                parsed_list.append(char)

        if sort_method == 'a':
            parsed_list.sort()
        elif sort_method == 'd':
            parsed_list.sort(reverse=True)
        elif sort_method == 's':
            return [str(ele) for ele in parsed_list].sort()

        return parsed_list

    def __respond_client_success(self, connection, response: str):
        msg_send = "SORTED "
        msg_send += " ".join(map(str, response))

        connection.sendall(msg_send.encode("ascii"))

    def __respond_client_error(self, connection) -> None:
        connection.sendall("ERROR".encode("ascii"))

    def __check_int_float(self, char: str) -> int | float | bool:
        """Check if character is an int or float."""
        if char.isnumeric():
            return int(char)
        else:
            try:
                char = float(char)
            except ValueError:
                return False
            else:
                return char


if __name__ == "__main__":
    server = SortServer(HOST, PORT)
    server.run_server()
