import requests
import click
from pathlib import Path
from format import format_file_details


@click.group()
def cli() -> None:
    pass


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
@click.argument("paths", nargs = -1)
# TODO: handle multiple files
def uploadFile(paths: tuple, fbin: str) -> None:

    fpaths = {}

    for path in paths:
        checkPath: Path = Path(path) 
        if not checkPath.exists() or not checkPath.is_file():
            click.secho(f"The script can not find the file: {checkPath.resolve()}, Perhaps you entered a directory? \n ", err=True)
            break

        filename: str = checkPath.name; # extract filename from paths  
        fpaths[filename] = checkPath

        # uploadFileHelper(checkPath, fbin, filename)

    if fbin is None:
        click.secho("Creating a bin...", bold = True)
        fbin = getFilebinURL(); # get a bin if fbin flag is not specified

        if (len(fbin)  >= 8 and  len(fbin) <= 20):
            click.secho(f"Your bin has been created: {fbin}", fg="green", bold=True)
        else:
            click.echo("An issue was encoutnered while creating a bin", err=True)
            return
    else:
        click.secho("Bin alraedy specified...", bold = True)


    # Upload files one by one from the dictionary 
    for name, path in fpaths.items():
        uploadFileHelper(path, fbin, name)


    
def uploadFileHelper(path, fbin, filename): 
    # "rb" specifies to read data in binary form which is application/octet-stream
    with open(path, "rb") as file:
        contents = file.read()
        click.secho(f"Successfully read {filename}", fg="green")

    try:
        click.echo(f"Uploading {filename} to: https://filebin.net/{fbin}")
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
                click.echo("Page not found", err=True)
            case 405:
                click.echo("The bin is locked and can't be written to", err=True)
            case 500:        
                click.echo("Internal server error", err=True)
        
    except Exception as e:
        click.echo(f"An error occured while uploading the file, {e}", err=True)



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
        click.echo(f"An error occured while fetching from the bin: {fbin}", err=True)
        click.echo(e.with_traceback);


#TODO: use this in the getdetails method and also as a standalone command
@click.command(name = "download")
@click.argument("fbin")
@click.argument("filenames", nargs=-1)
@click.option("--path", "-p", default="root", help="The path to download the file to. File is downloaded in root dir if path is not specified ")
def downloadFile(fbin: str, filenames: tuple, path: str) -> None:

    tempPaths = []

    # If path is root we simple save the files in the current directory
    # else we need to make paths for each file where savePath variable comes into play

    if path != "root":
        savePath = Path(path)
        if savePath.exists() and savePath.is_dir():
            for file in filenames:
                tempPaths.append(savePath / file)
            # fullpath = savePath / filename

        else:
            click.echo("The script could not find the path specified, Perhaps it is not a directory?", err=True)
            # TODO: ask user if he wants to download in the current directory
            value = click.prompt("Download in the current directory? Y/n", type=str).lower()
            if value in ("y","yes", "true"):
                click.echo("Downloading file in the current directory!")
                path = "root"
            else:
                click.echo("Aborting the script...")
                return


    if path == "root":
        for file in filenames:
            tempPaths.append(Path(file))


    for file in tempPaths:
        # TODO: complete logic of downlaoding file one by one from the link,

    click.echo(f"Downloading file from: https://filebin.net/{fbin}/{filename}");
    
    try: 
        response = requests.get(f"https://filebin.net/{fbin}/{filename}", stream=True
        , headers= {
            "User-Agent": "curl/7.68.0",  # tricks Filebin into skipping the warning page
            "Accept": "*/*"
        })

        click.echo(f"status code: {response.status_code}");
    
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
                    click.secho(f"File successfully downloaded at: {fullpath.resolve()}", fg="green")
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