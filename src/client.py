# client.py

import socket                       # For network communication with the server
import tkinter as tk                # For creating the graphical user interface (GUI)
from tkinter import messagebox, filedialog  # For displaying dialog boxes and file selection dialogs
import os                           # For interacting with the operating system (e.g., file paths)

# Define server configuration constants
HOST = '127.0.0.1'      # Server's IP address (localhost)
PORT = 12345            # Server's port number
ENDING_MSG = "q"        # Message to terminate the client connection (if used)

# Mapping to assist in constructing selected extensions
available_file_types = {
    "TXT": ".txt",
    "PDF": ".pdf",
    "HTML": ".html",
    "Excel": ".xlsx"
}

# Mapping of file extensions to their corresponding directories (useful for selecting specific files)
data_folders = {
    ".txt": "data/txt/",
    ".pdf": "data/pdf/",
    ".html": "data/html/",
    ".xlsx": "data/excel/"
}

def send_request_to_server(request):
    """
    Sends a request to the server and receives the response.
    
    Args:
        request (str): The search request to send to the server.
        
    Returns:
        str: The server's response or an error message.
    """
    try:
        # Create a TCP/IP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))               # Connect to the server
            client.send(request.encode('utf-8'))       # Send the request encoded in UTF-8
            response = client.recv(4096).decode('utf-8')  # Receive the response (max 4096 bytes)
        return response  # Return the decoded response
    except Exception as e:
        # Return an error message if communication fails
        return f"Error communicating with the server: {e}"

def get_selected_extensions():
    """
    Retrieves the file extensions selected by the user via checkboxes.
    
    Returns:
        list: A list of selected file extensions.
    """
    selected = []  # Initialize an empty list to store selected extensions
    if var_txt.get():
        selected.append(".txt")
    if var_pdf.get():
        selected.append(".pdf")
    if var_html.get():
        selected.append(".html")
    if var_excel.get():
        selected.append(".xlsx")
    return selected  # Return the list of selected extensions

def perform_search():
    """
    Executes the search based on user input and displays the results.
    """
    keyword = keyword_entry.get().strip()  # Retrieve the entered keyword and remove leading/trailing spaces
    search_mode = search_mode_var.get()    # Retrieve the selected search mode ("All Files" or "Specific File")

    # Validate that both search mode and keyword are provided
    if not search_mode or not keyword:
        messagebox.showerror("Input Error", "Please complete all fields.")  # Show error message
        return  # Exit the function if validation fails

    selected_extensions = get_selected_extensions()  # Get the list of selected file extensions
    extension_str = ",".join(selected_extensions)    # Convert the list to a comma-separated string

    if search_mode == "Specific File":
        # If the user selected to search within a specific file
        if len(selected_extensions) > 1:
            # If multiple file types are selected, show an error
            messagebox.showerror("Selection Error", "Please select only one file type for Specific File search.")
            return  # Exit the function
        elif len(selected_extensions) == 1:
            # If exactly one file type is selected, open a file dialog to choose the specific file
            ext = selected_extensions[0]
            start_folder = data_folders.get(ext, "data/")  # Get the starting directory based on extension
            file_name = filedialog.askopenfilename(
                title="Select a file",
                initialdir=start_folder,
                filetypes=[(f"{ext.upper()} Files", f"*{ext}")]  # Filter files by selected extension
            )
            if not file_name:
                return  # If no file is selected, exit the function
            file_name_only = os.path.basename(file_name)  # Extract the file name without the path
            request = f"{file_name_only}|{keyword}|{ext}"  # Format the search request
        else:
            # If no file type is selected, allow the user to choose any file
            file_name = filedialog.askopenfilename(
                title="Select a file",
                initialdir="data/",
                filetypes=[("All Files", "*.*")]
            )
            if not file_name:
                return  # If no file is selected, exit the function
            chosen_ext = os.path.splitext(file_name)[1]  # Extract the file extension
            file_name_only = os.path.basename(file_name)  # Extract the file name without the path
            request = f"{file_name_only}|{keyword}|{chosen_ext}"  # Format the search request
    else:
        # If the user selected to search across all files
        request = f"ALL|{keyword}|{extension_str}"  # Format the search request

    if not request.strip():
        return  # If the request is empty, do nothing

    # Send the search request to the server and get the results
    results = send_request_to_server(request)
    # Clear any existing text in the results display area
    results_text.delete(1.0, tk.END)
    # Insert the new search results into the text area
    results_text.insert(tk.END, results)

