import os
from dotenv import load_dotenv

load_dotenv()

CHATBOT_TARGET   = os.getenv("CHATBOT_TARGET", "claude").lower()
CHATBOT_EMAIL    = os.getenv("CHATBOT_EMAIL", "")
CHATBOT_PASSWORD = os.getenv("CHATBOT_PASSWORD", "")

# Add more chatbots here anytime
CHATBOT_CONFIGS = {
    "claude": {
        "url":         "https://claude.ai/new",
        "input_box":   'div[contenteditable="true"]',
        "send_button": 'button[aria-label="Send message"]',
        "response":    'div[data-testid="assistant-message"]',
        "login": {
            "email_field":    'input[type="email"]',
            "password_field": 'input[type="password"]',
            "submit_button":  'button[type="submit"]',
        }
    },
    "gemini": {
        "url":         "https://gemini.google.com",
        "input_box":   'div.ql-editor',
        "send_button": 'button.send-button',
        "response":    'message-content.model-response-text',
        "login": {
            "email_field":    'input[type="email"]',
            "password_field": 'input[type="password"]',
            "submit_button":  'button[type="submit"]',
        }
    },
    "chatgpt": {
        "url":         "https://chatgpt.com",
        "input_box":   'div#prompt-textarea',
        "send_button": 'button[data-testid="send-button"]',
        "response":    'div[data-message-author-role="assistant"]',
        "login": {
            "email_field":    'input[type="email"]',
            "password_field": 'input[type="password"]',
            "submit_button":  'button[type="submit"]',
        }
    },
}

# Validate the chosen target
if CHATBOT_TARGET not in CHATBOT_CONFIGS:
    raise ValueError(
        f"Unknown CHATBOT_TARGET '{CHATBOT_TARGET}'. "
        f"Choose from: {', '.join(CHATBOT_CONFIGS.keys())}"
    )

# Export the active config so browser_manager can just import it
ACTIVE_CONFIG = CHATBOT_CONFIGS[CHATBOT_TARGET]
CHATBOT_URL   = ACTIVE_CONFIG["url"]
SELECTORS     = ACTIVE_CONFIG