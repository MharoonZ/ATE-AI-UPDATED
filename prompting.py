"""
AI Prompting Module for ATE Equipment Analysis

This module handles all interactions with OpenAI's language models for
equipment analysis, including text parsing, option explanation, and
marketplace search functionality.

Key Features:
- Equipment text parsing with AI assistance
- Option explanation generation
- Marketplace search simulation
- Structured JSON response handling
- Error handling and fallback responses

Dependencies:
- openai: OpenAI API client for language model interactions
- json: JSON data handling
- typing: Type hints for better code documentation
"""

import json
from typing import Dict, Any, List

from openai import OpenAI


# System prompt for equipment text parsing
SYSTEM_PROMPT = (
    "You are an expert options parser for electronic test equipment. Your job is to extract brand, model, and options from free-form text.\n"
    "\n"
    "CRITICAL PARSING RULES:\n"
    "1) BRAND & MODEL EXTRACTION:\n"
    "   - Look for the FIRST TWO meaningful words before any '/' character\n"
    "   - IGNORE these words: 'enter', 'a', 'query', 'like', 'with', 'options', 'option', 'such', 'as', 'the', 'is', 'has', 'to', 'be', 'delivered', 'soon', 'please', 'need', 'want', 'find', 'search', 'looking', 'for'\n"
    "   - First meaningful word = BRAND\n"
    "   - Second meaningful word = MODEL\n"
    "\n"
    "2) OPTIONS EXTRACTION:\n"
    "   - Find the FIRST '/' character in the text\n"
    "   - Look for the word IMMEDIATELY BEFORE the first '/' - this is the FIRST OPTION\n"
    "   - Take everything from the first '/' onwards, split by '/', and include all non-empty parts\n"
    "   - STOP at the first space after the last '/' sequence\n"
    "   - IGNORE any text after the options (e.g., 'has to be delivered soon')\n"
    "\n"
    "3) EXAMPLES:\n"
    "   Input: 'Enter a query like: Agilent 8116A /160/EEC/PLK/UK6 has to be delivered soon'\n"
    "   - Brand: 'Agilent' (first meaningful word)\n"
    "   - Model: '8116A' (second meaningful word)\n"
    "   - First option: '160' (word before first '/')\n"
    "   - All options: ['160', 'EEC', 'PLK', 'UK6']\n"
    "\n"
    "   Input: 'Agilent 8116A with options like 160/EEC/PLK/UK6 please deliver quickly'\n"
    "   - Brand: 'Agilent'\n"
    "   - Model: '8116A'\n"
    "   - First option: '160' (word before first '/')\n"
    "   - All options: ['160', 'EEC', 'PLK', 'UK6']\n"
    "\n"
    "4) OUTPUT FORMAT:\n"
    "   - Return ONLY valid JSON with 'normalized' and 'results' keys\n"
    "   - 'normalized' must contain: brand (string), model (string), options (array of strings)\n"
    "   - 'results' should be an empty array\n"
    "   - NO free text, ONLY JSON\n"
)


