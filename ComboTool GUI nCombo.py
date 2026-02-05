import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, filedialog, messagebox
import re
import os
import psutil
import threading
import time


def get_text_content(text_widget):
    """Get text widget content without tkinter's trailing newline."""
    content = text_widget.get(1.0, tk.END)
    if content.endswith("\n"):
        content = content[:-1]
    return content


# Functions to update text areas and line counts
def update_output():
    content = get_text_content(input_text)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, content)
    update_line_count()


def update_line_count():
    input_content = get_text_content(input_text)
    output_content = get_text_content(output_text)
    input_count = len(input_content.splitlines()) if input_content else 0
    output_count = len(output_content.splitlines()) if output_content else 0
    input_lines.set(f"Input Lines: {input_count}")
    output_lines.set(f"Output Lines: {output_count}")


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
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_contents[file_path] = f.read()
            update_file_list()
        except Exception as e:
            messagebox.showerror(
                "Error", f"Could not read file {file_path}: {str(e)}"
            )


# Function to display selected file content
def display_file_content(event):
    try:
        selected_index = file_listbox.curselection()
        if not selected_index:
            return
        display_name = file_listbox.get(selected_index)
        full_path = display_to_path.get(display_name)
        if full_path is None or full_path not in file_contents:
            messagebox.showerror(
                "Error", "Selected file not found in file contents"
            )
            return
        input_text.delete(1.0, tk.END)
        input_text.insert(tk.END, file_contents[full_path])
        update_line_count()
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")


# Function to merge files
def merge_files():
    if not file_contents:
        messagebox.showinfo("Info", "No files loaded to merge.")
        return
    merged_content = "\n".join(file_contents.values())
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, merged_content)
    update_line_count()


# Function to update file listbox (shows filenames only)
def update_file_list():
    file_listbox.delete(0, tk.END)
    display_to_path.clear()
    for file_path in file_contents.keys():
        display_name = os.path.basename(file_path)
        # Handle duplicate filenames by appending parent dir
        if display_name in display_to_path:
            parent = os.path.basename(os.path.dirname(file_path))
            display_name = f"{parent}/{display_name}"
        display_to_path[display_name] = file_path
        file_listbox.insert(tk.END, display_name)


# Function to remove duplicate lines (preserves order)
def remove_duplicates():
    input_content = get_text_content(input_text)
    lines = input_content.splitlines()
    unique_lines = list(dict.fromkeys(lines))
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "\n".join(unique_lines))
    update_line_count()


# Function to sort lines
def sort_lines():
    input_content = get_text_content(input_text)
    sorted_lines = sorted(input_content.splitlines())
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "\n".join(sorted_lines))
    update_line_count()


# Function to filter lines based on a plaintext pattern
def filter_plaintext_lines():
    pattern = simpledialog.askstring("Input", "Enter plaintext pattern:")
    if pattern:
        input_content = get_text_content(input_text)
        filtered_lines = [
            line for line in input_content.splitlines() if pattern in line
        ]
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "\n".join(filtered_lines))
        update_line_count()


# Function to filter lines based on a regex pattern
def filter_regex_lines():
    pattern = simpledialog.askstring("Input", "Enter regex pattern:")
    if pattern:
        try:
            compiled = re.compile(pattern)
            input_content = get_text_content(input_text)
            filtered_lines = [
                line for line in input_content.splitlines()
                if compiled.search(line)
            ]
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, "\n".join(filtered_lines))
            update_line_count()
        except re.error as e:
            messagebox.showerror(
                "Error", f"Invalid regex pattern: {str(e)}"
            )


# Function to split file content into multiple files
def split_files():
    num_lines = simpledialog.askinteger(
        "Input", "Enter number of lines per file:", minvalue=1
    )
    if num_lines:
        # Read content on main thread (thread-safe)
        input_content = get_text_content(input_text).splitlines()
        split_thread = threading.Thread(
            target=perform_split, args=(num_lines, input_content)
        )
        split_thread.start()


def perform_split(num_lines, lines):
    root.after(0, lambda: output_text.delete(1.0, tk.END))
    for i in range(0, len(lines), num_lines):
        split_content = "\n".join(lines[i:i + num_lines])
        part_num = i // num_lines + 1
        text = f"--- File part {part_num} ---\n{split_content}\n"
        root.after(0, update_split_output, text)


def update_split_output(split_content):
    output_text.insert(tk.END, split_content)
    update_line_count()


# Function to append file content
def append_files():
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                append_content = f.read()
            input_text.insert(tk.END, "\n" + append_content)
            update_line_count()
        except Exception as e:
            messagebox.showerror(
                "Error", f"Could not read file {file_path}: {str(e)}"
            )


