import os, sys, subprocess

def crawlerCurl(urlAdress):
    """ Performs curl response to the requested url address """
    holder = subprocess.check_output(['curl', '-k', urlAdress]).split('\n')
    return holder

url = "https://gamewith.net/cod-modernwarfare/article/show/11872"

response = crawlerCurl(url)