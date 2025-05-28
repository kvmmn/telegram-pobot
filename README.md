# Telegram Purchase Order (PO) Bot

## 1. Overview

This Telegram bot allows users to create Purchase Orders (POs) through a conversational interface. The created POs are then automatically saved to a designated Google Sheet for record-keeping and further processing.

## 2. Features

*   **Conversational PO Creation:** Guides users step-by-step to gather PO details.
*   **Google Sheets Integration:** Securely stores PO data in a specified Google Sheet.
*   **Simple Commands:** Easy-to-use commands like `/create_po` to initiate and `/cancel` to abort PO creation.
*   **State Management:** Remembers the user's progress during PO creation.
*   **Environment-based Configuration:** Securely managed via environment variables.

## 3. Prerequisites

*   Python 3.7+
*   A Telegram account.
*   A Google Cloud Platform (GCP) account with billing enabled (required for Google Sheets API usage beyond free tier limits, though basic usage is often free).
*   `git` for cloning the repository.

## 4. Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url> 
    # Replace <your-repository-url> with the actual URL of this repository
    ```
2.  **Navigate to Project Directory:**
    ```bash
    cd telegram-po-bot 
    # Or your chosen directory name
    ```
3.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    ```
4.  **Activate the Virtual Environment:**
    *   **Windows:**
        ```powershell
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
5.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 5. Configuration (Environment Variables)

This bot relies on environment variables for configuration. Ensure these are set in your deployment environment.

### 5.1. `TELEGRAM_BOT_TOKEN`

*   **How to get it:**
    1.  Open Telegram and search for "BotFather".
    2.  Start a chat with BotFather by sending the `/start` command.
    3.  Create a new bot by sending the `/newbot` command.
    4.  Follow the instructions provided by BotFather to choose a name and username for your bot.
    5.  BotFather will provide you with an API token. This is your `TELEGRAM_BOT_TOKEN`.
*   **Important:** Keep this token secure and do not share it publicly.
*   The `bot.py` script reads this token to connect to the Telegram API.

### 5.2. `GOOGLE_APPLICATION_CREDENTIALS`

*   This variable should hold the **absolute path** to the JSON key file for your Google Cloud service account.
*   **Setup Steps for Google Cloud Service Account & JSON Key:**
    1.  **Google Cloud Console Project:** Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project or select an existing one.
    2.  **Enable Google Sheets API:** In your project, navigate to "APIs & Services" -> "Library". Search for "Google Sheets API" and enable it.
    3.  **Create Service Account:**
        *   Go to "IAM & Admin" -> "Service Accounts".
        *   Click "+ CREATE SERVICE ACCOUNT".
        *   Provide a name (e.g., "telegram-po-bot-writer") and description.
        *   Click "CREATE AND CONTINUE".
        *   **Grant Role:** For simplicity, grant the "Editor" role (under "Basic" roles) to this service account for the project. For production, use a more restrictive role with only Google Sheets append permissions.
        *   Click "CONTINUE", then "DONE".
    4.  **Generate JSON Key:**
        *   Find your newly created service account.
        *   Go to its "KEYS" tab.
        *   Click "ADD KEY" -> "Create new key". Select "JSON".
        *   A JSON file will be downloaded. **Store this file securely and do NOT commit it to Git.**
*   The `google_sheets.py` script uses this key file to authenticate with Google Sheets.

### 5.3. `GOOGLE_SHEET_ID`

*   **How to get it:**
    1.  Create a new Google Sheet or use an existing one.
    2.  The Sheet ID is part of its URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`
*   **Share the Sheet:**
    *   Open your Google Sheet.
    *   Click the "Share" button.
    *   Add the service account's email address (found in the JSON key file as `client_email` or in the GCP console under service account details) and grant it "Editor" permissions for this specific sheet.
*   The `bot.py` script uses this ID to know which sheet to write to.

### 5.4. How to Set Environment Variables

