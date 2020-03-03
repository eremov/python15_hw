#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pickle
import yaml
from datetime import datetime


def get_tags_dictionary(htmlText):
    from html.parser import HTMLParser
    tagDictionary = {}

    class HTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag in tagDictionary:
                currentCount = tagDictionary.get(tag)
                tagDictionary.update({tag: currentCount + 1})
            else:
                tagDictionary[tag] = 1

    parser = HTMLParser()
    parser.feed(htmlText)
    return tagDictionary


def get_str_from_url(url):
    import urllib.request
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    return mystr


def log_to_file(url):
    now = datetime.now()
    f = open("log.txt", "a")
    f.write('{0} - {1} - {2}\n'.format(now.date(), now.time(), url))
    f.close()


def get_synonyms():
    with open(r'synonyms.yml') as file:
        documents = yaml.full_load(file)
    return documents


def put_sysnonyms(dict):
    with open('synonyms.yml', 'w') as yaml_file:
        yaml.dump(dict, yaml_file)


def get_connection():
    conn = sqlite3.connect("tagcounter.db")
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS tagcounter
                      (sitename text, url text, date text,
                       dict blob)
                   """)
    return conn


def add_site_Info_to_db(siteName, url, date, dict, conn):
    cursor = conn.cursor()
    dict_blob = pickle.dumps(dict, pickle.HIGHEST_PROTOCOL)
    insert_query = """ INSERT INTO tagcounter VALUES(?, ?, ?, ?)"""
    data_tuple = (siteName, url, date, sqlite3.Binary(dict_blob))
    cursor.execute(insert_query, data_tuple)
    conn.commit()


def select_by_url(domain, conn):
    cur = conn.cursor()
    cur.execute("SELECT dict FROM tagcounter WHERE url like '{}' ORDER BY date DESC LIMIT 1".format(domain))
    row = cur.fetchone()
    if row is None:
        return {}
    else:
        return pickle.loads(row[0])


if __name__ == '__main__':
    import sys

    argvLength = sys.argv.__len__();
    if argvLength > 2:
        if sys.argv[1] == "--get":
            url = sys.argv[2]
            synonyms = get_synonyms()
            if url in synonyms:
                url = synonyms.get(url)
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url
            conn = get_connection()
            htmlStr = get_str_from_url(url)
            myDict = get_tags_dictionary(htmlStr)
            now = datetime.now()
            siteName = url.split("//")[-1].split("/")[0]
            add_site_Info_to_db(siteName, url, now, myDict, conn)
            log_to_file(url)
            print(myDict)
        if sys.argv[1] == "--view":
            myDict = select_by_url(sys.argv[2], get_connection())
            print(myDict)
        if sys.argv[1] == "--add":
            urlPair = sys.argv[2].split(":", 1)
            syn = get_synonyms()
            syn.update({urlPair[0]: urlPair[1]})
            put_sysnonyms(syn)

    elif argvLength == 1:
        from tkinter import *


        def load():
            url = message.get()
            synonyms = get_synonyms()
            if not synonyms is None:
                if url in synonyms:
                    url = synonyms.get(url)
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url
            conn = get_connection()
            htmlStr = get_str_from_url(url)
            myDict = get_tags_dictionary(htmlStr)
            from datetime import datetime
            now = datetime.now()
            siteName = url.split("//")[-1].split("/")[0]
            add_site_Info_to_db(siteName, url, now, myDict, conn)
            log_to_file(url)
            text.delete(1.0, END)
            for key, value in myDict.items():
                text.insert(1.0, "{} - {}\n".format(key, value))


        def getFromDB():
            url = message.get()
            myDict = select_by_url(url, get_connection())
            if bool(myDict):
                text.delete(1.0, END)
                for key, value in myDict.items():
                    text.insert(1.0, "{} - {}\n".format(key, value))
            else:
                text.delete(1.0, END)
                text.insert(1.0, "В базе нет такого адреса")


        root = Tk()

        root.title("tagcounter")
        root.geometry("300x250")

        top_frame = Frame(root)
        middle_frame = Frame(root)
        bottom_frame = Frame(root)

        message = StringVar()

        url_label = Label(top_frame, text="Адрес: ")
        message_entry = Entry(top_frame, width=100, textvariable=message)
        button1 = Button(middle_frame, text="Загрузить", command=load)
        button2 = Button(middle_frame, text="Показать из базы", command=getFromDB)
        text = Text(bottom_frame, height=15, wrap=WORD)

        top_frame.pack()
        middle_frame.pack()
        bottom_frame.pack()

        url_label.pack(side=LEFT)
        message_entry.pack(side=TOP)
        button1.pack(side=LEFT)
        button2.pack(side=RIGHT)
        text.pack()

        root.mainloop()
