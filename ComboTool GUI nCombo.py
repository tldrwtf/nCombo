import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, filedialog, messagebox
import re
import os
import psutil
import threading
import time

# Functions to update text areas and line counts
def update_output():
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, input_text.get(1.0, tk.END))
    update_line_count()

def update_line_count():
    input_lines.set(f"Input Lines: {len(input_text.get(1.0, tk.END).splitlines())}")
    output_lines.set(f"Output Lines: {len(output_text.get(1.0, tk.END).splitlines())}")

# Function to paste clipboard content to input_text widget
def paste_to_input():
    try:
        clipboard_content = root.clipboard_get()
        input_text.delete(1.0, tk.END)
        input_text.insert(tk.END, clipboard_content)
        update_line_count()
    except tk.TclError:
        messagebox.showerror("Error", "Could not paste from clipboard")

# Function to upload files
def upload_files():
    file_paths = filedialog.askopenfilenames()
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                file_contents[file_path] = file.read()
            update_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file {file_path}: {str(e)}")

# Function to display selected file content
def display_file_content(event):
    try:
        selected_index = file_listbox.curselection()
        if not selected_index:
            return
        selected_file = file_listbox.get(selected_index)
        if selected_file not in file_contents:
            raise ValueError("Selected file not found in file contents")
        input_text.delete(1.0, tk.END)
        input_text.insert(tk.END, file_contents[selected_file])
        update_line_count()
    except ValueError as ve:
        messagebox.showerror("Error", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")

# Function to merge files
def merge_files():
    merged_content = "\n".join(file_contents.values())
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, merged_content)
    update_line_count()

# Function to update file listbox
def update_file_list():
    file_listbox.delete(0, tk.END)
    for file_path in file_contents.keys():
        file_listbox.insert(tk.END, file_path)

# Function to remove duplicate lines
def remove_duplicates():
    input_content = input_text.get(1.0, tk.END)
    unique_lines = "\n".join(set(input_content.splitlines()))
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, unique_lines)
    update_line_count()

# Function to sort lines
def sort_lines():
    input_content = input_text.get(1.0, tk.END)
    sorted_lines = "\n".join(sorted(input_content.splitlines()))
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, sorted_lines)
    update_line_count()

# Function to filter lines based on a plaintext pattern
def filter_plaintext_lines():
    pattern = simpledialog.askstring("Input", "Enter plaintext pattern:")
    if pattern:
        input_content = input_text.get(1.0, tk.END)
        filtered_lines = "\n".join(line for line in input_content.splitlines() if pattern in line)
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, filtered_lines)
        update_line_count()

# Function to filter lines based on a regex pattern
def filter_regex_lines():
    pattern = simpledialog.askstring("Input", "Enter regex pattern:")
    if pattern:
        try:
            input_content = input_text.get(1.0, tk.END)
            filtered_lines = "\n".join(line for line in input_content.splitlines() if re.search(pattern, line))
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, filtered_lines)
            update_line_count()
        except re.error as e:
            messagebox.showerror("Error", f"Invalid regex pattern: {str(e)}")

# Function to split file content into multiple files
def split_files():
    num_lines = simpledialog.askinteger("Input", "Enter number of lines per file:")
    if num_lines:
        split_thread = threading.Thread(target=perform_split, args=(num_lines,))
        split_thread.start()

def perform_split(num_lines):
    input_content = input_text.get(1.0, tk.END).splitlines()
    for i in range(0, len(input_content), num_lines):
        split_content = "\n".join(input_content[i:i + num_lines])
        root.after(0, update_split_output, f"\n--- File part {i // num_lines + 1} ---\n{split_content}")

def update_split_output(split_content):
    output_text.insert(tk.END, split_content)
    update_line_count()

# Function to append file content
def append_files():
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                append_content = file.read()
            input_text.insert(tk.END, "\n" + append_content)
            update_line_count()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file {file_path}: {str(e)}")

# Function to update memory usage label
def update_memory_usage():
    while True:
        memory_info = psutil.virtual_memory()
        memory_usage.set(f"Memory Usage: {memory_info.percent}%")
        time.sleep(1)

