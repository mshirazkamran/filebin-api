import requests


def getMapping(shortCode):

    """
        Returns a tuple of 2 elements, (Data,Error) so its easy for error handling
    """

    try:
        response = requests.get(f"https://filebin-api-backend.onrender.com/shortcode-to-binid?code={shortCode}",
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
        
        jsonData = response.json()

        if response.status_code == 200:
            return (jsonData.get("binid", None))
        
        elif response.status_code == 400:
            return (None, jsonData.get("error"))
        
        elif response.status_code == 404:
            return (None, jsonData.get("error"))
        
        else:
            return(None, "An unknown error occured, Please contact fbin dev")

    except Exception:
        return (None, "There was an issue sending the request")
    


def generateEncodingFromServer(binid):

    """
        Returns a tuple of 2 elements, (Data,Error) so its easy for error handling
    """

    try:
        response = requests.post(f"https://filebin-api-backend.onrender.com/generate", 
            headers = {
                "Accept": "application/json"
            },
            data = {
                "binid": binid,
            })

        status = response.status_code
        jsonData = response.json()


        if status == 200:
            return (jsonData.get("code"), None)
        elif status == 400:
            return (None, jsonData.get("error"))
        elif status == 500:
            return (None, jsonData.get("error"))
        else:
            return (None, "An unknown error occured, contact fbin dev")
        
    except Exception:
        return (None, "An unknown error occured, contact fbin dev")



def isShortCode(binid: str):
    return ("-" in binid)


#TODO: implement a function to clear ttl expired entries

# add db
# add shortcode-to-binid endpoint 
# add ping endpoint 




# def persistShortCode(res) -> None:
     
#     if res is None:
#         click.echo("Server issued a faulty code. Please contact the fbin dev")
#         return

#     if res["binid"] and res["code"] and res["ttl"]:
#         click.echo("Storing code...")
#         filepath = getDataFile()

#         key = res["code"]
#         value = {
#             "binid": res["binid"],
#             "ttl": res["ttl"]
#         }
#         appendToJsonFile(filepath, key, value)

                

# # helper func
# def appendToJsonFile(filepath, key, value):

#     dataFilePath = Path(filepath)

#     if dataFilePath.exists() and dataFilePath.is_file():
#         with open(dataFilePath, "r") as f:
#             try:
#                 jsonData = json.load(f)
#             except JSONDecodeError as e:
#                 click.echo("Invalid JSON data file, please contact fbin team")
#                 jsonData = {}

#     else: 
#         jsonData = {}
    
#     jsonData[key] = value

#     with open(dataFilePath, "w") as f:
#         json.dump(jsonData, f, indent=4)



# def getDataFile():
    
#     APP_NAME = "filebin-cli"
#     APP_AUTHOR = "shiraz"
    
#     data_dir = user_data_dir(APP_NAME, APP_AUTHOR)
#     os.makedirs(data_dir, exist_ok=True)
#     return os.path.join(data_dir, "data.json")
