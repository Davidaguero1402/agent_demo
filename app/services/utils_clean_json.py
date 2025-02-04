def clean_json_response(response_text):
    """
    Clean and extract JSON from the model's response text.
    Handles various formats that might be returned by the model.
    """
    # Remove code blocks if present
    cleaned = response_text.replace('```json', '').replace('```', '').strip()
    
    # Try to find JSON content between curly braces
    try:
        start_idx = cleaned.index('{')
        end_idx = cleaned.rindex('}') + 1
        json_str = cleaned[start_idx:end_idx]
        return json_str
    except ValueError:
        # If no valid JSON structure is found, return None
        return None