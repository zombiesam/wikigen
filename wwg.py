#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Coded by Sam (info@sam3.se)

import threading, Queue, urllib2, StringIO, re, sys, os, optparse, inspect
reload(sys)
sys.setdefaultencoding("latin-1")


# Add Wikipedia links you do not wish the crawler to visit here
bad_urls = ['/wiki/Wikipedia:Tutorial/Registration', '/wiki/Wikipedia:Authority_control'\
            '/wiki/Help:Contents', '/wiki/Help:Contents', \
            '/wiki/Wikipedia:External_links','/wiki/Wikipedia:Contact_us' \
            '/wiki/Wikipedia:Contact_us_-_Readers','/wiki/Wikipedia:Contact_us_-_Press', \
            '/wiki/Press/Contact/Chapters', '/wiki/Wikipedia:General_disclaimer', \
            '/wiki/Wikipedia:Stub', '/wiki/Wikipedia:Subpages', '/wiki/Wikipedia', \
            '/wiki/Wikipedia_talk:Do_not_use_subpages', '/wiki/Terms_of_Use']

# Add/Remove any word or character you wish to skip
banned = [':', ';', '\\', '/', '[', '{', ']', '}', '&', '&', '*', '(', ')', '.', ',', '\'', '\'', '"', '#', '=', '”', '’',\
          'Deltagarportalen', 'Wikipedia', 'Wikimedia', 'diskussionssidan', 'Utskriftsvänlig', 'engelskspråkiga', \
          'användarvillkor', 'Grundprinciperna', 'ქართული', 'ÙØ§Ø±Ø³ÛŒ', '日本語', 'oʻzbekcha', 'العربية', '⇒', '·', \
          'ifwindowmw', '한국어', 'മലയാളം', 'việt', 'тыла', 'Перем', 'kreyòl', 'ไทย', '粵語', 'پنجابی', 'Български', 'کوردی', \
          'தமிழ்', 'བོད་ཡིག', 'Հայերեն', 'Авар', 'ᨅᨔ', 'తెలుగు', 'avañeẽ', 'తెలుగు', 'Српски', 'српскохрватски', 'မြန်မာဘာသာ', \
          'ಕನ್ನಡ', 'Коми', 'Эрзянь', 'Чӑвашла', 'Беларуская', 'ଓଡ଼ିଆ', '⇐', 'ଓଡ଼ିଆ', 'documentwriteu003cdiv', 'Русский',\
          'Македонски', 'Лакку', 'ܐܪܡܝܐ', 'فارسی', 'ትግርኛ', '客家語hak-kâ-ngî', 'ייִדיש', 'اردو', 'Ελληνικά', 'მარგალური', \
          'ᨕᨘᨁᨗ', '贛語', 'Аҧсшәа', 'עברית', 'Українська', 'việt', '中文', 'ગુજરાતી', 'тарашкевіца‎', '文言', 'Ирон', 'नेपाल']

firstlayerqueue = Queue.Queue()
secondlayerqueue = Queue.Queue()

