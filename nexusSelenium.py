#!/usr/bin/python2.7
# -*-coding:Latin-1 -* 

import os
import tarfile
import time
import configparser
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import logging
import inspect
from datetime import datetime
import cryptman


# 1 - Declaration de variables globaux (logging, logins et mot de passes)
currentDir        = os.getcwd()
TIMESTAMP         = datetime.now().strftime("%Y%m%d")
YEAR              = datetime.now().strftime("%Y")
destinationFolder = currentDir + '\\destination'
logging.basicConfig(filename=currentDir + '/log/'+TIMESTAMP+'_export_Nexus.log', filemode='w',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
config = configparser.ConfigParser()
config.read(currentDir + '\\config')
#exportFolder      = currentDir + '\\export'
exportFolder = "C:\Users\m_merrien\Documents\CCO\WELLDATA_XML"
fichiers = []
key            = str(config['DEFAULT']['key'])
nexus_user     = config['NEXUS']['username']
nexus_pass     = cryptman.decrypt(config['NEXUS']['password'])
nexus_url      = config['NEXUS']['url']
nexus_repo_url = config['NEXUS']['repo_url']

logging.info(str(inspect.stack()[0][3]) +
                 " : " + "Dossier de travail  : " + currentDir)
logging.info(str(inspect.stack()[0][3]) +
                 " : " + "Dossier export  : " + exportFolder)

# 2- Definition Options chrome, dossier de telechargement des tgz
chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory": exportFolder}
chromeOptions.add_experimental_option("prefs", prefs)
#chromeOptions.headless = True
chromeOptions.add_argument("disable-gpu")


def creation_Dossier_Nexus():
    logging.info(str(inspect.stack()[0][3]) + " : " +
                 "Creation du dossier Nexus")

# 3 - Telechargement des fichier tgz
def download_Files():
    try:
        driver = webdriver.Chrome(
            'chromedriver/chromedriver.exe', options=chromeOptions)
        driver.get(nexus_url)
        time.sleep(3)
        sign_in_btn = driver.find_element_by_id('nx-header-signin-1145-btnInnerEl')
        sign_in_btn.click()
        username = driver.find_element_by_id('textfield-1273-inputEl')
        user_password = driver.find_element_by_id('textfield-1274-inputEl')
        username.send_keys(nexus_user)
        user_password.send_keys(nexus_pass)
        sign_in_btn_ = driver.find_element_by_id('button-1276-btnInnerEl')
        sign_in_btn_.click()
        driver.get(nexus_repo_url)
        lnks = driver.find_elements_by_tag_name("a")
        files = getFilesLinks(lnks)
        for fichier in files:
            logging.info(str(inspect.stack()[
                         0][3]) + " : " + "Telechargement du fichier : " + fichier["nom"])
            driver.get(fichier["lien"])
            download_wait(exportFolder, 30)
    except Exception as ex:
        logging.error(str(inspect.stack()[0][3]) + " : " + str(ex))

# 4 - Obtenir que les liens des fichier souhaites  tgz
def getFilesLinks(lnks):
    logging.info(str(inspect.stack()[0][3]) + " : " +
                 "Obtention des liens de fichiers à télécharger")
    try:
        for lnk in lnks:
            if lnk.get_attribute('text') != 'Parent Directory':
                fichiers.append({"lien": lnk.get_attribute(
                    'href'), "nom": lnk.get_attribute('text')})
        return fichiers
    except Exception as ex:
        logging.error(str(inspect.stack()[0][3]) + " : " + str(ex))

# 5 - Vérification si le téléchargement est fini __________________________
def download_wait(directory, timeout, nfiles=None):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True
        for fname in files:
            if fname.endswith('.crdownload'):
                dl_wait = True
        seconds += 1
    return seconds

# 6 - Unzip les fichiers dans le dossier destinataire
def extract(tar_file, extract_path='.'):
    logging.info(str(inspect.stack()[0][3]) +
                 " : " + "Extraction des fichiers : " + str(tar_file))
    try:
        tar = tarfile.open(tar_file, 'r')
        sub_folder = os.path.basename(os.path.splitext(tar_file)[0])

        if os.path.exists(extract_path + '\\'+ YEAR +'\\'+ TIMESTAMP + '\\' + sub_folder):
            os.makedirs(extract_path + '\\'+ YEAR +'\\'+ TIMESTAMP + '\\' + sub_folder)
        for item in tar:
            tar.extract(item, extract_path + '\\'+ YEAR +'\\'+ TIMESTAMP + '\\' + sub_folder)
            if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
                extract(item.name, "./" + item.name[:item.name.rfind('/')])
    except Exception as ex:
        logging.error(str(inspect.stack()[0][3]) + " : " + str(ex))

# 7 - Extraction et suppression des archives
def export():
    try:
        for file in os.listdir(exportFolder):
            if file.endswith(".tgz"):
                extract(os.path.join(exportFolder, file), destinationFolder)
        #for f in os.listdir(exportFolder):
            #os.remove(os.path.join(exportFolder, f))
    except Exception as ex:
        logging.error(str(inspect.stack()[0][3]) + " : " + str(ex))
    
# ______________________Main functions_____________________
logging.info(str(inspect.stack()[0][3]) + " : " + "Debut de l'export Nexus")
download_Files()
#export()





