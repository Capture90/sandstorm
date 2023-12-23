import os
import sys
import re
import shutil
import pathlib
import tempfile
import datetime
import collections

RESULTS_FOLDERS = ("images", "videos", "documents", "audio", "archives")

def normalize(file_name):
    map = {
        ord('А'): 'A',
        ord('а'): 'a',
        ord('Б'): 'B',
        ord('б'): 'b',
        ord('В'): 'V',
        ord('в'): 'v',
        ord('Г'): 'H',
        ord('г'): 'h',
        ord('Ґ'): 'G',
        ord('ґ'): 'g',
        ord('Д'): 'D',
        ord('д'): 'd',
        ord('Е'): 'E',
        ord('е'): 'e',
        ord('Є'): 'Ye',
        ord('є'): 'ie',
        ord('Ж'): 'Zh',
        ord('ж'): 'zh',
        ord('З'): 'Z',
        ord('з'): 'z',
        ord('И'): 'Y',
        ord('и'): 'y',
        ord('І'): 'I',
        ord('і'): 'i',
        ord('Ї'): 'Yi',
        ord('ї'): 'i',
        ord('Й'): 'Y',
        ord('й'): 'i',
        ord('К'): 'K',
        ord('к'): 'k',
        ord('Л'): 'L',
        ord('л'): 'l',
        ord('М'): 'M',
        ord('м'): 'm',
        ord('Н'): 'N',
        ord('н'): 'n',
        ord('О'): 'O',
        ord('о'): 'o',
        ord('П'): 'P',
        ord('п'): 'p',
        ord('Р'): 'R',
        ord('р'): 'r',
        ord('С'): 'S',
        ord('с'): 's',
        ord('Т'): 'T',
        ord('т'): 't',
        ord('У'): 'U',
        ord('у'): 'u',
        ord('Ф'): 'F',
        ord('ф'): 'f',
        ord('Х'): 'Kh',
        ord('х'): 'kh',
        ord('Ц'): 'Ts',
        ord('ц'): 'ts',
        ord('Ч'): 'Ch',
        ord('ч'): 'ch',
        ord('Ш'): 'Sh',
        ord('ш'): 'sh',
        ord('Щ'): 'Shch',
        ord('щ'): 'shch',
        ord('Ю'): 'Yu',
        ord('ю'): 'iu',
        ord('Я'): 'Ya',
        ord('я'): 'ia'
    }

    file_name = re.sub(r'[^a-zA-Z0-9А-Яа-яЁёҐґЄєІіЇїЙй]', '_', file_name)

    return str(file_name).translate(map)

####
def is_file_corrupted(file_path):
    try:
        # Attempt to read the file
        with open(file_path, 'rb') as file:
            file_content = file.read()
        return False  # File is not corrupted
    except Exception:
        return True  # File is corrupted

def process_archive(result_path, element):
    result_path /= "archives"

    archive_folder = result_path / f"{normalize(element.stem)}"
    archive_folder.mkdir(parents=True, exist_ok=True)

    try:
        shutil.unpack_archive(
            str(element), str(archive_folder), element.suffix[1:].lower()
        )

        # Check for corrupted files and delete them
        for file_name in os.listdir(archive_folder):
            file_path = os.path.join(archive_folder, file_name)

            if is_file_corrupted(file_path):
                print(f"Corrupted file detected: {file_name}. Deleting.")
                os.remove(file_path)

    except Exception as e:
        print(f"Error while processing archive {element}: {e}")
####

def process_dir(result_path, element, extensions_info):
    res = False

    if element.name not in RESULTS_FOLDERS:
        folder_res = diver(result_path, element, extensions_info)
        if folder_res is False and element.exists():
            try:
                element.rmdir()
            except OSError:
                shutil.rmtree(str(element), ignore_errors=True)

        res |= folder_res

    return res


