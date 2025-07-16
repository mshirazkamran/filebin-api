from datetime import datetime, timezone


def format_size(size_bytes: int) -> str:
    """Converts a size in bytes to a human-readable string (KB, MB, GB)."""
    if not isinstance(size_bytes, (int, float)):
        return "N/A"
    if size_bytes < 1024:
        return f"{size_bytes} Bytes"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.2f} MB"
    else:
        return f"{size_bytes/1024**3:.2f} GB"

def format_datetime_string(dt_string: str) -> str:
    """Converts an ISO 8601 timestamp string to a readable format."""
    if not dt_string:
        return "N/A"
    try:
        # Handle the 'Z' (Zulu time) for UTC
        if dt_string.endswith('Z'):
            dt_string = dt_string[:-1] + '+00:00'
        
        # Parse the ISO format string into a datetime object
        dt_object = datetime.fromisoformat(dt_string)
        
        # Convert to UTC to ensure consistent timezone display
        utc_dt = dt_object.astimezone(timezone.utc)
        
        # Format it into a more friendly string
        return utc_dt.strftime("%B %d, %Y at %I:%M %p (UTC)")
    except (ValueError, TypeError):
        return "Invalid date format"


def format_file_details(file_list: list, detailed: bool = True) -> str:
    """
    Formats a list of file dictionaries into a single, user-friendly string.

    Args:
        file_list: A list of dictionaries, where each dictionary contains
                   details about a file.
        detailed: If True, shows all details. If False, shows a compact view.
    
    Returns:
        A formatted string containing the details of all files.
    """
    if not file_list:
        return "No file details to display."

    output_lines = []
    separator = "=" * 50
    
    if detailed:
        output_lines.append(separator)

    for i, file_info in enumerate(file_list, 1):
        # --- Extract data using .get() for safety ---
        filename = file_info.get('filename', 'N/A')
        content_type = file_info.get('content_type', 'N/A')
        
        if detailed:
            size_bytes = file_info.get('size_bytes')
            updated_at = file_info.get('updated_at')
            created_at = file_info.get('created_at')
            
            # --- Append detailed formatted details ---
            output_lines.append(f"File #{i}: {filename}")
            output_lines.append("-" * 50)
            output_lines.append(f"  {'Type:':<12} {content_type}")
            output_lines.append(f"  {'Size:':<12} {format_size(size_bytes)}")
            output_lines.append(f"  {'Created:':<12} {format_datetime_string(created_at)}")
            output_lines.append(f"  {'Updated:':<12} {format_datetime_string(updated_at)}")
            output_lines.append(separator)
        else:
            # --- Append compact formatted details ---
            output_lines.append("-" * 50)
            output_lines.append(f"File # {i}: {filename} ({content_type})")
            output_lines.append(separator)

    # Join all the lines into a single string with newline characters
    return "\n".join(output_lines)

