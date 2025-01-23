"""
User creates a list of integers + floats which is then sorted and printed.

Author: Liam Gugliotta
Class: CSI-275-01
Assignment: Lab 1 -- Sorting With Python

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


def build_list():
    """
    Docstring here.

    double lines
    """
    exit_keyword = "exit"
    unsorted_list = []
    val_to_append = ""

    while val_to_append != exit_keyword:
        val_to_append = input(f"Enter Number(type {exit_keyword} to stop): ")
        if val_to_append == exit_keyword:
            break

        if (val_to_append.isdigit()):
            unsorted_list.append(int(val_to_append))
        else:
            try:
                val_to_append = float(val_to_append)
            except ValueError:
                print(f"{val_to_append} is not an integer or float")
            except Exception as e:
                print(type(e).__name__, ':', e, "\n\nSomething went critically\
                       wrong; How did you do this.")
            else:
                unsorted_list.append(float(val_to_append))

    return unsorted_list


def sort_list(unsorted_list):
    """Another docstring."""
    unsorted_list.sort()


if __name__ == "__main__":
    my_list = build_list()
    print(my_list)
    sort_list(my_list)

    print(my_list)
