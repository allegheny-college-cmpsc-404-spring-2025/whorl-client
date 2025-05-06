# Setting up Whorl-Client

## Prerequisites

### Clone the client repository

```sh
git clone git@github.com:allegheny-college-cmpsc-404-spring-2025/whorl-client.git
```

### Setup a virtual environment

Here you work to utilize `venv` which is short for virtual environment specific for your client.

Create a virtual environment in the root of the `whorl-client` repository by running the command below.

```sh
python -m venv .venv
```

Then activate your virtual environment

```sh
source .venv/bin/activate
```

PSA - your virtual environment will stay open so when finished run command `deactivate` to close it.

### Development Install

Once your virtual environment is set up, perform a development install by running the command below

```sh
python -m pip install -e .
```

### Install Node.js and Manage Environment Variables

The client repository requires `.env` files using `dotenv.org` to manage our files. You will need to have Node.js installed on your machine, which you can download using the npx command. You can follow the link below to download Node.js to your machine.

[Download Node.js](https://nodejs.org/en/download)

### Pull Latest Changes

Lastly, pull from the `whorl-client` repository again if you have cloned it and cd to the main folder and run the command:

```sh
npx dotenv-vault@latest pull
```

## Testing whorl-client locally

### Requirements

1. Clone the Repository:

    ```sh
    git clone https://github.com/whorlassignments/starship-assignment.git
    ```

2. Set Up Your Environment:

    Before running the following commands, ensure that the virtual environment for `whorl-client` is activated. Navigate to the `whorl-client` repository and activate the virtual environment:

    ```sh
    cd path/to/whorl-client
    source .venv/bin/activate
    ```

    Then, move to the starship-assignment directory:

    ```sh
    cd path/to/starship-assignment
    ```

### Collect Required Items

You will need to move between directories ("rooms") to collect specific Python files, which will act as "items" in your inventory.

Move from "room" to "room" and use the `get` command to add the necessary Python files to your inventory. Here's what you need to collect:

- 3 Copies of `Sprocket.py`
- 1 Copy of `FluxCapacitor.py`
- 1 Copy of `ThermoCube.py`

To collect these items, navigate to the respective folder and type:

```sh
get FILENAME.py
```

Use the `inventory` command to check your collected items.

### Start the Engine

Once you have all the required files in your inventory, navigate to the `engine-room` directory and run the engine:

```sh
./Engine
```

### Verify the Engine Status

If the engine starts successfully, proceed to the `bridge` directory and run:

```sh
./Controls
```

This should confirm that the engine has started.

### Example Walkthrough

- **Navigate to Rooms:** Use `cd` to move between directories and collect the required files.
- **Check Inventory:** Periodically verify your inventory to ensure you have all the necessary items.
- **Start and Verify:** Follow the steps above to start the engine and confirm it through the controls.

### Notes

- Each file must be explicitly collected by typing `get FILENAME.py` in the appropriate directory.
- The sequence of operations matters: ensure you have all items before starting the engine.

By following these steps, you can confirm that the whorl-client functions as intended!

## Commands

This section explains the function of different commands along with their inputs.

| **Command**   | **Description**                                                                                                                                              | **Usage Example**                |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| `who`         | Displays who is active in the world.                                                                                                                         | `who`                             |
| `talk`        | Talks to an object and allows the user to access an OpenAI chatbot.                                                                                          | `talk`                            |
| `look`        | Takes the name of an object as input and returns a description of what the object looks like.                                                                | `look ObjectName`                 |
| `presence`    | Indicates that the user is in the file system.                                                                                                               | `presence`                        |
| `inventory`   | Displays all the items in the user's inventory. If there are no items, the table will appear blank.                                                          | `inventory`                       |
| `get`         | Adds an object to the inventory.                                                                                                                             | `get File.py`                     |
| `use`         | Checks if an inventory item has a use.                                                                                                                       | `use ItemInInventory`             |
| `give`        | Transfers an object to another user.                                                                                                                         | `give ItemInInventory username`   |
| `info`        | Provides information about an item in your inventory. This command can only be used for items already in the inventory.                                      | `info ItemInInventory`            |
| `drop`        | Removes an item from the inventory and outputs a dictionary to confirm its functionality.                                                                    | `drop ItemInInventory`            |

## Behind the Scenes

This section explains how each API works.

## Climate API

The climate API is run using the command climate. The climate API uses api_url and api_port to get a dictionary of information about the climate but this file mainly just takes that dictionary and manipulates it. First, there is a function that will change the temperature value from Kelvin to Celsius or Fahrenheit. Then the code makes a table using the Rich Python program.

## Persona API

This API allows a user to talk to an AI chat bot and to look at objects. Looking at an object calls a file with the object information. If there is nothing the Look.py program will return a string indicating that there is no information.

## Narrator API

Narrator API includes four different files: Checkpoint.py, Narrator.py, Path.py, and Question.py. Narrator pulls its information from a .yml in order to know what scene the user is in. When a user `cd`s into different folders flags will be dropped. This allows the grader for the assignment to see if the user has completed the required assignment and cded into all the different folders. Checkpoint.py is the file where flags are dropped. Narrator.py accesses and reads the yaml file. Path.py changes scenes for the user. Question.py interacts with the user and gives them different questions to answer.

## Omnipresence API

This API allows the user to interact with itself and know who is using the program. Omnipresence includes the commands who and presence. who alerts the users to who is using the program and it gives an output like: Users active in /home/student/whorl-client: 🧙 student. While presence won’t give an output but alerts the computer to the users location. `who` calls the omnipresence file and gets the user information and returns that to the user. This shows the location of the user at every turn they take. Presence automatically reports where people are.

## Inventory API

This API has the most commands out of any of the other API folders. This API allows the user to access their inventory and with the different commands they can add to the inventory, see the info of their objects, remove items, use the items and give items away. Each of these actions are defined in a python file committed to that action.

### Using a Backpack

After picking up a back for example by typing `get backpack.py`

type: `use backpack`

```bash
To add an item: Type 'add' in the terminal
To drop an item: Type 'drop' in the terminal
To use an item: Type 'use' in the terminal
    Input: <Type your response here>
```

After typing add, drop or use. When using add type a valid Items file to add it to the pack
Otherwise just type an item that is in the packs inventory to either drop or use it depending on what was specified.