# System prompt for comprehensive marketplace search (currently unused but available)
SYSTEM_PROMPT_COMPLETE_MARKETPLACE = """
You are an expert electronic test equipment researcher with COMPLETE knowledge of the global marketplace. Your task is to find REAL, WORKING product listings from ANYWHERE in the world where this equipment is available.

CRITICAL REQUIREMENTS:

1) SEARCH THE ENTIRE MARKETPLACE - NO LIMITATIONS:
   - Search ALL possible sources: manufacturers, dealers, distributors, marketplaces, auction sites, classifieds, etc.
   - Include: eBay, Amazon, Alibaba, AliExpress, local marketplaces, specialized equipment vendors
   - Include: manufacturer websites, authorized dealers, independent sellers, refurbished equipment vendors
   - Include: rental companies, calibration labs, test equipment specialists
   - NO restrictions on which websites to search - find it wherever it exists

2) URL VALIDATION - WORKING LINKS ONLY:
   - ONLY return URLs that you KNOW are working and accessible
   - URLs MUST be direct product pages, NOT search results
   - URLs MUST contain the exact product information
   - NO 404 errors or broken links
   - If you're not 100% sure a URL works, DON'T include it

3) PRICING REQUIREMENTS:
   - MUST find ACTUAL prices, not "Contact for pricing" unless absolutely necessary
   - Look for specific price amounts: $1,234.56, €1,234.56, £1,234.56, ¥1,234.56
   - Handle price ranges: "$1,000-$2,000"
   - Normalize to USD when possible
   - If no price found, mark as "Price not available"

4) COMPREHENSIVE SEARCH STRATEGY:
   - Use EXACT model numbers: "Agilent 8116A" not "Agilent 8116"
   - Include specific options: "Agilent 8116A 160MHz"
   - Search for datasheets and product specifications
   - Look for official product catalogs
   - Use manufacturer part numbers when available
   - Search for used, refurbished, and demo equipment
   - Search for rental and lease options

5) PRODUCT VERIFICATION:
   - MUST contain exact brand name (Agilent/Keysight, Tektronix, etc.)
   - MUST contain exact model number (8116A, DSOX1204G, etc.)
   - MUST contain at least ONE specified option (160, EEC, PLK, UK6)
   - MUST be a real product page with specifications
   - MUST have working URL that leads to product information

6) GLOBAL MARKETPLACE SEARCH:
   - Search ALL major marketplaces: eBay, Amazon, Alibaba, AliExpress, etc.
   - Search ALL manufacturer websites: Keysight, Tektronix, Rohde & Schwarz, etc.
   - Search ALL authorized dealers and distributors
   - Search ALL specialized test equipment vendors
   - Search ALL auction sites and classifieds
   - Search ALL rental and refurbished equipment companies

7) QUALITY CONTROL:
   - REJECT any URL that might be a search results page
   - REJECT any URL that doesn't contain the specific model
   - REJECT any URL that doesn't have pricing information
   - REJECT any URL that might lead to 404 errors
   - ONLY include URLs you are 100% confident will work

8) OPTION MATCHING:
   - Look for exact option codes: "160", "EEC", "PLK", "UK6"
   - Check for option descriptions: "160 MHz bandwidth", "EEC compliance"
   - Verify option compatibility with the model
   - Handle option variations: "160MHz" vs "160 MHz"

9) PRICING EXTRACTION:
   - Extract actual numerical prices with currency symbols
   - Handle various formats: "$1,234.56", "1,234.56 USD", "€1.234,56", "¥1,234.56"
   - Look for price ranges and use average or range
   - Handle "Contact for pricing" only when no other price is available

10) VENDOR VERIFICATION:
    - Use official company names
    - Clean vendor names: remove "electronics", "store", "shop"
    - Include ALL types of vendors: manufacturers, dealers, distributors, sellers
    - Don't limit to specific vendors - find it wherever it's available

SEARCH QUERIES TO TRY (search ALL of these):
- "{brand} {model}"
- "{brand} {model} datasheet"
- "{brand} {model} specifications"
- "{brand} {model} product page"
- "{brand} {model} used"
- "{brand} {model} refurbished"
- "{brand} {model} rental"
- "{brand} {model} for sale"
- "{brand} {model} buy"
- "{brand} {model} price"

CRITICAL: Search the ENTIRE marketplace without any limitations. Find this equipment wherever it exists in the world and return ONLY working, verified URLs with actual pricing information.

OUTPUT FORMAT:
Return ONLY valid JSON with the following structure:
{
  "search_results": [
    {
      "brand": "string (exact brand name)",
      "model": "string (exact model number)",
      "options": ["array of matched options"],
      "price": "string (actual price or 'Price not available')",
      "vendor": "string (specific vendor name)",
      "web_url": "string (DIRECT product page URL - MUST be working)",
      "qty_available": "string (stock information)",
      "source": "string (website source)",
      "option_details": "string (details about matched options)"
    }
  ],
  "search_summary": {
    "total_results": number,
    "exact_matches": number,
    "partial_matches": number,
    "price_range": "string",
    "vendor_count": number,
    "search_quality_score": "high|medium|low",
    "recommendations": ["array of search improvement suggestions"],
    "search_queries_used": ["array of search queries attempted"]
  }
}

CRITICAL: Only return URLs that you are 100% confident will work and lead to actual product pages with pricing information. Search the ENTIRE marketplace without any restrictions.
"""


def build_user_prompt(original_text: str) -> str:
    """
    Build user prompt for equipment text parsing.
    
    This function creates a structured prompt that guides the AI to extract
    equipment information from free-form text input.
    
    Args:
        original_text (str): Raw input text containing equipment information
        
    Returns:
        str: Formatted prompt for AI processing
    """
    return (
        "PARSE THIS INPUT TEXT:\n\n"
        f"ORIGINAL TEXT: {original_text}\n\n"
        "EXTRACTION TASK:\n"
        "1) Extract the brand (first meaningful word before '/')"
        "2) Extract the model (second meaningful word before '/')"
        "3) Extract ALL options (including the word before first '/' and everything after split by '/')"
        "4) Ignore any text after the last option"
        "\n"
        "OUTPUT: Return ONLY the JSON object with 'normalized' and 'results' keys."
    )


