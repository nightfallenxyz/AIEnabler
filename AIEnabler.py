import os
import tkinter as tk
from tkinter import filedialog
from lxml import etree

def action_prompt():
    print("Select an option:")
    print("1. Enable AI")
    print("2. Undo AI")
    choice = input("Enter 1 or 2: ").strip()
    
    if choice not in ['1', '2']:
        print("Invalid input. Please enter 1 or 2.")
        return action_prompt()
    
    return choice

def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    file_path = filedialog.askopenfilename(
        title="Select a .plist file",
        filetypes=(("plist files", "*.plist"), ("all files", "*.*"))
    )

    if not file_path:
        print("No file selected. Exiting.")
        exit()

    return file_path

def modify_plist(file_path, action_choice):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    destination_folder = os.path.join(script_dir, 'tweak', 'files')
    original_file_path = os.path.join(destination_folder, 'plistbackup')
    normal_file_path = os.path.join(destination_folder, 'com.apple.MobileGestalt.plist')
    noai_file_path = os.path.join(destination_folder, 'noai.plist')

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    if action_choice == '1':
        # Enable AI
        if os.path.exists(normal_file_path):
            os.rename(normal_file_path, original_file_path)
            print(f"Original file backed up as '{original_file_path}'")

        # Load and modify plist
        tree = etree.parse(file_path)
        root = tree.getroot()
        cache_extra_found = False
        key_found = False
        
        # Namespaces are used in plist files, so we need to handle them
        ns = {'': 'http://www.apple.com/DTDs/PropertyList-1.0.dtd'}

        # Iterate through the XML elements to find and modify
        for elem in root.iter():
            if elem.tag == 'key' and elem.text == 'CacheExtra':
                cache_extra_found = True
                # Create and insert the new key-value pair
                for next_elem in elem.itersiblings():
                    if next_elem.tag == 'dict':
                        # Add new keys and values
                        new_key = etree.Element('key')
                        new_key.text = 'A62OafQ85EJAiiqKn4agtg'
                        new_value = etree.Element('integer')
                        new_value.text = '1'
                        next_elem.append(new_key)
                        next_elem.append(new_value)
                        print("Added <key>A62OafQ85EJAiiqKn4agtg</key> with value <integer>1</integer> under <key>CacheExtra</key>")
                        break

            if elem.tag == 'key' and elem.text == 'h9jDsbgj7xIVeIQ8S3/X3Q':
                key_found = True
                next_elem = elem.getnext()
                if next_elem is not None and next_elem.tag == 'string':
                    next_elem.text = 'iPhone16,2'
                    print("Updated <key>h9jDsbgj7xIVeIQ8S3/X3Q</key> to 'iPhone16,2'")

        if not cache_extra_found:
            # If 'CacheExtra' is not found, add it with the required elements
            cache_extra_elem = etree.Element('key')
            cache_extra_elem.text = 'CacheExtra'
            dict_elem = etree.Element('dict')
            cache_extra_elem.append(dict_elem)
            root.append(cache_extra_elem)

            # Add required key-value pairs
            new_key = etree.Element('key')
            new_key.text = 'A62OafQ85EJAiiqKn4agtg'
            new_value = etree.Element('integer')
            new_value.text = '1'
            dict_elem.append(new_key)
            dict_elem.append(new_value)
            print("Added <key>CacheExtra</key> with <key>A62OafQ85EJAiiqKn4agtg</key> and <integer>1</integer>")

        if not key_found:
            # Add the 'h9jDsbgj7xIVeIQ8S3/X3Q' key if not found
            new_key = etree.Element('key')
            new_key.text = 'h9jDsbgj7xIVeIQ8S3/X3Q'
            new_value = etree.Element('string')
            new_value.text = 'iPhone16,2'
            root.append(new_key)
            root.append(new_value)
            print("Added <key>h9jDsbgj7xIVeIQ8S3/X3Q</key> with value 'iPhone16,2'")

        tree.write(file_path, xml_declaration=True, encoding='utf-8')

        # Rename modified file and copy it
        os.rename(file_path, normal_file_path)
        print(f"File copied and renamed to '{normal_file_path}'")

        # Create a copy named noai.plist
        with open(normal_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        with open(noai_file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Modified file saved as '{noai_file_path}'")

    elif action_choice == '2':
        # Undo AI
        if os.path.exists(normal_file_path):
            os.remove(normal_file_path)
            print(f"Deleted existing file '{normal_file_path}'")

        if os.path.exists(noai_file_path):
            os.rename(noai_file_path, normal_file_path)
            print(f"Replaced with 'noai.plist' as '{normal_file_path}'")
        else:
            print(f"'noai.plist' not found in '{destination_folder}'. Prompting for file selection.")

            # Prompt for file selection if 'noai.plist' doesn't exist
            plist_file = select_file()
            if plist_file:
                # Use the selected file to undo AI
                os.rename(plist_file, noai_file_path)
                print(f"Selected file '{plist_file}' saved as '{noai_file_path}'")
                os.rename(noai_file_path, normal_file_path)
                print(f"Replaced with selected file as '{normal_file_path}'")
            else:
                print("No file selected. Exiting.")

def main():
    action_choice = action_prompt()
    
    plist_file = None
    if action_choice == '1':
        plist_file = select_file()

    modify_plist(plist_file, action_choice)

if __name__ == "__main__":
    main()
