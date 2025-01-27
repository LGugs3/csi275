"""
User creates a list of integers + floats which is then sent to a server to be \
sorted.

Author: Liam Gugliotta
Class: CSI-275-01
Assignment: Lab 3 -- Socket Sorting

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


from makeList import CustomList

if __name__ == "__main__":
    my_list = CustomList()

    my_list.build_list()
    response = my_list.sort_list()
    if "SORTED" not in response:
        print(response)
    else:
        print("Sorted List:", response.replace("SORTED ", ''))
