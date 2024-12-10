# SAE 3.02: Search Engine for Textual Data

## Overview
This project is a Python-based client-server application that allows users to search for keywords in various file formats, such as:
- Plain text files (`.txt`)
- HTML files (`.html`)
- PDF files (`.pdf`)
- Excel files (`.xlsx`)

The server performs the search operations, while the client interacts with the server to submit queries and receive results.

---

## Features
1. Search for keywords in multiple file formats.
2. Receive context and locations of the keywords found.
3. Client-server architecture for better modularity and scalability.

---

## Requirements
Install the required Python libraries with the following command:
```bash
pip install -r requirements.txt
```
---

## How to run 
1. Start the Server
Run the following command to start the server:

python server.py

The server will start running and listen for incoming requests from the client.

2. Start the Client
Run the following command to start the client:

python client.py

The client will prompt you to input a keyword. Once entered, it will search across the available files in the data/ directory and display the results in the terminal.

---
