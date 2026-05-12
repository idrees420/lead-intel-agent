import re
from typing import Optional

def validate_company_name(company_name: str) -> bool:
    """Validate company name format"""
    if not company_name or len(company_name.strip()) < 2:
        return False
    # Basic validation - no special characters except &, -, .
    pattern = r'^[a-zA-Z0-9\s\&\-\.]+$'
    return bool(re.match(pattern, company_name.strip()))

def validate_email_draft(email_content: str) -> tuple[bool, Optional[str]]:
    """Validate email draft for quality"""
    if not email_content or len(email_content) < 50:
        return False, "Email is too short"
    
    if len(email_content) > 1000:
        return False, "Email is too long (max 1000 characters)"
    
    # Check for placeholders
    placeholders = ['[Your Company]', '[Your Name]', '[Product]', '[Your Product]']
    for placeholder in placeholders:
        if placeholder in email_content:
            return False, f"Email contains placeholder: {placeholder}"
    
    # Check for generic phrases
    generic_phrases = [
        'i hope this email finds you well',
        'i am writing to you today',
        'i wanted to reach out',
        'i came across your company'
    ]
    
    email_lower = email_content.lower()
    for phrase in generic_phrases:
        if phrase in email_lower:
            return False, f"Email contains generic phrase: '{phrase}'"
    
    return True, None

def sanitize_feedback(feedback: str) -> str:
    """Sanitize and validate human feedback"""
    if not feedback:
        return ""
    
    # Remove any potentially harmful characters
    feedback = re.sub(r'[<>]', '', feedback)
    
    # Limit length
    if len(feedback) > 500:
        feedback = feedback[:500]
    
    return feedback.strip()