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

    def genloc(self, locstr):
        key = locstr[0]
        file = self.sourcefile_map[key]
        return SourceLoc(locstr, key, file)

    def build(self):
        sourcefile_map = get_sourcefile_map()
        
        self.sourcefiles = [ SourceFile(key, filename) for (filename, key) in sourcefile_map.items() ]
        self.sourcefiles.sort(key=lambda obj: obj.key)
        self.sourcefile_map = { obj.key: obj for obj in self.sourcefiles }

        self.routines = [ Routine(map, gen=self) for map in json_routines ]
        self.globals = [ Global(map, gen=self) for map in json_globals ]

        for file in self.sourcefiles:
            file.buildsource(json_source[file.filename])

    def write(self):
        template = self.jenv.get_template('home.html')
        with open('static/index.html', 'w') as outfl:
            outfl.write(template.render(files=self.sourcefiles))

        ls = list(self.routines)
        ls.sort(key=lambda rtn: rtn.name)
        template = self.jenv.get_template('routines.html')
        with open('static/routines.html', 'w') as outfl:
            outfl.write(template.render(routines=ls))

        ls = list(self.globals)
        ls.sort(key=lambda glob: glob.name)
        template = self.jenv.get_template('globals.html')
        with open('static/globals.html', 'w') as outfl:
            outfl.write(template.render(globals=ls))

        template = self.jenv.get_template('source.html')
        for file in self.sourcefiles:
            with open('static/zil-%s.html' % (file.basename,), 'w') as outfl:
                outfl.write(template.render(lines=file.lines))
            
class SourceFile:
    def __init__(self, key, filename):
        assert filename.endswith('.zil')
        self.key = key
        self.filename = filename
        self.basename = filename[ : -4 ]
        self.lines = []
        
    def __repr__(self):
        return '<SourceFile (%s) "%s">' % (self.key, self.filename,)

    def buildsource(self, lines):
        for lineobj in lines:
            els = []
            for obj in lineobj:
                if type(obj) is int:
                    el = LineEl(' ' * obj)
                elif type(obj) is str:
                    el = LineEl(obj)
                else:
                    (objstyle, obj) = obj
                    el = LineEl(obj, objstyle)
                els.append(el)
            if not els:
                els.append(LineEl(' '))
            self.lines.append(SourceLine(els))

class SourceLine:
    def __init__(self, els):
        self.els = els
    
class LineEl:
    def __init__(self, text, style=None):
        self.text = text
        self.style = style

class SourceLoc:
    def __init__(self, locstr, key, file):
        self.locstr = locstr
        self.key = key
        self.file = file
    
class Routine:
    def __init__(self, map, gen):
        self.name = map['name']
        self.addr = map['addr']
        self.sourceloc = map['sourceloc']

        self.hexaddr = '$%04X' % (self.addr,)
        self.loc = gen.genloc(self.sourceloc)

class Global:
    def __init__(self, map, gen):
        self.name = map['name']
        self.num = map['num']
        self.sourceloc = map['sourceloc']

        self.loc = None
        if self.sourceloc:
            self.loc = gen.genloc(self.sourceloc)

json_routines = loadjsonp('src/game/routines.js')
json_source = loadjsonp('src/game/source.js')
json_globals = loadjsonp('src/game/globals.js')

gen = Gen()
gen.build()
gen.write()


