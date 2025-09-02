# Paysend Macro Manager

**File:** `macro_manager.py`
**Date:** 02-09-2025

---

## 1. Introduction

Macro Manager is a desktop GUI application built with Python and Tkinter. It helps users manage, search, and copy text macros efficiently. The tool is especially useful for roles such as customer support, where standardized text responses are frequently used. Features include placeholder handling, quick macro search, multi-copy mode, and keyboard hotkey macros.

---

## 2. Application Architecture

* **Main Window:** Search bar, macro list, and control buttons.
* **Macro Storage:** Macros are stored in `macros.json`.
* **Placeholders:** Supports special fields such as `[DATE]`, `[AMOUNT]`, `[COUNTRY]`, which are replaced using dedicated input widgets.
* **Clipboard Integration:** Copies macros directly to the system clipboard.
* **Multi-Copy Mode:** Monitors the clipboard to collect multiple copied items until pasted.
* **Keyboard Macros:** Allows global hotkeys for pasting predefined macros.
* **External Integrations:**

  * BIN lookup via HTTP API.
  * Country lookup via JSON configuration files.

---

## 3. File and Folder Structure

```
macro_manager.py            # Main application file
macros.json                 # Stores user macros (auto-created)

assets/                     # Contains icons and images
  ├── psicon.png
  ├── edit.png
  ├── copy2.png
  ├── on.png
  ├── off.png
  └── ...

config/
  ├── country_codes.json     # Mapping of calling codes to country names
  ├── countries.json         # List of country names for autocomplete
  └── keyboard_macros.json   # Keyboard macro definitions (auto-created)
```

---

## 4. Installation and Setup

1. Clone or download this repository.
2. Ensure Python 3.9+ is installed.
3. Install required dependencies:

   ```bash
   pip install Pillow pyperclip requests tkcalendar python-dateutil ttkwidgets keyboard
   ```
4. Run the application:

   ```bash
   python macro_manager.py
   ```

---

## 5. Usage Guide

* **Search:** Type keywords into the search bar. Special commands include:

  * Phone numbers → formatted result
  * `/bin123456` → BIN lookup
  * `/cc+381` → country lookup
* **Copy Macro:** Click on a macro to copy it to the clipboard.
* **Add Macro:** Use the `+` button to add a new macro.
* **Edit Macro:** Open a macro with placeholders to fill values.
* **Delete Macro:** Enable delete mode (`🗑️`) and click a macro to remove it.
* **Multi-Copy Mode:** Toggle using the copy icon. Stops after you paste (`Ctrl+V`).
* **Keyboard Macros:** Configure hotkeys in Settings → Manage keyboard macros.

**Supported Placeholders:**

* `XXXXXXX` — free text
* `[AMOUNT]` — amount input
* `[REST]` — sent amount input
* `[SENT]` — computed as `AMOUNT - REST`
* `[DATE]`, `[DATE1]`, `[DATE2]` — date inputs
* `[COUNTRY]` — country autocomplete

---

## 6. Extending the Project

* Add new placeholders by extending placeholder parsing logic.
* Customize UI by modifying assets.
* Extend import/export to other formats like CSV or databases.
* Add scrollbar to the main window
---

## 7. Future Improvements

* Add unit tests for key functions.
* Improve error handling for missing assets/configs.
* Use asynchronous requests for API calls.
* Add localization support (multi-language UI).
* Provide an installer for easier setup.

---

## License

This project is open for personal or internal use. Add a proper license file if redistributed.

---

