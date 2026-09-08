#!/usr/bin/env python3

import sys
import re
import json
import jinja2

from writer import get_sourcefile_map

def loadjsonp(filename):
    with open(filename) as infl:
        dat = infl.read()
    dat = dat.strip()
    if dat.endswith(';'):
        dat = dat[ : -1 ]
    pos = dat.find('=')
    dat = dat[ pos+1 : ]
    return json.loads(dat)

class Gen:
    def __init__(self):
        self.jenv = jinja2.Environment(loader=jinja2.FileSystemLoader('visiterp/staticlib'), autoescape=jinja2.select_autoescape())

    def build(self):
        sourcefile_map = get_sourcefile_map()
        
        self.sourcefiles = [ SourceFile(key, filename) for (filename, key) in sourcefile_map.items() ]
        self.sourcefiles.sort(key=lambda obj: obj.key)
        self.sourcefile_map = { obj.key: obj for obj in self.sourcefiles }

        self.routines = [ Routine(map) for map in routines ]

    def write(self):
        template = self.jenv.get_template('home.html')
        with open('static/index.html', 'w') as outfl:
            outfl.write(template.render(files=self.sourcefiles))

        ls = list(self.routines)
        ls.sort(key=lambda rtn: rtn.name)
        template = self.jenv.get_template('routines.html')
        with open('static/routines.html', 'w') as outfl:
            outfl.write(template.render(routines=ls))
            
class SourceFile:
    def __init__(self, key, filename):
        assert filename.endswith('.zil')
        self.key = key
        self.filename = filename
        self.filebase = filename[ : -4 ]

    def __repr__(self):
        return '<SourceFile (%s) "%s">' % (self.key, self.filename,)

class Routine:
    def __init__(self, map):
        self.name = map['name']
        self.addr = map['addr']
        self.sourceloc = map['sourceloc']

        self.hexaddr = '$%04X' % (self.addr,)

routines = loadjsonp('src/game/routines.js')

gen = Gen()
gen.build()
gen.write()


