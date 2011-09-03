"""
 Copyright (c) 2010 Johan Wieslander, <johan[d0t]wieslander<(a)>gmail[d0t]com>

 Permission is hereby granted, free of charge, to any person
 obtaining a copy of this software and associated documentation
 files (the "Software"), to deal in the Software without
 restriction, including without limitation the rights to use,
 copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following
 conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.
"""
import xbmc
import xbmcgui
import xbmcplugin
import re
import urllib2
import urllib
import math

BASE_URL = "http://www.pinkbike.com/video"
 
from BeautifulSoup import MinimalSoup as BeautifulSoup, SoupStrainer

def getHTML(url):
        try:
            print 'getHTML :: url = ' + url
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            link = response.read()
            response.close()
        except urllib2.HTTPError, e:
            print "HTTP error: %d" % e.code
        except urllib2.URLError, e:
            print "Network error: %s" % e.reason.args[1]
        else:
            return link

def listPage(url):
    html = getHTML(urllib.unquote_plus(url))
    soup = BeautifulSoup(html) 
    currentPage = soup.find('li', 'current-page').a['href']
    nextPage = soup.find('li', 'next-page').a['href']
    maxPage = soup.find('li', 'next-page').findPrevious('li').a['href']
    for inItem in soup.findAll('div', 'inItem'):
        try:
            title = inItem.findAll('a')[1].contents[0]
        except:
            title = ""
        link = inItem.find('a')['href']
        re_pinkbike = 'video/(\d+)/'
        id = re.findall(re_pinkbike, link)[0]
        id = int(id)
        partId = int(math.fabs(id/10000))
        url = 'http://lv1.pinkbike.org/vf/' + str(partId) + '/pbvid-' + str(id) + '.flv'
        thumb = inItem.find('img', 'thimg')['src']
        time = inItem.find('span', 'fblack').contents[0]
        plot = inItem.find('p', 'uFullInfo f10 fgrey3').contents[0]
        #
        listitem=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=thumb)
        listitem.setInfo(type="Video", infoLabels={ "Title": title, "Plot" : plot, "Duration" : time })
        listitem.setPath(url)
        listitem.setProperty("IsPlayable", "true")
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem)
    if currentPage != maxPage:
        item=xbmcgui.ListItem('Next page...', iconImage="DefaultFolder.png")
        xurl = sys.argv[0] + '?' + "next=true" + "&url=" + urllib.quote_plus(nextPage.replace('&amp;','&'))
        item.setInfo(type="Video", infoLabels={ "Title": ""})
        item.setPath(xurl)
        folder = True
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=xurl, listitem=item, isFolder=folder)
    return
    
def nextPage(params):
    get = params.get
    url = get("url")
    return listPage(url)

def firstPage():
    html = getHTML(urllib.unquote_plus(BASE_URL))
    soup = BeautifulSoup(html)
    # Favorites
    for links in soup.findAll('a','iconlink'):
        try:
            title = links.contents[0]
        except:
            title = "No title"
        try:
            link = links['href']
        except:
            link = None
        if link and title and not "img" in str(title):
            addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')))
    # Topics
    for table in soup.findAll('tr'):
        for line in table.findAll('a'):
            title = line.contents[0]
            link = line['href']
            addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')))
    # Search
    addPosts('Search..', '&search=True')
    return

def addPosts(title, url):
 listitem=xbmcgui.ListItem(title, iconImage="DefaultFolder.png")
 listitem.setInfo( type="Video", infoLabels={ "Title": title } )
 xurl = "%s?next=True&url=" % sys.argv[0]
 xurl = xurl + url
 listitem.setPath(xurl)
 folder = True
 xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=xurl, listitem=listitem, isFolder=folder)

def search_site():
    encodedSearchString = search()
    if not encodedSearchString == "":
        url = 'http://www.pinkbike.com/video/search/?q=' + encodedSearchString
        listPage(url)
    else:
        firstPage()
    return

def search():
    searchString = unikeyboard("", 'Search PinkBike.com')
    if searchString == "":
        xbmcgui.Dialog().ok('PinkBike.com','Missing text')
    elif searchString:
        dialogProgress = xbmcgui.DialogProgress()
        dialogProgress.create('PinkBike.com', 'Searching for: ' , searchString)
        #The XBMC onscreen keyboard outputs utf-8 and this need to be encoded to unicode
    encodedSearchString = urllib.quote_plus(searchString.decode("utf_8").encode("raw_unicode_escape"))
    return encodedSearchString

#From old undertexter.se plugin    
def unikeyboard(default, message):
    keyboard = xbmc.Keyboard(default, message)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        return keyboard.getText()
    else:
        return ""

#FROM plugin.video.youtube.beta  -- converts the request url passed on by xbmc to our plugin into a dict  
def getParameters(parameterString):
    commands = {}
    splitCommands = parameterString[parameterString.find('?')+1:].split('&')
    for command in splitCommands: 
        if (len(command) > 0):
            splitCommand = command.split('=')
            name = splitCommand[0]
            value = splitCommand[1]
            commands[name] = value
    return commands

if (__name__ == "__main__" ):
    if (not sys.argv[2]):
        firstPage()
    else:
        params = getParameters(sys.argv[2])
        get = params.get
        if (get("search")):
            search_site()
        if (get("next")) and not (get("search")):
            nextPage(params)

xbmcplugin.endOfDirectory(int(sys.argv[1]))