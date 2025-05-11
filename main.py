import requests

req: requests = requests.get("https://filebin.net");

# print(req.text);
binURL: int = str(req.text).find("binURL");
print(binURL);
temp: str = str(req.text);
url: str = temp[1313:1340];
print(url);


# TODO: calculate the binURL dymanically 


b = temp[1324:1340]
print(b + "\n");

