def import_markdown_as_string(filename):
    """
    Reads the contents of a Markdown file into a string.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            markdown_string = file.read()
        return markdown_string
    except FileNotFoundError:
        return f"Error: The file '{filename}' was not found."
    except Exception as e:
        return f"An error occurred: {e}"
