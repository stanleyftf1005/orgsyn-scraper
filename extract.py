import requests
from bs4 import BeautifulSoup
from scraper import domain, extractAllVolume
from scraper import totalVolume
from pathlib import Path
from lxml import etree
import os
import pandas as pd


rxPageURLPrefix = 'https://www.orgsyn.org/demo.aspx?prep='

imageSrcPrefix = '/content/figures/'



#Declare path variables for all output files
dir = Path.cwd()
folderPath = Path('rxImg/')

#target xpath value for the reaction route image
targetImgXPATH = {
    '1': './/*[@id="ctl00_MainContent_procedureBody"]/div[4]/table/tbody/tr/td/img',
    '2': './/*[@id="ctl00_MainContent_procedureBody"]/div[5]/table/tbody/tr/td/img'
}


dataset = []


#helper function to generate reaction page url: 'https://www.orgsyn.org/demo.aspx?prep=' + 'id'
def rxURL(id: str):
    return rxPageURLPrefix+id

#helper function to generate image src if cannot be parsed from webpage
def rxnImgSrcFallback(id):
    return domain+f'{imageSrcPrefix}{id}.gif'

def downloadImg(id: str, imgURL: str):
    fileName = id+'.jpg'
    r = requests.get(imgURL)
    filePath = os.path.join(dir, folderPath, fileName)
        
    with open(filePath, 'wb') as f:
        f.write(r.content)
    
    relPath = os.path.relpath(filePath)
    
    return relPath

#export extracted metadata to a file named 'dataset.csv'
def exportCSV(dataset: list):
    data = dataset
    fileName = 'dataset.csv'
    filePath = os.path.join(dir, fileName)

    df = pd.DataFrame(data)
    df.to_csv(filePath, index=False, header=True)


#extract all metadata from each individual reaction page
def extractPageContent(id: str):
    url = rxURL(id)
    response = requests.get(url).text


    #initialise soup
    soup = BeautifulSoup(response, 'html.parser')

    #initialise lxml
    dom = etree.HTML(str(soup))

    #extract image url

    filePath = ''



    if len(dom.xpath(targetImgXPATH['1']))>0:

        imgURL = domain + dom.xpath(targetImgXPATH['1'])[0].get('src')
        #download the image, write to /rxImg folder and return a filePath reference
        filePath = downloadImg(id, imgURL)

    elif len(dom.xpath(targetImgXPATH['2']))>0:

        imgURL = domain + dom.xpath(targetImgXPATH['2'])[0].get('src')
        #download the image, write to /rxImg folder and return a filePath reference
        filePath = downloadImg(id, imgURL)
    
    else:
        imgURL = rxnImgSrcFallback(id)
        filePath = downloadImg(id, imgURL)



    #Extract procedures text
    steps = soup.find_all('div', class_='step')

    procedures = []

    #extract reaction procedure(s)
    if len(steps) > 1:
        for index, step in enumerate(steps):
            
            stepData = {
                'id': 'Route '+str(index+1),
                'steppara': [steppara.text for steppara in step.find_all('div', class_='steppara')]
            }

            procedures.append(stepData)
    elif len(steps) == 1:
        stepData = {
                'id': 'Route 1',
                'steppara': [steppara.text for steppara in steps[0].find_all('div', class_='steppara')]
            }

        procedures.append(stepData)

    data = {
        'pageURL': url,
        'fileURL': filePath,
        'possibleRoutes': len(steps),
        'procedures': procedures
    }

    dataset.append(data)



if __name__ == '__main__':

    #first obtain a list of reaction page id from the scraper module and store them in a list
    rxID = extractAllVolume(totalVolume)

    #loop through individual item in the list and extract useful content
    for index, id in enumerate(rxID):
        extractPageContent(id)
        print(f'Record - {id} processed. {str(len(rxID)-index)} records remaining...')

    
    exportCSV(dataset)
    print('all data exported.')
    





        










