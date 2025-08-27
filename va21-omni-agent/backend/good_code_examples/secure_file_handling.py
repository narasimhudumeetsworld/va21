"""
This is an example of secure and robust file handling in Python.
It uses a try-except-finally block to ensure that file resources are
always closed, even if errors occur during processing. It also handles
potential exceptions gracefully.
"""

def read_and_process_file(filepath):
    """
    Reads a file, processes its content, and ensures it's closed properly.

    Args:
        filepath (str): The path to the file to be read.

    Returns:
        str: The processed content of the file, or an error message.
    """
    file_handle = None
    try:
        file_handle = open(filepath, 'r', encoding='utf-8')
        content = file_handle.read()
        # In a real scenario, more processing would happen here.
        processed_content = content.upper()
        return processed_content
    except FileNotFoundError:
        return f"Error: The file at {filepath} was not found."
    except IOError as e:
        return f"Error: An I/O error occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
    finally:
        if file_handle:
            file_handle.close()
            print(f"File '{filepath}' closed successfully.")
