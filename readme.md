# 🧠 DeepSeek Chat (Qt6 + C++20 + Python)

A cross-platform desktop chat interface using **Qt6 (C++20)** for the frontend and **Python** for backend requests to a DeepSeek LLM server. Built with **CMake**, supports **Windows (MSYS2 + MinGW)** and **macOS (Clang)**.

---

## 📸 Features

- Chat-style UI: chat log, input box, send button
- Sends user input to DeepSeek LLM via a Python script
- Uses `QProcess` to bridge C++ and Python
- Designed with Qt Designer and CMake

---

## 📁 Project Structure

```
DeepSeekChat/
├── CMakeLists.txt          # Build configuration
├── src/                    # All source files
│   ├── main.cpp
│   ├── MainWindow.cpp/h
│   ├── MainWindow.ui
│   └── python_interface.py
└── README.md
```

---

## 🔧 Requirements

### ✅ Common

- CMake ≥ 3.16
- Python 3.8+
- `requests` Python library:
  ```bash
  pip install requests
  ```

---

## 🪟 Windows Build Instructions (MSYS2 + MinGW)

### 1. 🏗 Install Dependencies

Open **MSYS2 MinGW 64-bit shell** and run:

```bash
pacman -Syu   # First time only
pacman -S --needed \
  mingw-w64-x86_64-toolchain \
  mingw-w64-x86_64-cmake \
  mingw-w64-x86_64-qt6-base \
  mingw-w64-x86_64-python-pip \
  git

pip install requests
```

### 2. 🛠 Build

```bash
git clone https://github.com/yourname/deepseek-chat.git
cd deepseek-chat
mkdir build && cd build
cmake .. -G "MinGW Makefiles"
mingw32-make
./DeepSeekChat.exe
```

---

## 🍎 macOS Build Instructions (Clang)

> This uses the default macOS Clang compiler and Homebrew-installed Qt6.

### 1. 📦 Install Qt6 & CMake

```bash
brew install qt cmake python
pip3 install requests
```

> ⚠️ Qt is keg-only. You'll need to specify the Qt path manually in CMake.

### 2. ⚙️ Build

```bash
git clone https://github.com/yourname/deepseek-chat.git
cd deepseek-chat
mkdir build && cd build
cmake .. -DCMAKE_PREFIX_PATH="$(brew --prefix qt)"
make
./DeepSeekChat
```

---

## 🧪 Running the App

1. Launch the app from terminal or double-click the binary.
2. Type your message in the input box and press **Send**.
3. The app uses `QProcess` to call `python_interface.py`, which queries the DeepSeek API.
4. The AI’s response appears in the chat window.

---

## 🔐 DeepSeek API Key

Edit `src/python_interface.py` and replace the `Authorization` header with your own key:

```python
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY_HERE"
}
```

---

## 💡 UI Components

These widgets are defined in `src/MainWindow.ui`:
- `QTextEdit` (name: `chatDisplay`, read-only)
- `QLineEdit` (name: `inputBox`)
- `QPushButton` (name: `sendButton`, text: "Send")

---

## 🧼 Cleanup

To remove build files:

```bash
rm -rf build
```

To rebuild cleanly:

```bash
mkdir build && cd build
cmake .. && make
```

---

## 📌 Notes

- On macOS, you can also build universal binaries for Intel + ARM.
- If you want to build Windows `.exe` files on macOS, consider using [MinGW-w64](https://brew.sh/) and a CMake toolchain file.
- You may optionally replace `QProcess` with a C++ HTTP client (like Boost.Beast) for direct API access if Python is not preferred.

---

## 📜 License

MIT License – Free to use, modify, and distribute.
