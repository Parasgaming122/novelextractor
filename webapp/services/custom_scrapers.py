"""
Custom web scrapers for free translation services
Implements Bing translator without API key requirements
"""
import re
import requests


class FreeBingTranslator:
    """
    Free Bing Translator using web scraping techniques.
    No API key required - extracts tokens from Bing homepage.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://bing.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.token = None
        self.key = None
        self.ig = None

    def _fetch_tokens(self):
        """Extract authentication tokens from Bing homepage"""
        try:
            res = self.session.get("https://bing.com", timeout=5)
            html = res.text
            
            # Extract IG parameter
            ig_match = re.search(r'IG:"([A-Z0-9]+)"', html)
            if ig_match:
                self.ig = ig_match.group(1)
            
            # Extract token and key from params_AbusePreventionHelper
            params_match = re.search(r'params_AbusePreventionHelper\s*=\s*\[(.*?)\];', html)
            if params_match:
                params_data = params_match.group(1).split(',')
                if len(params_data) >= 3:
                    self.token = params_data[1].strip('"\' ')
                    self.key = params_data[2].strip('"\' ')
                    
            return bool(self.token and self.ig)
        except Exception as e:
            print(f"Token fetch error: {e}")
            return False

    def translate(self, text: str, from_lang: str = "zh-Hans", to_lang: str = "en") -> str:
        """
        Translate text using Bing's free translation service
        
        Args:
            text: Text to translate
            from_lang: Source language code (default: zh-Hans for Chinese Simplified)
            to_lang: Target language code (default: en for English)
            
        Returns:
            Translated text or empty string on failure
        """
        # Fetch tokens if not already available
        if not self.token or not self.ig:
            if not self._fetch_tokens():
                return ""
        
        # Construct translation URL with IG parameter
        url = f"https://www.bing.com/ttranslatev3?IG={self.ig}&IID=translator.5026"
        
        payload = {
            'fromLang': from_lang,
            'to': to_lang,
            'text': text,
            'token': self.token,
            'key': self.key
        }
        
        try:
            res = self.session.post(url, data=payload, timeout=10)
            
            # Handle authentication errors by refreshing tokens
            if res.status_code in [401, 403]:
                self._fetch_tokens()
                return self.translate(text, from_lang, to_lang)
            
            # Parse response
            result = res.json()
            if result and len(result) > 0 and 'translations' in result[0]:
                return result[0]['translations'][0]['text']
                
            return ""
            
        except Exception as e:
            print(f"Bing translation error: {e}")
            return ""
