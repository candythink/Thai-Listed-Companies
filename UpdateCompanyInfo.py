import pandas as pd
import subprocess
import time
import paramiko
import os
import re
from pymongo import MongoClient
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
sys.path.append('/root/app')
from Logging.mongo_logging import MongoHandler
import logging

import uuid

def CreateLogger(name):
    # Configure logging to save messages to MongoDB
    mongoCollection = name
    uuid4 = uuid.uuid4()
    mongo_handler = MongoHandler(mongoCollection, str(uuid4))

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger()
    logger.addHandler(mongo_handler)


mongoUser = "batt"
mongoPassword = "qazwsx1q2w"
mongoIP = "fireball-fireball-mongo-1"
mongoPort = 27017
mongoDatabase = "th"
mongoCollection = "stocks"

mongo_uri = f"mongodb://{mongoUser}:{mongoPassword}@{mongoIP}:{mongoPort}/{mongoDatabase}"

def MongoConnect():
    client = MongoClient(mongo_uri)
    db = client[mongoDatabase]
    return db[mongoCollection]

#ปิดการเชื่อมต่อ
def MongoClose():
    client = MongoClient(mongo_uri)
    client.close

    
def initialize_webdriver(url, username, password):
    auth_url = f"https://{username}:{password}@{url.lstrip('http://')}"
    options = webdriver.ChromeOptions()
    driver = webdriver.Remote(command_executor=auth_url, options=options)
    return driver


def CloseWebdriver(driver):
    driver.close()
    driver.quit()
    
def DownloadPP_001(driver):
    url = 'https://www.fe-data.or.th'
    username = 'lumduan'
    password = 'uFcPSaScVn5VXu9'
    
    waitingLoadTime = 5
    
    
    try:
        logging.info(f'Open {url}')
        driver.implicitly_wait(3)
        driver.get(url)
        
        logging.info('Accept Cookies')
        cookiesButton =  WebDriverWait(driver, waitingLoadTime).until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/main/div/footer/div[2]/div/div/button')))
        cookiesButton.click()
        
        try:
            logging.info("Logging In...")
            loginButton =  WebDriverWait(driver, waitingLoadTime).until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/nav/div/div[3]/button[4]')))
            loginButton.click()
            
            userInputbox = WebDriverWait(driver, waitingLoadTime).until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div[7]/div/div[1]/form/div[1]/div/div[1]/div[2]/input')))
            passwordInputbox = driver.find_element(By.XPATH,'//*[@id="password"]')
            userInputbox.send_keys(username)
            passwordInputbox.send_keys(password)
            
            loginButton =  driver.find_element(By.XPATH,'//*[@id="app"]/div[7]/div/div[1]/div[2]/div/button')
            loginButton.click()
            logging.info('Loggin Success')
            
            try:
                logging.info('Goto Performent page')
                time.sleep(2)
                driver.implicitly_wait(waitingLoadTime)
                menuClick = WebDriverWait(driver, waitingLoadTime).until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/aside/div[1]/ul/li[1]/div[1]/div[1]')))
                menuClick.click()
                menuClick = WebDriverWait(driver, waitingLoadTime).until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/aside/div[1]/ul/li[1]/div[2]/div/div/div-span/a/div')))
                menuClick.click()
                
                logging.info('Try to download file')
                downloadClick = WebDriverWait(driver, waitingLoadTime).until(EC.presence_of_element_located((By.XPATH,'//*[@id="0"]/div[2]/div[3]')))
                downloadClick.click()
                logging.info('Files "PP_001" is Downloaded')
                
                try:
                    logging.info('Logging Out..')
                    logoutButton = WebDriverWait(driver, waitingLoadTime).until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/nav/div/div[3]/button[4]')))
                    logoutButton.click()
                    # time.sleep(1)
                    logoutButton = WebDriverWait(driver, waitingLoadTime).until(EC.presence_of_element_located((By.XPATH,'/html/body/div/div[12]/div[2]')))
                    driver.execute_script("arguments[0].scrollIntoView(true);", logoutButton)
                    logoutButton.click()
                    logging.info('Logout Success')
                    CloseWebdriver(driver)
                    return True
                    
                except Exception as e:
                    logging.error("Failed Logout:", e)
                    return False
                
        
            except Exception as e:
                logging.error("Failed to Download File:", e)
                return False
            
        except Exception as e:
            logging.error("Failed Login:", e)
            return False
        
    except Exception as e:
        logging.error("Failed to open web:", e)
        return False
        
        
def Tranferfile():
    time.sleep(2)
    logging.info('Tranferfile From Remote Server')
    
    # SSH connection details
    hostname = 'lumduan.thddns.net'
    port = 9222
    username = 'batt'
    privateKeyPath = '/root/.ssh/id_rsa'  # Path to your private key file

    # Path of the file on the remote server
    remotePath = '/home/batt/docker/selenium/files/PP_001.xlsx'

    # Local directory where you want to save the file
    localDirectory = '/root/app/bot/Update-Company-Info/'

    try:
        # Create an SSH client instance
        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load your private key
        privateKey = paramiko.RSAKey.from_private_key_file(privateKeyPath)

        # Connect to the remote server using key-based authentication
        sshClient.connect(hostname=hostname, port=port, username=username, pkey=privateKey)
        logging.info("Login successful.")

        # Open an SFTP session
        sftp = sshClient.open_sftp()

        # Extract the filename from the remotePath
        filename = os.path.basename(remotePath)

        # Construct the local file path
        localFilePath = os.path.join(localDirectory, filename)

        # Download the file from the remote server to your local machine
        sftp.get(remotePath, localFilePath)
        logging.info("File transfer successful.")

        # Remove the file from the remote server
        sftp.remove(remotePath)
        logging.info("Remote file removed successfully.")

        # Close the SFTP session
        sftp.close()
        

    except paramiko.AuthenticationException:
        logging.error("Login failed. Authentication error.")
        return False

    except paramiko.SSHException as e:
        logging.error(f"Login failed. SSH error: {e}")
        return False


    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False

    finally:
        # Close the SSH connection
        sshClient.close()
        logging.info("Logged out.")
        return True
        
