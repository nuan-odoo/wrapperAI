CHATBOT_CONFIGS = {
    "claude": {
        "url":         "https://claude.ai/new",
        "input_box":   'div[contenteditable="true"]',
        "send_button": 'button[aria-label="Send message"]',
        "response":    'div[data-testid="assistant-message"]',
        "auth":        "cookie",
    },
    "chatgpt": {
        "url":         "https://chatgpt.com",
        "input_box":   'div#prompt-textarea',
        "send_button": 'button[data-testid="send-button"]',
        "response":    'div[data-message-author-role="assistant"]',
        "auth":        "password",
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
        "auth":        "password",
        "login": {
            "email_field":    'input[type="email"]',
            "password_field": 'input[type="password"]',
            "submit_button":  'button[type="submit"]',
        }
    },
}
