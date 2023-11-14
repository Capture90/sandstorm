import os
import shutil
import transliterate
import sys


def normalize_filename(filename):

    transliterated = transliterate.translit(filename, reversed=True)
    

    normalized = ''.join(c if c.isalnum() else '_' for c in transliterated)

    return normalized


def organize_files(file_path):

    categories = {
        'images': ('.jpeg', '.jpg', '.png', '.svg'),
        'videos': ('.avi', '.mp4', '.mov', '.mkv'),
        'documents': ('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
        'audio': ('.mp3', '.ogg', '.wav', '.amr'),
        'archives': ('.zip', '.gz', '.tar'),
    }


    category_dirs = {category: os.path.join(file_path, category) for category in categories}
    

    for category_dir in category_dirs.values():
        os.makedirs(category_dir, exist_ok=True)


    for filename in os.listdir(file_path):
        file_path = os.path.join(file_path, filename)
        

        if os.path.isdir(file_path):
            continue


        normalized_filename = normalize_filename(filename)


        extension = os.path.splitext(filename)[1]
        for category, extensions in categories.items():
            if extension.lower() in extensions:
                category_dir = category_dirs[category]

                shutil.move(file_path, os.path.join(category_dir, normalized_filename))
                break
        else:

            pass


def organize_directory_recursively(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            organize_files(file_path)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python organize_files.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    organize_directory_recursively(folder_path)
