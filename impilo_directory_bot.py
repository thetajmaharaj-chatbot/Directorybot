import csv, re, time
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

PROFILE={"business_name":"Impilo Drilling","phone":"083 419 2100","email":"info@impilodrilling.co.za","website":"https://impilodrilling.co.za","services":["Borehole Drilling","Divining","Geo Survey","Pump Installation","Water Tank Installation","Water Testing","Water Purification"]}
SEED_URLS=[
"https://www.sabusinessdirectory.co.za/select-directory-package/",
"https://www.gautengbusiness.co.za/submit-listing/",
"https://www.entrepo.co.za/business-directory",
"https://www.thebusinessdirectory.co.za/add-listing/listings/",
"https://digitalorbitweb.co.za/",
"https://www.dukacentral.com/submit"]
OUT=Path("impilo_directory_targets.csv")
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; ImpiloDirectoryBot/1.0; +https://impilodrilling.co.za)"}

@dataclass
class Candidate:
    domain:str; url:str; title:str; likely_form:bool; free_signal:bool
    captcha_signal:bool; account_signal:bool; status:str; notes:str

def fetch(url):
    r=requests.get(url,headers=HEADERS,timeout=20)
    r.raise_for_status()
    return r.text

def analyse(url):
    html=fetch(url); soup=BeautifulSoup(html,"html.parser")
    text=" ".join(soup.stripped_strings).lower()
    title=soup.title.get_text(" ",strip=True) if soup.title else urlparse(url).netloc
    form=soup.find("form") is not None
    free=bool(re.search(r"\bfree\b|r\s*0(?:\.00)?|no cost",text))
    captcha=bool(re.search(r"captcha|recaptcha|hcaptcha|turnstile",text))
    account=bool(re.search(r"register|create account|sign in|log in|verification email",text))
    if captcha: status,notes="MANUAL_ACTION","CAPTCHA/anti-bot signal detected"
    elif account: status,notes="ACCOUNT_OR_VERIFICATION","Account/login/verification may be required"
    elif form: status,notes="FORM_CANDIDATE","Submission form detected"
    else: status,notes="DISCOVERED","No direct form detected; inspect links"
    return Candidate(urlparse(url).netloc,url,title,form,free,captcha,account,status,notes)

def find_submission_links(url):
    try: soup=BeautifulSoup(fetch(url),"html.parser")
    except Exception: return []
    domain=urlparse(url).netloc; hits=[]
    rx=re.compile(r"(add|submit|register|list).*(business|listing)|business.*(add|submit|register)",re.I)
    for a in soup.find_all("a",href=True):
        href=urljoin(url,a["href"]); label=" ".join(a.stripped_strings)
        if urlparse(href).netloc==domain and rx.search(label+" "+href): hits.append(href)
    return list(dict.fromkeys(hits))[:10]

def main():
    queue=list(SEED_URLS); seen=set(); rows=[]
    while queue:
        url=queue.pop(0)
        if url in seen: continue
        seen.add(url); print("[SCAN]",url)
        try:
            item=analyse(url); rows.append(item); print(" ",item.status,"free=",item.free_signal,"form=",item.likely_form)
            queue.extend(x for x in find_submission_links(url) if x not in seen)
        except Exception as e:
            rows.append(Candidate(urlparse(url).netloc,url,"",False,False,False,False,"ERROR",str(e)[:180]))
            print(" ERROR",e)
        time.sleep(1)
    with OUT.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(Candidate.__dataclass_fields__)); w.writeheader()
        for row in rows: w.writerow(asdict(row))
    print("Saved",len(rows),"targets to",OUT)

if __name__=="__main__": main()