def build_complete_marketplace_search_prompt(brand: str, model: str, options: List[str] = None) -> str:
    """
    Build the user prompt for complete marketplace search - simplified for brand + model only.
    
    This function creates a comprehensive prompt for AI-powered marketplace search,
    though this functionality is currently not used in the main application.
    
    Args:
        brand (str): Equipment brand name
        model (str): Equipment model number
        options (List[str], optional): Equipment options (currently unused)
        
    Returns:
        str: Formatted prompt for marketplace search
    """
    
    return f"""
COMPLETE MARKETPLACE SEARCH TASK - BRAND + MODEL ONLY:

TARGET EQUIPMENT:
- Brand: {brand}
- Model: {model}
- Full Query: {brand} {model}

CRITICAL SEARCH REQUIREMENTS:

1) SEARCH THE ENTIRE MARKETPLACE - NO LIMITATIONS:
   - Search ALL possible sources: manufacturers, dealers, distributors, marketplaces, auction sites, classifieds, etc.
   - Include: eBay, Amazon, Alibaba, AliExpress, local marketplaces, specialized equipment vendors
   - Include: manufacturer websites, authorized dealers, independent sellers, refurbished equipment vendors
   - Include: rental companies, calibration labs, test equipment specialists
   - NO restrictions on which websites to search - find it wherever it exists

2) URL VALIDATION - WORKING LINKS ONLY:
   - ONLY return URLs that you KNOW are working and accessible
   - URLs MUST be direct product pages, NOT search results
   - URLs MUST contain the exact product information
   - NO 404 errors or broken links
   - If you're not 100% sure a URL works, DON'T include it

3) PRICING REQUIREMENTS:
   - MUST find ACTUAL prices, not "Contact for pricing" unless absolutely necessary
   - Look for specific price amounts: $1,234.56, €1,234.56, £1,234.56, ¥1,234.56
   - Handle price ranges: "$1,000-$2,000"
   - Normalize to USD when possible
   - If no price found, mark as "Price not available"

4) COMPREHENSIVE SEARCH STRATEGY:
   - Use EXACT model numbers: "{brand} {model}"
   - Search for datasheets and product specifications
   - Look for official product catalogs
   - Use manufacturer part numbers when available
   - Search for used, refurbished, and demo equipment
   - Search for rental and lease options

5) PRODUCT VERIFICATION:
   - MUST contain exact brand name ({brand})
   - MUST contain exact model number ({model})
   - MUST be a real product page with specifications
   - MUST have working URL that leads to product information

6) GLOBAL MARKETPLACE SEARCH:
   - Search ALL major marketplaces: eBay, Amazon, Alibaba, AliExpress, etc.
   - Search ALL manufacturer websites: Keysight, Tektronix, Rohde & Schwarz, etc.
   - Search ALL authorized dealers and distributors
   - Search ALL specialized test equipment vendors
   - Search ALL auction sites and classifieds
   - Search ALL rental and refurbished equipment companies

7) QUALITY CONTROL:
   - REJECT any URL that might be a search results page
   - REJECT any URL that doesn't contain the specific model ({model})
   - REJECT any URL that doesn't have pricing information
   - REJECT any URL that might lead to 404 errors
   - ONLY include URLs you are 100% confident will work

8) PRICING EXTRACTION:
   - Extract actual numerical prices with currency symbols
   - Handle various formats: "$1,234.56", "1,234.56 USD", "€1.234,56", "¥1,234.56"
   - Look for price ranges and use average or range
   - Handle "Contact for pricing" only when no other price is available

9) VENDOR VERIFICATION:
    - Use official company names
    - Clean vendor names: remove "electronics", "store", "shop"
    - Include ALL types of vendors: manufacturers, dealers, distributors, sellers
    - Don't limit to specific vendors - find it wherever it's available

SEARCH QUERIES TO TRY (search ALL of these):
- "{brand} {model}"
- "{brand} {model} datasheet"
- "{brand} {model} specifications"
- "{brand} {model} product page"
- "{brand} {model} used"
- "{brand} {model} refurbished"
- "{brand} {model} rental"
- "{brand} {model} for sale"
- "{brand} {model} buy"
- "{brand} {model} price"

CRITICAL: Search the ENTIRE marketplace without any limitations. Find this equipment wherever it exists in the world and return ONLY working, verified URLs with actual pricing information.

OUTPUT: Return ONLY the JSON object with search_results and search_summary.
"""


