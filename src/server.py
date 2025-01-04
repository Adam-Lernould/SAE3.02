import socket
import threading
import os
import glob
import PyPDF2
import openpyxl
import re
from bs4 import BeautifulSoup
import logging

# Configure logging for debugging purposes
logging.basicConfig(
    filename='server.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define constants
HOST = '127.0.0.1'  # Server's IP address
PORT = 12345        # Server's port number
ENDING_MSG = "q"    # Message indicating the client wants to terminate the connection
FOLDERS = {         # Mapping of file extensions to their respective directories
    ".txt": "data/txt/",
    ".pdf": "data/pdf/",
    ".html": "data/html/",
    ".xlsx": "data/excel/"
}

# Helper Functions

def parse_keywords(keyword):
    """
    Parses the input keyword string to identify logical operators (AND/OR) or regex patterns.
    
    Args:
        keyword (str): The keyword string input by the user.
        
    Returns:
        tuple: A tuple containing a list of keywords, the operator used ('OR', 'AND', or 'SINGLE'),
               and a boolean indicating if the keyword is a regex pattern.
    """
    # Check for 'OR' operator
    if " OR " in keyword:
        return [kw.strip() for kw in keyword.split(" OR ")], "OR", False
    # Check for 'AND' operator
    elif " AND " in keyword:
        return [kw.strip() for kw in keyword.split(" AND ")], "AND", False

    # If no logical operator, check if it's a regex
    try:
        re.compile(keyword)
        is_regex = True
    except re.error:
        is_regex = False

    return [keyword.strip()], "SINGLE", is_regex

def matches_with_operator(line, keywords, operator, is_regex):
    """
    Determines if a given line matches the search criteria based on keywords and the operator.
    
    Args:
        line (str): The line of text to be evaluated.
        keywords (list): List of keywords to search for.
        operator (str): The logical operator ('OR', 'AND', or 'SINGLE').
        is_regex (bool): Indicates whether the keywords should be treated as regex patterns.
        
    Returns:
        bool: True if the line matches the search criteria, False otherwise.
    """
    if operator == "OR":
        # At least one keyword must match
        return any(re.search(kw, line) if is_regex else kw in line for kw in keywords)
    elif operator == "AND":
        # All keywords must match
        return all(re.search(kw, line) if is_regex else kw in line for kw in keywords)
    elif operator == "SINGLE":
        # Only one keyword to match
        return re.search(keywords[0], line) if is_regex else keywords[0] in line
    return False

# Search Functions for Different File Types

def search_txt(file_path, keyword):
    """
    Searches for keywords within a TXT file.
    
    Args:
        file_path (str): The path to the TXT file.
        keyword (str): The keyword or regex pattern to search for.
        
    Returns:
        list: A list of formatted strings indicating where matches were found.
    """
    results = []
    count = 1
    keywords, operator, is_regex = parse_keywords(keyword)

    logging.debug(f"Searching in file: {file_path} with keywords={keywords}, operator={operator}, is_regex={is_regex}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line_num, line in enumerate(lines, start=1):
                if matches_with_operator(line, keywords, operator, is_regex):
                    logging.debug(f"Match found in {file_path} on line {line_num}: {line.strip()}")
                    results.append(f"{count} - {os.path.basename(file_path)} - Line {line_num}: {line.strip()}")
                    count += 1
    except Exception as e:
        logging.error(f"Error reading TXT file {file_path}: {e}")

    if not results:
        logging.debug(f"No matches found in file: {file_path}")
    return results

def search_pdf(file_path, keyword):
    """
    Searches for keywords within a PDF file.
    
    Args:
        file_path (str): The path to the PDF file.
        keyword (str): The keyword or regex pattern to search for.
        
    Returns:
        list: A list of formatted strings indicating where matches were found.
    """
    results = []
    count = 1
    keywords, operator, is_regex = parse_keywords(keyword)

    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split('\n')
                for line_num, line in enumerate(lines, start=1):
                    if matches_with_operator(line, keywords, operator, is_regex):
                        results.append(f"{count} - {os.path.basename(file_path)} - Page {page_num}, Line {line_num}: {line.strip()}")
                        count += 1
    except Exception as e:
        logging.error(f"Error reading PDF file {file_path}: {e}")

    return results

def search_html(file_path, keyword):
    """
    Searches for keywords within an HTML file.
    
    Args:
        file_path (str): The path to the HTML file.
        keyword (str): The keyword or regex pattern to search for.
        
    Returns:
        list: A list of formatted strings indicating where matches were found.
    """
    results = []
    count = 1
    keywords, operator, is_regex = parse_keywords(keyword)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            for tag in soup.find_all(text=True):
                tag_text = tag.strip()
                if not tag_text:
                    continue
                if matches_with_operator(tag_text, keywords, operator, is_regex):
                    results.append(f"{count} - {os.path.basename(file_path)} - {tag_text}")
                    count += 1
    except Exception as e:
        logging.error(f"Error reading HTML file {file_path}: {e}")

    return results

def search_xlsx(file_path, keyword):
    """
    Searches for keywords within an Excel (XLSX) file.
    
    Args:
        file_path (str): The path to the XLSX file.
        keyword (str): The keyword or regex pattern to search for.
        
    Returns:
        list: A list of formatted strings indicating where matches were found.
    """
    results = []
    count = 1
    keywords, operator, is_regex = parse_keywords(keyword)
    try:
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            for row in sheet.iter_rows():
                for cell in row:
                    cell_value = str(cell.value) if cell.value else ""
                    if matches_with_operator(cell_value, keywords, operator, is_regex):
                        results.append(f"{count} - {os.path.basename(file_path)} - Sheet {sheet_name}, Cell ({cell.row}, {cell.column}): {cell_value}")
                        count += 1
    except Exception as e:
        logging.error(f"Error reading Excel file {file_path}: {e}")

    return results

def search_all_files(folder, extension, keyword):
    """
    Searches for keywords within all files of a specific type in a given folder.
    
    Args:
        folder (str): The directory containing the files.
        extension (str): The file extension to search for.
        keyword (str): The keyword or regex pattern to search for.
        
    Returns:
        list: A list of formatted strings indicating where matches were found or a message if no matches.
    """
    results = []
    for file_path in glob.glob(os.path.join(folder, f"*{extension}")):
        if extension == ".txt":
            results.extend(search_txt(file_path, keyword))
        elif extension == ".pdf":
            results.extend(search_pdf(file_path, keyword))
        elif extension == ".html":
            results.extend(search_html(file_path, keyword))
        elif extension == ".xlsx":
            results.extend(search_xlsx(file_path, keyword))
    return results if results else ["No matches found in any file."]

def search_all_file_types(keyword):
    """
    Searches for keywords across all defined file types.
    
    Args:
        keyword (str): The keyword or regex pattern to search for.
        
    Returns:
        list: A list of formatted strings indicating where matches were found or a message if no matches.
    """
    results = []
    for extension, folder in FOLDERS.items():
        results.extend(search_all_files(folder, extension, keyword))
    return results if results else ["No matches found in any file."]

def handle_search(search_target, keyword, file_extension):
    """
    Handles the search logic based on the target (ALL or specific file) and file extensions provided.
    
    Args:
        search_target (str): "ALL" to search all files or the name of a specific file.
        keyword (str): The keyword or regex pattern to search for.
        file_extension (str): Comma-separated file extensions to include in the search.
        
    Returns:
        list: A list of formatted strings indicating where matches were found or error messages.
    """
    # Split multiple extensions separated by commas
    extensions = [ext.strip() for ext in file_extension.split(',') if ext.strip()] if file_extension else []

    if search_target.upper() == "ALL":
        # If no specific extensions are provided, search across all file types
        if not extensions:
            return search_all_file_types(keyword)
        else:
            # Search only within the specified extensions
            results = []
            for ext in extensions:
                folder = FOLDERS.get(ext)
                if not folder:
                    results.append(f"Unsupported file type: {ext}")
                else:
                    res = search_all_files(folder, ext, keyword)
                    if not res or (len(res) == 1 and res[0].startswith("No matches")):
                        # If no results found for this extension
                        res = [f"No matches found for file type: {ext}."]
                    results.extend(res)
            return results
    else:
        # Search within a specific file. Assume only one extension is provided
        if len(extensions) > 1:
            return ["Error: Multiple extensions provided for a single file search."]
        ext = extensions[0] if extensions else ""
        folder = FOLDERS.get(ext)
        if not folder:
            return [f"Unsupported file type: {ext}"]
        file_path = os.path.join(folder, search_target)
        if os.path.exists(file_path):
            if ext == ".txt":
                return search_txt(file_path, keyword) or ["No matches found."]
            elif ext == ".pdf":
                return search_pdf(file_path, keyword) or ["No matches found."]
            elif ext == ".html":
                return search_html(file_path, keyword) or ["No matches found."]
            elif ext == ".xlsx":
                return search_xlsx(file_path, keyword) or ["No matches found."]
        else:
            return [f"File not found: {file_path}"]

def handle_client(client_socket):
    """
    Handles communication with a connected client.
    
    Args:
        client_socket (socket.socket): The client's socket connection.
    """
    try:
        while True:
            # Receive message from the client
            client_msg = client_socket.recv(1024).decode('utf-8')
            logging.debug(f"Received message: {client_msg}")
            if client_msg == ENDING_MSG:
                logging.debug("Termination message received. Closing connection.")
                break
            try:
                # Parse the received message
                search_target, keyword, file_extension = client_msg.split("|")
                search_target = search_target.strip()
                keyword = keyword.strip()
                file_extension = file_extension.strip()
                logging.debug(f"Parsed: search_target={search_target}, keyword={keyword}, file_extension={file_extension}")
                # Perform the search
                results = handle_search(search_target, keyword, file_extension)
                response = "\n".join(results)
            except ValueError:
                # Handle incorrect message format
                response = "Invalid format. Use: <search_target>|<keyword>|<file_extension>"
            # Send the response back to the client
            client_socket.send(response.encode('utf-8'))
    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        client_socket.close()
        logging.debug("Client connection closed.")

def main():
    """
    The main function to start the server, listen for incoming connections,
    and handle client requests.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        try:
            server.bind((HOST, PORT))
            server.listen(5)
            print(f"[Server] Running on {HOST}:{PORT}. Press 'q' to stop.")
            logging.info(f"Server started on {HOST}:{PORT}")

            def stop_server():
                """
                Function to stop the server when the user inputs 'q'.
                """
                while True:
                    if input().strip().lower() == 'q':
                        print("[Server] Shutting down.")
                        logging.info("Server shutdown initiated by user.")
                        os._exit(0)  # Forcefully exit the program

            # Start a daemon thread to listen for the shutdown command
            threading.Thread(target=stop_server, daemon=True).start()

            while True:
                # Accept incoming client connections
                client_socket, addr = server.accept()
                logging.info(f"Accepted connection from {addr}")
                # Start a new thread to handle the client
                threading.Thread(target=handle_client, args=(client_socket,)).start()
        except Exception as e:
            logging.error(f"Server error: {e}")
            print(f"[Server] Error: {e}")

if __name__ == "__main__":
    main()
