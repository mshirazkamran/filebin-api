from email.policy import default
import requests
import click
from pathlib import Path
from re import fullmatch
import pkg_resources

from .utils import downloadArchiveHelper, formatFileDetails, uploadFileHelper, downloadFileHelper
from .encoding import isShortCode, generateEncodingFromServer, getMapping


@click.group()
@click.version_option(pkg_resources.get_distribution("filebin-cli").version)
def cli() -> None:
    """FILEBIN CLI TOOL"""
    pass


def getFilebinURL() -> tuple:

    req = requests.get("https://filebin.net")
    binURL_index: int = str(req.text).find("binURL")  # Find the position of 'binURL'

    # Calculate the start and end indices to extract the URL
    start_index: int = binURL_index + 11  # 11 characters after 'binURL'
    end_index: int = start_index + 20     # Adjust as needed for the actual URL length

    temp: str = str(req.text)
    url: str = temp[start_index:end_index]
    finalURL = url.strip().rstrip('";')

    if len(finalURL) >= 19:
        click.secho("Error getting filebin url, contact fbin dev", fg="red")
        return (None, None)

    finalShortCode, error = generateEncodingFromServer(finalURL)

    if error is not None:
        click.secho(error, fg="red")
        return(None, None);


    # click.secho("final url is: " + finalURL)

    return (finalURL, finalShortCode)



@click.command(name = "upload", help = "Upload 1 or many files to the bin. Note that There is a limit to filesize.")
@click.option("--binid", "-b", help = "Upload files to a bin. The bin is auto created if not specified with the --binid flag", default = None)
@click.argument("paths", nargs = -1)
def uploadFile(binid, paths: tuple ) -> None:

    if binid is not None:
        if isShortCode(binid):
            data, error = getMapping(binid)

            if error is not None:
                click.secho(error, fg="red")
                return
            
            shortcode = binid
            binid = data


    if len(paths) == 0:
        click.secho("No files specified. Please specify atleast one file", err = True, fg="red")
        return

    fpaths = {}

    for path in paths:
        checkPath: Path = Path(path) 
        if not checkPath.exists() or not checkPath.is_file():
            click.secho(f"The script can not find the file: {checkPath.resolve()}, Perhaps you entered a directory? \n ", fg="red")
            break

        filename: str = checkPath.name; # extract filename from paths  
        fpaths[filename] = checkPath

        # uploadFileHelper(checkPath, binid, filename)

    if binid is None:
        click.secho("Creating a bin...", bold = True)
        binid, shortcode = getFilebinURL(); # Note that this method returns a tuple
        if binid is None:
            click.secho("An error occured while creating a bin!", fg="red")
            return

    else:
        click.secho("Bin alraedy specified...", bold = True)


    # Upload files one by one from the dictionary 
    for name, path in fpaths.items():
        uploadFileHelper(binid, path, name)

    
    click.secho(f"NOTE: Your short code to use this bin is: {shortcode}", fg="green")
    click.secho(f"You can use {shortcode} instead of the original binid", fg="green")


@click.command(name = "details", help = "Show the file contents of the bin")
@click.argument("binid")
@click.option("--details", "-d", is_flag = True, default = False, help = "Print detailed metadata of files in the sepcified bin")
def getBinDetails(binid, details: bool):

    if isShortCode(binid):
        data, error = getMapping(binid)

        if error is not None:
            click.secho(error, fg="red")
            return
        
        binid = data

    click.secho(f"fetching details of: https://filebin.net/{binid}");
    try: 
        response = requests.get(f"https://filebin.net/{binid}", headers={
            "accept": "application/json"
        })

        files = []

        if response.status_code == 200:
            # click.secho("Response was successfull!", fg="green")
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
            
        usf: str = formatFileDetails(files, details)
        click.secho(usf)
        return files # files is a list of files metadata, see the above key-value pairs.
         

    except Exception as e:
        click.secho(f"An error occured while fetching from the bin: {binid}", fg="red")
        # click.secho(e.with_traceback)


