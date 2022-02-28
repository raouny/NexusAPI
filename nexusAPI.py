#!/usr/bin/python2.7
# -*-coding:Latin-1 -* 

import requests
from requests.auth import HTTPBasicAuth
import configparser
import os
import cryptman
from datetime import datetime
import logging
import inspect



currentDir        = os.getcwd()
TIMESTAMP         = datetime.now().strftime("%Y%m%d")
#logging.basicConfig(filename='C:\\CCO_Logs/'+TIMESTAMP+'_export_Nexus.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_Global_Variables():
    try:
        logging.info(str(inspect.stack()[0][3]) +
                 " : " + "Debut du script")
        currentDir        = os.getcwd()
        TIMESTAMP         = datetime.now().strftime("%Y%m%d")
        YEAR              = datetime.now().strftime("%Y")
        #destination = currentDir+'/export/'
        destination = "C:\\Users\\m_merrien\\Documents\\CCO\\WELLDATA_XML\\"
        config = configparser.ConfigParser()
        config.read(currentDir + '\\config')
        
        return currentDir, destination, config
    except Exception as ex:
        logging.error(str(inspect.stack()[0][3]) + " : " + str(ex))                     

# Télécharger les archives dans un dossier donné
def download_file(url, destination):
    try:
        
        filename = url.split('/')[-1]
        logging.info(str(inspect.stack()[0][3]) +
                 " : " + "Téléchargement du fichier : " + str(filename))
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(destination+filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        return filename
    except Exception as ex:
        logging.error(str(inspect.stack()[0][3]) + " : " + str(ex))

# Chercher un repo donné via Nexus Rest API
def nexus_API_Get_Assets(config):
    try:
        logging.info(str(inspect.stack()[0][3]) +
                 " : " + "nexus_API_Get_Assets Starting now!")
        response = requests.request("GET", config['NEXUS']['endpoint'], auth=HTTPBasicAuth(config['NEXUS']['username'], cryptman.decrypt(config['NEXUS']['password'])))
        json_Data = response.json()
        for item in json_Data["items"]:
            download_file(item["assets"][0]["downloadUrl"], destination)
    except Exception as ex:
        logging.error(str(inspect.stack()[0][3]) + " : " + str(ex))
#currentDir, destination, config = setup_Global_Variables()
#nexus_API_Get_Assets(config)

print("All good " + str(currentDir))
