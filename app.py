#/* Copyright (c) 2025 Oscar Ventura. All Rights Reserved.
# *
#  This software and its source code are the exclusive property of Oscar M Ventura.
#  Unauthorized copying, distribution, modification, or use of this software,
# in whole or in part, without express written permission from the author is strictly prohibited.
# For licensing inquiries, please contact oscarmventura@icloud.com
# /

import pdfplumber
import difflib
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pickle
import re
from tabulate import tabulate

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file line by line."""
    text_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_lines.extend(text.split('\n'))
    return text_lines

def categorize_lines(lines):
    """Categorizes lines based on work area sections."""
    categories = {}
    current_category = "General"
    
    for line in lines:
        match = re.match(r'^(\w+\s*\w*):$', line.strip())
        if match:
            current_category = match.group(1)
            categories[current_category] = []
        else:
            categories.setdefault(current_category, []).append(line)
    
    return categories

def compare_estimates(file1, file2):
    """Compares two estimate files and highlights differences line by line within categories."""
    lines1 = extract_text_from_pdf(file1)
    lines2 = extract_text_from_pdf(file2)
    
    categories1 = categorize_lines(lines1)
    categories2 = categorize_lines(lines2)
    
    differences = []
    
    for category in set(categories1.keys()).union(categories2.keys()):
        diff = list(difflib.unified_diff(
            categories1.get(category, []),
            categories2.get(category, []),
            lineterm=''
        ))
        if diff:
            differences.append((category, diff))
    
    save_differences(differences)
    return differences

def save_differences(differences):
    """Saves the differences in a learning model."""
    try:
        with open("difference_history.pkl", "rb") as file:
            history = pickle.load(file)
    except FileNotFoundError:
        history = []
    
    history.append(differences)
    with open("difference_history.pkl", "wb") as file:
        pickle.dump(history, file)

def display_results(differences):
    """Displays the comparison results in a GUI window."""
    result_window = tk.Toplevel()
    result_window.title("Comparison Results")
    
    text_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=100, height=30)
    for category, diff in differences:
        text_area.insert(tk.INSERT, f"\n=== {category} ===\n")
        text_area.insert(tk.INSERT, '\n'.join(diff) + "\n")
    text_area.config(state=tk.DISABLED)
    text_area.pack(padx=10, pady=10)

def display_table(differences):
    """Displays the comparison results in a table format."""
    table_data = []
    for category, diff in differences:
        table_data.append([category, '\n'.join(diff)])
    
    table = tabulate(table_data, headers=["Category", "Differences"], tablefmt="grid")
    print(table)

def upload_and_compare():
    """Handles file selection and comparison through a GUI."""
    root = tk.Tk()
    root.withdraw()
    file1 = filedialog.askopenfilename(title="Select First Estimate PDF", filetypes=[("PDF Files", "*.pdf")])
    file2 = filedialog.askopenfilename(title="Select Second Estimate PDF", filetypes=[("PDF Files", "*.pdf")])
    
    if file1 and file2:
        differences = compare_estimates(file1, file2)
        
        with open("estimate_differences.txt", "w", encoding="utf-8") as output_file:
            for category, diff in differences:
                output_file.write(f"\n=== {category} ===\n")
                output_file.write('\n'.join(diff) + "\n")
        
        messagebox.showinfo("Comparison Completed", "Differences saved in estimate_differences.txt")
        display_results(differences)
        display_table(differences)
    else:
        messagebox.showwarning("File Selection", "File selection cancelled.")

def login():
    """Displays the login window and handles user authentication."""
    def authenticate():
        username = username_entry.get()
        password = password_entry.get()
        
        # Simple authentication logic (replace with your own logic)
        if username == "admin" and password == "password":
            login_window.destroy()
            main()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x150")

    tk.Label(login_window, text="Username:").pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    login_button = tk.Button(login_window, text="Login", command=authenticate)
    login_button.pack(pady=10)

    login_window.mainloop()

def main():
    """Creates the main GUI window."""
    root = tk.Tk()
    root.title("Estimate Comparison Tool")
    root.geometry("1080x780")
    
    label = tk.Label(root, text="Upload two estimate PDFs to compare:")
    label.pack(pady=10)
    
    compare_button = tk.Button(root, text="Compare Estimates", command=upload_and_compare)
    compare_button.pack(pady=10)
    
    exit_button = tk.Button(root, text="Exit", command=root.quit)
    exit_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    login()
