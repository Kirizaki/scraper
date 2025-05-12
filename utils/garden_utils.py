import re

def has_garden(text: str, keywords=None):
    ## POPRAWIĆ PRZESZUKIWANIE BODY TXT BO SZUKA W REKLAMACH!
    if keywords is None:
        keywords = ["ogród", "ogródek", "z ogrodem", "dostęp do ogrodu"]
    
    text_lower = text.lower()
    for keyword in keywords:
        match = re.search(rf"\b{re.escape(keyword)}\b", text_lower)
        if match:
            start = max(match.start() - 30, 0)
            end = min(match.end() + 30, len(text))
            return True, text[start:end]
    return False, None
