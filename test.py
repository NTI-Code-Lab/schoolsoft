#!/usr/bin/env python3
from pprint import pprint
from bs4 import BeautifulSoup
import requests
import re
import os
from time import gmtime, strftime
import argparse


def Login():
    session = requests.Session()
    redirectedUrl = session.get('')
    print(first.url)
    print(first.cookies.get_dict())

def main():
    url = 'https://sms.schoolsoft.se/nti/sso'
    SmalUrl = 'https://sms.schoolsoft.se/Shibboleth.sso/SAML2/POST'
    with requests.session() as session:
        redirected  = session.get(url)
        redirectedPage = BeautifulSoup(redirected.text, 'html.parser')
        grandidSessionKey = redirectedPage.find('input',{'name':'grandidsession'})['value']
        credential = {
            'fc':'',
            'grandidsession': grandidSessionKey,
            'idpPlugin': True,
            'username': 'matin.akbari',
            'password': 'HP@NTI5379902'
        }
        redirectedSAML = session.post(redirected.url, data=credential)

        redirectedSamlPage = BeautifulSoup(redirectedSAML.text, 'html.parser')

        SAMLResponseKey = redirectedSamlPage.find('input',{'name':'SAMLResponse'})['value']
        RelayStateKey = redirectedSamlPage.find('input',{'name':'RelayState'})['value']

        verification = {
            'SAMLResponse': SAMLResponseKey,
            'RelayState': RelayStateKey
        }

        session.post(SmalUrl, data=verification)

        response = session.get('https://sms.schoolsoft.se/nti/jsp/student/right_student_lunchmenu.jsp?menu=lunchmenu')
        print(response.url)


if __name__ == "__main__":
    main()