class Crawl(threading.Thread):
    def __init__(self, firstlayerqueue, secondlayerqueue):
        threading.Thread.__init__(self)
        self.firstlayerqueue = firstlayerqueue
        self.secondlayerqueue = secondlayerqueue

    def run(self):
        self.url = self.firstlayerqueue.get()
        #print 'IN THREAD: ' + self.url # uncomment to watch a lot of spam
        try:
            self.req = urllib2.Request(self.url, headers={'User-Agent' : "Mozilla/4.0(compatible; MSIE 7.0b; Windows NT 6.0)"}) # :)
            self.con = urllib2.urlopen( self.req )
            self.data = self.con.read()
        except:
            self.firstlayerqueue.task_done()
            return 1
        self.urls = self.getUrls(self.data)
        self.data = self.getWords(self.data)
        self.writeWords(self.data)
        for url in self.urls:
            self.secondlayerqueue.put(url)
        self.firstlayerqueue.task_done()

    def writeWords(self, data):
        global outputfile, words
        self.data = data
        for line in self.data:
            try:
                line_encoded = line.encode('ISO-8859-1')
                #line_encoded = line.encode('UTF-8') # might want to uncomment utf-8 and comment out ISO if you run into encoding problems
            except:
                continue
            f = open(outputfile, 'a')
            f.write(line_encoded.lower() + '\n')
            f.close()
            words += 1


    def getWords(self, test):
        global banned
        self.rv = []
        self.test = test
        self.skip = True
        for lines in StringIO.StringIO(self.test):
            lines = lines.strip('\n').strip('\n\r').strip('\t')
            self.testa = re.sub('<.*?>', ' ', lines).split(' ')
            for word in self.testa:
                if word.find('<div id="content" class="mw-body" role="main">') :
                    skip = False
                if skip == True and word.find('<span class="mw-headline" id="References">'):
                    skip = True
                # 'wtf does this even do?' can't remember... probably nothing
                    pass
                if len(word) >= 6 and len(word) <= 30 and skip == False:
                    for ban in banned:
                        try:
                            while 1:
                                word = word.replace(ban, '')
                                if word.find(ban) == -1:
                                    break
                        except:
                            pass
                    if word == '' or word == ' ' or len(word) < 6:
                        continue
                    else:
                        self.rv.append(word.lower())
                else:
                    pass
        return list(set(self.rv))

    def getUrls(self, data):
        global bad_urls
        self.test = data
        self.rv = []
        for lineA in StringIO.StringIO(self.test):
            match = re.findall(r'<a href=".*?">.+</a>', lineA)
            if match:
                match2 = re.findall(r'<a href="/w/.*?">.+</a>', lineA)
                if match2 != True:
                    for i in match:
                        try:
                            reg = re.compile('/wiki/.*?"')
                            self.urlvalue = reg.search(i).group(0)
                            self.urlvalue.replace('"', '')
                            self.urlvalue = str(URLVALUE) + str(self.urlvalue).strip('"')
                            if self.urlvalue.endswith('.jpg') or self.urlvalue.endswith('.svg') or self.urlvalue.endswith('.png') or self.urlvalue.endswith('.gif') :
                                pass
                            elif '/wiki/Wikipedia:' in self.urlvalue or '/wiki/Portal:' in self.urlvalue or '/wiki/Special:' in self.urlvalue or '%' in self.urlvalue or '/wiki/Template' in self.urlvalue:
                                pass
                            else:
                                self.rv.append(self.urlvalue)
                        except Exception, e:
                            pass
            else:
                pass
        return list(set(self.rv))

filename = os.path.split(inspect.getfile(inspect.currentframe()))
parser = optparse.OptionParser('Usage: [+] Usage: ' + filename[1] + ' <args>' + '\n[+] Wikipedia Wordlist Generator\nURL must be formated as following (most subdomains should work): '
                                                                                'http://en.wikipedia.org/wiki/wikipage\n\nExample: python %s -u http://en.wikipedia.org/wiki/Europe -o wordlist.txt -t 5'
                                                                                '\n\nIt will generate close to no visible output.\nctrl+c to break\n\nI suggest doing something like this to clean the wordlist:'
                                                                                ' cat wordlist.txt | sort | uniq > n_wordlist.txt' % filename[1])
parser.add_option('-u', dest='starturl', type='string', help='Wikipedia URL to use as start for the crawler')
parser.add_option('-t', dest='nrthreads', type='int', help='Amount of threads')
parser.add_option('-o', dest='outputfile', type='string', help='File to write output to')

(options, args) = parser.parse_args()
nrthreads = options.nrthreads
starturl = options.starturl
outputfile = options.outputfile

if starturl == None or outputfile == None or nrthreads == None:
    print parser.print_help()
    quit(0)

words = 0
URLVALUE = starturl.split('/wiki')[0]
bad_urls = [bad_url.replace(bad_url, str(URLVALUE) + str(bad_url)) for bad_url in bad_urls]

firstlayerqueue.put(starturl)
while 1: # generate first crawl content
    thread = Crawl(firstlayerqueue, secondlayerqueue)
    thread.daemon = True
    thread.start()
    if thread.isAlive():
        break

int_count = 0
while 1:
    if firstlayerqueue.empty():
        while 1:
            firstlayerqueue.put(secondlayerqueue.get())
            if secondlayerqueue.empty():
                print '\nWrote %i words to %s. Queue empty, filling...' % (words, outputfile)
                break

    if not firstlayerqueue.empty():
        alivethread = 0
        for i in range(nrthreads):
            if not firstlayerqueue.empty():
                alivethread += 1
                thread = Crawl(firstlayerqueue, secondlayerqueue)
                thread.daemon = True
                thread.start()
        for i in range(alivethread):
            thread.join(5)
        int_count += 1
        if int_count == 3:
            print 'Joined %i threads. Queue size: %i' % (alivethread, firstlayerqueue.qsize())
            int_count = 0
        continue