import urllib2
import os
import threading
import Queue
from datetime import datetime

completed = Queue.Queue()

def getURLContent(url):
    requestHeader = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'}
    requestTimeout = 60
    attempts = 10
    downloaded = False
    content = ""
    while attempts and not downloaded:
        try:
            request = urllib2.Request(url, "", requestHeader)
            content = urllib2.urlopen(request, timeout = requestTimeout).read()
            downloaded = True
        #except urllib2.URLError, e:
            #raise MyException("There was an error: %r" % e)
        except:
            attempts -= 1
            print "Request to {0} failed. {1} attempts left".format(url, attempts)
    
    if not downloaded:
        print "Unable to download {0}".format(url)

    return content

def downloadPicture(name, url, index, count):
    print "Requesting outer {0}/{1}: {2}".format(index, count, url)
    outer = getURLContent(url)

    picPrefix = '"contentUrl": "'
    picSuffix = '"'
    urlStart = outer.find(picPrefix) + len(picPrefix)
    urlEnd = outer.find(picSuffix, urlStart)
    picURL = outer[urlStart:urlEnd]
    
    print "Requesting inner {0}/{1}: {2}".format(index, count, picURL)
    pic = getURLContent(picURL)
    f = open(name, 'wb')
    f.write(pic)
    f.close()

    global completed

    completed.put(url)
    downloaded = completed.qsize()
    remaining = count - downloaded    
    
    print "File {0} downloaded. Total files: {1}. Downloaded: {2}. Remaining: {3}".format(index, count, downloaded, remaining)

def PageScrape(pageurl):
    start = datetime.now()
    print "Requesting {0}".format(pageurl)
    html = getURLContent(pageurl)

    galPrefix = "<title>Porn pics of "
    galSuffix = " (Page 1)</title>"
    galStart = html.find(galPrefix) + len(galPrefix)
    galEnd = html.find(galSuffix, galStart)
    galName = html[galStart:galEnd]
    
    while galName[-1] == '.' or galName[-1] == ' ':
        galName = galName[:-1]

    picPrefix = 'href="/photo/'
    picSuffix = "/?pgid=&amp;gid="
    picCount = html.count(picPrefix)

    print "\nThere are {0} pics in the gallery: {1}\n".format(picCount, galName)

    foldername = 'Downloads/' + galName

    try:
        os.makedirs(foldername)
    except:
        print "Error, make sure there is no directory with this script"
        return 0

    #finding pic indexes within www.imagefap.com/photo/
    pics = list()
    picStart = 0
    while True:
        picStart = html.find(picPrefix, picStart)
        if picStart >= 0:
            picStart += len(picPrefix)
            picEnd = html.find(picSuffix, picStart)
            pics.append(html[picStart:picEnd])
        else:
            break

    #downloading pics
    threads = list()
    picIndex = 1
 
    for pic in pics:
        picName = "{0}/{1:04}_{2}.jpg".format(foldername, picIndex, pic)
        picURL = "http://www.imagefap.com/photo/{0}/".format(pic)

        #downloadPicture(picName, picURL, picIndex, picCount)

        t = threading.Thread(target = downloadPicture, args = (picName, picURL, picIndex, picCount))
        threads.append(t)
        t.start()

        picIndex += 1

    for t in threads:
        t.join()
    
    global completed
    end = datetime.now()

    print ""
    print "Gallery '{0}' downloaded ({1} files)".format(galName, completed.qsize()) 
    print "Source url: {0}".format(pageurl)
    print "Time elapsed: {0}".format(end - start)
    print ""

    completed.queue.clear()

    return 0
    
while True:
    url = raw_input("Enter the url or 'quit' to exit: ")
    if url == "quit":
        break
    else:
        if url.find("?") >= 0:
            url += "&"
        else:
            url += "?"
        url += "view=2"
        PageScrape(url)
        
