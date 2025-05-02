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


SERVER_READ_ADDR = ("localhost", 8000)
SERVER_WRITE_ADDR = ("localhost", 9000)

MESSAGE_TYPES = ["START",
                 "EXIT",
                 "BROADCAST",
                 "PRIVATE",
                 "VERIFY",
                 "MESSAGE",
                 "ERROR",
                 "CONT"
                 ]