def CleansingData():
    logging.info('Cleansing Excel Data')
    time.sleep(2)
    def findHeaderRow(sheet, headerText):
        """
        Finds the row index where the specified header text is located.

        :param sheet: The sheet object from which to find the header row.
        :param headerText: The text to search for in the first row.
        :return: The index of the header row.
        """
        for i, row in sheet.iterrows():
            if row[0] == headerText:
                return i
        return 0

    def findLastRow(sheet, columnName):
        """
        Finds the last row index with actual data before any explanatory notes or blank rows.

        :param sheet: The sheet object to search in.
        :param columnName: The name of the column to check for the last row with data.
        :return: The index of the last valid row.
        """
        # Iterate backwards from the end of the DataFrame until a non-empty row is found
        for i in reversed(range(len(sheet))):
            if pd.notnull(sheet.loc[i, columnName]):
                return i
        return None

    def cleanSpaces(cell):
        """
        Replaces sequences of more than two spaces with a single space in a string.

        :param cell: The string to clean.
        :return: The cleaned string with spaces normalized.
        """
        if isinstance(cell, str):
            return re.sub(r' {2,}', ' ', cell)
        return cell

    def removeAllSpaces(cell):
        """
        Removes all spaces from a string.
        """
        if isinstance(cell, str):
            return cell.replace(' ', '')
        return cell

    def readAndCleanExcel(filePath, sheetName, headerText):
        """
        Reads an Excel file, identifies the correct header based on the given text, cleans the spaces,
        and cleans the data.

        :param filePath: The path to the Excel file.
        :param sheetName: The name of the sheet to extract data from.
        :param headerText: The text to identify the header row.
        :return: A cleaned Pandas DataFrame.
        """
        try:
            # Read the sheet without headers first
            sheet = pd.read_excel(filePath, sheet_name=sheetName, header=None)

            # Find the header row
            headerRow = findHeaderRow(sheet, headerText)
            if headerRow == 0:
                raise ValueError(f"Header row with '{headerText}' not found")

            # Read the data again with the correct header row
            data = pd.read_excel(filePath, sheet_name=sheetName, header=headerRow)

            # Find the last valid row
            lastRow = findLastRow(data, headerText)
            data = data.loc[:lastRow - 4]

            # Clean spaces in the data and remove all spaces from 'Security Symbol' column
            for column in data.columns:
                if column == headerText:
                    data[column] = data[column].apply(removeAllSpaces)
                else:
                    data[column] = data[column].apply(cleanSpaces)
            
            data['CG Score'] = data['CG Score'].fillna(0)
            data = data.map(lambda x: ' '.join(x.split()) if isinstance(x, str) else x)

            logging.info('Data is Cleaned')
            return data

        except Exception as e:
            logging.error(f"{e}")
            return None

    def exportToCsv(data, filePath):
        """
        Exports a DataFrame to a CSV file.

        :param data: Pandas DataFrame to export.
        :param filePath: Path where the CSV file will be saved.
        """
        try:
            data.to_csv(filePath, index=False)
            logging.info(f"Data successfully exported to {filePath}")
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")

    def exportToJson(data, filePath):
        """
        Exports a DataFrame to a JSON file with UTF-8 encoding.

        :param data: Pandas DataFrame to export.
        :param filePath: Path where the JSON file will be saved.
        """
        try:
            data.to_json(filePath, orient='records', lines=True, force_ascii=False, default_handler=str)
            logging.info(f"Data successfully exported to {filePath}")
        except Exception as e:
            logging.error(f"Error exporting to JSON: {e}")

    # Example Usage
    filePath = '/root/app/bot/Update-Company-Info/PP_001.xlsx'
    sheetName = 'profile'
    headerText = 'Security Symbol'

    cleanedData = readAndCleanExcel(filePath, sheetName, headerText)

    if cleanedData is not None:
        # Export to Excel
        exportToCsv(cleanedData, '/root/app/bot/Update-Company-Info/ThaiListedCompanies.csv')
        # Export to JSON
        exportToJson(cleanedData, '/root/app/bot/Update-Company-Info/ThaiListedCompanies.json')    
        return True

    else:
        return False
        
def UploadToGithub():
    # Change the current working directory
    repo_path = '/root/app/bot/Update-Company-Info'
    try:
        os.chdir(repo_path)
    except FileNotFoundError:
        logging.error("Error: Specified directory does not exist.")
        return
    except PermissionError:
        logging.error("Error: Permission denied to change directory.")
        return

    # Execute shell commands to add, commit, and push changes
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "update"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        logging.info("Changes successfully pushed to GitHub.")
        return True
    
    except subprocess.CalledProcessError as e:
        logging.error("Error Upload to Github:", e)
        return False
        
def MainCode():
    url = 'sel.spellred.com'
    username = 'batt'
    password = 'h3nNem8TVQfqYxjtDUR4r6gpya9ZEsPXG5dK2AuHc7kMSvzJbW'
    driver = initialize_webdriver(url, username, password)
    
    if DownloadPP_001(driver):
            if Tranferfile():
                if CleansingData():
                    if UploadToGithub():
                        logging.info('Script Runcomplete Exit script...')
    
if __name__ == "__main__":
    logger = CreateLogger('UpdateCompanyInfo')
    MainCode()
    
    # logging.info(infoLog)
    # logging.error(errorLog)
