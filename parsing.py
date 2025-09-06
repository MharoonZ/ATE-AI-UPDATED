"""
Text Parsing Module for ATE Equipment

This module provides text parsing functionality to extract equipment information
from free-form text input, including brand names, model numbers, and options.

Key Features:
- Brand and model extraction from natural language
- Options parsing with slash-separated format
- Filtering of common connecting words
- Deterministic option splitting

Dependencies:
- typing: Type hints for better code documentation
"""

from typing import Dict


def parse_query(text: str) -> Dict[str, str]:
    """
    Parse free-form text to extract equipment brand, model, and options.
    
    This function analyzes input text to identify equipment specifications
    in various formats, handling both simple brand/model pairs and complex
    option lists separated by slashes.
    
    Args:
        text (str): Input text containing equipment information
        
    Returns:
        Dict[str, str]: Parsed equipment data with keys:
            - brand: Equipment manufacturer name
            - model: Equipment model number
            - raw_options: Unprocessed options string
    """
    # Clean input text by removing leading/trailing whitespace
    text = text.strip()
    
    # Look for the first "/" to separate brand/model from options
    slash_index = text.find("/")
    
    if slash_index == -1:
        # No options found, just brand and model
        words = text.split()
        # Filter out common connecting words that don't represent equipment info
        filtered_words = [word for word in words if word.lower() not in ["with", "options", "option", "like", "such", "as", "enter", "a", "query", "like"]]
        
        # Extract brand (first meaningful word) and model (second meaningful word)
        brand = filtered_words[0] if filtered_words else ""
        model = filtered_words[1] if len(filtered_words) > 1 else ""
        
        return {"brand": brand, "model": model, "raw_options": ""}
    
    # Find the end of options (next space after the last "/" sequence)
    # Look for patterns like "/160/EEC/PLK/UK6 has to be" -> stop at "has"
    options_end_index = slash_index
    current_pos = slash_index
    
    # Iterate through all slashes to find the complete options section
    while current_pos < len(text):
        # Find next "/" character
        next_slash = text.find("/", current_pos + 1)
        if next_slash == -1:
            # No more slashes, find the next space to determine end
            next_space = text.find(" ", current_pos)
            if next_space == -1:
                # No space found, take everything to the end
                options_end_index = len(text)
            else:
                # Found space, check if there's a word after the last "/"
                last_part = text[current_pos:next_space].strip()
                if last_part and not last_part.startswith("/"):
                    # There's a word after the last "/", include it
                    options_end_index = next_space
                else:
                    # Just slashes, stop at the last "/"
                    options_end_index = current_pos + 1
            break
        else:
            # Found another "/", continue searching
            current_pos = next_slash
    
    # Extract brand/model part (everything before first "/")
    brand_model_part = text[:slash_index].strip()
    brand_model_words = brand_model_part.split()
    
    # Filter out common connecting words from brand/model section
    filtered_words = [word for word in brand_model_words if word.lower() not in ["with", "options", "option", "like", "such", "as", "enter", "a", "query", "like"]]
    
    # Extract brand (first meaningful word) and model (second meaningful word)
    brand = filtered_words[0] if filtered_words else ""
    model = filtered_words[1] if len(filtered_words) > 1 else ""
    
    # Find the last word before the "/" - this should be the first option
    last_word_before_slash = ""
    if brand_model_words:
        last_word = brand_model_words[-1]
        # If the last word is not a connecting word, it's the first option
        if last_word.lower() not in ["with", "options", "option", "like", "such", "as", "enter", "a", "query", "like"]:
            last_word_before_slash = last_word
    
    # Extract options part (from first "/" to end of options)
    options_part = text[slash_index:options_end_index].strip()
    
    # Don't combine with last word before slash to avoid including model name
    raw_options = options_part
    
    return {"brand": brand, "model": model, "raw_options": raw_options}


def split_options_deterministic(raw_options: str) -> list[str]:
    """
    Deterministic option splitter that splits on '/' and cleans up each option.
    
    This function takes a raw options string (e.g., "/160/EEC/PLK/UK6") and
    splits it into a clean list of individual options, removing empty entries
    and whitespace.
    
    Args:
        raw_options (str): Raw options string with slash separators
        
    Returns:
        list[str]: Clean list of individual options
    """
    if not raw_options:
        return []
    
    # Split on '/' and clean each option
    options = []
    for option in raw_options.split('/'):
        option = option.strip()  # Remove leading/trailing whitespace
        if option:  # Only add non-empty options
            options.append(option)
    
    return options


