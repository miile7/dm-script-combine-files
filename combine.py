import re
import os
import pathlib

"""
Shows a command line program to open a main.s file and create a file that 
contains all the files that are required by this file.
"""

def printOverview():
    global main_path, base_path, save_path, require_function, include_main_content, comment, version, current_dir

    writeHead()
    print("")
    print(current_dir)
    print("")
    print("<1> main file is:          {}".format(os.path.relpath(main_path, current_dir)))
    print("<2> save file is:          {}".format(os.path.relpath(save_path, current_dir)))
    print("<3> require relative to:   {}".format(os.path.relpath(base_path, current_dir)))
    print("<4> require-function name: {}".format(require_function))
    print("<5> include main content:  {}".format("yes" if include_main_content else "no"))
    print("<6> comment:               {}".format(comment))
    print("<7> combined file version: {}".format(version))
    print("")
    action = input("Type the number to change the value, press [Enter] to start, type [x] to exit: ")
    action = action.strip().lower()

    if action == "1":
        readMainPath()
    elif action == "2":
        readSavePath()
    elif action == "3":
        readBasePath()
    elif action == "4":
        readRequireFunctionName()
    elif action == "5":
        readIncludeMainContent()
    elif action == "6":
        readComment()
    elif action == "7":
        readVersion()
    elif action == "x":
        exit(0)
    else:
        return
    
    printOverview()

def checkPath(check_path, is_dir = True):
    global current_dir

    check_path = os.path.abspath(check_path)

    if is_dir:
        return os.path.exists(check_path) and os.path.isdir(check_path)
    else:
        return os.path.exists(check_path) and os.path.isfile(check_path)

def readBasePath(msg = ""):
    global base_path, current_dir
    writeHead()
    print("Type in the path that the main file is requiring relative to.")
    print("")
    if msg != "":
        print(msg)
    
    print(current_dir)
    base_path = input("Base path of requiring: ")

    if not checkPath(base_path):
        readBasePath("The directory '{}' does not exist.\n".format(base_path))
    else:
        base_path = os.path.abspath(base_path)

def readSavePath():
    global save_path, current_dir
    writeHead()
    print("Type in the path (including the file name) of the file to generate " + 
          "and fill with the contents loaded from the main.")
    print("")
    print(current_dir)
    save_path = os.path.abspath(input("Path of save file: "))

def readMainPath(msg = ""):
    global main_path, current_dir
    writeHead()
    print("Type in the path of the main.s which contains the 'require()' functions.")
    print("")
    if msg != "":
        print(msg)

    print(current_dir)
    main_path = input("Path of main.s: ")

    if not checkPath(main_path, False):
        readMainPath("The file '{}' does not exist.\n".format(main_path))
    else:
        main_path = os.path.abspath(main_path)

def readRequireFunctionName():
    global require_function
    writeHead()
    print("Type in the name of the function that requires the files. This file will search for\n" + 
          "   <anything><require function name>(<quote><text><quote>)\n" + 
          "where <quote> can be ' or \" and spaces and tabs are ignored.")
    require_function = input("Require function name: ")

def readIncludeMainContent():
    global include_main_content
    writeHead()
    print("Set whether to add the content of the main file or not.")
    include_main_content = input("Include main content (y/n): ")

    if include_main_content.lower().strip() in ("yes", "y", "true", 1, "on"):
        include_main_content = True
    else: 
        include_main_content = False

def readComment():
    global comment
    writeHead()
    print("A comment that will be added to the head of the combined file. To print no comment " + 
          "set the comment to an empty string (the version has to be empty too).")
    comment = input("Comment: ")

def readVersion():
    global version
    writeHead()
    print("The version to print in the comment section of the combined file. To print no version "
          "set the version to an empty string.")
    version = input("Version: ")

def writeHead():
    os.system('cls' if os.name in ('nt', 'dos') else 'writeHead')

    title = "Combine .s files"
    print(title)
    print("*" * len(title))
    print("")
    print("")

current_dir = os.path.abspath(".")
writeHead()

main_path = ""
readMainPath()

base_path = pathlib.Path(__file__).parent.absolute()
save_path = os.path.join(pathlib.Path(main_path).parent.absolute(), "combined.s")
require_function = "require"
include_main_content = False
comment = ""
version = ""

printOverview()

writeHead()

reg = re.compile(require_function + r"\(\s*(\"|')([^\1]+)\1\s*\)")
combined_content = ""

if version != "":
    if comment != "":
        comment += "\n\n"

    comment += "@version " + version

if comment != "":
    combined_content = ("/**\n" + 
                        " * " + comment.strip().replace("\n", "\n * ") + "\n" + 
                        " */" + 
                        "\n\n")

try:
    main_content = ""

    with open(main_path, "r") as file:
        print("Reading {}".format(main_path))
        
        i = 1
        for line in file:
            matches = reg.search(line)

            if include_main_content:
                main_content += line
            
            if matches != None:
                print("  Found {}-function on line {}.".format(require_function, i))
                rel_path = matches.group(2)
                abs_path = os.path.join(base_path, rel_path)

                try:
                    f = open(abs_path, "r")
                    if combined_content == "":
                        combined_content += "\n\n"
                    
                    combined_content += "/* = = = file {} = = = */\n".format(rel_path)
                    combined_content += f.read()
                    print("  Adding contents of {}.".format(rel_path))
                except Exception as e:
                    print("  Main file requires {} but the file {} cannot be opened.".format(rel_path, abs_path))
            i += 1
    
    if include_main_content:
        combined_content += "\n\n/* = = = file {} = = = */\n\n".format(main_path)
        combined_content += main_content

    if combined_content != "":
        try:
            with open(save_path, "w") as file:
                file.write(combined_content)
            
            print("Successfully wrote {}.".format(save_path))
        except Exception as e:
            print("Could not open {}: {}".format(save_path, e))
    else:
        print("There is no content to write in the combined file.")
except Exception as e:
    print("Could not open {}: {}".format(main_path, e))