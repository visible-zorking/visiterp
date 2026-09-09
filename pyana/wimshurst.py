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
        self.symtable = {}

    def addsymbol(self, name, obj):
        if name in self.symtable:
            print('Warning: duplicate symbol: %s' % (name,))
            return
        self.symtable[name] = obj

    def genloc(self, locstr):
        if not locstr:
            return None
        ls = locstr.split(':')
        assert len(ls) in (3, 5)
        key = ls[0]
        file = self.sourcefile_map[key]
        startline = int(ls[1])
        endline = startline
        if len(ls) == 5:
            if ls[3]:
                endline = int(ls[3])
            if ls[4] == '0' and endline > startline:
                endline -= 1
        return SourceLoc(locstr, key, file, startline, endline)

    def build(self):
        sourcefile_map = get_sourcefile_map()
        
        self.sourcefiles = [ SourceFile(key, filename) for (filename, key) in sourcefile_map.items() ]
        self.sourcefiles.sort(key=lambda obj: obj.key)
        self.sourcefile_map = { obj.key: obj for obj in self.sourcefiles }

        self.routines = [ Routine(map, gen=self) for map in json_routines ]
        self.globals = [ Global(map, gen=self) for map in json_globals ]
        self.constants = [ Constant(map, gen=self) for map in json_constants ]

        for file in self.sourcefiles:
            file.buildsource(json_source[file.filename], gen=self)

    def write(self):
        template = self.jenv.get_template('home.html')
        with open('static/index.html', 'w') as outfl:
            outfl.write(template.render(files=self.sourcefiles))
            outfl.write('\n')

        ls = list(self.routines)
        ls.sort(key=lambda rtn: rtn.name)
        template = self.jenv.get_template('routines.html')
        with open('static/routines.html', 'w') as outfl:
            outfl.write(template.render(routines=ls))
            outfl.write('\n')

        ls = list(self.globals)
        ls.sort(key=lambda glob: glob.name)
        template = self.jenv.get_template('globals.html')
        with open('static/globals.html', 'w') as outfl:
            outfl.write(template.render(globals=ls))
            outfl.write('\n')

        template = self.jenv.get_template('source.html')
        for file in self.sourcefiles:
            with open('static/zil-%s.html' % (file.basename,), 'w') as outfl:
                outfl.write(template.render(homekey=file.key, lines=file.lines))
                outfl.write('\n')
            
class SourceFile:
    def __init__(self, key, filename):
        assert filename.endswith('.zil')
        self.key = key
        self.filename = filename
        self.basename = filename[ : -4 ]
        self.lines = []
        
    def __repr__(self):
        return '<SourceFile (%s) "%s">' % (self.key, self.filename,)

    def buildsource(self, lines, gen):
        index = 1
        for lineobj in lines:
            els = []
            for obj in lineobj:
                if type(obj) is int:
                    el = LineEl(' ' * obj)
                elif type(obj) is str:
                    el = LineEl(obj)
                else:
                    (objstyle, obj) = obj
                    loc = None
                    if objstyle == 'Id':
                        loc = gen.symtable.get(obj)
                    el = LineEl(obj, objstyle, loc)
                els.append(el)
            if not els:
                els.append(LineEl(' '))
            self.lines.append(SourceLine(index, els))
            index += 1

class SourceLine:
    def __init__(self, num, els):
        self.num = num
        self.els = els
    
class LineEl:
    def __init__(self, text, style=None, linkref=None):
        self.text = text
        self.style = style
        self.linkref = linkref
        self.linkloc = linkref.loc if linkref else None

class SourceLoc:
    def __init__(self, locstr, key, file, startline, endline):
        self.locstr = locstr
        self.key = key
        self.file = file
        self.startline = startline
        self.endline = endline
        
        if self.endline == self.startline:
            self.str = '%s:%d' % (self.file.basename, self.startline,)
        else:
            self.str = '%s:%d-%d' % (self.file.basename, self.startline, self.endline,)
        
    
class Routine:
    def __init__(self, map, gen):
        self.name = map['name']
        self.addr = map['addr']
        self.sourceloc = map['sourceloc']

        self.hexaddr = '$%04X' % (self.addr,)
        self.loc = gen.genloc(self.sourceloc)

        gen.addsymbol(self.name, self)

class Global:
    def __init__(self, map, gen):
        self.name = map['name']
        self.num = map['num']
        self.sourceloc = map['sourceloc']

        self.loc = gen.genloc(self.sourceloc)

        gen.addsymbol(self.name, self)

class Constant:
    def __init__(self, map, gen):
        self.name = map['name']
        self.sourceloc = map['sourceloc']

        self.loc = gen.genloc(self.sourceloc)

        gen.addsymbol(self.name, self)

json_routines = loadjsonp('src/game/routines.js')
json_source = loadjsonp('src/game/source.js')
json_globals = loadjsonp('src/game/globals.js')
json_constants = loadjsonp('src/game/constants.js')
json_objects = loadjsonp('src/game/objects.js')

gen = Gen()
gen.build()
gen.write()


