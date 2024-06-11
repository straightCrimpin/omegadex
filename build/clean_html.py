import os

def delete_files_without_extension(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            # Check if the file has an extension
            if '.' not in file:
                os.remove(os.path.join(root, file))

# Usage
delete_files_without_extension('../Data')