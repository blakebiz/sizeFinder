import os
import time


def scan_dir(directory: str,
             ignore: list[str] = None,
             local_dir: bool = True,
             local_ignore: bool = True,
             print_errors: bool = True):
    """
    :param directory: The directory to begin searching in
    :param ignore: list of string file paths to ignore while searching
    :param local_dir: whether or not the directory is local to the directory this script is running in
    :param local_ignore: whether or not the paths in the ignore list are local or absolute paths
    :param print_errors: whether or not to display errors that occur such as permission denied
    :return:
    """
    denied = []

    def helper(_directory, _ignore, _local, _start_dir):
        total = 0
        files = []
        try:
            with os.scandir(_directory) as scan:
                for path in scan:
                    if path.is_file() and not path.is_symlink():
                        if _local:
                            if path.path.replace(f'{_start_dir}/', '') not in ignore:
                                files.append(path.path)
                                total += path.stat().st_size
                        elif path.path not in ignore:
                            files.append(path.path)
                            total += path.stat().st_size

                    elif path.is_dir() and not path.is_symlink() and not any(map(path.path.startswith, denied)):
                        if _local:
                            if path.path.replace(f'{_start_dir}/', '') not in ignore:
                                total += helper(path.path, _ignore, _local, _start_dir)
                        elif path.path not in ignore:
                            total += helper(path.path, _ignore, _local, _start_dir)
            return total
        except PermissionError:
            denied.append(_directory)
            if print_errors:
                print(f'permission denied for folder "{_directory}"')
            return total

    return helper(directory, ignore, local_ignore, directory)


def format_size(_bytes):
    if _bytes < 1000:
        return f'{_bytes} Bytes'
    elif 10**3 <= _bytes < 10**6:
        return f'{_bytes/(10**3):.2f} KB'
    elif 10**6 <= _bytes < 10**9:
        return f'{_bytes/(10**6):.2f} MB'
    elif 10**9 <= _bytes < 10**12:
        return f'{_bytes/(10**9):.2f} GB'
    else:
        return f'{_bytes/10**12:.2f} TB'


def analyze_dir(directory: str,
                ignore: list[str] = None,
                local_dir: bool = True,
                local_ignore: bool = True,
                print_errors: bool = True,
                reversed: bool = True):
    """
    :param directory: The directory to begin searching in
    :param ignore: list of string file paths to ignore while searching
    :param local_dir: whether or not the directory is local to the directory this script is running in
    :param local_ignore: whether or not the paths in the ignore list are local or absolute paths
    :param print_errors: whether or not to display errors that occur such as permission denied
    :param reversed: whether or not to reverse the results. True = high to low, False = low to high
    :return:
    """
    ignore = ignore or ['/proc']
    if '/proc' not in ignore:
        ignore.append('/proc')
    directory = directory.replace('\\', '/')
    if local_dir:
        if directory.startswith('/'):
            directory = '.' + directory
        else:
            directory = './' + directory
    for index in range(len(ignore)):
        ignore[index] = ignore[index].replace('\\', '/')

    results = dict()

    for path in os.scandir(directory):
        if path.is_dir() and path.path not in ignore:
            results[path.name] = scan_dir(path.path, ignore, local_dir, local_ignore, print_errors)

    return list(sorted(results.items(), key=lambda x: x[1], reverse=reversed))


def pprint(tup):
    for key, value in tup:
        print(f'{repr(key)}: {format_size(value)}')


def main():
    start = time.perf_counter()
    result = analyze_dir('/', local_dir=False, print_errors=False, reversed=False)
    total = 0
    for item in result:
        total += item[1]
    pprint(result)
    print('\ntotal:', format_size(total))
    print(f'\ntotal runtime: {time.perf_counter() - start} seconds')


if __name__ == '__main__':
    main()

