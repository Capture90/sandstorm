import os
import shutil
import transliterate
import sys

# Function to normalize filenames
def normalize_filename(filename):
    transliterated = transliterate.translit(filename, reversed=True)
    normalized = ''.join(c if c.isalnum() else '_' for c in transliterated)
    normalized = normalized.lstrip('_')
    return normalized


def move_file(file_path, category, normalized_filename):
    category_folder = category_dirs[category]

    try:
        os.makedirs(category_folder, exist_ok=True)
        shutil.move(file_path, os.path.join(category_folder, normalized_filename))
    except Exception as e:
        print(f"Error organizing file {category_folder}: {e}")

def images(file_path, normalized_filename):
    move_file(file_path, 'images', normalize_filename)

def videos(file_path, normalized_filename):
    move_file(file_path, 'videos', normalize_filename)

def documents(file_path, normalized_filename):
    move_file(file_path, 'documents', normalize_filename)

def audio(file_path, normalized_filename):
    move_file(file_path, 'audio', normalize_filename)

def archives(file_path, normalized_filename):
    move_file(file_path, 'archives', normalize_filename)

def extract_and_move_archives(archive_path, normalized_filename):
    category_folder = category_dirs['archive']

    try:
        os.makedirs(category_folder, exist_ok=True)
        with shutil.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(category_folder)
        os.remove(archive_path)
    except:
        print(f'Error while organizing archives')

def get_category(extension):
    for category, extensions in categories.items():
        if extension.lower() in extensions:
            return category
    return 'unknown'

# Function to organize files in a folder
def organize_files(folder_path):


    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if it's a file
        if os.path.isfile(file_path):
            normalized_filename = normalize_filename(filename)
            extension = os.path.splitext(filename)[1]
            category = get_category(extension)
            handler_function = globals().get(category, None)
            if handler_function:
                handler_function(file_path, normalized_filename)
            else:
                print(f'No category for a desired function')



        # Check if it's a directory and skip it
        elif os.path.isdir(file_path):
            print(f"Skipping directory: {file_path}")

        # Skip processing if it's neither a file nor a directory
        else:
            print(f"Skipping non-file, non-directory item: {file_path}")


# Function to recursively organize files in a directory and its subdirectories
def organize_directory_recursively(folder_path):
    print(f"Current folder path: {folder_path}")
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                organize_files(file_path)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python organize_files_final.py <folder_path>")
        sys.exit(1)

    folder_path = os.path.abspath(sys.argv[0])
    print(f"Folder path provided: {folder_path}")

    try:
        # Define categories
        categories = {
            'images': ('.jpeg', '.jpg', '.png', '.svg'),
            'videos': ('.avi', '.mp4', '.mov', '.mkv'),
            'documents': ('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
            'audio': ('.mp3', '.ogg', '.wav', '.amr'),
            'archives': ('.zip', '.gz', '.tar', 'rar'),
            'unknown': (),
        }

        # Initialize dictionaries for categories
        category_dirs = {category: os.path.join(folder_path, category) for category in categories}

        organize_directory_recursively(folder_path)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
