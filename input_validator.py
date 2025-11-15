"""
Input validation with character limits and safety checks
Prevents malicious or chaotic inputs that could break the model
"""
import re
from typing import Tuple, List


class InputValidator:
    """Validates user input for safety and quality"""
    
    # Configuration
    MAX_CHARS = 500  # Maximum characters allowed
    MIN_CHARS = 10   # Minimum for meaningful input
    
    # Forbidden patterns (potential prompt injection or malicious content)
    FORBIDDEN_PATTERNS = [
        # Prompt injection attempts
        r'ignore\s+(previous|all|above)',
        r'disregard\s+(instructions|rules|constraints)',
        r'new\s+instructions?:',
        r'system\s*:',
        r'assistant\s*:',
        r'you\s+are\s+now',
        r'forget\s+(everything|all)',
        
        # Command injection
        r'<\s*script',
        r'<\s*iframe',
        r'javascript:',
        r'eval\s*\(',
        r'exec\s*\(',
        
        # Extreme profanity or offensive content
        r'\b(fuck|shit|ass|bitch|damn)\w*\b',
        
        # Repetitive spam patterns
        r'(.)\1{20,}',  # Same character 20+ times
        r'(\w+)\s+\1\s+\1\s+\1',  # Same word 4+ times in row
    ]
    
    # Warning patterns (allowed but flagged)
    WARNING_PATTERNS = [
        (r'\d{10,}', "Contains very long numbers"),
        (r'[A-Z]{30,}', "Contains excessive capitalization"),
        (r'[!?]{5,}', "Contains excessive punctuation"),
        (r'https?://\S+', "Contains URLs (may not be processed)"),
    ]
    
    @classmethod
    def validate(cls, text: str) -> Tuple[bool, str, List[str]]:
        """
        Validate user input
        
        Returns:
            (is_valid, error_message, warnings)
        """
        warnings = []
        
        # 1. Check if empty
        if not text or not text.strip():
            return True, "", []  # Empty is OK (optional field)
        
        text = text.strip()
        
        # 2. Check character count
        char_count = len(text)
        if char_count < cls.MIN_CHARS:
            return False, f"Input too short (minimum {cls.MIN_CHARS} characters)", []
        
        if char_count > cls.MAX_CHARS:
            return False, f"Input too long (maximum {cls.MAX_CHARS} characters, you entered {char_count})", []
        
        # 3. Check for forbidden patterns
        text_lower = text.lower()
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "Input contains forbidden content or potential security risk", []
        
        # 4. Check for warning patterns
        for pattern, warning_msg in cls.WARNING_PATTERNS:
            if re.search(pattern, text):
                warnings.append(warning_msg)
        
        # 5. Check for excessive special characters (>30% of content)
        special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', text))
        if special_chars / char_count > 0.3:
            warnings.append("High density of special characters detected")
        
        # 6. Check for balanced parentheses/brackets (basic sanity check)
        if text.count('(') != text.count(')'):
            warnings.append("Unbalanced parentheses detected")
        if text.count('[') != text.count(']'):
            warnings.append("Unbalanced brackets detected")
        
        return True, "", warnings
    
    @classmethod
    def sanitize(cls, text: str) -> str:
        """
        Sanitize input by removing/replacing problematic content
        Use this as a fallback if you want to auto-clean instead of rejecting
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Limit consecutive special characters
        text = re.sub(r'([!?.]){5,}', r'\1\1\1', text)
        
        # Limit consecutive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Trim to max length if needed
        if len(text) > cls.MAX_CHARS:
            text = text[:cls.MAX_CHARS].rsplit(' ', 1)[0] + "..."
        
        return text.strip()
