import os
from enum import Enum

def main():
    source = open("instances_from_website.txt", "r")
    counter = 1

    if not os.path.isdir("instances"):        
        os.mkdir("instances")
    else:
        c = input("Might override files in directory 'instances', do you want to continue? (y/n)")
        if c != 'y':
            print("Aborting.")

    instance_c = 1  
    for line in source:
        write_line(line, instance_c)
        instance_c += 1

    source.close()


def digit(c):
    if(c >= '0' and c <= '9'):
        return True
    return False


def write_line(line, num):
    dest = open("instances/instance_"+str(num)+".dzn", "w+")
    dest.write("[")
    found_numbers = False
    count = 0
    for c in line:
        if(found_numbers):
            if(c == " "):
                dest.write("<>")
            else:
                dest.write(c)
            count += 1
            if(count == 10):
                dest.write("]\n[")
            elif(count == 20):
                dest.write("]")
                break
            else:
                dest.write(", ")
        elif(found_numbers == False) and (c == '"'):
            found_numbers = True
    dest.close()

main()
