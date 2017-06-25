from pprint import pprint
from bs4 import BeautifulSoup

html_content = open('bs_sample.html') # http://dl.dropbox.com/u/49962071/blog/python/resource/bs_sample.html

soup = BeautifulSoup(html_content) # making soap

print soup.prettify() # prettify html_content even complete uncompleted tag
print 20*'+'
print soup.title # page title tag
print soup.title.name # page title name
print soup.title.parent.name # page title parent
print soup.p # first p tag
print soup.p.string # string content of first p tag
print soup.p['class'] # first p tag class name
print soup.a # # first a tag
print 20*'+'
pprint( soup.find_all('a'))  # all a tag
pprint( soup.find_all('p'))  # all p tag
print 20*'+'
print soup.find(id='link3') # find tag with id = link3
print 'All links:'
for link in soup.find_all('a'):
    print link.get('href')

#print soup.get_text() # return text part of html_document
