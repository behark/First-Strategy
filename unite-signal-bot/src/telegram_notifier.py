"""
Telegram Notifier Module

Sends trading signals to Telegram.
"""
import logging
import requests
from time import sleep
from src.signal_engine import Signal

logger = logging.getLogger(__name__)

class TelegramAPIError(Exception):
    """Exception raised when Telegram API request fails."""
    pass


class TelegramNotifier:
    """
    Sends trading signals to Telegram.
    
    Attributes:
        bot_token: Telegram bot token
        chat_id: Telegram chat ID
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize TelegramNotifier instance.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
    def send_signal(self, signal: Signal) -> None:
        """
        Send trading signal to Telegram.
        
        Args:
            signal: Trading signal
            
        Raises:
            TelegramAPIError: If Telegram API request fails
        """
        # Format message
        emoji = "🚀" if signal.direction.value == "LONG" else "🔻"
        message = (
            f"{emoji} {signal.direction.value} @ {signal.entry_price:.6f} | "
            f"TP: {signal.take_profit:.6f} | "
            f"SL: {signal.stop_loss:.6f} | "
            f"t={signal.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        )
        
        # Send message
        self._send_message(message)
        
    def _send_message(self, message: str, retry_count: int = 0) -> None:
        """
        Send message to Telegram.
        
        Args:
            message: Message text
            retry_count: Current retry count
            
        Raises:
            TelegramAPIError: If Telegram API request fails after max retries
        """
        max_retries = 3
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
            
            # Handle response
            if response.status_code == 200:
                logger.info("Message sent successfully")
                return
                
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                logger.warning(f"Rate limited, retrying after {retry_after}s")
                sleep(retry_after)
                self._send_message(message, retry_count)
                return
                
            # Handle authentication error
            if response.status_code == 401:
                logger.error("Authentication failed, check bot token")
                raise TelegramAPIError("Authentication failed, check bot token")
                
            # Handle server errors
            if response.status_code >= 500:
                if retry_count < max_retries:
                    backoff = 2 ** retry_count
                    logger.warning(f"Server error {response.status_code}, retrying in {backoff}s")
                    sleep(backoff)
                    self._send_message(message, retry_count + 1)
                    return
                else:
                    logger.error(f"Server error {response.status_code} after {max_retries} retries")
                    raise TelegramAPIError(f"Server error {response.status_code} after {max_retries} retries")
                    
            # Handle other errors
            logger.error(f"Telegram API error: {response.status_code} - {response.text}")
            raise TelegramAPIError(f"Telegram API error: {response.status_code} - {response.text}")
            
        except requests.RequestException as e:
            if retry_count < max_retries:
                backoff = 2 ** retry_count
                logger.warning(f"Request error: {e}, retrying in {backoff}s")
                sleep(backoff)
                self._send_message(message, retry_count + 1)
            else:
                logger.error(f"Request error: {e} after {max_retries} retries")
                raise TelegramAPIError(f"Request error: {e} after {max_retries} retries")