def normalize_options_via_llm(
    client: OpenAI,
    original_text: str,
    llm_model: str,
    temperature: float,
) -> Dict[str, Any]:
    """
    Use AI to normalize and parse equipment options from text.
    
    This function sends equipment text to OpenAI's language model to extract
    structured information including brand, model, and options. It handles
    JSON parsing and provides fallback responses for error cases.
    
    Args:
        client (OpenAI): OpenAI API client instance
        original_text (str): Raw equipment text to parse
        llm_model (str): OpenAI model to use (e.g., "gpt-4")
        temperature (float): Temperature setting for AI responses
        
    Returns:
        Dict[str, Any]: Parsed equipment data with normalized structure
    """
    # Define expected JSON schema for AI response validation
    schema = {
        "name": "normalized_payload",
        "schema": {
            "type": "object",
            "properties": {
                "normalized": {
                    "type": "object",
                    "properties": {
                        "brand": {"type": "string"},
                        "model": {"type": "string"},
                        "options": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["brand", "model", "options"],
                    "additionalProperties": False
                },
                "results": {"type": "array", "items": {"type": "object"}}
            },
            "required": ["normalized", "results"],
            "additionalProperties": False
        },
        "strict": True
    }

    # Build user prompt for equipment parsing
    user_prompt = build_user_prompt(original_text)

    # Call OpenAI API for text processing
    completion = client.chat.completions.create(
        model=llm_model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    # Extract and parse AI response
    content = completion.choices[0].message.content or "{}"
    try:
        data = json.loads(content)
        # Ensure the response has the correct structure
        if "normalized" not in data:
            data = {
                "normalized": {
                    "brand": "",
                    "model": "",
                    "options": []
                },
                "results": []
            }
        return data
    except Exception:
        # Return fallback structure if JSON parsing fails
        return {
            "normalized": {
                "brand": "",
                "model": "",
                "options": []
            },
            "results": []
        }


def complete_marketplace_search_via_llm(
    client: OpenAI,
    brand: str,
    model: str,
    options: List[str] = None,
    llm_model: str = "gpt-4",
    temperature: float = 0.0
) -> Dict[str, Any]:
    """
    Use LLM to search the COMPLETE marketplace without any limitations.
    
    This function simulates comprehensive marketplace search using AI,
    though it's currently not used in the main application. It provides
    a framework for AI-powered market research.
    
    Args:
        client (OpenAI): OpenAI API client instance
        brand (str): Equipment brand name
        model (str): Equipment model number
        options (List[str], optional): Equipment options (currently unused)
        llm_model (str): OpenAI model to use
        temperature (float): Temperature setting for AI responses
        
    Returns:
        Dict[str, Any]: Marketplace search results with metadata
    """
    
    # Build the complete marketplace search prompt (simplified for brand + model only)
    user_prompt = build_complete_marketplace_search_prompt(brand, model, [])
    
    # Define the expected schema for complete marketplace search
    schema = {
        "name": "complete_marketplace_search_payload",
        "schema": {
            "type": "object",
            "properties": {
                "search_results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "brand": {"type": "string"},
                            "model": {"type": "string"},
                            "price": {"type": "string"},
                            "vendor": {"type": "string"},
                            "web_url": {"type": "string"},
                            "qty_available": {"type": "string"},
                            "source": {"type": "string"}
                        },
                        "required": ["brand", "model", "price", "vendor", "web_url", "qty_available", "source"]
                    }
                },
                "search_summary": {
                    "type": "object",
                    "properties": {
                        "total_results": {"type": "integer"},
                        "exact_matches": {"type": "integer"},
                        "partial_matches": {"type": "integer"},
                        "price_range": {"type": "string"},
                        "vendor_count": {"type": "integer"},
                        "search_quality_score": {"type": "string", "enum": ["high", "medium", "low"]},
                        "recommendations": {"type": "array", "items": {"type": "string"}},
                        "search_queries_used": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["total_results", "exact_matches", "partial_matches", "price_range", "vendor_count", "search_quality_score"]
                }
            },
            "required": ["search_results", "search_summary"]
        },
        "strict": True
    }
    
    try:
        # Call OpenAI API for marketplace search simulation
        completion = client.chat.completions.create(
            model=llm_model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_COMPLETE_MARKETPLACE},
                {"role": "user", "content": user_prompt},
            ],
        )
        
        # Parse AI response
        content = completion.choices[0].message.content or "{}"
        data = json.loads(content)
        
        # Ensure the response has the correct structure
        if "search_results" not in data:
            data = {
                "search_results": [],
                "search_summary": {
                    "total_results": 0,
                    "exact_matches": 0,
                    "partial_matches": 0,
                    "price_range": "No results found",
                    "vendor_count": 0,
                    "search_quality_score": "low",
                    "recommendations": ["No search results available"],
                    "search_queries_used": []
                }
            }
        
        return data
        
    except Exception as e:
        print(f"Complete marketplace search error: {e}")
        # Return empty results on error
        return {
            "search_results": [],
            "search_summary": {
                "total_results": 0,
                "exact_matches": 0,
                "partial_matches": 0,
                "price_range": "Search failed",
                "vendor_count": 0,
                "search_quality_score": "low",
                "recommendations": [f"Search failed due to error: {e}"],
                "search_queries_used": []
            }
        }