*   **Linux/macOS (Terminal):**
    ```bash
    export TELEGRAM_BOT_TOKEN="YOUR_API_TOKEN"
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
    export GOOGLE_SHEET_ID="YOUR_SHEET_ID"
    ```
    (Add these to your shell's profile file like `~/.bashrc` or `~/.zshrc` for persistence)
*   **Windows (Command Prompt):**
    ```cmd
    set TELEGRAM_BOT_TOKEN="YOUR_API_TOKEN"
    set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\credentials.json"
    set GOOGLE_SHEET_ID="YOUR_SHEET_ID"
    ```
*   **Windows (PowerShell):**
    ```powershell
    $env:TELEGRAM_BOT_TOKEN="YOUR_API_TOKEN"
    $env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\credentials.json"
    $env:GOOGLE_SHEET_ID="YOUR_SHEET_ID"
    ```
    (For permanent settings on Windows, search for "environment variables" in the system settings.)

## 6. Running the Bot

1.  Ensure all dependencies are installed (see Section 4).
2.  Ensure all environment variables are correctly set (see Section 5).
3.  Activate your virtual environment if you haven't already:
    *   **Windows:** `venv\Scripts\activate`
    *   **macOS/Linux:** `source venv/bin/activate`
4.  Run the bot script:
    ```bash
    python bot.py
    ```
    The bot should now be running and connected to Telegram.

## 7. How to Use

1.  Open Telegram and find the bot you created (using the username you set with BotFather).
2.  Start a chat with your bot.
3.  Type `/start` to get a welcome message.
4.  Type `/create_po` to begin creating a new Purchase Order.
5.  The bot will prompt you for:
    *   Item/Service Description
    *   Quantity or Amount
    *   Supplier/Vendor
    *   Justification/Project Code
6.  After providing all details, the bot will show you a preview.
7.  Type `yes` to confirm and save the PO to Google Sheets.
8.  Type `cancel` at any point during the PO creation process (or when asked for confirmation) to abort.

## 8. Project Structure

```
.
├── bot.py                # Main Telegram bot logic, command handlers, conversation flow
├── google_sheets.py      # Functions for Google Sheets API interaction
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## 9. Troubleshooting

*   **`GOOGLE_APPLICATION_CREDENTIALS not found`**: Ensure the environment variable is set to the correct *absolute path* of your JSON key file and that the file exists at that path.
*   **`google.auth.exceptions.RefreshError` (or similar auth errors)**:
    *   Verify your service account JSON key is valid and not expired.
    *   Ensure the Google Sheets API is enabled in your GCP project.
    *   Check that the Google Sheet is shared with the correct service account email with "Editor" permissions.
*   **Bot not responding**:
    *   Check if the `TELEGRAM_BOT_TOKEN` is correct.
    *   Ensure the `python bot.py` script is running without errors in your terminal.
    *   Check your internet connection.
*   **Modules not found (e.g., `ImportError: No module named 'telegram'`)**: Make sure you have activated your virtual environment (`source venv/bin/activate` or `venv\Scripts\activate`) before running `pip install -r requirements.txt` and `python bot.py`.

## 10. Future Enhancements

*   **Unit Tests:** Implement comprehensive unit tests for better reliability and easier refactoring.
*   **Persistent State Management:** For scalability and to prevent data loss on bot restarts, replace the in-memory `conversation_states` dictionary with a persistent database solution (e.g., Redis, SQLite, or a cloud-based NoSQL DB).
*   **Advanced Input Validation:** Implement more specific validation for inputs like quantity (e.g., ensuring it's numeric) or dates if they were to be added.
*   **Webhook Support:** For production deployments, configure the bot to use webhooks instead of polling for improved efficiency and responsiveness.
*   **More Flexible Configuration:** Allow specifying target Google Sheet columns or other parameters via a configuration file or additional environment variables.
*   **Error Reporting:** Implement more robust error reporting, potentially sending alerts to an admin if critical failures occur (e.g., consistent failure to write to Google Sheets).
*   **Interactive PO Listing/Management:** Add commands to list recent POs or manage existing ones (though this would significantly increase complexity).

---
This README provides a comprehensive guide to setting up and using the Telegram PO Bot.
```
