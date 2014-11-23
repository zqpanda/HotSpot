#!/bin/env python
# -*- coding:utf-8 -*-
import sys,time,os,ConfigParser,re,chardet
import urllib,urllib2,simplejson,getopt
sys.path.extend(['../conf/', '../lib/'])
import conf
def para_read(para_path):
    cf = ConfigParser.ConfigParser()
    cf.read(para_path)
    return cf

def urlparse(url):
    from urlparse import urlparse
    url = urlparse(url)
    return {'hostname':url.hostname,'port':url.port,'path':url.path}

def filter(raw_data):
    fread = open('../conf/filter_list')
    filter_list = list()
    for line in fread.readlines():
        filter_list.append(line.strip())
    result = list()
    for word in raw_data:
        if word in filter_list:
            continue
        result.append(word)
    return result

def has_chinese_character(content):
    encoding = chardet.detect(content)['encoding']
    iconvcontent = content.decode(encoding)
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    match = zhPattern.search(iconvcontent)
    if match:
        return True
    else:
        return False 
    
def game_site(cou):
    filename = 'jogos_web_' + cou
    web_host_list = list()
    try:
        with open('../conf/' + filename) as fread:
            for link in fread.readlines():
                link = link.strip()
                if link.startswith('http'):
                    web_host_list.append(urlparse(link)['hostname'])
        return web_host_list
    except IOError,e:
        print e
        return web_host_list



def google_query(search,country='br',page=0):
    url= ('https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s&rsz=8&start=%s') % (urllib.quote(search),page)
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent' : user_agent}
    values = { 'name' : 'Zhou Qiang',
               'location' : 'Northampton',
               'language' : 'Python' }
    data = urllib.urlencode(values)
    try:
        request = urllib2.Request(url,None,headers)
        response = urllib2.urlopen(request,timeout=30)
        results = simplejson.load(response)
        info = list()
        if results['responseStatus'] == 200:
            info = results['responseData']['results']
        else:
            time.sleep(1)
            response = urllib2.urlopen(request,timeout=30)
            results = simplejson.load(response)
            if results['responseStatus'] == 200:
                info = results['responseData']['results'] 
    except Exception,e:
        print e
        return None
    game_related = 0
    for minfo in info:
        for key in minfo.keys():
            if key == 'url':
                url_info = urlparse(minfo[key])
                if url_info['hostname'] in game_site(country):
                    game_related = 1
    if game_related:
        return True
    else:
        return None

def game_query_extract(query_list,country='br'):
    game_words = list()
    for query in query_list:
        encoding = chardet.detect(query)['encoding']
        iconvcontent = query.decode(encoding)
        zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
        match = zhPattern.search(iconvcontent)
        if not match and google_query(query,country):
            game_words.append(query) 
            time.sleep(1)
    return game_words

def usage():
    print 'Usage of HotSpot:'

def main():
    opts,args = getopt.getopt(sys.argv[1:], "hc:m:", ["help", "country=", "month"]) 
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        if opt in ('-c', '--country'):
            if val not in conf.COUNTRY_LIST:
                print 'Illegal country name!!!'
                sys.exit(1)
            country = val
        if opt in ('-m', '--month'):
            if val not in conf.MONTH_LIST:
                print 'Illegal month!!!'
                sys.exit(1)
            month = val
    query_file = '../data/' + country + '_top2000_' + month
    output_file = '../data/' + country + '_game_words_' + month
    try:
        raw_data = list()
        with open(query_file) as fread:
            for line in fread.readlines():
                line = line.strip() 
                query_list = line.split('\t')
                raw_data.append(query_list[0])
            filtered_words = filter(raw_data)
            game_words = game_query_extract(filtered_words,country)
            with open(output_file, 'w') as fout:
                for query in game_words:
                    fout.write(query + '\n')
    except IOError,e:
        print e
if __name__ == '__main__':
    main()
