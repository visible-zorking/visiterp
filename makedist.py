#!/usr/bin/env python3

import os, os.path
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--dist', default='dist')
parser.add_argument('--game')

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
    
with open(os.path.join(gamedir, 'index.html'), 'w') as fl:
    fl.write(indexdat)


