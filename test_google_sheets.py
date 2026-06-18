import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_google_sheets():
    """Test Google Sheets integration."""
    try:
        # Check if required environment variables are set
        required_vars = [
            'GOOGLE_APPLICATION_CREDENTIALS',
            'GOOGLE_SHEET_ID'
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                logger.error(f"{var} environment variable is not set")
                return False
        
        # Check if service account file exists
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not os.path.exists(creds_path):
            logger.error(f"Service account file not found at: {creds_path}")
            return False
            
        logger.info("All environment variables are set correctly")
        logger.info(f"Using service account: {creds_path}")
        
        # Import google_sheets after environment check
        import google_sheets
        
        # Test service initialization
        logger.info("Testing Google Sheets service initialization...")
        service = google_sheets.get_google_sheets_service()
        if not service:
            logger.error("Failed to initialize Google Sheets service")
            return False
            
        logger.info("Successfully initialized Google Sheets service")
        
        # Test sheet access
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        logger.info(f"Testing access to sheet ID: {sheet_id}")
        
        # Try to get sheet info
        try:
            sheet = service.spreadsheets()
            result = sheet.get(spreadsheetId=sheet_id).execute()
            logger.info(f"Successfully accessed sheet: {result.get('properties', {}).get('title')}")
            
            # Check if sheet has the required headers
            range_name = 'A1:Z1'  # Check first row for headers
            result = sheet.values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            headers = result.get('values', [[]])[0] if 'values' in result else []
            logger.info(f"Current headers in first row: {headers}")
            
            # Check if sheet is writable
            test_data = {
                'values': [
                    ['Test Header 1', 'Test Header 2', 'Test Header 3'],
                    ['Test Value 1', 'Test Value 2', 'Test Value 3']
                ]
            }
            
            append_result = sheet.values().append(
                spreadsheetId=sheet_id,
                range='A1',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=test_data
            ).execute()
            
            logger.info("Successfully wrote test data to sheet")
            logger.info(f"Update response: {append_result}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error accessing/writing to sheet: {str(e)}")
            if hasattr(e, 'content'):
                logger.error(f"Error details: {e.content.decode('utf-8')}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return False

if __name__ == '__main__':
    print("Testing Google Sheets integration...\n")
    success = test_google_sheets()
    
    if success:
        print("\n✅ Google Sheets integration test passed!")
    else:
        print("\n❌ Google Sheets integration test failed. Check the logs above for details.")
