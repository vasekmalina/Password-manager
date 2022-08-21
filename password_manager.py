from cryptography.fernet import Fernet
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.theme import Theme
import json
import pathlib
import string
import random
import pwinput
import sys
import time
import os

#Once you set new password remove lines 195, 196 and 197


#variables
path = str(pathlib.Path(__file__).parent.resolve()) + "\\" # path to directory with script
k = b'oAf19KW55Jujo4VtDjrnt39jz2377EWl4u8PlToxawY=' # key to the cyphre
key = Fernet(k)

#print menu table styling
task = ["Show list of passwords", "Enter new password", "Delete password", "Get password", "Modify password", "Reset login password", "Clear screen", "Exit"]
press = ["l", "n", "d", "g", "m", "r", "c", "e"]

menu_table = Table()
menu_table.add_column("Task", style="bold chartreuse1", justify = "left")
menu_table.add_column("Press key", style="bold deep_sky_blue1", justify= "right")
for t, p in zip(task, press):
        menu_table.add_row(t, p)

my_theme = Theme({"success": "bold green", "error": "bold red"})

console = Console(theme=my_theme)


def encry(string):
    #transfering plain text to cyphre
    s = string.encode()
    e = key.encrypt(s).decode()

    return e 

def decry(string):
    #transfering cyphre to plain text
    x = string.encode()
    decrypted = key.decrypt(x)
    d = decrypted.decode()

    return d

def load_data():
    #takes data from json and stores it in variable
    with open(path + "data.json",'r+') as file:
        file_data = json.load(file)

    return file_data


def new_pass():
    #func responsible for creating a new password
    max_pass_len = 25
    n_list = []
    run = True
    file_data = load_data()

    for dic in file_data["pass"]:
        l_name = decry(dic["e"])
        n_list.append(l_name)

    while run:
        name = input("Enter what for is this password: ")
        if name in n_list:
            console.print("This name was already used for different password.", style="error")
        elif len(name) == 0:
            console.print("This name is too short.", style="error")
        elif len(name) > max_pass_len:
            console.print("This name is too long.", style="error")
        else:
            run = False



    user = input("Enter username: ")
    email = input("Enter email adress assossiated with this password: ")
    password = input("Enter the password: ")

    #encryption
    p_data = []    
    for i in name, user, email, password:
        enc = encry(i)
        p_data.append(enc)

    dic = {
        "e": p_data[0],
        "r": p_data[1],
        "l": p_data[2],
        "d": p_data[3]
    }

    #writing it in .json file
    with open(path + "data.json",'r+') as file:
        file_data = json.load(file)

        file_data["pass"].append(dic)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

    console.print("New password has been successfully saved.", style="success")


def show_list():
    #takes all passwords "names" and displays them
    list_of_names = []
    longest = "" # longest is variable that makes sure that all columns has same width
    file_data = load_data()
    for item in file_data["pass"]:
        n = decry(item["e"])
        list_of_names.append(n)
        if len(n) > len(longest):
            longest = n 

    #showing in it form of table using rich library:   
    print()
    #setting and styling of table
    list_table = Table()
    for i in range(3):
        list_table.add_column("#", justify= "center")
        #"\U0001F512" unicode for lock emoji, does not work in cmd though

    add_item = len(list_of_names)%3

    if add_item == 1:
            list_of_names.append("")
            list_of_names.append("")
    if add_item == 2:
            list_of_names.append("")

    for i in range(0, len(list_of_names), 3):
            list_table.add_row(list_of_names[i], list_of_names[i+1], list_of_names[i+2])

    #making sure all columns have same width
    list_table.add_row(" "*len(longest), " "*len(longest), " "*len(longest))


    console.print(list_table)
    print()


def display_pass():
    #func responsible for displaying all data for particular password that user requested
    n_list = []
    run = True

    file_data = load_data()

    for dic in file_data["pass"]:
        l_name = decry(dic["e"])
        n_list.append(l_name)
    
    while run:
        name = input("Which password do you want? ")
        if name in n_list:
            for dic in file_data["pass"]:
                l_name = decry(dic["e"])
                if name == l_name:
                    print()

                    text = ["Site", "Username", "Email", "Password"]
                    display_table = Table()
                    for t in text:
                        display_table.add_column(t, justify="center")

                    display_table.add_row(decry(dic["e"]), decry(dic["r"]), decry(dic["l"]), decry(dic["d"]))

                    console.print(display_table)

                    print()
                    run = False     
        else:
            console.print("Password has not been found.", style="error")
            
def generate_key():
    #this func provides new key for reseting login password
    letters = string.ascii_letters
    key = ''.join(random.choice(letters) for i in range(15))
    return key