# Initialize main GUI window
root = tk.Tk()
root.title("nCombo @wiseroldman")
root.geometry("1130x600")
root.resizable(False, False)
root.configure(bg="#333")

# Styling
style = ttk.Style(root)
style.configure("TFrame", background="#333")
style.configure("TLabel", background="#333", foreground="#ddd")
style.configure("TButton", background="#555", foreground="black")
style.configure("TText", background="#444", foreground="#ddd", insertbackground='white')

# Main frame
main_frame = ttk.Frame(root)
main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Input and output labels
input_label = ttk.Label(main_frame, text="Input:")
input_label.grid(row=0, column=0, sticky=tk.W, pady=5)

output_label = ttk.Label(main_frame, text="Output:")
output_label.grid(row=2, column=0, sticky=tk.W, pady=5)

# Input and output text areas
input_text = tk.Text(main_frame, wrap=tk.WORD, height=10, undo=True, maxundo=-1)
input_text.grid(row=1, column=0, pady=5, sticky=tk.EW)
input_text.bind("<KeyRelease>", lambda e: update_line_count())

output_text = tk.Text(main_frame, wrap=tk.WORD, height=10, undo=True, maxundo=-1)
output_text.grid(row=3, column=0, pady=5, sticky=tk.EW)

# Line count labels
input_lines = tk.StringVar()
input_lines_label = ttk.Label(main_frame, textvariable=input_lines)
input_lines_label.grid(row=0, column=1, sticky=tk.W, pady=5)

output_lines = tk.StringVar()
output_lines_label = ttk.Label(main_frame, textvariable=output_lines)
output_lines_label.grid(row=2, column=1, sticky=tk.W, pady=5)

# File list box for managing multiple files
file_listbox = tk.Listbox(main_frame, height=10)
file_listbox.grid(row=1, column=1, pady=5, sticky=tk.EW)
file_listbox.bind("<<ListboxSelect>>", display_file_content)

# Dictionary to store file contents
file_contents = {}

# Buttons
paste_button = ttk.Button(main_frame, text="Paste", command=paste_to_input)
paste_button.grid(row=4, column=0, pady=5, sticky=tk.W)

upload_button = ttk.Button(main_frame, text="Upload", command=upload_files)
upload_button.grid(row=4, column=1, pady=5, sticky=tk.W)

merge_button = ttk.Button(main_frame, text="Merge", command=merge_files)
merge_button.grid(row=4, column=2, pady=5, sticky=tk.W)

remove_duplicates_button = ttk.Button(main_frame, text="Remove Duplicates", command=remove_duplicates)
remove_duplicates_button.grid(row=5, column=0, pady=5, sticky=tk.W)

sort_lines_button = ttk.Button(main_frame, text="Sort Lines", command=sort_lines)
sort_lines_button.grid(row=5, column=1, pady=5, sticky=tk.W)

filter_plaintext_button = ttk.Button(main_frame, text="Filter Plaintext", command=filter_plaintext_lines)
filter_plaintext_button.grid(row=5, column=2, pady=5, sticky=tk.W)

filter_regex_button = ttk.Button(main_frame, text="Filter Regex", command=filter_regex_lines)
filter_regex_button.grid(row=5, column=3, pady=5, sticky=tk.W)

split_files_button = ttk.Button(main_frame, text="Split Files", command=split_files)
split_files_button.grid(row=6, column=0, pady=5, sticky=tk.W)

append_files_button = ttk.Button(main_frame, text="Append Files", command=append_files)
append_files_button.grid(row=6, column=1, pady=5, sticky=tk.W)

# Memory usage label
memory_usage = tk.StringVar()
memory_usage_label = ttk.Label(main_frame, textvariable=memory_usage)
memory_usage_label.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=5)

# Start memory usage update thread
memory_thread = threading.Thread(target=update_memory_usage, daemon=True)
memory_thread.start()

# Start the main event loop
root.mainloop()
