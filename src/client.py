import socket
import tkinter as tk
from tkinter import messagebox, filedialog
import os

# Define server configuration
HOST = '127.0.0.1'  # Server's IP address
PORT = 12345        # Server's port number
ENDING_MSG = "q"    # Message to terminate the client connection

# Mapping to assist in constructing selected extensions
available_file_types = {
    "TXT": ".txt",
    "PDF": ".pdf",
    "HTML": ".html",
    "Excel": ".xlsx"
}

# Folders by file type (useful for selecting specific files)
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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))
            client.send(request.encode('utf-8'))
            response = client.recv(4096).decode('utf-8')
        return response
    except Exception as e:
        return f"Error communicating with the server: {e}"

def get_selected_extensions():
    """
    Retrieves the file extensions selected by the user via checkboxes.
    
    Returns:
        list: A list of selected file extensions.
    """
    selected = []
    if var_txt.get():
        selected.append(".txt")
    if var_pdf.get():
        selected.append(".pdf")
    if var_html.get():
        selected.append(".html")
    if var_excel.get():
        selected.append(".xlsx")
    return selected

def perform_search():
    """
    Executes the search based on user input and displays the results.
    """
    keyword = keyword_entry.get().strip()  # Retrieve the entered keyword
    search_mode = search_mode_var.get()    # Retrieve the selected search mode

    # Validate that both search mode and keyword are provided
    if not search_mode or not keyword:
        messagebox.showerror("Input Error", "Please complete all fields.")
        return

    selected_extensions = get_selected_extensions()  # Get selected file extensions
    extension_str = ",".join(selected_extensions)    # Convert list to comma-separated string

    if search_mode == "Specific File":
        # If searching for a specific file
        if len(selected_extensions) > 1:
            # If multiple file types are selected, show an error
            messagebox.showerror("Selection Error", "Please select only one file type for Specific File search.")
            return
        elif len(selected_extensions) == 1:
            # If one file type is selected, open file dialog to choose the file
            ext = selected_extensions[0]
            start_folder = data_folders.get(ext, "data/")
            file_name = filedialog.askopenfilename(
                title="Select a file",
                initialdir=start_folder,
                filetypes=[(f"{ext.upper()} Files", f"*{ext}")]
            )
            if not file_name:
                return  # User cancelled file selection
            file_name_only = os.path.basename(file_name)  # Get the file name without the path
            request = f"{file_name_only}|{keyword}|{ext}"  # Format the request
        else:
            # If no file type is selected, allow user to choose any file
            file_name = filedialog.askopenfilename(
                title="Select a file",
                initialdir="data/",
                filetypes=[("All Files", "*.*")]
            )
            if not file_name:
                return
            chosen_ext = os.path.splitext(file_name)[1]  # Get the selected file's extension
            file_name_only = os.path.basename(file_name)
            request = f"{file_name_only}|{keyword}|{chosen_ext}"
    else:
        # If searching across all files
        request = f"ALL|{keyword}|{extension_str}"

    if not request.strip():
        return  # Do nothing if the request is empty

    # Send the search request to the server and get results
    results = send_request_to_server(request)
    # Display the results in the text widget
    results_text.delete(1.0, tk.END)
    results_text.insert(tk.END, results)

def quit_application():
    """
    Exits the application after confirming with the user.
    """
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

# Create the GUI using Tkinter
root = tk.Tk()
root.title("Client Search Application")
root.geometry("800x900")  # Set the window size

# Frame for selecting the search mode (All files or Specific file)
search_mode_frame = tk.Frame(root)
search_mode_frame.pack(pady=10)

search_mode_label = tk.Label(search_mode_frame, text="Search Mode:")
search_mode_label.pack(side=tk.LEFT, padx=5)

search_mode_var = tk.StringVar(value="All Files")  # Variable to store the selected search mode
search_mode_options = ["All Files", "Specific File"]  # Available search modes
search_mode_menu = tk.OptionMenu(search_mode_frame, search_mode_var, *search_mode_options)
search_mode_menu.pack(side=tk.LEFT, padx=5)

# Frame for file type checkboxes
file_types_frame = tk.Frame(root)
file_types_frame.pack(pady=10)

tk.Label(file_types_frame, text="Select File Types (leave all unchecked to search ALL):").pack()

# Variables associated with each checkbox
var_txt = tk.BooleanVar()
var_pdf = tk.BooleanVar()
var_html = tk.BooleanVar()
var_excel = tk.BooleanVar()

# Checkboxes for each file type
chk_txt = tk.Checkbutton(file_types_frame, text="TXT", variable=var_txt)
chk_pdf = tk.Checkbutton(file_types_frame, text="PDF", variable=var_pdf)
chk_html = tk.Checkbutton(file_types_frame, text="HTML", variable=var_html)
chk_excel = tk.Checkbutton(file_types_frame, text="Excel", variable=var_excel)

# Arrange checkboxes horizontally
chk_txt.pack(side=tk.LEFT, padx=5)
chk_pdf.pack(side=tk.LEFT, padx=5)
chk_html.pack(side=tk.LEFT, padx=5)
chk_excel.pack(side=tk.LEFT, padx=5)

# Frame for keyword entry
keyword_frame = tk.Frame(root)
keyword_frame.pack(pady=10)

keyword_label = tk.Label(keyword_frame, text="Enter Keywords (Use 'OR' or 'AND' if needed):")
keyword_label.pack(side=tk.LEFT, padx=5)

keyword_entry = tk.Entry(keyword_frame, width=50)  # Entry field for keywords
keyword_entry.pack(side=tk.LEFT, padx=5)

# Frame for the search button
search_button_frame = tk.Frame(root)
search_button_frame.pack(pady=10)

search_button = tk.Button(search_button_frame, text="Search", command=perform_search)
search_button.pack(side=tk.LEFT, padx=10)

# Label and text area for displaying results
results_label = tk.Label(root, text="Results:")
results_label.pack(pady=5)

results_text = tk.Text(root, height=30, width=90)
results_text.pack(pady=10)

# Quit button to exit the application
quit_button = tk.Button(root, text="Quit", command=quit_application, bg="red", fg="white")
quit_button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
