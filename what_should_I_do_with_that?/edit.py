import re
import sys

def update_image_references(filename, folder_name):
    try:
        # Read the file
        with open(filename, 'r') as file:
            content = file.read()
        
        # Define the replacement pattern
        updated_content = re.sub(
            r'!\[\[Pasted image (\d+\.png)\]\]',
            rf'![/home/user/myblog/_site](/assets/img/posts/{folder_name}/Pasted image \1)',
            content
        )
        
        # Write the updated content back to the file
        with open(filename, 'w') as file:
            file.write(updated_content)
        
        print(f"File '{filename}' updated successfully with folder '{folder_name}'.")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Check if the correct number of arguments is provided
if len(sys.argv) != 3:
    print("Usage: python script.py <filename> <folder_name>")
else:
    # Get the filename and folder name from the arguments
    input_file = sys.argv[1]
    input_folder = sys.argv[2]
    update_image_references(input_file, input_folder)

