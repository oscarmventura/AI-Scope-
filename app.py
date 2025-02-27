#/* Copyright (c) 2025 Oscar Ventura. All Rights Reserved.
# *
#  This software and its source code are the exclusive property of Oscar M Ventura.
#  Unauthorized copying, distribution, modification, or use of this software,
# in whole or in part, without express written permission from the author is strictly prohibited.
# For licensing inquiries, please contact oscarmventura@icloud.com
# /

import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pdfplumber
import re

def extract_text_from_pdf(pdf_path):
    text_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_lines.extend(text.split('\n'))
    return text_lines

def extract_room_items(lines):
    rooms = {"General": {}}
    current_room = "General"
    
    construction_categories = [
        "Drywall", "Flooring", "Baseboards", "Painting", "Ceiling", "Trim", "Doors", "Windows", "Insulation", "Cabinets"
    ]
    
    for line in lines:
        room_match = re.match(r'^(Bedroom|Kitchen|Bathroom|Entry|Dining Room|Living Room|Hallway|Laundry Room|Closet|Garage):$', line.strip(), re.IGNORECASE)
        if room_match:
            current_room = room_match.group(1)
            rooms.setdefault(current_room, {})
        else:
            category = "Other"
            for cat in construction_categories:
                if cat.lower() in line.lower():
                    category = cat
                    break
            
            cost_match = re.search(r'\$([0-9,]+\.\d*)', line)
            sf_match = re.search(r'([0-9,]+(?:\.\d+)?)\s?sq\.?\s?ft', line, re.IGNORECASE)
            cost = float(cost_match.group(1).replace(',', '')) if cost_match else 0
            sf = float(sf_match.group(1).replace(',', '')) if sf_match else 0
            
            rooms[current_room].setdefault(category, [])
            rooms[current_room][category].append((line, cost, sf))
    
    return rooms

def compare_estimates(dryforce_file, adjuster_file):
    lines1 = extract_text_from_pdf(dryforce_file)
    lines2 = extract_text_from_pdf(adjuster_file)
    
    rooms1 = extract_room_items(lines1)
    rooms2 = extract_room_items(lines2)
    
    comparison_data = []
    
    for room in rooms1.keys():
        categories1 = rooms1.get(room, {})
        categories2 = rooms2.get(room, {})
        
        all_categories = set(categories1.keys()).union(categories2.keys())
        for category in all_categories:
            items1 = {item[0]: item for item in categories1.get(category, [])}
            items2 = {item[0]: item for item in categories2.get(category, [])}
            
            all_items = set(items1.keys()).union(items2.keys())
            for item in all_items:
                cost1, sf1 = items1.get(item, (item, 0, 0))[1:]
                cost2, sf2 = items2.get(item, (item, 0, 0))[1:]
                cost_diff = cost2 - cost1
                sf_diff = sf2 - sf1
                comparison_data.append([room, category, item, cost1, cost2, cost_diff, sf1, sf2, sf_diff])
    
    df = pd.DataFrame(comparison_data, columns=["Room", "Category", "Line Item", "Cost (DryForce)", "Cost (Adjuster)", "Cost Difference", "SF (DryForce)", "SF (Adjuster)", "SF Difference"])
    return df

def display_results(df):
    result_window = tk.Toplevel()
    result_window.title("Comparison Results")
    result_window.geometry("1200x500")
    
    frame = ttk.Frame(result_window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    tree = ttk.Treeview(frame, columns=df.columns.tolist(), show='headings')
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(side="left", fill="both", expand=True)
    
    for col in df.columns:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center", width=150)
    
    for i, row in enumerate(df.itertuples(index=False)):
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree.insert("", tk.END, values=row, tags=(tag,))
    
    tree.tag_configure("evenrow", background="#f2f2f2")
    tree.tag_configure("oddrow", background="#ffffff")

def upload_and_compare():
    dryforce_file = filedialog.askopenfilename(title="Select DryForce Estimate PDF", filetypes=[("PDF Files", "*.pdf")])
    adjuster_file = filedialog.askopenfilename(title="Select Adjuster Estimate PDF", filetypes=[("PDF Files", "*.pdf")])
    
    if dryforce_file and adjuster_file:
        comparison_df = compare_estimates(dryforce_file, adjuster_file)
        display_results(comparison_df)
        messagebox.showinfo("Comparison Completed", "Results displayed successfully.")
    else:
        messagebox.showwarning("File Selection", "File selection cancelled.")

def main():
    root = tk.Tk()
    root.title("Estimate Comparison Tool")
    root.geometry("400x200")

    tk.Label(root, text="Upload two estimate files to compare:").pack(pady=10)
    tk.Button(root, text="Select Estimate Files", command=upload_and_compare).pack(pady=10)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
