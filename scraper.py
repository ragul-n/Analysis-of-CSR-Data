import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import sys
from alive_progress import alive_bar


csr_data=pd.read_csv("C:\Projects\CSR Data\Datasets\master data\master_data.csv")


def get_company_data(CIN, page_content):

    table=pd.read_html(page_content)[0]
    table=table.T
    table.columns=table.iloc[0]
    table=table.iloc[1:]
    table["CIN"]=CIN
    return table

def  get_yearwise_data(page_content):  
    soup = BeautifulSoup(url_contents, features="html")
    divs= soup.find_all("div", {"class": "panel panel-default"})

    projects_data=[]
    csr_aggregate=[]
    for  div in divs:
        
        year = div.find("h4", {"class":"panel-title"}).getText()

        #reading projects data
        try:
            table=pd.read_html(str(div), attrs={"id":"datatable"})[0]
            table["year"]=year
            projects_data.append(table)
        except:
            pass
        
        
        #reading aggregate CSR spending
        try:
            table=pd.read_html(str(div), attrs={"id":"employee_data"})[0]
            table=table.T
            table.columns=table.iloc[0]
            table=table.iloc[1:]
            table["CIN"]=CIN
            table["year"]=year
            csr_aggregate.append(table)
        except:
            pass

    projects_data=pd.concat(projects_data)
    csr_aggregate=pd.concat(csr_aggregate)
    
    return projects_data, csr_aggregate


def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()
    
if __name__=="__main__":
    company_data=[]
    projects_data=[]
    csr_spending_data=[]

    with alive_bar(5) as bar: 
        for CIN in csr_data.CIN_Number.unique()[:5]:
            #for CIN in progressbar(csr_data.CIN_Number.unique()[:2], "Completed: ", 100):
            url = "https://csr.gov.in/companyprofile.php?year=FY+2015-16&CIN=" + CIN
            url_contents = urllib.request.urlopen(url).read()

            company=get_company_data(CIN, url_contents)
            projects, spending= get_yearwise_data(url_contents)
            
            company_data.append(company)
            projects_data.append(projects)
            csr_spending_data.append(spending)

            pd.concat(company_data).to_csv("company_data.csv")
            pd.concat(projects_data).to_csv("projects_data.csv")
            pd.concat(csr_spending_data).to_csv("csr_spending_data.csv")
            bar()