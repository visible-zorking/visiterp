#!/usr/bin/env python3

import sys
import re
import json
import jinja2

from writer import get_sourcefile_map

sourcefile_map = None

def loadjsonp(filename):
    with open(filename) as infl:
        dat = infl.read()
    dat = dat.strip()
    if dat.endswith(';'):
        dat = dat[ : -1 ]
    pos = dat.find('=')
    dat = dat[ pos+1 : ]
    return json.loads(dat)

def build():
    global sourcefile_map
    sourcefile_map = get_sourcefile_map()

    jenv = jinja2.Environment(loader=jinja2.FileSystemLoader('visiterp/staticlib'), autoescape=jinja2.select_autoescape())

    template = jenv.get_template('home.html')

    with open('static/index.html', 'w') as outfl:
        outfl.write(template.render())
    

routines = loadjsonp('src/game/routines.js')

build()

