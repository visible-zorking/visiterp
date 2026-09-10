#!/usr/bin/env python3

import sys
import re
import html
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

def loadjsonsp(filename):
    res = []
    with open(filename) as infl:
        dat = infl.read()
    ls = dat.split('\n')
    for dat in ls:
        dat = dat.strip()
        if not dat:
            continue
        if dat.endswith(';'):
            dat = dat[ : -1 ]
        pos = dat.find('=')
        dat = dat[ pos+1 : ]
        res.append(json.loads(dat))
    return res

class Gen:
    def __init__(self):
        self.jenv = jinja2.Environment(loader=jinja2.FileSystemLoader('visiterp/staticlib'), autoescape=jinja2.select_autoescape())
        self.symtable = {}

    def addsymbol(self, name, obj):
        if name in self.symtable:
            print('Warning: duplicate symbol: %s' % (name,))
            return
        self.symtable[name] = obj

    def locforsymbol(self, name):
        obj = self.symtable.get(name)
        if not obj:
            return None
        return obj.loc

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
        self.objects = [ Object(map, gen=self) for map in json_objects ]
        self.globals = [ Global(map, gen=self) for map in json_globals ]
        self.constants = [ Constant(map, gen=self) for map in json_constants ]

        self.commentary = { key: Comment(key, vals, gen=self) for (key, vals) in json_commentary.items() }

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

        ls = list(self.objects)
        ls.sort(key=lambda obj: obj.name)
        template = self.jenv.get_template('objects.html')
        with open('static/objects.html', 'w') as outfl:
            outfl.write(template.render(objects=ls))
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
        comls = list(json_commentarymap[self.key] or [])
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
            comment = None
            if comls and comls[0] == index:
                comls.pop(0)
                comkey = comls.pop(0)
                comment = gen.commentary.get(comkey)
            sourceln = SourceLine(index, els, comment)
            self.lines.append(sourceln)
            index += 1

class SourceLine:
    def __init__(self, num, els, comment):
        self.num = num
        self.els = els
        self.comment = comment
    
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

class Comment:
    def __init__(self, key, ls, gen):
        self.key = key
        self.ls = ls
        self.rawhtml = self.text(gen)

    def text(self, gen):
        res = []
        for val in self.ls:
            if type(val) is str:
                text = html.escape(val, False)
                res.append(text)
                continue
            key = val[0]
            if key == 'br':
                res.append('</p><p>')
                continue
            if key == 'code':
                text = html.escape(val[1], False)
                res.append('<code>%s</code>' % (text,))
                continue
            if key == 'emph':
                text = html.escape(val[1], False)
                res.append('<em>%s</em>' % (text,))
                continue
            if key == 'bold':
                text = html.escape(val[1], False)
                res.append('<b>%s</b>' % (text,))
                continue
            if key == 'credit':
                text = html.escape(val[1], False)
                res.append('</p><p class="Contrib">(contrib: %s)</p><p>' % (text,))
                continue
            if key == 'extlink':
                href = html.escape(val[1], True)
                ### game-relative
                text = html.escape(val[2], False)
                cla = 'External'
                res.append('<a class="%s" target="_blank" href="%s">%s</a>' % (cla, href, text,))
                continue
            if key in ('src', 'com', 'comsrc'):
                [ _, id, idtyp, label ] = val
                if not label:
                    label = id
                loc = gen.locforsymbol(id)
                text = html.escape(label, False)
                if not loc:
                    res.append(text)
                    continue
                isid = (label == label.upper())
                cla = 'Internal'
                if isid:
                    cla += ' Com_Id'
                href = 'zil-%s.html#line_%s' % (loc.file.basename, loc.startline,)
                res.append('<a class="%s" href="%s">%s</a>' % (cla, href, text,))
                continue
            raise Exception('unhandled comment span %s' % (val,))
                
        return ''.join(res)

class Routine:
    def __init__(self, map, gen):
        self.name = map['name']
        self.addr = map['addr']
        self.sourceloc = map['sourceloc']

        self.hexaddr = '$%04X' % (self.addr,)
        self.loc = gen.genloc(self.sourceloc)

        gen.addsymbol(self.name, self)

class Object:
    def __init__(self, map, gen):
        self.name = map['name']
        self.num = map['onum']
        self.sourceloc = map['sourceloc']

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
json_commentary, json_commentarymap = loadjsonsp('src/game/commentary.js')
gen = Gen()
gen.build()
gen.write()


