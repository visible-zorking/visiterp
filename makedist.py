#!/usr/bin/env python3

import os, os.path
import shutil
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--dist', default='dist')
parser.add_argument('--game')
parser.add_argument('--common', action='store_true')

args = parser.parse_args()

distdir = args.dist
game = args.game
if not game:
    game = os.path.basename(os.getcwd())

gamedir = os.path.join(distdir, game)
    
print(f'writing to {gamedir}')

if not os.path.exists(distdir):
    os.mkdir(distdir)
if not os.path.exists(gamedir):
    os.mkdir(gamedir)

with open('index.html') as fl:
    indexdat = fl.read()

indexdat = indexdat.replace('"visiterp/css/', '"../css/')
indexdat = indexdat.replace('"visiterp/pic/', '"../pic/')
indexdat = indexdat.replace('// assetdir: \'visiterp\'', 'assetdir: \'..\'')
indexdat = indexdat.replace(
    '<span id="distlink">The Visible Zorker</span>',
    '<a id="distlink" href="..">The Visible Zorker</a>'
)

path = os.path.join(gamedir, 'index.html')
print('writing', path)
with open(path, 'w') as fl:
    fl.write(indexdat)

def copydirfiles(srcdir, destdir):
    print('copying to', destdir)
    if not os.path.exists(destdir):
        os.mkdir(destdir)
    for ent in os.scandir(srcdir):
        if ent.is_file() and not ent.path.endswith('~'):
            shutil.copy(ent.path, destdir)

copydirfiles('./js', os.path.join(gamedir, 'js'))
copydirfiles('./pic', os.path.join(gamedir, 'pic'))
if os.path.exists('./css'):
    copydirfiles('./css', os.path.join(gamedir, 'css'))

if os.path.exists('./pic/map.svg'):
    with open('./pic/map.svg') as fl:
        mapdat = fl.read()
        mapdat = mapdat.replace('../visiterp/font/', '../../font/')
        path = os.path.join(gamedir, 'pic/map.svg')
        print('writing', path)
        with open(path, 'w') as fl:
            fl.write(mapdat)
        

if args.common:
    copydirfiles('./visiterp/css', os.path.join(distdir, 'css'))
    copydirfiles('./visiterp/pic', os.path.join(distdir, 'pic'))
    copydirfiles('./visiterp/font', os.path.join(distdir, 'font'))

