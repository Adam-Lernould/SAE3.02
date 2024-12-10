import socket
import tkinter as tk
from tkinter import messagebox, filedialog
import os

# Define server configuration
HOST = '127.0.0.1'  # Server's IP address
PORT = 12345        # Server's port
ENDING_MSG = "q"    # Message to quit the client

# Mapping pour aider à construire les extensions choisies
available_file_types = {
    "TXT": ".txt",
    "PDF": ".pdf",
    "HTML": ".html",
    "Excel": ".xlsx"
}

# Dossier par type (utile pour sélection fichier spécifique)
data_folders = {
    ".txt": "data/txt/",
    ".pdf": "data/pdf/",
    ".html": "data/html/",
    ".xlsx": "data/excel/"
}


def send_request_to_server(request):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))
            client.send(request.encode('utf-8'))
            response = client.recv(4096).decode('utf-8')
        return response
    except Exception as e:
        return f"Error communicating with the server: {e}"

def get_selected_extensions():
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
    keyword = keyword_entry.get().strip()
    search_mode = search_mode_var.get()

    if not search_mode or not keyword:
        messagebox.showerror("Input Error", "Please complete all fields.")
        return

    selected_extensions = get_selected_extensions()
    extension_str = ",".join(selected_extensions)

    if search_mode == "Specific File":
        # Si plusieurs extensions sont sélectionnées, affichez une erreur ou gérez le cas.
        if len(selected_extensions) > 1:
            messagebox.showerror("Selection Error", "Please select only one file type for Specific File search.")
            return
        elif len(selected_extensions) == 1:
            ext = selected_extensions[0]
            start_folder = data_folders.get(ext, "data/")
            file_name = filedialog.askopenfilename(
                title="Select a file",
                initialdir=start_folder,
                filetypes=[(f"{ext} Files", f"*{ext}")]
            )
            if not file_name:
                return
            file_name_only = os.path.basename(file_name)
            request = f"{file_name_only}|{keyword}|{ext}"
        else:
            # Aucune extension sélectionnée : l'utilisateur choisit n'importe quel fichier
            file_name = filedialog.askopenfilename(
                title="Select a file",
                initialdir="data/",
                filetypes=[("All Files", "*.*")]
            )
            if not file_name:
                return
            chosen_ext = os.path.splitext(file_name)[1]
            file_name_only = os.path.basename(file_name)
            request = f"{file_name_only}|{keyword}|{chosen_ext}"
    else:
        # ALL files
        request = f"ALL|{keyword}|{extension_str}"

    if not request.strip():
        return

    results = send_request_to_server(request)
    results_text.delete(1.0, tk.END)
    results_text.insert(tk.END, results)



def quit_application():
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()


# Create the GUI
root = tk.Tk()
root.title("Client Search Application")
root.geometry("800x900")

# Frame pour le choix du mode (All files ou Specific file)
search_mode_frame = tk.Frame(root)
search_mode_frame.pack(pady=10)

search_mode_label = tk.Label(search_mode_frame, text="Search Mode:")
search_mode_label.pack(side=tk.LEFT, padx=5)

search_mode_var = tk.StringVar(value="All Files")
search_mode_options = ["All Files", "Specific File"]
search_mode_menu = tk.OptionMenu(search_mode_frame, search_mode_var, *search_mode_options)
search_mode_menu.pack(side=tk.LEFT, padx=5)

# Frame pour les checkboxes de type de fichier
file_types_frame = tk.Frame(root)
file_types_frame.pack(pady=10)

tk.Label(file_types_frame, text="Select File Types (leave all unchecked to search ALL):").pack()

var_txt = tk.BooleanVar()
var_pdf = tk.BooleanVar()
var_html = tk.BooleanVar()
var_excel = tk.BooleanVar()

chk_txt = tk.Checkbutton(file_types_frame, text="TXT", variable=var_txt)
chk_pdf = tk.Checkbutton(file_types_frame, text="PDF", variable=var_pdf)
chk_html = tk.Checkbutton(file_types_frame, text="HTML", variable=var_html)
chk_excel = tk.Checkbutton(file_types_frame, text="Excel", variable=var_excel)

chk_txt.pack(side=tk.LEFT, padx=5)
chk_pdf.pack(side=tk.LEFT, padx=5)
chk_html.pack(side=tk.LEFT, padx=5)
chk_excel.pack(side=tk.LEFT, padx=5)

# Keyword entry frame
keyword_frame = tk.Frame(root)
keyword_frame.pack(pady=10)

keyword_label = tk.Label(keyword_frame, text="Enter Keywords (Use 'OR' or 'AND' if needed):")
keyword_label.pack(side=tk.LEFT, padx=5)

keyword_entry = tk.Entry(keyword_frame, width=50)
keyword_entry.pack(side=tk.LEFT, padx=5)

# Search button
search_button_frame = tk.Frame(root)
search_button_frame.pack(pady=10)

search_button = tk.Button(search_button_frame, text="Search", command=perform_search)
search_button.pack(side=tk.LEFT, padx=10)

# Results display
results_label = tk.Label(root, text="Results:")
results_label.pack(pady=5)

results_text = tk.Text(root, height=30, width=90)
results_text.pack(pady=10)

# Quit button
quit_button = tk.Button(root, text="Quit", command=quit_application, bg="red", fg="white")
quit_button.pack(pady=20)

root.mainloop()
