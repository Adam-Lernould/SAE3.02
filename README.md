# SAE 3.02: Search Engine for Textual Data

## Overview <a name="Overview-top"></a>

SAE 3.02 is a Python-based client-server application designed to facilitate efficient keyword searches across various file formats. This application leverages a modular client-server architecture to provide a scalable and user-friendly interface for searching through different types of documents.

Supported File Formats : 
- Plain text files (`.txt`)
- HTML files (`.html`)
- PDF files (`.pdf`)
- Excel files (`.xlsx`)

The server handles all search operations, while the client provides an intuitive graphical user interface (GUI) for users to submit queries and view results.

---

## Features <a name="features"></a>

1. Multi-Format Keyword Search:
- Search for specific keywords across multiple file formats including TXT, PDF, HTML, and Excel.

2. Advanced Search Capabilities:
- Utilize logical operators (AND, OR) to perform complex searches.
- Support for regular expressions to enhance search flexibility.

3. Client-Server Architecture:
- Server: Manages search requests, processes files, and returns results.
- Client: Provides a GUI for users to input search queries and view results.
4. Graphical User Interface (GUI):
- User-friendly interface built with Tkinter.
- Options to select search modes (All Files or Specific File) and file types.
- File dialog for selecting specific files when required.
5. Real-Time Results Display:
- Search results are displayed within the client GUI, showing file names, locations, and context of matches.
6. Logging and Debugging:
- Comprehensive logging on the server side for monitoring and debugging purposes.
7. Scalability and Modularity:
- Capable of handling multiple client connections simultaneously.
- Easy to extend support for additional file formats or functionalities.

[back to top](#Overview-top)

---

## Directory Structure <a name="directory-structure"></a>

- data/: Directory containing subfolders for each supported file type.
- txt/: Stores .txt files.
- pdf/: Stores .pdf files.
- html/: Stores .html files.
- excel/: Stores .xlsx files.
- server.py: Server-side script handling search operations.
- client.py: Client-side script providing the GUI for user interactions.
- requirements.txt: Lists all Python dependencies required for the project.
- README.md: Project documentation.
- LICENSE.txt: License information.
- Ensure that the data/ directory and its subfolders exist and contain the files you intend to search.

---

## Requirements <a name="requirements"></a>

Before running the application, ensure you have Python 3.x installed on your system. Install the required Python libraries using the following command:

`pip install -r requirements.txt`

[back to top](#Overview-top)

---

## How to Run <a name="how-to-run"></a>

1. Prepare the Environment
- Clone the Repository:

`git clone https://gitlab.univ-artois.fr/adam_lernould/sae3.02-s3-iut-de-bethune.git`
`
- Navigate to the Project Directory:

`cd sae3.02-s3-iut-de-bethune`

- Install Dependencies:

`pip install -r requirements.txt`

- Organize Your Data:
Place the files you want to search in the respective subfolders within the data/ directory:
.txt files in data/txt/
.pdf files in data/pdf/
.html files in data/html/
.xlsx files in data/excel/

2. Start the Server

- Run the server script to start listening for client requests.

`python server.py`

- Server Output:

`[Server] Running on 127.0.0.1:12345. Press 'q' to stop.`

- Logging:

All server activities and errors are logged in server.log.

[back to top](#Overview-top)

3. Start the Client

- Run the client script to launch the GUI application.

`python client.py`

4. Using the Client GUI
- Select Search Mode:

All Files: Search across all supported file types.
Specific File: Search within a specific file type and a chosen file.

- Select File Types:

Choose one or more file types (TXT, PDF, HTML, Excel) to include in the search.
Note: If no file types are selected, the search defaults to all supported types.

- Enter Keywords:

Input the keywords you want to search for.
Use logical operators AND or OR to refine your search.
Example: python AND server
Example: error OR failure
Supports regular expressions for advanced search patterns.

- Execute Search:

Click the Search button to submit your query.
If Specific File mode is selected, you will be prompted to choose a file.

- View Results:

Search results are displayed in the Results section of the GUI, detailing the file name, location of the match, and context.

- Quit Application:

Click the Quit button to exit the application gracefully.

[back to top](#Overview-top)

---

## Usage Examples <a name="usage-examples"></a>

1. Example 1: Search Across All Files.

Search Mode: All Files
File Types: Select TXT, PDF, HTML, Excel
Keywords: data AND analysis
Result: Displays all occurrences where both "data" and "analysis" appear within the selected file types.

2. Example 2: Search for a Specific File.

Search Mode: Specific File
File Type: Select PDF
File Selection: Choose report.pdf from data/pdf/
Keywords: financial OR revenue
Result: Displays all lines in report.pdf where either "financial" or "revenue" appear.

3. Example 3: Using Regular Expressions.

Search Mode: All Files
File Types: Select TXT
Keywords: \berror\b
Result: Displays all exact matches of the word "error" in .txt files.

[back to top](#Overview-top)

---

## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

[back to top](#Overview-top)

---

## Contact

Adam Lernould - adam.lernould@gmail.com

Project Link: [https://gitlab.univ-artois.fr/adam_lernould/sae3.02-s3-iut-de-bethune/-/tree/main?ref_type=heads](https://gitlab.univ-artois.fr/adam_lernould/sae3.02-s3-iut-de-bethune/-/tree/main?ref_type=heads)

[back to top](#Overview-top)

