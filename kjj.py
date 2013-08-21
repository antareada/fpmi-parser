#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'nchugueva'

import codecs
import HTMLParser
import os
import re

import requests


class Parser (HTMLParser.HTMLParser):
    stock = []

    state = None
    biography = []
    publication = []
    stateDegree = False  # найдена или нет степень препода

    def handle_starttag(self, tag, attrs):
        #print "Encountered a start tag:", tag
        self.currentTag = tag

        if self.currentTag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.stock.append(tag)

    def handle_endtag(self, tag):
        #print "Encountered an end tag :", tag
        if self.stock and self.currentTag == self.stock[-1]:
            self.stock.pop(-1)

    def handle_startendtag(self, tag, attrs):
        #print "Encountered an startend tag :", tag
        pass

    def handle_data(self, data):
        data = data.strip()  # убирает начальные и хвостовые пробелы
        if data and self.stock:
            #Запись в файл
            #self.myFile.write(data.encode('utf-8') + '\r\n')

            #self.myFile.write((u' '.join(words) + u'\r\n').encode('utf-8'))
            fullName = self.name(data)

            #ФИО
            if fullName:
                print u' '.join(fullName)
            if not self.stateDegree:
                self.academicDegree(data)

    def __init__(self, myFile):
        HTMLParser.HTMLParser.__init__(self)
        self.myFile = myFile

        with open("dictionaryDegree.txt", "rb") as dictionaryDegree:
            self.degree = set(self.word(
                dictionaryDegree.read().lstrip(codecs.BOM_UTF8).decode("utf-8"))
            )  # разделили на слова и добавили в словарь

    #В эту переменную я передаю текущий тег
    currentTag = None

    #Метод делит текст в текущем теге на слова
    def word(self, data):
        words = [word for word in re.split(r" |\-|\)|\(|:|!|\.|;|,|/|\n|\r", data) if word.strip()]
        return words

    def name(self, data):
        fullName = []
        words = self.word(data)
        if len(words) == 3:
            for currentWord in words:
                if currentWord.lower() == u'биография':
                    self.state = 'biography'
                elif u'публик' in currentWord.lower():
                    self.state = 'publication'
                elif currentWord.lower() in [u'сайты', u'структура']:
                    self.state = None
                elif self.state == 'biography':
                    self.biography.append(currentWord)
                elif self.state == 'publication':
                    self.publication.append(currentWord)

                if len(fullName) != 3:
                    if ord(u'А') <= ord(currentWord[0]) <= ord(u'Я') and len(currentWord) > 1:
                        fullName.append(currentWord)
                    else:
                        fullName = []

        return fullName if len(fullName) == 3 else None

    def academicDegree(self, data):  # поиск ученой степени, опираясь на словарик
        words = set(map(unicode.lower, self.word(data)))  # map применяет ловер к каждому эл-ту циклом
        result = self.degree & words
        #print u', '.join(words)  # отладка
        if result:
            #print u", ".join(result) #отладка
            print data
            self.stateDegree = True


def main(link):
    r = requests.get(link)
    r.raise_for_status()

    with codecs.open("parser.txt", 'wb', encoding='utf-8') as myFile:  # конструкция гарантирует закрытие
        parser = Parser(myFile)
        parser.feed(r.text.replace(u"&nbsp;", u" "))

        print >> myFile, u'Биография', os.linesep
        print >> myFile, u' '.join(parser.biography), os.linesep
        print >> myFile, u'Публикации', os.linesep
        print >> myFile, u' '.join(parser.publication), os.linesep


with open("links.txt", "rt") as links:
    map(main, links)

