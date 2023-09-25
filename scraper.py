from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import time
import os

from bs4 import BeautifulSoup

#Initialise Chromium Driver

domain = 'https://www.orgsyn.org'
data_source = 'https://www.orgsyn.org/result.aspx'
rxID = []
totalVolume = 100

reactionItemClassName = "collapsibleContainer ui-widget"


#Identify The select element to choose volume
def chooseVol(chrome, vol: str):
    try: 
        volume_select = chrome.find_element(By.NAME, 'ctl00$QuickSearchAnnVolList1')
        select = Select(volume_select)

        #volume_options = select.options
        select.select_by_value(vol) #fromm 100 to 1
        time.sleep(1)
    except Exception as e:
        print('select is not clicked')
        print(e)


#Identify Go Button
def clickGo(chrome):
    try:
        go_button_xpath = '//*[@id="tabs-1"]/div/table/tbody/tr/td[5]/a'
        go_button = chrome.find_element(By.XPATH, go_button_xpath)
        go_button.click()
        print('go btn clicked')
    except Exception as e:
        print('go btn is not clicked')
        print(e)


#Check if the popup modal is visible and click 'accept' only when visible
def handlePopup(chrome):
    try:
        WebDriverWait(chrome, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "hazardTable")))
        chrome.find_element(By.ID, 'ImageButton33').click()
        print('accept btn clicked')
    except Exception as e:
        print('popup is not clicked')
        print(e)


    
#Click ALl Button to make sure all records are visible
def clickToShowAll(chrome):
    try:
        all_btn = chrome.find_element(By.NAME, 'ctl00$MainContent$btnAllTop')
        all_btn.click()
        time.sleep(1)
    except Exception as e:
        print('All button is not clicked')
        print(e)




'''

#Helper Functions
def idByXPATH(num: int):
    return f'//*[@id="content"]/div[{num}]/div/div[2]/div[2]/div[3]/text()[2]'

def prettify(rawText: str):
    first = rawText.replace('10.15227/orgsyn.', 'v')
    second = first.replace('.', 'p')

    return second
'''



#Extract RxID for each vol page
def extractRxID(vol: int, chrome):
    
    #Initialise beautifulSoup for effective parsing
    soup = BeautifulSoup(chrome.page_source, 'html.parser')

    #Initialise etree toparse element by xpath
    #dom = etree.HTML(str(soup))

    #Find all div with class name = 'tocdoi' and store the results in an array
    
    numOfReactions = len(soup.find_all('div', class_=reactionItemClassName))

    for i in soup.find_all('div', class_=reactionItemClassName):
        id = i.get('id')
        rxID.append(id)
        print(id)
        #rxID.append(prettify(id))
        #print(prettify(id))

    print(f'{numOfReactions} is expected for vol-{vol}, total records obtained is {len(rxID)}, {vol}/{totalVolume}')
    time.sleep(1)
    
    

def extractAllVolume(totalVolume):
    
    chrome = webdriver.Chrome()
    chrome.get(data_source)
    for i in range(1,totalVolume+1):
        chooseVol(chrome, str(i))
        clickGo(chrome)
        if i == 1:
            handlePopup(chrome)
        clickToShowAll(chrome)
        extractRxID(i, chrome)
    chrome.quit()


    
    return rxID


        
    


if __name__ == '__main__':
    extractAllVolume(totalVolume)
    








