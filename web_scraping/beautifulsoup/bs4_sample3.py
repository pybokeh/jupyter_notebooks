from pprint import pprint
import re
from bs4 import BeautifulSoup

html_content = open('bs_sample3.html') # http://dl.dropbox.com/u/49962071/blog/python/resource/bs_sample.html
soup = BeautifulSoup(html_content) # making soap

pprint(soup.select("title")) # get title tag
pprint(soup.select("body a")) # all a tag inside body
pprint(soup.select("html head title")) # html->head->title
pprint(soup.select("head > title")) # head->title
pprint(soup.select("p > a")) # all a tag that inside p
pprint(soup.select("body > a")) # all a tag inside body
pprint(soup.select(".sister")) # select by class
pprint(soup.select("#link1")) # select by id
pprint(soup.select('a[href="http://example.com/elsie"]')) # find tags by attribute value
pprint(soup.select('a[href^="http://example.com/"]'))
# find tags by attribute value, all contains 'http://example.com/'
pprint(soup.select('p[lang|=en]')) # Match language codes





