import requests
from bs4 import BeautifulSoup
import re
import os
import urllib
from requests.adapters import HTTPAdapter, Retry
try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")
s = requests.Session()
retries = Retry(total=10,
    backoff_factor=0.1,
    status_forcelist=[ 500, 502, 503, 504 ])
s.mount('https://', HTTPAdapter(max_retries=retries))
# to search
query = "developer linkedin resumes .pdf"
i=115
for j in search(query, num_results=100, safe=100, sleep_interval=2):
    if ('.pdf' in j):
        print(j)
        i = i+1
        print("Downloading file: ", i)
 # Get response object for link
        try:
            response = s.get(j)
 #Write content in pdf file
            pdf = open(f"./resumes/{str(i)}.pdf", 'wb')
            pdf.write(response.content)
            pdf.close()
        except:
            print("Error")
        print("File ", i, " downloaded")
print("All PDF files downloaded")