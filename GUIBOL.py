from tkinter import*
from tkinter import messagebox, ttk, Checkbutton
import requests, json, datetime, time, random, traceback
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd
import concurrent.futures


def caller():
    class GUI:
        def __init__(self, root):
            self.root = root
            self.root.title("GUI")
            self.root.resizable(False,False)
            self.root.geometry("500x200+300+150")
            self.listofdict = list()
            self.date = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")       
            self.datesave = datetime.datetime.now().strftime("%d-%m-%Y")  
            self.headers = {
                'Accept': '*/*',
                'Accept-Language': 'en-PK,en-US;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
                'content-type': 'application/json, text/javascript, */*; q=0.01',
                'sec-ch-ua': '^\^',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '^\^Windows^^',
            }
            #------------- Main Frame for Inputs---------------
            Frame_Inputs = Frame(self.root, bg='wheat',borderwidth = 2, relief = "sunken")
            Frame_Inputs.place(x=10,y=5, height =120 , width =480)
        
            title = Label(Frame_Inputs, text = "Bol.com" ,font=("Times New Roman",22,"bold" ),fg="white", bg="blue").place(x=200 , y=1)
            title_Keyword= Label(Frame_Inputs, text = "Keyword" ,font=("Times New Roman",12,"bold" ),fg="black", bg="wheat").place(x=10 , y=45)
            self.txtKeyword = Entry(Frame_Inputs,font=("Times New Roman",12,"bold" ),borderwidth = 3, bg="white", relief = "sunken")
            self.txtKeyword.place(x=130 , y=45,height =30 , width =330)

            title_URL= Label(Frame_Inputs, text = "URL. " ,font=("Times New Roman",12,"bold" ),fg="black", bg="wheat").place(x=10 , y=80)
            self.txtURL = Entry(Frame_Inputs,font=("Times New Roman",12,"bold"),borderwidth = 3, bg="white", relief = "sunken")
            self.txtURL.place(x=130 , y=80,height =30 , width =330)
            #-------------  Frame for Buttons---------------
            
            Frame_buttons = Frame(self.root, bg='wheat',borderwidth = 2, relief = "sunken")
            Frame_buttons.place(x=10,y=125, height =70 , width =480)
            self.excelvar = BooleanVar()
            self.chkExcel = Checkbutton(Frame_buttons,text='Excel',variable=self.excelvar, onvalue=1, bg='wheat')
            self.chkExcel.place(x=20 , y=10)
            self.csvvar = BooleanVar()
            self.chkCSV = Checkbutton(Frame_buttons,text='CSV', onvalue=1,variable=self.csvvar, bg='wheat')
            self.chkCSV.place(x=20 , y=30)
           
            Scrap_Button = Button(Frame_buttons,text = "Scrap It",command= self.user_data,cursor="hand2", font=("Times New Roman" , 12))
            Scrap_Button.config( height = 2, width = 15 )
            Scrap_Button.place(x=320 , y=5)
           

        #------------- Bot Speed Slow---------------
        def delay(self):
            time.sleep(random.randint(2, 5))

        #------------- Scrape Single Page Product---------------
        def scraper(self, productid):
            self.delay()
            datadict = dict()
            response = requests.get(f'https://www.bol.com/nl/ajax/dataLayerEndpoint.html?product_id={productid}', headers=self.headers)
            json_res = response.json()
            datadict['EAN CODE'] = json_res.get('dmp').get('ean') 
            datadict['RESELL PRICE'] = json_res.get('dmp').get('price') if json_res.get('dmp').get('price') != 0 else 'OOS'
            datadict['BRAND'] =  json_res.get('dmp').get('brand') if json_res.get('dmp').get('brand') != '' else json_res.get('dmp').get('author')
            datadict['DATE'] = self.datesave
            self.listofdict.append(datadict)
            print(datadict)

        #------------- Scrape Mian Pages ---------------
        def scrapedata(self,driver):
            while True:
                try:
                    self.delay()
                    productidlist  = [productid.get_attribute('data-id') for productid in driver.find_elements(By.XPATH, '//ul[@id="js_items_content"]/li')]
                    # for i in productidlist[:5]:
                    #     self.scraper(i)
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.map(self.scraper, productidlist)
                    try:
                        driver.find_element(By.XPATH,'//li[@class="[ pagination__controls pagination__controls--next ] js_pagination_item"]').click()
                    except:
                        try:
                            driver.refresh()
                            self.delay()
                            driver.find_element(By.XPATH,'//li[@class="[ pagination__controls pagination__controls--next ] js_pagination_item"]').click()
                        except NoSuchElementException:
                            break
                except: 
                    traceback.print_exc()
           

        #------------- Initiate Web Browser ---------------
        def initiate_browser(self):
            ser=Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=ser)
            # text = 'ellanora'
            return driver           

        #------------- Calling Main Pages Function ---------------
        def saraping_keyword_pages(self):
            driver = self.initiate_browser()
            #keywords                             
            for searchkeyword in self.p1:
                if searchkeyword != '':
                    searchkeyword = searchkeyword.strip()
                    driver.get(f'https://www.bol.com/nl/nl/s/?page=1&searchtext={searchkeyword}&view=tile&availability=non')
                    time.sleep(5)  
                    try:driver.find_element(By.XPATH,'//button[@data-test="consent-modal-confirm-btn"]/span').click()
                    except: pass
                    page_title = driver.find_element(By.XPATH, '//h1[@data-test="page-title"]').text
                    self.scrapedata(driver)
                    self.save_data(page_title)
                    self.listofdict.clear()
            #URLS
            for url in self.p2:                
                if url != '':
                    url = url.strip()
                    driver.get(url)
                    time.sleep(5)
                    try:driver.find_element(By.XPATH,'//button[@data-test="consent-modal-confirm-btn"]/span').click()
                    except: pass
                    page_title = driver.find_element(By.XPATH, '//h1[@data-test="page-title"]').text
                    self.scrapedata(driver)
                    self.save_data(page_title)
                    self.listofdict.clear()
            print('Scraping Complete!!')          

        #------------- Save Data ---------------
        def save_data(self,page_title):
            if self.csvvar.get() == 1:
                df = pd.DataFrame.from_dict(self.listofdict)
                df.to_csv(f'bol-{page_title}-{self.date}.csv',index=False)        
                print('Saved Data in CSV!!')
            if self.excelvar.get() == 1:
                df = pd.DataFrame.from_dict(self.listofdict)
                df.to_excel(f'bol-{page_title}-{self.date}.xlsx',index=False)
                print('Saved Data in Excel!!')
            
       #------------- User Data ---------------    
        def user_data(self):
            try:               
                if self.csvvar.get() != 0 or  self.excelvar.get() != 0:
                    p1 = self.txtKeyword.get()
                    try: self.p1 = p1.split(',')
                    except: self.p1 = p1
                    p2 = self.txtURL.get()
                    try: self.p2 = p2.split(',')
                    except: self.p2 = p2
                    print(self.p1, self.p2)
                    try:
                        self.saraping_keyword_pages()
                    except: traceback.print_exc()
                if self.csvvar.get() == 0 and  self.excelvar.get() == 0:
                        messagebox.showerror("Error", "Please Select CSV or Excel for output.", parent=self.root)                    
            except Exception as es:
                    messagebox.showerror("Error", f"Error due to: {str(es)}", parent=self.root)
    root = Tk()
    obj = GUI(root)
    root.mainloop()
caller()



    
        