# 📦 filebin-cli

### A simple and hassle-free CLI tool to **share files temporarily** — upload files directly from your terminal. No login. No setup. Just share the link.

Built with ❤️ in Python, `filebin-cli` is a simple and convenient command-line interface for interacting with the file-sharing service [filebin.net](https://filebin.net).

This tool allows you to upload, download, and manage files and bins directly from your terminal, featuring progress bars for downloads, support for multiple files, and bin management capabilities.

---

## 📑 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start & Examples](#quick-start--examples)
  - [📤 Upload Files](#-upload-files)
  - [📋 Get Bin Details](#-get-bin-details)
  - [📥 Download Files](#-download-files)
  - [🛠️ Manage Bins](#️-manage-bins)
- [🧾 Command Reference](#-command-reference)
  - [`upload`](#upload)
  - [`details`](#details)
  - [`download`](#download)
  - [`lock`](#lock)
  - [`delete`](#delete)
- [🔧 Requirements](#-requirements)
- [🧑‍💻 Author](#-author)
- [LICENSE](#license)

---

## Features

- ⬆️ **Upload** one or multiple files to a new or existing bin.
- ⬇️ **Download** files with a progress bar.
- ℹ️ **List** the contents of any bin with basic or detailed metadata.
- 🔒 **Lock** a bin to make it read-only.
- 🗑️ **Delete** an entire bin permanently.

---

## Installation

Install the tool from PyPI using `pip`:

```bash
pip install filebin-cli
```

---

## Quick Start & Examples

### 📤 Upload Files

Upload a single file to a new bin:

```bash
fbin upload document.pdf
```

Upload multiple files to a new bin:

```bash
fbin upload image.jpg report.docx archive.zip
```

Upload a file to a specific, existing bin:

```bash
fbin upload --binid <your-bin-id> new-file.txt
```

---

### 📋 Get Bin Details

List the files in a bin:

```bash
fbin details <your-bin-id>
```

Get detailed metadata for all files in a bin:

```bash
fbin details -d <your-bin-id>
```

---

### 📥 Download Files

Download a single file from a bin to the current directory:

```bash
fbin download <your-bin-id> document.pdf
```

Download multiple files:

```bash
fbin download <your-bin-id> image.jpg report.docx
```

Download files to a specific directory:

```bash
fbin download <your-bin-id> archive.zip -p /path/to/my/downloads
```

---

### 🛠️ Manage Bins

Lock a bin to make it read-only (**this is permanent!**):

```bash
fbin lock <your-bin-id>
```

Delete an entire bin and all its contents (**this is permanent!**):

```bash
fbin delete <your-bin-id>
```

---

## 🧾 Command Reference

### `upload`

Uploads one or more files. If no `--binid` is provided, a new bin is created automatically.

**Usage**:
```bash
fbin upload [OPTIONS] [PATHS]...
```

**Arguments**:
- `PATHS...`: One or more paths to the files you want to upload.

**Options**:
- `--binid TEXT`: Specify an existing bin ID to upload to.

---

### `details`

Fetches and displays the metadata for all files in a specified bin.

**Usage**:
```bash
fbin details [OPTIONS] BINID
```

**Arguments**:
- `BINID`: The ID of the bin you want to inspect.

**Options**:
- `-d`, `--details`: Display detailed metadata, including timestamps and MD5 hash.

---

### `download`

Downloads one or more files from a bin.

**Usage**:
```bash
fbin download [OPTIONS] BINID [FILENAMES]...
```

**Arguments**:
- `BINID`: The ID of the bin to download from.
- `FILENAMES...`: The exact name(s) of the file(s) to download.

**Options**:
- `-p`, `--path TEXT`: The local directory path where files should be saved. Defaults to the current directory.

---

### `lock`

Permanently locks a bin, making it read-only. No new files can be uploaded.

**Usage**:
```bash
fbin lock BINID
```

**Arguments**:
- `BINID`: The ID of the bin to lock.

---

### `delete`

Permanently deletes a bin and all of its contents.

**Usage**:
```bash
fbin delete BINID
```

**Arguments**:
- `BINID`: The ID of the bin to delete.

---

## 🔧 Requirements

- `click`
- `requests`

These will be installed automatically when you install the tool.

---

## 🧑‍💻 Author

Made by [@mshirazkamran](https://github.com/mshirazkamran)

---

## LICENSE

This tool is Licensed under the MIT license 
