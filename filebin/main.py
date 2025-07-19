from asyncio.base_subprocess import ReadSubprocessPipeProto
from email.policy import default
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



@click.command(name = "upload", help = "Upload 1 or many files to the bin. Note that There is a limit to filesize.")
@click.option("--binid", help = "Upload files to a bin. The bin is auto created if not specified with the --binid flag", default = None)
@click.argument("paths", nargs = -1)
# TODO: handle multiple files
def uploadFile(paths: tuple, binid: str) -> None:

    if len(paths) == 0:
        click.secho("No files specified. Please specify atleast one file", err = True, fg="red")
        return

    fpaths = {}

    for path in paths:
        checkPath: Path = Path(path) 
        if not checkPath.exists() or not checkPath.is_file():
            click.secho(f"The script can not find the file: {checkPath.resolve()}, Perhaps you entered a directory? \n ", err=True)
            break

        filename: str = checkPath.name; # extract filename from paths  
        fpaths[filename] = checkPath

        # uploadFileHelper(checkPath, binid, filename)

    if binid is None:
        click.secho("Creating a bin...", bold = True)
        binid = getFilebinURL(); # get a bin if binid flag is not specified

        if (len(binid)  >= 8 and  len(binid) <= 20):
            click.secho(f"Your bin has been created: {binid}", fg="green", bold=True)
        else:
            click.echo("An issue was encoutnered while creating a bin", err=True)
            return
    else:
        click.secho("Bin alraedy specified...", bold = True)


    # Upload files one by one from the dictionary 
    for name, path in fpaths.items():
        uploadFileHelper(path, binid, name)


    
def uploadFileHelper(path, binid, filename): 
    # "rb" specifies to read data in binary form which is application/octet-stream
    with open(path, "rb") as file:
        contents = file.read()
        click.secho(f"Successfully read {filename}", fg="green")

    try:
        click.echo(f"Uploading {filename} to: https://filebin.net/{binid}")
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
            click.secho("Invalid input, typically invalid bin or filename specified", err=True)

        elif status == 403:
            click.echo("Max storage limit was reached", err=True)

        elif status == 404:
            click.echo("Page not found", err=True)

        elif status == 405:
            click.echo("The bin is locked and can't be written to", err=True)

        elif status == 500:
            click.echo("Internal server error", err=True)

        else:
            click.echo(f"Unhandled status code: {status}", err=True)

    except Exception as e:
        click.echo(f"An error occured while uploading the file, {e}", err=True)



@click.command(name = "details")
@click.argument("binid")
@click.option("--details", "-d", is_flag = True, default = False, help = "Print detailed metadata of files in the sepcified bin")
def getBinDetails(binid: str, details: bool):

    click.echo(f"fetching details of: https://filebin.net/{binid}");
    try: 
        response = requests.get(f"https://filebin.net/{binid}", headers={
            "accept": "application/json"
        })

        files = []

        
        if response.status_code == 200:
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
                    
                files.append(file_details)

        elif response.status_code == 404:
            click.secho("The bin does not exist or is not available", err = True)
            return

        

            
        usf: str = format_file_details(files, details)
        click.secho(usf)
        return files # files is a list of files metadata, see the above key-value pairs.
         

    except Exception as e:
        click.echo(f"An error occured while fetching from the bin: {binid}", err=True)
        # click.echo(e.with_traceback)


