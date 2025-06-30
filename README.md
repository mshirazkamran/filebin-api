# 📦 filebin-cli

A simple and hassle-free CLI tool to **share files temporarily** using the [filebin.net](https://filebin.net) public API.

Built with ❤️ in Python, `filebin-cli` lets you upload files directly from your terminal — no login, no setup, just share the link.

---

## 🚀 Features

- 📤 Upload files directly from the command line  
- 🔗 Get an instant shareable URL  
- 🧹 No registration or account required  
- 🐍 Lightweight & powered by `click` and `requests`  

---

## 📦 Installation

Make sure you have Python 3.7+ installed.

```bash
git clone https://github.com/mshirazkamran/filebin-cli.git
cd filebin-cli
pip install -e .
```

---

## ⚡ Usage

```bash
filebin <path-to-your-file>
```

### Example:

```bash
filebin my_photo.png
```

Output:

```
File uploaded successfully!
🔗 https://filebin.net/abcd1234/my_photo.png
```

Just copy the link and share it — done.

---

## 🔧 Requirements

- `click`
- `requests`

These will be installed automatically when you install the tool.

---

## 🧑‍💻 Author

Made by [@mshirazkamran](https://github.com/mshirazkamran)

---

## 📜 License

This project uses the MIT License.