#TODO: use this in the getdetails method and also as a standalone command
@click.command(name = "download", help = "Download files using their binid and the exact names of the file to download, refer to details command for knowing the filenames (interactive download will be added in future)")
@click.option("--binid", "-b", required=True, help="The bin to downlaod the files from, You can also use shortcode")
@click.argument("filenames", nargs=-1)
@click.option("--path", "-p", default="root", help="The path to download the file to. File is downloaded in root dir if path is not specified ")
def downloadFile(binid, filenames: tuple, path: str) -> None:

    if binid is None:
        click.secho("No binid specified. Pleas provide the binid", fg = "red")


    if isShortCode(binid):
        data, error = getMapping(binid)

        if error is not None:
            click.secho(error, fg="red")
            return
        
        binid = data
        

    if not filenames:
        click.secho("No files specified. Pleas provide atleast one", fg = "red")
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
            click.secho("The script could not find the directory specified, Perhaps it is not a directory?", fg="red")
            # TODO: ask user if he wants to download in the current directory
            value = click.prompt("Download in the current directory? Y/n", default="y", type=str).lower()
            if value in ("y","yes", "true"):
                click.secho("Downloading files in the current directory!")
                path = "root"
            else:
                click.secho("Aborting the script...")
                return


    if path == "root":
        for file in filenames:
            tempPaths.append(Path(file))


    for file in tempPaths:
        filename = file.name
        downloadFileHelper(binid, file, filename)

    

@click.command(name = "lock", help="This will make a bin read only. A read only bin does not accept new files to be uploaded or existing files to be updated. This provides some content integrity when distributing a bin to multiple parties. Note that it is possible to delete a read only bin.")
@click.argument("binid")
def lockBin(binid) -> None:

    if isShortCode(binid):
        data, error = getMapping(binid)

        if error is not None:
            click.secho(error, fg="red")
            return
        
        binid = data

    value = click.prompt("This option is undoable, Are you sure you want to LOCK the bin? Y/n?",type=str, default="n").lower()

    if value in ("y","yes", "true"):
        click.secho("Locking the bin...")
    else:
        click.secho("Aborting the script!")
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
            click.secho(f"The bin: {binid} does not exist or is not available", fg="red")
        else:
            click.secho(f"An error occured: {status}", fg="red")

    except Exception as e:
        click.secho("Some error occured!", err = True)
        # click.secho(e)


@click.command(name = "delete", help = "This will delete all files from a bin. It is not possible to reuse a bin that has been deleted. Everyone knowing the URL to the bin have access to delete it")
@click.argument("binid")
def deleteBin(binid) -> None:

    if isShortCode(binid):
        data, error = getMapping(binid)

        if error is not None:
            click.secho(error, fg="red")
            return
        
        binid = data


    value = click.prompt("This option is undoable, Are you sure you want to DELETE the bin? Y/n?",type=str, default="n").lower()

    if value in ("y","yes", "true"):
        click.secho("Deleting the bin...")
    else:
        click.secho("Aborting the script!")
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
            click.secho(f"The bin: {binid} does not exist or is not available", fg="red")
        else:
            click.secho("An error occured!", err = True)

    except Exception as e:
        click.secho("Some error occured!", err = True)
        # click.secho(e)


@click.command(name = "tar", help = "Get all the files of the bin in tar archive")
@click.argument("binid")
@click.option("--path", "-p",default="root", help="The path to download the archive to")
def downloadBinAsTAR(binid, path):

    if isShortCode(binid):
        data, error = getMapping(binid)

        if error is not None:
            click.secho(error, fg="red")
            return
        
        binid = data


    if path != "root":
        savePath = Path(path)
        if savePath.exists() and savePath.is_dir():
            fullpath = savePath / "archive.tar"

        else:
            click.secho("The script could not find the directory specified, Perhaps it is not a directory?", fg="red")
            # TODO: ask user if he wants to download in the current directory
            value = click.prompt("Download in the current directory? Y/n", default="y", type=str).lower()
            if value in ("y","yes", "true"):
                click.secho("Downloading files in the current directory!")
                path = "root"
            else:
                click.secho("Aborting the script...")
                return
            
    if path == "root":
        fullpath = "archive.tar"

        #TODO: change the archive name so multiple downloads can be supported
        

    value = click.prompt("Are you sure you want to DOWNLOAD all contents of the bin in TAR archive? Y/n?",type=str, default="n").lower()

    if value in ("y","yes", "true"):
        click.secho("Downloading the bin...")
    else:
        click.secho("Aborting the script!")
        return
   
    downloadArchiveHelper(binid, "zip", fullpath)




cli.add_command(getBinDetails)
cli.add_command(downloadFile)
cli.add_command(uploadFile)
cli.add_command(lockBin)
cli.add_command(deleteBin)
cli.add_command(downloadBinAsTAR)
#TODO: add the commands to download the bin in tar or zip archive



def main():
    cli()

if __name__ == "__main__":
    main()