# Function to save output to a file
def save_output():
    content = get_text_content(output_text)
    if not content:
        messagebox.showinfo("Info", "Output is empty. Nothing to save.")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Success", f"Output saved to {file_path}")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Could not save file: {str(e)}"
            )


# Function to copy output to clipboard
def copy_output():
    content = get_text_content(output_text)
    if not content:
        messagebox.showinfo("Info", "Output is empty. Nothing to copy.")
        return
    root.clipboard_clear()
    root.clipboard_append(content)


# Function to clear input area
def clear_input():
    input_text.delete(1.0, tk.END)
    update_line_count()


# Function to clear output area
def clear_output():
    output_text.delete(1.0, tk.END)
    update_line_count()


# Function to transfer output to input for chaining operations
def transfer_output_to_input():
    content = get_text_content(output_text)
    if not content:
        messagebox.showinfo("Info", "Output is empty. Nothing to transfer.")
        return
    input_text.delete(1.0, tk.END)
    input_text.insert(tk.END, content)
    update_line_count()


# Function to remove loaded files from the file list
def remove_selected_file():
    selected_index = file_listbox.curselection()
    if not selected_index:
        return
    display_name = file_listbox.get(selected_index)
    full_path = display_to_path.get(display_name)
    if full_path and full_path in file_contents:
        del file_contents[full_path]
    update_file_list()


# Function to update memory usage label
def update_memory_usage():
    while True:
        memory_info = psutil.virtual_memory()
        memory_usage.set(f"Memory Usage: {memory_info.percent}%")
        time.sleep(1)


# Initialize main GUI window
root = tk.Tk()
root.title("nCombo @wiseroldman")
root.geometry("1130x650")
root.minsize(800, 500)
root.configure(bg="#333")

# Styling
style = ttk.Style(root)
style.configure("TFrame", background="#333")
style.configure("TLabel", background="#333", foreground="#ddd")
style.configure("TButton", background="#555", foreground="black")

# Main frame
main_frame = ttk.Frame(root)
main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Configure grid weights so text areas expand on resize
main_frame.columnconfigure(0, weight=3)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(1, weight=1)
main_frame.rowconfigure(3, weight=1)

# Input label
input_label = ttk.Label(main_frame, text="Input:")
input_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 2))

# Input line count
input_lines = tk.StringVar(value="Input Lines: 0")
input_lines_label = ttk.Label(main_frame, textvariable=input_lines)
input_lines_label.grid(row=0, column=0, sticky=tk.E, pady=(0, 2))

# Input text area with scrollbar
input_frame = ttk.Frame(main_frame)
input_frame.grid(row=1, column=0, pady=(0, 5), sticky=tk.NSEW)
input_frame.rowconfigure(0, weight=1)
input_frame.columnconfigure(0, weight=1)

input_text = tk.Text(
    input_frame, wrap=tk.WORD, height=10, undo=True, maxundo=-1,
    bg="#444", fg="#ddd", insertbackground="white", selectbackground="#666"
)
input_text.grid(row=0, column=0, sticky=tk.NSEW)
input_scrollbar = ttk.Scrollbar(
    input_frame, orient=tk.VERTICAL, command=input_text.yview
)
input_scrollbar.grid(row=0, column=1, sticky=tk.NS)
input_text.configure(yscrollcommand=input_scrollbar.set)
input_text.bind("<KeyRelease>", lambda e: update_line_count())

# Output label
output_label = ttk.Label(main_frame, text="Output:")
output_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 2))

# Output line count
output_lines = tk.StringVar(value="Output Lines: 0")
output_lines_label = ttk.Label(main_frame, textvariable=output_lines)
output_lines_label.grid(row=2, column=0, sticky=tk.E, pady=(5, 2))

# Output text area with scrollbar
output_frame = ttk.Frame(main_frame)
output_frame.grid(row=3, column=0, pady=(0, 5), sticky=tk.NSEW)
output_frame.rowconfigure(0, weight=1)
output_frame.columnconfigure(0, weight=1)

output_text = tk.Text(
    output_frame, wrap=tk.WORD, height=10, undo=True, maxundo=-1,
    bg="#444", fg="#ddd", insertbackground="white", selectbackground="#666"
)
output_text.grid(row=0, column=0, sticky=tk.NSEW)
output_scrollbar = ttk.Scrollbar(
    output_frame, orient=tk.VERTICAL, command=output_text.yview
)
output_scrollbar.grid(row=0, column=1, sticky=tk.NS)
output_text.configure(yscrollcommand=output_scrollbar.set)

# File panel (right side)
file_panel = ttk.Frame(main_frame)
file_panel.grid(row=0, column=1, rowspan=4, padx=(10, 0), sticky=tk.NSEW)
file_panel.rowconfigure(1, weight=1)
file_panel.columnconfigure(0, weight=1)

