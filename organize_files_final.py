import os
import shutil
import transliterate

# Function to normalize filenames
def normalize_filename(filename):
    # Transliterate Cyrillic characters to Latin
    transliterated = transliterate.translit(filename, reversed=True)
    
    # Replace non-alphanumeric characters with underscores
    normalized = ''.join(c if c.isalnum() else '_' for c in transliterated)

    # Strip hyphens from the beginning of the filename
    normalized = normalized.lstrip('_')
    
    return normalized

# Function to organize files in a folder
def organize_files(folder_path):
    # Determine the category based on the file extension
    def get_category(extension):
        for category, extensions in categories.items():
            if extension.lower() in extensions:
                return category
        return 'unknown'

    # Iterate through the files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if it's a file or a directory
        if os.path.isfile(file_path):
            # Normalize the filename (you can implement this as needed)
            normalized_filename = normalize_filename(filename)

            # Determine the category based on the file extension
            extension = os.path.splitext(filename)[1]
            category = get_category(extension)

            # Create the category directory if it doesn't exist
            category_dir = category_dirs[category]
            os.makedirs(category_dir, exist_ok=True)

            # Move the file to its respective category directory
            shutil.move(file_path, os.path.join(category_dir, normalized_filename))
            
            # Remove the empty folder
            parent_dir = os.path.dirname(file_path)
            if not os.listdir(parent_dir):
                os.rmdir(parent_dir)

# Function to recursively organize files in a directory and its subdirectories
def organize_directory_recursively(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            organize_files(file_path)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Usage: python organize_files.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]

    # Define categories
    categories = {
        'images': ('.jpeg', '.jpg', '.png', '.svg'),
        'videos': ('.avi', '.mp4', '.mov', '.mkv'),
        'documents': ('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
        'audio': ('.mp3', '.ogg', '.wav', '.amr'),
        'archives': ('.zip', '.gz', '.tar', 'rar'),
        'unknown': (),  # For unknown extensions
    }

    # Initialize dictionaries for categories
    category_dirs = {category: os.path.join(folder_path, category) for category in categories}

    organize_directory_recursively(folder_path)
