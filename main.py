import requests
import pprint

def getFilebinURL() -> str:
    req = requests.get("https://filebin.net")
    binURL_index: int = str(req.text).find("binURL")  # Find the position of 'binURL'

    # Calculate the start and end indices to extract the URL
    start_index: int = binURL_index + 11  # 11 characters after 'binURL'
    end_index: int = start_index + 20     # Adjust as needed for the actual URL length

    temp: str = str(req.text)
    url: str = temp[start_index:end_index]
    finalURL = url.strip().rstrip('";')
    print("final url is: " + finalURL)

    return finalURL



# class Bin:
#     def __init__(self, binUrl: str, filenames: list[str]) -> None:
#         self.binUrl = binUrl
#         self.filenames = filenames

#     def _str___(self):
#         print(f"The bin url is: {self.binUrl}")
#         for filename in self.filenames:
#             print(filename)


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

    # print("hellohello")
    # return


# Example usage:
url: str = getFilebinURL();
details = getBinDetails(url, False)

print("-" * 40)
if details:
    for detail in details:
        pprint.pprint(detail, indent=4, width=100);
        print("-" * 40)


# print("-" * 40)
# pprint.pprint(details)