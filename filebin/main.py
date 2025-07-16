from email.policy import default
import requests
import pprint
import click
import json
from format import format_file_details
from pathlib import Path



@click.group()
def cli() -> None:
    """Main CLI group"""
    pass


def main() -> None:
    click.echo("TOOL RUNNING")
                                    # Example usage:
    url: str = "qrk6qk1bwsf29slm"
    details = getBinDetails(url, False)


    filenames = {}

    click.echo("-" * 40)

    if details:
        i = 1;
        for detail in details:

            pprint.pprint(detail, indent=4, width=100);

            # Find the start and end positions of the filename
            temp = str(detail)
            start = temp.find("'filename': '") + len("'filename': '")
            end = temp.find("'", start)
            
            if start != -1 and end != -1:
                # Extract the filename and add it to the list
                filenames.setdefault(i, temp[start:end])
                i = i + 1


            click.echo("-" * 40)

    click.echo(filenames)

    click.echo("Please tell the number of file to download:");
    key: int = int(input()); 
    fileToDownload = filenames.get(key);
    downloadFile(url, fileToDownload);


    click.echo("-" * 40)
    pprint.pprint(details)




def getFilebinURL() -> str:

    req = requests.get("https://filebin.net")
    binURL_index: int = str(req.text).find("binURL")  # Find the position of 'binURL'

    # Calculate the start and end indices to extract the URL
    start_index: int = binURL_index + 11  # 11 characters after 'binURL'
    end_index: int = start_index + 20     # Adjust as needed for the actual URL length

    temp: str = str(req.text)
    url: str = temp[start_index:end_index]
    finalURL = url.strip().rstrip('";')
    click.echo("final url is: " + finalURL)

    return finalURL



@click.command(name = "upload")
@click.option("--fbin", help = "Upload files to a bin. The bin is auto created if not specified with the --bin flag", default = None)
@click.argument("path")
# TODO: handle multiple files
def uploadFile(path: str, fbin: str) -> None:

    filename: str = Path(path).name; # filename is gotten from here

    if fbin is None:
        click.secho("Creating a bin...", bold = True)
        fbin = getFilebinURL(); # get a bin if fbin flag is not specified
    else:
        click.secho("Bin alraedy specified...", bold = True)


    click.secho(f"Your bin is: {fbin}", bold = True, fg="green", bg="bright_black")


    URL: str = getFilebinURL()

    if not (len(URL)  >= 8 and  len(URL) <= 20):
        click.echo("An issue was encoutnered while creating a bin", err=True)
        return

    click.echo(click.style(f"Your bin has been created at: {URL}", fg="green", bold=True))


    # TODO:implement further :

    # "rb" specifies to read data in binary form which is application/octet-stream
    with open(path, "rb") as file:
        contents = file.read()
        click.secho(f"Successfully read file: {path}", fg="green")

    try:
        click.echo(f"\nuploading file to: https://filebin.net/{fbin}/{filename}\n")
        requests.post(f"https://filebin.net/{fbin}/{filename}"
                , data = contents
                , headers = {
                    "Content-Type": "application/octet-stream"
                })
        
    except Exception as e:
        raise e





@click.command(name = "details")
@click.argument("fbin")
@click.option("--details", "-d", is_flag = True, default = False, help = "Print detailed metadata of files in the sepcified bin")
def getBinDetails(fbin: str, details: bool):

    click.echo(f"fetching details of: https://filebin.net/{fbin}");
    try: 
        response = requests.get(f"https://filebin.net/{fbin}", headers={
            "accept": "application/json"
        })
        files = []

        if response.status_code != 200:
            click.echo(f"ERROR! The Filbin api returend code: ${response.status_code}")
            return None;
        
        elif response.status_code == 200:
            click.secho("Response was successfull!", fg="green")
            json_data = response.json()
            json_files = json_data["files"]

            file_details = {}
            
            for file in json_files:
                if details == True: 
                    file_details = {
                        "filename": file['filename'],
                        "content_type": file['content-type'],
                        "size_bytes": file['bytes'],
                        "updated_at": file['updated_at'],
                        "created_at": file['created_at']
                    }
                    
                else:
                    file_details = {
                        "filename" : file['filename'],
                        "content_type" : file['content-type'],
                    }
                    
                files.append(file_details);
                
        # click.echo(files);

        # formatted_json = json.dumps(files, indent=2)
        # click.secho(formatted_json, bold=True)

        # print("\n\n\n")

        usf: str = format_file_details(files, details)
        click.secho(usf)
        return files # files is a list of files metadata, see the above key-value pairs.
         

    except Exception as e:
        click.echo(f"An error occured while fetching the fbin: {fbin}", err=True)
        click.echo(e.with_traceback);


#TODO: use this in the getdetails method and also as a standalone command
def downloadFile(fbin, filename) -> None:

    click.echo(f"Downloading file from: https://filebin.net/{fbin}/{filename}");
    
    try: 
        response = requests.get(f"https://filebin.net/{fbin}/{filename}", stream=True
        , headers= {
            "User-Agent": "curl/7.68.0",  # tricks Filebin into skipping the warning page
            "Accept": "*/*"
        })

        click.echo(f"\n\nstatus code: ${response.status_code}\n\n");
        

        if response.status_code != 200:
            click.echo(f"ERROR! The Filbin api returend code: {response.status_code}")
            return None;
        
           
        
        elif response.status_code == 200:
            # click.echo("request successfull")
            # json_data = response.json();
            # click.echo(json_data);

            # TODO: implement directory to download file to, default should be where the command is run

            click.echo("Downloading the file in root directory!")
            with open(filename, 'wb') as f:
                # Iterate over the content in chunks
                for chunk in response.iter_content(chunk_size=(1024 * 1024)):
                    if chunk:  # Make sure there's content in the chunk
                        f.write(chunk)


    except Exception as e:
        click.echo(f"Error occured, {e}", err=True)
        raise e
    
    

# main();

cli.add_command(getBinDetails)
cli.add_command(uploadFile)



@click.command()
@click.option("-n", "--name", prompt = "Please enter your name", help = "Prints the name")
def greet(name: str) -> None:
    click.echo(f"Hello {name}")
    click.echo(f"Hello {name}")

if __name__ == "__main__":
    # main()
    cli()