file_label = ttk.Label(file_panel, text="Loaded Files:")
file_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 2))

file_listbox = tk.Listbox(
    file_panel, height=10, bg="#444", fg="#ddd",
    selectbackground="#666", selectforeground="#fff"
)
file_listbox.grid(row=1, column=0, sticky=tk.NSEW)
file_listbox.bind("<<ListboxSelect>>", display_file_content)

file_scrollbar = ttk.Scrollbar(
    file_panel, orient=tk.VERTICAL, command=file_listbox.yview
)
file_scrollbar.grid(row=1, column=1, sticky=tk.NS)
file_listbox.configure(yscrollcommand=file_scrollbar.set)

# File panel buttons
file_btn_frame = ttk.Frame(file_panel)
file_btn_frame.grid(row=2, column=0, columnspan=2, pady=(5, 0), sticky=tk.EW)

upload_button = ttk.Button(
    file_btn_frame, text="Upload", command=upload_files
)
upload_button.pack(side=tk.LEFT, padx=(0, 5))

remove_file_button = ttk.Button(
    file_btn_frame, text="Remove", command=remove_selected_file
)
remove_file_button.pack(side=tk.LEFT, padx=(0, 5))

merge_button = ttk.Button(
    file_btn_frame, text="Merge All", command=merge_files
)
merge_button.pack(side=tk.LEFT)

# Mapping from display names to full paths
display_to_path = {}

# Dictionary to store file contents
file_contents = {}

# Operation buttons (bottom area)
btn_frame = ttk.Frame(main_frame)
btn_frame.grid(row=4, column=0, columnspan=2, pady=(5, 0), sticky=tk.EW)

# Row 1: Input/Output operations
row1 = ttk.Frame(btn_frame)
row1.pack(fill=tk.X, pady=(0, 3))

paste_button = ttk.Button(row1, text="Paste", command=paste_to_input)
paste_button.pack(side=tk.LEFT, padx=(0, 5))

append_button = ttk.Button(
    row1, text="Append File", command=append_files
)
append_button.pack(side=tk.LEFT, padx=(0, 5))

clear_input_button = ttk.Button(
    row1, text="Clear Input", command=clear_input
)
clear_input_button.pack(side=tk.LEFT, padx=(0, 5))

ttk.Separator(row1, orient=tk.VERTICAL).pack(
    side=tk.LEFT, fill=tk.Y, padx=5
)

copy_output_button = ttk.Button(
    row1, text="Copy Output", command=copy_output
)
copy_output_button.pack(side=tk.LEFT, padx=(0, 5))

save_output_button = ttk.Button(
    row1, text="Save Output", command=save_output
)
save_output_button.pack(side=tk.LEFT, padx=(0, 5))

clear_output_button = ttk.Button(
    row1, text="Clear Output", command=clear_output
)
clear_output_button.pack(side=tk.LEFT, padx=(0, 5))

transfer_button = ttk.Button(
    row1, text="Output -> Input", command=transfer_output_to_input
)
transfer_button.pack(side=tk.LEFT, padx=(0, 5))

# Row 2: Processing operations
row2 = ttk.Frame(btn_frame)
row2.pack(fill=tk.X, pady=(0, 3))

update_output_button = ttk.Button(
    row2, text="Copy to Output", command=update_output
)
update_output_button.pack(side=tk.LEFT, padx=(0, 5))

remove_duplicates_button = ttk.Button(
    row2, text="Remove Duplicates", command=remove_duplicates
)
remove_duplicates_button.pack(side=tk.LEFT, padx=(0, 5))

sort_lines_button = ttk.Button(
    row2, text="Sort Lines", command=sort_lines
)
sort_lines_button.pack(side=tk.LEFT, padx=(0, 5))

filter_plaintext_button = ttk.Button(
    row2, text="Filter Plaintext", command=filter_plaintext_lines
)
filter_plaintext_button.pack(side=tk.LEFT, padx=(0, 5))

filter_regex_button = ttk.Button(
    row2, text="Filter Regex", command=filter_regex_lines
)
filter_regex_button.pack(side=tk.LEFT, padx=(0, 5))

split_files_button = ttk.Button(
    row2, text="Split Files", command=split_files
)
split_files_button.pack(side=tk.LEFT, padx=(0, 5))

# Memory usage label
memory_usage = tk.StringVar(value="Memory Usage: ...")
memory_usage_label = ttk.Label(main_frame, textvariable=memory_usage)
memory_usage_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

# Start memory usage update thread
memory_thread = threading.Thread(target=update_memory_usage, daemon=True)
memory_thread.start()

# Start the main event loop
root.mainloop()
