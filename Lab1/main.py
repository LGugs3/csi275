def build_list():
    exitKeyword = "exit"
    unsortedList = []
    valToAppend = ""

    while valToAppend != exitKeyword:
        valToAppend = input(f"Enter Number(type {exitKeyword} to stop): ")
        if valToAppend == exitKeyword: break

        if(valToAppend.isdigit()): unsortedList.append(int(valToAppend))
        else:
            try:
                valToAppend = float(valToAppend)
            except ValueError:
                print(f"{valToAppend} is not an integer or float")
            except Exception as e:
                print(type(e).__name__, ':',e,"\n\nSomething went critically wrong; How did you do this.")
            else:
                unsortedList.append(float(valToAppend))
    
    return unsortedList


def sort_list(unsortedList):
    unsortedList.sort()


if __name__ == "__main__":
    myList = build_list()
    print(myList)
    sort_list(myList)

    print(myList)