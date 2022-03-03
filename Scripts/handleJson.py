#!/usr/bin/python
# -*-coding:Latin-1 -* 

import sys
import json
import logging
import requests



# Lire le fichier json et recuperer les urls des archives
def read_json_file(filepath):
    with open(filepath, 'r') as f:
     data = json.load(f)
    return data


def get_nexus_archives(version):
    
    endpoint = "https://repositories-public.net.extra.laposte.fr/service/rest/v1/search?repository=npm-an&group=cddng&version="
    nexus_response = requests.get(endpoint+version)
    print(endpoint+version)
    with open("/home/rad/jenkins/CCO La Poste/output/response.json", "w+") as f:
        json.dump(nexus_response.json(), f)

def download_file(url, destination):
    try:
        filename = url.split('/')[-1]
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(destination+filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        return filename
    except Exception as ex:
        print( str(ex))

get_nexus_archives(sys.argv[2])
jsonObj = read_json_file(sys.argv[1])
for item in jsonObj["items"]:
    for asset in item["assets"]:
        downloadUrl = asset["downloadUrl"]
        download_file(downloadUrl, "/home/rad/jenkins/CCO La Poste/destination/")


