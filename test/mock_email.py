"""
Mock email module for testing - prevents actual emails during tests
"""

def send_email(message):
    """Mock email function that just logs the message"""
    print(f"MOCK EMAIL: {message}")
