# Production Search Tool test version 0.7

## General About
Production Search Tool is a Python-based application for searching files using a series of order numbers, a string that represents a portion of the file name, and listing the matches in an easy to read and decipher tree view. From this tree view you open files, copy information about them, 

## Special Note

With great power comes great responsibility- be sure to double check your work before moving more than one file to canceled. 

## Features

- Search for multiple order numbers at once by providing a comma-separated list (e.g - number1, number2, number3, number4, etc)
- Search across multiple network folders
- Display the search results in a clear and organized table
- Efficient search using multithreading
- One click move EVMs to specific folders 

## Installation 

Copy the entire dist folder to wherever you would like

## Usage

1. Enter a comma-separated list of order numbers you want to search for in the "Order Numbers" input field.
2. Click the "Search" button to start the search. The search results will be displayed in the table.
3. Search resutls with multiple results will be grouped together under one parent row, these are marked with a "+", and you double click to open them
4. Use sidebar buttons to move selected evms to destination folders, ctrl +click to get move multiple order numbers with one command
5. If you move a file somewhere you don't want to, click undo (as long as the file is still in that folder). 
6. Undo history is saved until you close the application so *do not spam click this* or it will undo everything you've done.
7. Files are moved one at a time, you can cancel pending movements by clicking undo, and then click again to undo already completed movements.
8. Action log text box at the bottom will give you a list of evms not found once search is completed
9. Use the settings menu to change theme, as well as adjust basic parameters of the application

## Move Button Destinations and Search Parameters

These are found in the config.json file, you can edit these by either directly editing the text or through the use of the options menu.

## Troubleshooting

If you encounter any issues while running the application, make sure that:

1. You have the necessary permissions to access the network folders.
2. All the required dependencies are present in the `dist` folder.