def process_file(result_path, element, extensions_info):

    table = (
        ('JPEG', 'PNG', 'JPG', 'SVG'),
        ('AVI', 'MP4', 'MOV', 'MKV'),
        ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
        ('MP3', 'OGG', 'WAV', 'AMR'),
        ('ZIP', 'GZ', 'TAR', 'RAR')
    )

    suffixes_dict = {
        table[i][j]: RESULTS_FOLDERS[i]
        for i in range(len(table))
        for j in range(len(table[i]))
    }

    suffix = element.suffix[1:].upper()

    known = suffixes_dict.get(suffix) is not None

    extensions_info["known" if known else "unknown"].add (suffix)

    if known:
        dest_folder = suffixes_dict[suffix]
        result_path /= dest_folder

        if not result_path.is_dir():
            result_path.mkdir()

        if dest_folder == "archives":
            result_path /= f"{normalize(element.stem)}"

            shutil.unpack_archive(
                str(element), str(result_path), element.suffix[1:].lower()
            )
        else:
            result_path /= f"{normalize(element.stem)}{element.suffix}"

            shutil.copy(str(element), str(result_path))

    else:
        other_folder = result_path / "other"
        other_folder.mkdir(parents=True, exist_ok=True)

        result_path_other = other_folder / f"{normalize(element.stem)}{element.suffix}"

        shutil.copy(str(element), str(result_path_other))

    return True


def diver(result_path, folder_path, extensions_info):
    res = False


    for folder in RESULTS_FOLDERS:
        (result_path / folder).mkdir(parents=True, exist_ok=True)

    if not any(folder_path.iterdir()):
        folder_path.rmdir() #THIS is added
        return res

    for element in folder_path.iterdir():
        print(f"Processing element: {element}")
        processor = process_dir if element.is_dir() else process_file
        res |= processor(result_path, element, extensions_info)

    return res


def post_processor(results_path, extensions_info):
        print(f"Known extensions: {extensions_info['known']}")
        if len(extensions_info['unknown']):
           print(f"Unknown extensions: {extensions_info['unknown']}")

        for folder in results_path.iterdir():
            print(f"{folder.name}:")
            for item in folder.iterdir():
               print(f"\t{item.name}")


def sorter(folder_platform_path):
    extensions_info = collections.defaultdict(set)
    folder_path = pathlib.Path(folder_platform_path)

    if not folder_path.is_dir():
        raise RuntimeError("Error: no such directory")

    with tempfile.TemporaryDirectory() as tmp_platform_path:
        print(f"Temporary directory path: {tmp_platform_path}")
        tmp_path = pathlib.Path(tmp_platform_path)

        if diver(tmp_path, folder_path, extensions_info) is False:
            raise RuntimeError("It's an empty directory")

        os.makedirs("results", exist_ok=True)

        results_path = pathlib.Path(f"results/result_{datetime.datetime.now().strftime('%d.%m.%y_%H_%M')}")

        try:
            shutil.copytree(
                str(tmp_path),
                str(results_path)
            )


            normalized_results_name = normalize(results_path.name)

            normalized_results_path = results_path.parent / normalized_results_name

            print(f"Results path after normalization: {normalized_results_path}")


            results_path.rename(normalized_results_path)

            # Iterate over items in the normalized_results_path
            for item in normalized_results_path.iterdir():
                new_name = normalize(item.name)
                item.rename(normalized_results_path / new_name)

            # Check if the element is a directory and its name is "archives"
                if item.is_dir() and item.name == "archives":
                    # Iterate over files in the "archives" directory and process them
                    for archive_file in item.iterdir():
                        process_archive(normalized_results_path, archive_file)


            post_processor(normalized_results_path, extensions_info)

        except Exception as e:
            print(f"Error during copytree or post-processing: {e}")


            results_path = pathlib.Path(normalize(str(results_path)))
            print(f"Results path: {results_path}")
            print("Contents of results path:")
            for item in results_path.iterdir():
                print(item)
                new_name = normalize(item.name)
                item.rename(results_path / new_name)

            post_processor(results_path, extensions_info)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError(f"usage: {sys.argv[0]} folder_platform_path")

    sorter(sys.argv[1])