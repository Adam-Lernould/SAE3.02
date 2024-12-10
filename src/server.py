import socket
import threading
import os
import glob
import PyPDF2
import openpyxl
import re
from bs4 import BeautifulSoup
import logging

# Configure logging for debugging
logging.basicConfig(filename='server.log', level=logging.DEBUG)

# Define constants
HOST = '127.0.0.1'
PORT = 12345
ENDING_MSG = "q"
FOLDERS = {
    ".txt": "data/txt/",
    ".pdf": "data/pdf/",
    ".html": "data/html/",
    ".xlsx": "data/excel/"
}


# Helper functions
def parse_keywords(keyword):
    # Priorité aux opérateurs AND/OR
    if " OR " in keyword:
        return [kw.strip() for kw in keyword.split(" OR ")], "OR", False
    elif " AND " in keyword:
        return [kw.strip() for kw in keyword.split(" AND ")], "AND", False

    # Pas d'opérateur logique, on teste si c'est une regex
    try:
        re.compile(keyword)
        is_regex = True
    except re.error:
        is_regex = False

    return [keyword.strip()], "SINGLE", is_regex


def matches_with_operator(line, keywords, operator, is_regex):
    if operator == "OR":
        # Au moins un mot-clé doit correspondre
        return any(re.search(kw, line) if is_regex else kw in line for kw in keywords)
    elif operator == "AND":
        # Tous les mots-clés doivent correspondre
        return all(re.search(kw, line) if is_regex else kw in line for kw in keywords)
    elif operator == "SINGLE":
        # Un seul mot-clé
        return re.search(keywords[0], line) if is_regex else keywords[0] in line
    return False


# Search functions
def search_txt(file_path, keyword):
    results = []
    count = 1
    keywords, operator, is_regex = parse_keywords(keyword)

    logging.debug(f"Searching in file: {file_path} with keywords={keywords}, operator={operator}, is_regex={is_regex}")
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line_num, line in enumerate(lines, start=1):
            if matches_with_operator(line, keywords, operator, is_regex):
                logging.debug(f"Match found in file {file_path} on line {line_num}: {line.strip()}")
                results.append(f"{count} - {os.path.basename(file_path)} - Line {line_num}: {line.strip()}")
                count += 1
    if not results:
        logging.debug(f"No matches found in file: {file_path}")
    return results


def search_pdf(file_path, keyword):
    results = []
    count = 1
    keywords, operator, is_regex = parse_keywords(keyword)

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
    return results


def search_html(file_path, keyword):
    results = []
    count = 1
    keywords, operator, is_regex = parse_keywords(keyword)

    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        for tag in soup.find_all(text=True):
            tag_text = tag.strip()
            if not tag_text:
                continue
            if matches_with_operator(tag_text, keywords, operator, is_regex):
                results.append(f"{count} - {os.path.basename(file_path)} - {tag_text}")
                count += 1
    return results


def search_xlsx(file_path, keyword):
    results = []
    count = 1
    keywords, operator, is_regex = parse_keywords(keyword)
    workbook = openpyxl.load_workbook(file_path)
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        for row in sheet.iter_rows():
            for cell in row:
                cell_value = str(cell.value) if cell.value else ""
                if matches_with_operator(cell_value, keywords, operator, is_regex):
                    results.append(f"{count} - {os.path.basename(file_path)} - Sheet {sheet_name}, Cell ({cell.row}, {cell.column}): {cell_value}")
                    count += 1
    return results


def search_all_files(folder, extension, keyword):
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
    results = []
    for extension, folder in FOLDERS.items():
        results.extend(search_all_files(folder, extension, keyword))
    return results if results else ["No matches found in any file."]


def handle_search(search_target, keyword, file_extension):
    # file_extension peut maintenant contenir plusieurs extensions séparées par des virgules
    extensions = [ext.strip() for ext in file_extension.split(',') if ext.strip()] if file_extension else []

    if search_target == "ALL":
        # Si aucune extension n'est spécifiée, recherche dans tous les types
        if not extensions:
            return search_all_file_types(keyword)
        else:
            # Recherche dans toutes les extensions sélectionnées
            results = []
            for ext in extensions:
                folder = FOLDERS.get(ext)
                if not folder:
                    results.append(f"Unsupported file type: {ext}")
                else:
                    res = search_all_files(folder, ext, keyword)
                    if not res or (len(res) == 1 and res[0].startswith("No matches found")):
                        # Si pas de résultats pour cette extension
                        res = ["No matches found."]
                    results.extend(res)
            return results
    else:
        # Recherche dans un fichier précis. On suppose alors qu'il n'y a qu'une extension
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
    try:
        while True:
            client_msg = client_socket.recv(1024).decode('utf-8')
            logging.debug(f"Received message: {client_msg}")
            if client_msg == ENDING_MSG:
                break
            try:
                search_target, keyword, file_extension = client_msg.split("|")
                search_target = search_target.strip()
                keyword = keyword.strip()
                file_extension = file_extension.strip()
                logging.debug(f"Parsed: search_target={search_target}, keyword={keyword}, file_extension={file_extension}")
                results = handle_search(search_target, keyword, file_extension)
                response = "\n".join(results)
            except ValueError:
                response = "Invalid format. Use: <search_target>|<keyword>|<file_extension>"
            client_socket.send(response.encode('utf-8'))
    finally:
        client_socket.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[Server] Running on {HOST}:{PORT}. Press 'q' to stop.")

        def stop_server():
            while True:
                if input().strip().lower() == 'q':
                    print("[Server] Shutting down.")
                    os._exit(0)

        threading.Thread(target=stop_server, daemon=True).start()

        while True:
            client_socket, _ = server.accept()
            threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    main()
