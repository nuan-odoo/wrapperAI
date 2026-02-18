import os
from dotenv import load_dotenv

load_dotenv()

CHATBOT_URL = os.getenv("CHATBOT_URL", "https://claude.ai/new")
CHATBOT_EMAIL = os.getenv("CHATBOT_EMAIL", "")
CHATBOT_PASSWORD = os.getenv("CHATBOT_PASSWORD", "")

# CSS selectors that point to elements in the chatbot's UI
# If you switch to a different chatbot, update these
SELECTORS = {
    "input_box":   'div[contenteditable="true"]',
    "send_button": 'button[aria-label="Send message"]',
    "response":    'div[data-testid="assistant-message"]',
}
