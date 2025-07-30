#!/usr/bin/env python3
"""
Test Telegram bot connection and find correct chat ID.
"""
import requests
import asyncio
from ai_test_analyzer import TelegramNotifier


async def test_telegram_connection():
    """Test Telegram bot connection."""
    bot_token = "7634324156:AAFupAZCihSHKq-mj3wBZ3tDLfeyzXl5aRo"
    
    # Test bot info
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        print(f"Bot Info: {response.json()}")
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
        return
    
    # Test with different chat ID formats
    chat_ids = [
        "1507876704",
        "@1507876704",
        "-1001507876704",
        "1507876704"
    ]
    
    for chat_id in chat_ids:
        print(f"\nTesting chat ID: {chat_id}")
        notifier = TelegramNotifier(bot_token, chat_id)
        
        try:
            success = await notifier.send_message("🤖 Test message from AI Testing System")
            if success:
                print(f"✅ Success with chat ID: {chat_id}")
                break
            else:
                print(f"❌ Failed with chat ID: {chat_id}")
        except Exception as e:
            print(f"❌ Error with chat ID {chat_id}: {e}")


if __name__ == "__main__":
    asyncio.run(test_telegram_connection()) 