#TODO: use this in the getdetails method and also as a standalone command
@click.command(name = "download", help = "Use this to download files using their binid and the exact names of the file to download, refer to details command for knowing the filenames (interactive download will be added in future)")
@click.argument("binid")
@click.argument("filenames", nargs=-1)
@click.option("--path", "-p", default="root", help="The path to download the file to. File is downloaded in root dir if path is not specified ")
def downloadFile(binid: str, filenames: tuple, path: str) -> None:

    if not filenames:
        click.secho("No files specified. Pleas provide atleast one", err = True)
        return

    tempPaths = []

    # If path is root we simply save the files in the current directory
    # else we need to make paths for each file where savePath variable comes into play

    if path != "root":
        savePath = Path(path)
        if savePath.exists() and savePath.is_dir():
            for file in filenames:
                tempPaths.append(savePath / file)
            # fullpath = savePath / filename

        else:
            click.echo("The script could not find the directory specified, Perhaps it is not a directory?", err=True)
            # TODO: ask user if he wants to download in the current directory
            value = click.prompt("Download in the current directory? Y/n", default="y", type=str).lower()
            if value in ("y","yes", "true"):
                click.echo("Downloading files in the current directory!")
                path = "root"
            else:
                click.echo("Aborting the script...")
                return


    if path == "root":
        for file in filenames:
            tempPaths.append(Path(file))


    for file in tempPaths:
        filename = file.name
        downloadFileHelper(binid, file, filename)

    

def downloadFileHelper(binid: str, fullpath: Path, filename):
    click.echo(f"Downloading {filename} from: https://filebin.net/{binid}");
    
    try: 
        response = requests.get(f"https://filebin.net/{binid}/{filename}", stream=True
        , headers= {
            "User-Agent": "curl/7.68.0",  # tricks Filebin into skipping the warning page
            "Accept": "*/*"
        })

        click.echo(f"status code: {response.status_code}");
    
    except Exception as e:
        click.echo(f"Error occured, {e}", err=True)
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
            click.echo("An error occurred!", err=True)
            # raise e
        
    elif status == 403:
        click.echo("The file download count was reached", err=True)

    elif status == 404:
        click.echo("The file was not found. The bin may be expired, the file is deleted or it did never exist in the first place.", err=True)
    


@click.command(name = "lock", help="This will make a bin read only. A read only bin does not accept new files to be uploaded or existing files to be updated. This provides some content integrity when distributing a bin to multiple parties. Note that it is possible to delete a read only bin.")
@click.argument("binid")
def lockBin(binid: str) -> None:

    value = click.prompt("This option is undoable, Are you sure you want to LOCK the bin? Y/n?",type=str, default="n").lower()

    if value in ("y","yes", "true"):
        click.echo("Locking the bin...")
    else:
        click.echo("Aborting the script!")
        return


    try:
        response = requests.put(f"https://filebin.net/{binid}", 
            headers = {
                "Accept": "application/json"
            })

        status = response.status_code

        if status == 200:
            click.secho(f"Successfully locked the bin: {binid}", fg="green")
        elif status == 404:
            click.secho(f"The bin: {binid} does not exist or is not available", err=True)
        else:
            click.secho(f"An error occured: {status}", err=True)

    except Exception as e:
        click.secho("Some error occured!", err = True)
        # click.echo(e)


@click.command(name = "delete", help = "This will delete all files from a bin. It is not possible to reuse a bin that has been deleted. Everyone knowing the URL to the bin have access to delete it")
@click.argument("binid")
def deleteBin(binid: str) -> None:

    value = click.prompt("This option is undoable, Are you sure you want to DELETE the bin? Y/n?",type=str, default="n").lower()

    if value in ("y","yes", "true"):
        click.echo("Deleting the bin...")
    else:
        click.echo("Aborting the script!")
        return
    
    try:
        response = requests.delete(f"https://filebin.net/{binid}", 
            headers = {
                "Accept": "application/json"
            })

        status = response.status_code

        if status == 200:
            click.secho(f"Successfully deleted the bin: {binid}", fg="green")
        elif status == 404:
            click.secho(f"The bin: {binid} does not exist or is not available", err=True)
        else:
            click.secho("An error occured!", err = True)

    except Exception as e:
        click.secho("Some error occured!", err = True)
        # click.echo(e)

cli.add_command(getBinDetails)
cli.add_command(downloadFile)
cli.add_command(uploadFile)
cli.add_command(lockBin)
cli.add_command(deleteBin)
#TODO: add the commands to download the bin in tar or zip archive



def main():
    cli()

if __name__ == "__main__":
    main()
    # cli()