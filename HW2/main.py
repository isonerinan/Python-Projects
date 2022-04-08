"""# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
"""
import json

def register():
    person["name"] = input("Name: ")
    person["surname"] = input("Surname: ")
    person["department"] = input("Department: ")
    person["salary"] = input("Salary: ")

def update(i):
    with open("database.txt", "r") as file:
        for line in file:
            strippedLine = line.strip()
            lineList = strippedLine.split()
            database.append(lineList)

    database.pop(i-1)
    register()
    database.insert(i-1, person)
    print(database)

    with open("database.txt", "r+") as file:
        file.truncate(0)
        for data in database:
            file.write(f"{data}\n")

def save():
    writeData = json.dumps(database)
    with open("database.txt", "a") as file:
        file.write(f"{writeData}\n")

def show():
    i = 1
    with open("database.txt", "r") as file:
        for line in file:
            print(f"{i}.", line)
            i += 1


person = {"name": "", "surname": "", "department": "", "salary": ""}
database = [person]

if __name__ == '__main__':
    while 1:

        print("Actions:"
            "\n\t1. Register a person"
            "\n\t2. Update a person"
            "\n\t3. Delete a person from the database"
            "\n\t4. Save the person to the database"
            "\n\t5. Show the database"
            "\n\t6. ui")

        action = int(input())

        if action == 1:
            register()
            print("If you're sure, please save the person to the database.")

        if action == 2:
            show()
            updateNumber = int(input("Which person would you like to update? "))
            update(updateNumber)



        if action == 4:
            save()

        if action == 5:
            show()