import os
import logging
import datetime # Added import
from telegram.ext import Application, CommandHandler, MessageHandler, Filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration - Load from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID") # Placeholder

if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
    # It's good practice to exit or raise an error if critical config is missing
    # For this exercise, we'll just log the error.
    # exit(1) # Or raise EnvironmentError("TELEGRAM_BOT_TOKEN not set")

# State Management
conversation_states = {}

# Command Handlers
def start(update, context):
    """Sends a welcome message when the /start command is issued."""
    logger.info(f"User {update.effective_user.id} started the bot.")
    update.message.reply_text('Hello! I am your new Telegram bot. Use /create_po to start creating a Purchase Order.')

def start_po_creation(update, context):
    """Starts the Purchase Order creation process."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} initiated PO creation with /create_po.")
    conversation_states[user_id] = {'step': 1, 'po_data': {}}
    update.message.reply_text("Great! Let's create a new PO. What is the item or service you are purchasing?")

def cancel_po_creation(update, context):
    """Cancels the current Purchase Order creation process."""
    user_id = update.effective_user.id
    if user_id in conversation_states:
        del conversation_states[user_id]
        logger.info(f"User {user_id} cancelled PO creation.")
        update.message.reply_text("Purchase Order creation cancelled.")
    else:
        logger.info(f"User {user_id} tried to cancel PO creation, but no active process found.")
        update.message.reply_text("No active Purchase Order creation to cancel.")

def main():
    """Starts the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.critical("Bot cannot start without TELEGRAM_BOT_TOKEN.")
        return

    logger.info("Starting bot...")
    # Create the Application instance
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Get the dispatcher to register handlers
    # (Using application.add_handler directly is the modern way)

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("create_po", start_po_creation))
    application.add_handler(CommandHandler("cancel", cancel_po_creation))

    # Message handler for collecting PO data
    application.add_handler(MessageHandler(Filters.TEXT & ~Filters.COMMAND, handle_message))

    # Start the Bot
    logger.info("Bot started. Polling for updates...")
    application.run_polling()

    # Keep the bot running until you press Ctrl-C (handled by run_polling)
    # updater.idle() # Not needed with Application.run_polling()

# Message Handler for Data Collection
def handle_message(update, context):
    """Handles text messages for PO data collection."""
    user_id = update.effective_user.id
    text = update.message.text
    logger.info(f"User {user_id} sent text: '{text}'")

    if user_id not in conversation_states or 'step' not in conversation_states[user_id]:
        logger.warning(f"User {user_id} sent message '{text}' without active PO creation process.")
        update.message.reply_text("Please start by creating a Purchase Order using /create_po.")
        return

    current_step = conversation_states[user_id]['step']

    if current_step == 1:
        # Step 1: Handle Item Description
        logger.info(f"User {user_id} - PO Step 1: Item Description - '{text}'")
        conversation_states[user_id]['po_data']['item_description'] = text
        conversation_states[user_id]['step'] = 2
        update.message.reply_text("Got it. What is the quantity or total amount for this PO? (e.g., 5 units, or $250.00)")
    elif current_step == 2:
        # Step 2: Handle Quantity/Amount
        logger.info(f"User {user_id} - PO Step 2: Quantity/Amount - '{text}'")
        conversation_states[user_id]['po_data']['quantity_amount'] = text
        conversation_states[user_id]['step'] = 3
        update.message.reply_text("Understood. Who is the supplier or vendor?")
    elif current_step == 3:
        # Step 3: Handle Supplier/Vendor
        logger.info(f"User {user_id} - PO Step 3: Supplier/Vendor - '{text}'")
        conversation_states[user_id]['po_data']['supplier_vendor'] = text
        conversation_states[user_id]['step'] = 4
        update.message.reply_text("Almost there! Please provide a brief justification or project code for this PO.")
    elif current_step == 4:
        # Step 4: Handle Justification
        logger.info(f"User {user_id} - PO Step 4: Justification - '{text}'")
        conversation_states[user_id]['po_data']['justification'] = text
        requester_name = update.effective_user.full_name
        conversation_states[user_id]['po_data']['requester_name'] = requester_name
        conversation_states[user_id]['step'] = 5  # Confirmation step

        # Compile PO Preview
        po_data = conversation_states[user_id]['po_data']
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        preview_message = f"""PO Preview:
Item: {po_data.get('item_description', 'N/A')}
Amount/Qty: {po_data.get('quantity_amount', 'N/A')}
Supplier: {po_data.get('supplier_vendor', 'N/A')}
Justification: {po_data.get('justification', 'N/A')}
Requested by: {requester_name}
Date: {current_date}"""
        update.message.reply_text(preview_message + "\n\nIs this correct? (Type 'yes' to confirm or 'cancel' to start over)")
    elif current_step == 5:
        # Step 5: Waiting for confirmation ('yes' or 'cancel')
        logger.info(f"User {user_id} is at confirmation step (Step 5). Waiting for 'yes' or 'cancel'. Input: '{text}'")
        # Step 5: Waiting for confirmation ('yes' or 'cancel')
        logger.info(f"User {user_id} is at confirmation step (Step 5). Waiting for 'yes' or 'cancel'. Input: '{text}'")
        response_text = text.lower()
        if response_text == 'yes':
            finalize_po(update, context, user_id)
        elif response_text == 'cancel':
            # Re-use the cancel_po_creation logic
            # Need to pass update and context correctly
            # Since cancel_po_creation expects update, context, we can call it directly
            cancel_po_creation(update, context)
        else:
            update.message.reply_text("Please type 'yes' to confirm or 'cancel' to start over.")
    else:
        logger.warning(f"User {user_id} is at an undefined PO step {current_step} with message '{text}'.")
        update.message.reply_text("I'm not sure what to do with that input right now. You might need to restart with /create_po or /cancel.")


