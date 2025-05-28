import os
import datetime
import logging
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False
    logging.error("Google API libraries are not installed. Please install google-api-python-client, google-auth-httplib2, and google-auth-oauthlib.")

logger = logging.getLogger(__name__)

def get_google_sheets_service():
    """
    Authenticates and returns a service object for the Google Sheets API.
    Credentials are loaded from the GOOGLE_APPLICATION_CREDENTIALS environment variable.
    """
    if not GOOGLE_LIBS_AVAILABLE:
        logger.error("Google libraries not found. Cannot initialize Google Sheets service.")
        return None

    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path:
        logger.error("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
        return None

    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
        service = build('sheets', 'v4', credentials=creds)
        logger.info("Google Sheets service initialized successfully.")
        return service
    except FileNotFoundError:
        logger.error(f"Service account file not found at: {creds_path}")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets service: {e}")
        return None

def append_po_to_sheet(service, sheet_id, po_data):
    """
    Appends a Purchase Order to the specified Google Sheet.

    Args:
        service: The Google Sheets API service object.
        sheet_id: The ID of the Google Sheet.
        po_data: A dictionary containing the PO data.

    Returns:
        The po_id if successful, None otherwise.
    """
    if not service:
        logger.error("Google Sheets service is not available. Cannot append PO.")
        return None
    if not sheet_id:
        logger.error("Google Sheet ID is not provided. Cannot append PO.")
        return None

    try:
        po_id = f"PO-{int(datetime.datetime.now().timestamp())}"
        po_data['po_id'] = po_id # Add po_id to the dictionary for completeness

        # Define the order of columns for the sheet
        # Ensure 'timestamp' is the last one as it's generated here
        column_order = ['po_id', 'item_description', 'quantity_amount', 'supplier_vendor', 'justification', 'requester_name', 'timestamp']
        
        row_values = []
        for col_name in column_order:
            if col_name == 'timestamp':
                row_values.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                row_values.append(po_data.get(col_name, "")) # Default to empty string if key missing

        body = {
            'values': [row_values]
        }

        request = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range='A1',  # Appends after the last row with data in this range
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        )
        response = request.execute()
        logger.info(f"Successfully appended PO {po_id} to sheet. Response: {response}")
        return po_id
    except Exception as e:
        logger.error(f"Failed to append PO {po_data.get('po_id', 'N/A')} to sheet: {e}")
        return None

if __name__ == '__main__':
    # Example Usage (for testing, requires env vars to be set)
    # This part will not run during bot operation but can be used for direct script testing.
    logger.info("Testing Google Sheets module...")
    if GOOGLE_LIBS_AVAILABLE:
        test_service = get_google_sheets_service()
        if test_service:
            test_sheet_id = os.environ.get("GOOGLE_SHEET_ID") # Make sure this is set for testing
            if test_sheet_id:
                test_po_data = {
                    'item_description': 'Test Item from script',
                    'quantity_amount': '1 unit',
                    'supplier_vendor': 'Test Supplier',
                    'justification': 'Test Justification',
                    'requester_name': 'Script Test User'
                }
                logger.info(f"Attempting to append test PO data to sheet ID: {test_sheet_id}")
                new_po_id = append_po_to_sheet(test_service, test_sheet_id, test_po_data)
                if new_po_id:
                    logger.info(f"Test PO appended successfully. PO ID: {new_po_id}")
                else:
                    logger.error("Failed to append test PO.")
            else:
                logger.error("GOOGLE_SHEET_ID environment variable not set. Cannot run test append.")
        else:
            logger.error("Failed to get Google Sheets service for testing.")
    else:
        logger.warning("Google client libraries not installed, skipping Google Sheets specific tests.")
