#!/usr/bin/env python3
"""
Telegram Setup Script
Helps configure the correct chat ID for notifications.
"""
import requests
import json
from pathlib import Path


def setup_telegram():
    """Setup Telegram bot configuration."""
    bot_token = "7634324156:AAFupAZCihSHKq-mj3wBZ3tDLfeyzXl5aRo"
    
    print("🤖 Telegram Bot Setup")
    print("=" * 50)
    
    # Test bot connection
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        bot_info = response.json()
        
        if bot_info["ok"]:
            print(f"✅ Bot connected successfully!")
            print(f"Bot Name: {bot_info['result']['first_name']}")
            print(f"Bot Username: @{bot_info['result']['username']}")
        else:
            print("❌ Bot connection failed")
            return
    except Exception as e:
        print(f"❌ Error connecting to bot: {e}")
        return
    
    print("\n📱 To get your chat ID:")
    print("1. Start a chat with @FirstStrateggyybot")
    print("2. Send any message to the bot")
    print("3. Visit: https://api.telegram.org/bot7634324156:AAFupAZCihSHKq-mj3wBZ3tDLfeyzXl5aRo/getUpdates")
    print("4. Look for 'chat' -> 'id' in the response")
    
    # Get chat ID from user
    chat_id = input("\nEnter your chat ID: ").strip()
    
    if chat_id:
        # Test the chat ID
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": "✅ Telegram notifications configured successfully!",
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                print("✅ Chat ID verified! Test message sent successfully.")
                
                # Update configuration
                config_file = Path("ai_test_config.json")
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                else:
                    config = {
                        "telegram": {},
                        "testing": {},
                        "ai_analysis": {},
                        "reporting": {}
                    }
                
                config["telegram"]["chat_id"] = chat_id
                config["telegram"]["bot_token"] = bot_token
                config["telegram"]["notifications_enabled"] = True
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print(f"✅ Configuration updated in {config_file}")
            else:
                print(f"❌ Failed to send test message: {response.text}")
        except Exception as e:
            print(f"❌ Error testing chat ID: {e}")
    else:
        print("❌ No chat ID provided")


if __name__ == "__main__":
    setup_telegram() 