import requests



def getFilebinURL() -> str:

    req = requests.get("https://filebin.net");

    binURL_index: int = str(req.text).find("binURL"); #binURL is the variable name of the 
    # print(binURL_index);                              #resource endpoint

    # TODO: calculate the binURL dymanically 
    start_index: int = binURL_index;
    start_index += 11; 
    end_index: int = start_index + 20;

    # print(start_index, end_index);

    temp: str = str(req.text);
    url: str = temp[start_index:end_index]; # [1324:1344] 
    # print(url);

    finalURL = url.strip().rstrip('";');
    print("final url is: " + finalURL);

    return finalURL;


class FileDetails:
    def __init__(self, filepath: str, filetype: str):
        self.filepath = filepath;
        self.filetype = filetype;


def httpMethodToFilebin(method: int, fileDetails: FileDetails) -> None:
    
    allowedMethods = {
        1: "get",
        2: "post",
        3: "delete"
    }
    print("hello");


# TODO: make details for bin methods too 

url: str = getFilebinURL();