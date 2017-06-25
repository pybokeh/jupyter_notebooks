from pprint import pprint
import re
from bs4 import BeautifulSoup

html_content = open('bs_sample.html') # http://dl.dropbox.com/u/49962071/blog/python/resource/bs_sample.html
soup = BeautifulSoup(html_content) # making soap

for tag in soup.find_all(re.compile("^p")): # find all tag start with p
    print tag.name

for tag in soup.find_all(re.compile("t")): # find all tag contains t
    print tag.name

for tag in soup.find_all(True): # find all tag
    print tag.name

pprint(soup.find_all('a')) # find all a tag
print 20*"++"
pprint(soup.find_all(["a", "b"])) # find multiple tag


def has_class_but_no_id(tag):
    return tag.has_key('class') and not tag.has_key('id')

pprint(soup.find_all(has_class_but_no_id)) # pass a function to find_all

pprint(soup.find_all(text=re.compile("sisters"))) # find all tag content contains key 'sisters'
print 20*"++"
pprint(soup.find_all(href=re.compile("my_url"))) # all links contains key "my_url"
pprint(soup.find_all(id=True)) # all links has id
pprint(soup.find_all(class_=True)) # all links has class

def has_six_characters(css_class):
    return css_class is not None and len(css_class) == 7

pprint(soup.find_all(class_=has_six_characters)) # find all class name contains 7 characters

pprint(soup.find_all("a", "sister")) # find all a tag have class named 'sister'
pprint(soup.find_all("a", re.compile("sister"))) # find all a tag have class named contains 'sister'
print 20*"++"

pprint(soup.find_all(href=re.compile("elsie"), id='link1')) # url name contains elsie and have id = link1
pprint(soup.find_all(attrs={'href' : re.compile("elsie"), 'id': 'link1'})) # url name contains elsie and have id = link1

pprint(soup.find_all("a", limit=2)) # use limit on findall

pprint(soup.html.find_all("title", recursive=True)) # use recursive on findall






