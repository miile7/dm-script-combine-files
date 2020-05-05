# Combine files program

A program to combine dm-script files that are glued with the `require()` function. This is an addition for the answer at https://stackoverflow.com/a/61345716/5934316.

Simply download and execute the `combine.py`. It asks for the paths and will then create the combined file.

Note: This requires a [python installation](https://www.python.org/downloads/).

## The requiring workaround

The scripting language [`dm-script` from Gatan](https://www.gatan.com/products/tem-analysis/gatan-microscopy-suite-software) does not have a proper way of including files. This is why I created the `require()` function together with the `main.s`. This `main.s` file is open in GMS 3 and it is barely changed. It will be executed for testing. The real program code is in `program.s` and can be edited by any other IDE. Also the libaries can be edited on runtime. This offers to split the code in modules.

Note that this requires deleting the plugin directory before or after every start of GMS. This can be done manually by using the batch script below

## The purpose of this file

When using the `require()` function defined in the `main.s` to create a modular dm-script program, one may run into the problem that debugging gets very difficult. dm-script jumps to the line where the error is but does not show an error message. If the files are loaded dynamically, dm-script cannot jump there.

There comes this program: It creates one big file that contains the content of all the required files which makes it easy to debug.

Note that you can also use the `require()` in your dm-scripts without defining it and then *always* run the combine file and only execute the combined file.

## The main.s

This is the `main.s` which is the only open file in GMS. This is the file that gets executed and will require all the other files, including the main code file `program.s`.

```c
/**
 * File: main.s
 */

String __file__;
GetCurrentScriptSourceFilePath(__file__);
String __base__ = __file__.PathExtractDirectory(0);

/**
 * Load and add the file `filename`, the name will be the `filename` without
 * the extension.
 *
 * This is dynamic only for the current session. If GMS is restarted, using 
 * this will create errors except if the plugins folder does not contain the 
 * required files (delete `%LOCALAPPDATA%\Gatan\Plugins\` before starting).
 *
 * @param filename The filename (or path) relative to the path of this file
 * @param name The internal name to register the script with
 */
void require(String filename, String name){
    // AddScriptFileToPackage(
    //    <file_path>, 
    //    <packageName: filename of .gtk file in plugins>, 
    //    <packageLevel: load order [0..3]>,
    //    <command_name: id/name of the libary/command>,
    //    <menu_name: name of the menu, ignored if isLibrary=1>
    //    <sub_menu_name: name of the submenu, ignored if isLibrary=1>,
    //    <isLibrary: wheter to add as library (1) or as menu item (0)>
    // )
    AddScriptFileToPackage(__base__.PathConcatenate(filename), "__require_main_" + name, 3, name, "", "", 1);
}

/**
 * Require the file `filename` with the basename of the `filename` as the name.
 *
 * @see require(String filename, String name);
 *
 * @param filename The filename (or path) relative to the path of this file
 */
void require(String filename){
    require(filename, PathExtractBaseName(filename, 0));
}

void main(){
    // add libaries
    require("string-lib.s");

    // add main file
    require("program.s");
}

main();
```

## The gatan-start.bat

This file can be used to start GMS. It will always delete the libaries defined by the `require()` function.

```bat
@echo off

rem
rem File: start-gatan.bat
rem ---------------------

echo Deleting GMS cached libaries...

SET plugins_path=%LOCALAPPDATA%\Gatan\Plugins\
SET gms_path=%PROGRAMFILES%\Gatan\DigitalMicrograph.exe

if exist %plugins_path% (
    echo Deleting all .gtk files in %plugins_path%...
    del %plugins_path%__require_main_*.gtk /F /Q
    del %plugins_path%__require_main_*.gt1 /F /Q
    del %plugins_path%__require_main_*.gt2 /F /Q
    del %plugins_path%__require_main_*.gt3 /F /Q

    if exist "%gms_path%" (
        echo Starting GMS
        start "" "%gms_path%"
    ) else (
        echo GMS path %gms_path% does not exist.
        pause
    )
) else (
    echo Plugins path %plugins_path% does not exist.
    pause
)
```
