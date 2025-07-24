
import click
import requests
from datetime import datetime
from pathlib import Path



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
    # if not dt_string:
    #     return "N/A"
    # try:
    #     # Handle the 'Z' (Zulu time) for UTC
    #     if dt_string.endswith('Z'):
    #         dt_string = dt_string[:-1] + '+00:00'
        
    #     # Parse the ISO format string into a datetime object
    #     dt_object = datetime.fromisoformat(dt_string)
        
    #     # Convert to UTC to ensure consistent timezone display
    #     utc_dt = dt_object.astimezone(timezone.utc)
        
    #     # Format it into a more friendly string
    #     return utc_dt.strftime("%B %d, %Y at %I:%M %p (UTC)")
    # except (ValueError, TypeError):
    #     return "Invalid date format"

    return dt_string if dt_string else "N/A"


def formatFileDetails(file_list: list, detailed: bool = True) -> str:

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

    
def uploadFileHelper(binid, path, filename): 
    # "rb" specifies to read data in binary form which is application/octet-stream
    with open(path, "rb") as file:
        contents = file.read()
        click.secho(f"Successfully read {filename}", fg="green")

    try:
        click.secho(f"Uploading {filename} to: https://filebin.net/{binid}")
        response = requests.post(f"https://filebin.net/{binid}/{filename}"
                , data = contents
                , headers = {
                    "Content-Type": "application/octet-stream",
                    "Accept": "application/json"
                });
    
        status = response.status_code
        if status == 201:
            click.secho(f"Successfully uploaded file: {filename} at: https://filebin.net/{binid}/{filename}", fg="green")

        elif status == 400:
            click.secho("Invalid input, typically invalid bin or filename specified", fg="red")

        elif status == 403:
            click.secho("Max storage limit was reached", fg="red")

        elif status == 404:
            click.secho("Page not found", fg="red")

        elif status == 405:
            click.secho("The bin is locked and can't be written to", fg="red")

        elif status == 500:
            click.secho("Internal server error", fg="red")

        else:
            click.secho(f"Error occured, code: {status}", fg="red")

    except Exception as e:
        click.secho(f"An error occured while uploading the file, {e}", fg="red")


def downloadFileHelper(binid, fullpath: Path, filename):
    
    click.secho(f"Downloading {filename} from: https://filebin.net/{binid}");
    try: 
        response = requests.get(f"https://filebin.net/{binid}/{filename}", stream=True
        , headers= {
            "User-Agent": "curl/7.68.0",  # tricks Filebin into skipping the warning page
            "Accept": "*/*"
        })

        click.secho(f"status code: {response.status_code}");
    
    except Exception as e:
        click.secho(f"Error occured, {e}", fg="red")
        raise e

    status = response.status_code    

    if status == 200:
        total_size = int(response.headers.get('content-length', 0))  # Total size in bytes

        try:
            with open(fullpath, 'wb') as f:
                with click.progressbar(length=total_size, label = filename) as bar:
                    for chunk in response.iter_content(chunk_size=(1024 * 1024)):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk)) 

            click.secho(f"File successfully downloaded at: {fullpath.resolve()}", fg="green")
        except Exception as e:
            click.secho("An error occurred!", fg="red")
            # raise e
        
    elif status == 403:
        click.secho("The file download count was reached", fg="red")

    elif status == 404:
        click.secho("The file was not found. The bin may be expired, the file is deleted or it did never exist in the first place.", fg="red")
    


def downloadArchiveHelper(binid, type, path):
    try:
        response = requests.get(f"https://filebin.net/archive/{binid}/{type}", stream=True, 
            headers = {
                "User-Agent": "curl/7.68.0",  # tricks Filebin into skipping the warning page
                "Accept": "*/*"
            })
        
        status = response.status_code


        
        # as total file size is unknown we are using an indeterminate bar which delivers a good UX
        if status == 200:

            # These are ued to show a random progress bar which is better than no progress bar
            bar_length = 16384
            increment = 2
            progress = 0

            click.secho("The progess bar is random!! because the total length of archive is unknown", fg="red")

            with open(path, "wb") as f, click.progressbar(length=bar_length, label="Downloading (unknown size)") as bar:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)

                        # Artificial progress update (max up to 99)
                        if progress < bar_length - 2048:
                            progress += increment
                            bar.update(increment)

                # Final update to complete the random bar
                bar.update(bar_length - progress)

            click.secho("Successfully downloaded file", fg="green")
        
        elif  status == 404:
            click.secho(f"The bin: {binid} does not exist or is not available", fg="red")
        else:
            click.secho("An error occured with the request, Please contact fbin dev!", fg = "red")

    except Exception:
        click.secho("Some error occured while downloading, Please contact fbin dev", fg = "red")

    
def tempFilenameGenerator(type: str) -> str:

    if type.lower() not in {"tar", "zip"}:
        raise ValueError("Unsupported archive type. Only 'tar' and 'zip' are allowed.")

    now = datetime.now()
    formattedTime = now.strftime("%d%B_%H-%M-%S") 
    return f"{formattedTime}.{type}"