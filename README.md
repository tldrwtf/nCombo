# nCombo

A Python GUI tool for manipulating and processing text files. Built with `tkinter`, nCombo provides operations like merging, deduplicating, sorting, filtering, splitting, and appending content of files through a user-friendly interface.

**Author:** @deliverings / tldrwtf(n3u)

## Features

### File Operations
- **Upload** multiple text files at once
- **Display** selected file content in the input area
- **Merge** all loaded files into a single output
- **Append** content from additional files to the input area
- **Remove** files from the loaded file list
- **Save** output to a file

### Text Processing
- **Remove Duplicates** - Deduplicate lines while preserving original order
- **Sort Lines** - Sort content alphabetically
- **Filter Plaintext** - Filter lines containing a text pattern
- **Filter Regex** - Filter lines matching a regular expression
- **Split Files** - Split content into numbered parts by line count

### Clipboard & Transfer
- **Paste** clipboard content into the input area
- **Copy Output** to clipboard
- **Transfer Output to Input** for chaining multiple operations

### Interface
- Resizable window with dark theme
- Scrollable input and output text areas
- Live line count display for both input and output
- Real-time system memory usage monitoring
- File list showing loaded files by name

## Requirements

- Python 3.10+
- `psutil` (for memory monitoring)
- `tkinter` (included with most Python installations)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python ncombo.py
```

## Running Tests

```bash
pip install pytest
pytest -v
```
