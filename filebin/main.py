import requests
import pprint
import logging

def main() -> None:
    print("TOOL RUNNING")


logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%m%d%y %I:%M:%S %p')

def getFilebinURL() -> str:
    req = requests.get("https://filebin.net")
    binURL_index: int = str(req.text).find("binURL")  # Find the position of 'binURL'

    # Calculate the start and end indices to extract the URL
    start_index: int = binURL_index + 11  # 11 characters after 'binURL'
    end_index: int = start_index + 20     # Adjust as needed for the actual URL length

    temp: str = str(req.text)
    url: str = temp[start_index:end_index]
    finalURL = url.strip().rstrip('";')
    logging.info(f"final url is: ${finalURL}");
    print("final url is: " + finalURL)

    return finalURL




def getBinDetails(bin: str, details: bool):

    print(f"https://filebin.net/{bin}");
    try: 
        response = requests.get(f"https://filebin.net/{bin}", headers={
            "accept": "application/json"
        })
        files = []

        if response.status_code != 200:
            print(f"ERROR! The Filbin api returend code: ${response.status_code}")
            return None;
        
        elif response.status_code == 200:
            print("Response was successfull!")
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
                
        return files

    except Exception as e:
        print("okokokok")
        print(e.with_traceback);



def downloadFile(bin, filename) -> None:

    print(f"https://filebin.net/{bin}/{filename}");
    
    try: 
        response = requests.get(f"https://filebin.net/{bin}/{filename}", stream=True
        , headers= {
            "User-Agent": "curl/7.68.0",  # tricks Filebin into skipping the warning page
            "Accept": "*/*"
        })

        print(f"\n\n\nstatus code: ${response.status_code}\n\n");
        

        if response.status_code != 200:
            print(f"ERROR! The Filbin api returend code: {response.status_code}")
            return None;
        
        elif response.status_code == 200:
            # print("request successfull")
            # json_data = response.json();
            # print(json_data);

            print("Downloading the file!")
            with open(filename, 'wb') as f:
                # Iterate over the content in chunks
                for chunk in response.iter_content(chunk_size=(1024 * 1024)):
                    if chunk:  # Make sure there's content in the chunk
                        f.write(chunk)

        # elif response.status_code == 200:
        #     print("Redirected to:", response.headers['Location'])
        #     # Now you can download from the new URL
        #     redirect_url = response.headers['Location']
        #     download_response = requests.get(redirect_url, stream=True)

        #     # if download_response.status_code == 200:
        #     with open(filename, 'wb') as f:
        #         for chunk in download_response.iter_content(chunk_size=8192):  # 1 MB chunks
        #             if chunk:
        #                 f.write(chunk)
        #     print("Download complete!")
        #     # else:
        #     print(f"Failed to download from redirect URL, status code: {download_response.status_code}")
        

    except Exception as e:
        logging.info("File couldnt be downloaded, error: ", e)


# Example usage:
# url: str = getFilebinURL();
# url: str = "qrk6qk1bwsf29slm"
# details = getBinDetails(url, False)


# filenames = {}

# print("-" * 40)

# if details:
#     i = 1;
#     for detail in details:

        # pprint.pprint(detail, indent=4, width=100);

        # Find the start and end positions of the filename
        # temp = str(detail)
        # start = temp.find("'filename': '") + len("'filename': '")
        # end = temp.find("'", start)
        
        # if start != -1 and end != -1:
        #     # Extract the filename and add it to the list
        #     filenames.setdefault(i, temp[start:end])
        #     i = i + 1


        # print("-" * 40)

# print(filenames)

# print("Please tell the number of file to download:");
# key: int = int(input()); 
# fileToDownload = filenames.get(key);
# downloadFile(url, fileToDownload);



# print("-" * 40)
# pprint.pprint(details)