def quit_application():
    """
    Exits the application after confirming with the user.
    """
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()  # Close the main window, effectively exiting the application

# Create the main application window
root = tk.Tk()
root.title("Client Search Application")  # Set the window title
root.geometry("800x900")                # Set the window size (width x height)

# Frame for selecting the search mode (All files or Specific file)
search_mode_frame = tk.Frame(root)
search_mode_frame.pack(pady=10)  # Add vertical padding

# Label for the search mode selection
search_mode_label = tk.Label(search_mode_frame, text="Search Mode:")
search_mode_label.pack(side=tk.LEFT, padx=5)  # Position to the left with horizontal padding

# Variable to store the selected search mode
search_mode_var = tk.StringVar(value="All Files")  # Default value is "All Files"

# Define available search modes
search_mode_options = ["All Files", "Specific File"]

# Dropdown menu for selecting the search mode
search_mode_menu = tk.OptionMenu(search_mode_frame, search_mode_var, *search_mode_options)
search_mode_menu.pack(side=tk.LEFT, padx=5)  # Position to the left with horizontal padding

# Frame for file type checkboxes
file_types_frame = tk.Frame(root)
file_types_frame.pack(pady=10)  # Add vertical padding

# Label instructing the user to select file types
tk.Label(file_types_frame, text="Select File Types (leave all unchecked to search ALL):").pack()

# Variables associated with each checkbox (to track their states)
var_txt = tk.BooleanVar()
var_pdf = tk.BooleanVar()
var_html = tk.BooleanVar()
var_excel = tk.BooleanVar()

# Create checkboxes for each file type
chk_txt = tk.Checkbutton(file_types_frame, text="TXT", variable=var_txt)
chk_pdf = tk.Checkbutton(file_types_frame, text="PDF", variable=var_pdf)
chk_html = tk.Checkbutton(file_types_frame, text="HTML", variable=var_html)
chk_excel = tk.Checkbutton(file_types_frame, text="Excel", variable=var_excel)

# Pack the checkboxes horizontally with padding
chk_txt.pack(side=tk.LEFT, padx=5)
chk_pdf.pack(side=tk.LEFT, padx=5)
chk_html.pack(side=tk.LEFT, padx=5)
chk_excel.pack(side=tk.LEFT, padx=5)

# Frame for keyword entry
keyword_frame = tk.Frame(root)
keyword_frame.pack(pady=10)  # Add vertical padding

# Label for the keyword entry field
keyword_label = tk.Label(keyword_frame, text="Enter Keywords (Use 'OR' or 'AND' if needed):")
keyword_label.pack(side=tk.LEFT, padx=5)  # Position to the left with horizontal padding

# Entry widget for the user to input keywords
keyword_entry = tk.Entry(keyword_frame, width=50)
keyword_entry.pack(side=tk.LEFT, padx=5)  # Position to the left with horizontal padding

# Frame for the search button
search_button_frame = tk.Frame(root)
search_button_frame.pack(pady=10)  # Add vertical padding

# Search button that triggers the search operation
search_button = tk.Button(search_button_frame, text="Search", command=perform_search)
search_button.pack(side=tk.LEFT, padx=10)  # Position to the left with horizontal padding

# Label for the results display area
results_label = tk.Label(root, text="Results:")
results_label.pack(pady=5)  # Add vertical padding

# Text widget to display search results
results_text = tk.Text(root, height=30, width=90)
results_text.pack(pady=10)  # Add vertical padding

# Quit button to exit the application
quit_button = tk.Button(root, text="Quit", command=quit_application, bg="red", fg="white")
quit_button.pack(pady=20)  # Add vertical padding

# Start the Tkinter event loop to make the GUI responsive
root.mainloop()