def login():
    #access to database/app is granted once user enters correct password
    file_data = load_data()

    password = decry(file_data["log"][0]["d"])
    r_key = decry(file_data["log"][0]["t"])
    print("Password is: ",password)
    print("Recovery key is: ",r_key)
    
    while True:
        log = pwinput.pwinput("Enter the password: ")
        if log == password:
            break
        else:
            console.print("Incorrect password.",style="error")
            print("For reseting the password type 'r'.")
            
        if log == "r":
            reset_login()


    console.print("Access granted", style="success")

def reset_login():
    #User can use this func for instance when he forgets login password or just want to set a new one for some reason
    file_data = load_data()

    recovery_key = decry(file_data["log"][0]["t"])
    key = input("Enter recovery key: ")
            
    if key == recovery_key:
        #create a new password and generate reset key
        while True:
            new_p = pwinput.pwinput("Enter your new password: ")
            new_p_check = pwinput.pwinput("Renter your new password: ")
                    
            if new_p == new_p_check:
                break
            else:
                console.print("Error", style="error")


        #encry and store in json + display
        new_k = generate_key()

        with open(path + "data.json") as file:
            file_data = json.load(file)


        with open(path + "data.json", "w") as file:
            file_data["log"][0]["d"] = encry(new_p)
            file_data["log"][0]["t"] = encry(new_k)
                    
            json.dump(file_data, file, indent = 4)

        print("Your new recovery key is", new_k)
        print("Creating file with your recovey key in folder: ", path)
        time.sleep(3)

        with open(path + "recovery_key.txt", "w") as f:
            f.write("This key is essential for reseting password. \n")
            f.write(new_k)
        
        #close app
        sys.exit()
    else:
        console.print("Inccorect recovery key.", style="error")

def delete():
    #this func deletes password once user provides its name in appropriate section of the app
    n_list = []
    run = True

    file_data = load_data()

    for dic in file_data["pass"]:
        l_name = decry(dic["e"])
        n_list.append(l_name)

    #user at first enters name, provided it exist it is then deleted
    while run:
        name = input("Which password do you want to delete? ")

        if name in n_list:
            new_dic = {'log': [{"d": file_data["log"][0]["d"], "t": file_data["log"][0]["t"]}], 'pass': []}
            #looping
            for i, dic in enumerate(file_data["pass"]):
                #deleting works in that way that it is beying left out in new_dic
                if decry(dic["e"]) == name:
                    pass
                else:
                    new_dic["pass"].append(dic)
                    
                with open(path + "data.json", "w") as f:
                    json.dump(new_dic, f, indent = 4)
                run = False
        else:
            console.print("Password has not been found.", style="error")

    console.print(f" '{name}' password has been deleted.", style="success")

def modify():
    n_list = []
    run = True
    run2 = True
    d = {0: "e", 1: "r", 2: "l",3:"d"}
    d_class = ""


    file_data = load_data()

    for dic in file_data["pass"]:
        l_name = decry(dic["e"])
        n_list.append(l_name)

    while run:
        name = input("Which password do you want to modify? ")
        if name in n_list:
            while run2:
                atrr = int(input("What kind of data do you want to modify? (0= name, 1=user, 2=email, 3=password) "))
                if atrr >= 0 and atrr < 4:
                    d_class = d[atrr]
                    run = False
                    run2 = False
                else:
                    console.print("Wrong input.", style="error")
        else:
            console.print("Password has been found.", style="error")


    new_input = input("Enter new data: ")

    with open(path + "data.json",'r+') as file:
        file_data = json.load(file)
        
        for i, dic in enumerate(file_data["pass"]):
            l_name = decry(dic["e"])
            if l_name == name:
                file_data["pass"][i][d_class] = encry(new_input)

        file.seek(0)
        json.dump(file_data, file, indent = 4)

    console.print("Password has been succesffully modified.", style="success")

def menu_print():
    #simply printing menu so user knows what option he has
    console.print(menu_table)

def clear_screen():
    #clears all text on screen 
    if os.name == "nt":
        _ = os.system("cls")


def headline():
    MARKDOWN = """# PASSWORD MANAGER"""
    md = Markdown(MARKDOWN)
    console.print(md)

def main():
    #dictionary that stores key and appropriate func (This replaced long block which consisted from 7 if statements)
    func_dic = {"l": show_list, "n": new_pass, "d": delete, "g": display_pass, "r": reset_login, "c": clear_screen, "m":modify}
    login()
    headline()
    while True:
        print()
        console.print("Press Ctrl + c if you want to get back from selected task.")
        print()
        menu_print()
        answer = input("What do you want to do? ")

        #exit() cannot be for some reason executed from dictionary like other funcs ↑
        if answer == "e":
            sys.exit()
        else:
            try:  
                do = func_dic.get(answer)
                do()
            except SystemExit:
                sys.exit()
            except:    
                console.print("Error", style="error")

main()