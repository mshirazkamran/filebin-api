import requests
import click
from pathlib import Path
from format import format_file_details


@click.group()
def cli() -> None:
    """Main CLI group"""
    pass


# def main() -> None:
#     click.echo("TOOL RUNNING")
#                                     # Example usage:
#     url: str = "qrk6qk1bwsf29slm"
#     details = getBinDetails(url, False)


#     filenames = {}

#     click.echo("-" * 40)

#     if details:
#         i = 1;
#         for detail in details:

#             pprint.pprint(detail, indent=4, width=100);

#             # Find the start and end positions of the filename
#             temp = str(detail)
#             start = temp.find("'filename': '") + len("'filename': '")
#             end = temp.find("'", start)
            
#             if start != -1 and end != -1:
#                 # Extract the filename and add it to the list
#                 filenames.setdefault(i, temp[start:end])
#                 i = i + 1


#             click.echo("-" * 40)



#     click.echo("-" * 40)
#     pprint.pprint(details)




def getFilebinURL() -> str:

    req = requests.get("https://filebin.net")
    binURL_index: int = str(req.text).find("binURL")  # Find the position of 'binURL'

    # Calculate the start and end indices to extract the URL
    start_index: int = binURL_index + 11  # 11 characters after 'binURL'
    end_index: int = start_index + 20     # Adjust as needed for the actual URL length

    temp: str = str(req.text)
    url: str = temp[start_index:end_index]
    finalURL = url.strip().rstrip('";')

    # click.echo("final url is: " + finalURL)

    return finalURL



@click.command(name = "upload")
@click.option("--fbin", help = "Upload files to a bin. The bin is auto created if not specified with the --bin flag", default = None)
@click.argument("path")
# TODO: handle multiple files
def uploadFile(path: str, fbin: str) -> None:

    filePath: Path = Path(path)
    if not filePath.exists() or not filePath.is_file():
        click.secho("The script can not find the file specified, Perhaps you linked a directory!", err=True)
        return

    filename: str = filePath.name; # extract filename from path  

    if fbin is None:
        click.secho("Creating a bin...", bold = True)
        fbin = getFilebinURL(); # get a bin if fbin flag is not specified

        if (len(fbin)  >= 8 and  len(fbin) <= 20):
            click.secho(f"Your bin has been created at: {fbin}", fg="green", bold=True)
        else:
            click.echo("An issue was encoutnered while creating a bin", err=True)
            return

    else:
        click.secho("Bin alraedy specified...", bold = True)


    # click.secho(f"\nYour bin is: {fbin}\n", bold = True, fg="green", bg="bright_black")


    # TODO:implement further :

    # "rb" specifies to read data in binary form which is application/octet-stream
    with open(path, "rb") as file:
        contents = file.read()
        click.secho(f"Successfully read file: {path}", fg="green")

    try:
        click.echo(f"\nUploading file to: https://filebin.net/{fbin}\n")
        res = requests.post(f"https://filebin.net/{fbin}/{filename}"
                , data = contents
                , headers = {
                    "Content-Type": "application/octet-stream",
                    "Accept": "application/json"
                });
    
        match res.status_code:
            case 201:
                # click.echo(f"Server replied: {pprint.pprint(res.json(), indent=3)}")
                click.secho(f"Successfully uploaded file: {filename} at: https://filebin.net/{fbin}/{filename}", fg = "green")
            case 400:
                # click.echo(f"Server replied: {pprint.pprint(res.json(), indent=3)}")
                click.secho("Invalid input, typically invalid bin or filename specified", err = True)
            case 403:
                click.echo("Max storage limit was reached", err=True)
            case 404:
                click.echo("Page not found")
            case 405:
                click.echo("The bin is locked and can't be written to")
            case 500:        
                click.echo("Internal server error")
        
    except Exception as e:
        click.echo(f"An error occured while uploading the file, {e}", err=True)
        





@click.command(name = "details")
@click.argument("BIN")
@click.option("--details", "-d", is_flag = True, default = False, help = "Print detailed metadata of files in the sepcified bin")
def getBinDetails(BIN: str, details: bool):

    click.echo(f"fetching details of: https://filebin.net/{BIN}");
    try: 
        response = requests.get(f"https://filebin.net/{BIN}", headers={
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
                        "created_at": file['created_at'],
                        "md5": file['md5']
                    }
                    
                else:
                    file_details = {
                        "filename" : file['filename'],
                        "content_type" : file['content-type'],
                        "size_bytes": file['bytes'],
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
        click.echo(f"An error occured while fetching from the bin: {BIN}", err=True)
        click.echo(e.with_traceback);


#TODO: use this in the getdetails method and also as a standalone command
@click.command(name = "download")
@click.argument("BIN")
@click.argument("filename")
@click.option("--path", "-p", default="root", dest="downloadTo", help="The path to download the file to. File is downloaded in root dir if path is not specified ")
def downloadFile(BIN: str, filename: str, downloadTo: str) -> None:

    if downloadTo != "root":
        savePath = Path(downloadTo)
        if  savePath.is_dir() and savePath.exists():
            fullpath = savePath / filename
        else:
            click.echo("The script could not find the path specified, Perhaps it is not a directory?", err=True)
            # TODO: ask user if he wants to download in the current directory
            value = click.prompt("Download in the current directory? Y/n", type=str).lower()
            if value in ("y","yes", "true"):
                click.echo("Downloading file in the current directory!")
                downloadTo = "root"
            else:
                click.echo("Aborting the script...")
                return


    if downloadTo == "root":
        fullpath = Path(filename)


    click.echo(f"Downloading file from: https://filebin.net/{BIN}/{filename}");
    
    try: 
        response = requests.get(f"https://filebin.net/{BIN}/{filename}", stream=True
        , headers= {
            "User-Agent": "curl/7.68.0",  # tricks Filebin into skipping the warning page
            "Accept": "*/*"
        })

        click.echo(f"\n\nstatus code: ${response.status_code}\n\n");
    
    except Exception as e:
        click.echo(f"Error occured, {e}", err=True)
        raise e
    
    match response.status_code:
        case 200:
            try:
                with open(fullpath, 'wb') as f:
                    # Iterate over the content in chunks
                    for chunk in response.iter_content(chunk_size=(1024 * 1024)):
                        if chunk:  # Make sure there's content in the chunk
                            f.write(chunk)
                    click.echo(f"File successfully downloaded at: {fullpath.resolve()}")
            except Exception as e:
                click.echo("An error occured!", err=True)
                raise e;
            
        case 403:
            click.echo("The file download count was reached", err=True)
            return

        case 404:
            click.echo("The file was not found. The bin may be expired, the file is deleted or it did never exist in the first place.", err=True)
            return
    


cli.add_command(getBinDetails)
cli.add_command(downloadFile)
cli.add_command(uploadFile)


def main():
    cli()

if __name__ == "__main__":
    main()
    # cli()