import google_sheets # Added import

# Function to finalize PO
def finalize_po(update, context, user_id):
    """Finalizes the Purchase Order and attempts to save it to Google Sheets."""
    if user_id not in conversation_states or 'po_data' not in conversation_states[user_id]:
        logger.error(f"finalize_po called for user {user_id} but no PO data found in conversation_states.")
        update.message.reply_text("Sorry, something went wrong. I couldn't find your PO data to finalize.")
        return

    po_data_to_save = conversation_states[user_id]['po_data'].copy()
    logger.info(f"PO confirmed by user {user_id}. Data: {po_data_to_save}. Attempting to save to Google Sheets.")

    sheet_id = os.environ.get('GOOGLE_SHEET_ID')
    if not sheet_id:
        logger.error("GOOGLE_SHEET_ID environment variable not set.")
        update.message.reply_text("PO confirmed, but Google Sheet ID not configured. Cannot save PO. Please contact an admin.")
        # Clear state even if saving fails to prevent resubmission issues
        if user_id in conversation_states:
            del conversation_states[user_id]
            logger.info(f"Cleared conversation state for user {user_id} after GOOGLE_SHEET_ID config error.")
        return

    service = google_sheets.get_google_sheets_service()
    if service:
        saved_po_id = google_sheets.append_po_to_sheet(service, sheet_id, po_data_to_save)
        if saved_po_id:
            # Escape MarkdownV2 characters for the PO ID
            escaped_po_id = saved_po_id.replace('-', '\\-').replace('.', '\\.') # Basic escaping for common chars in PO ID
            message_text = f"PO `{escaped_po_id}` created successfully and saved to Google Sheets!"
            update.message.reply_text(message_text, parse_mode='MarkdownV2')
            logger.info(f"Successfully saved PO {saved_po_id} to Google Sheets for user {user_id}.")
        else:
            update.message.reply_text(f"PO confirmed, but failed to save to Google Sheets. Please contact an admin. Ref: {user_id}")
            logger.error(f"Failed to save PO to Google Sheets for user {user_id}. Data: {po_data_to_save}")
    else:
        update.message.reply_text(f"PO confirmed, but Google Sheets service could not be initialized. Please contact an admin. Ref: {user_id}")
        logger.error(f"Google Sheets service could not be initialized for user {user_id} when trying to save PO.")

    # Clear Conversation State
    if user_id in conversation_states:
        del conversation_states[user_id]
        logger.info(f"Cleared conversation state for user {user_id} after PO finalization attempt.")


if __name__ == '__main__':
    main()
