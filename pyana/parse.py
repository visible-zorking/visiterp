#!/usr/bin/env python3

# python3 pyana/parse.py -z gamesrc/zork1.zil --obj --txd --gamedat
# python3 pyana/parse.py -z gamesrc/zork1.zil --src

import sys
import optparse

from zillex import Lexer, dumptokens
from zilana import Zcode
from zilana import stripcomments
from zilana import findsetg
from zilana import stripifdefs
from txdparse import TXDData, ObjDumpData, DictDumpData, GrammarDumpData
from writer import write_filenames, write_properties, write_attributes, write_actions, write_constants, write_globals, write_objects, write_routines, write_strings, write_dictwords, write_grammar, display_globals, compute_room_distances
from gensource import write_source, write_source_colored

popt = optparse.OptionParser()

popt.add_option('-z', '--zil',
                action='store', dest='zilfile',
                help='.zil file to parse (should be the main source file)')
popt.add_option('--zcode',
                action='store', dest='gamefile',
                help='z-code file to parse')
popt.add_option('--nostrip',
                action='store_true', dest='nostrip',
                help='leave comments and ifdefed code in zil code')
popt.add_option('--dump',
                action='store_true', dest='dump',
                help='dump zil parse to stdout')
popt.add_option('--game',
                action='store', dest='gameid', default='generic',
                help='identifier of the game being parsed (indicates special cases)')
popt.add_option('--gamedat',
                action='store_true', dest='gamedat',
                help='write all possible gamedat JSON files')
popt.add_option('-t', '--txd',
                action='store_true', dest='txdfile',
                help='read game-dump.txt (needed to write routines.js and strings.js)')
popt.add_option('-o', '--obj',
                action='store_true', dest='objdump',
                help='read obj-dump.txt (needed to write objects.js and strings.js)')
popt.add_option('-d', '--dict',
                action='store_true', dest='dictdump',
                help='read dict-dump.txt (needed to write dictwords.js and grammar.js)')
popt.add_option('-g', '--grammar',
                action='store_true', dest='grammardump',
                help='read grammar-dump.txt (needed to write actions.js and grammar.js)')
popt.add_option('--showglob',
                action='store_true', dest='showglob',
                help='list globals in (mostly) compiled order')
popt.add_option('--src',
                action='store_true', dest='sourcelist',
                help='write source.js with syntax coloring')

(opts, args) = popt.parse_args()

if opts.zilfile:
    print('reading %s...' % (opts.zilfile,))
    lex = Lexer(opts.zilfile, monkeypatch=opts.gameid)
    ls = lex.readfile(includes=True)
    if not opts.nostrip:
        stripcomments(ls)
    compileconstants = findsetg(ls)
    if not opts.nostrip:
        stripifdefs(ls, compileconstants, gameid=opts.gameid)
    if opts.dump:
        dumptokens(ls, withpos=False)
    zcode = Zcode(ls, gameid=opts.gameid, compileconstants=compileconstants)
    zcode.build()
    strset = set([ val.text for val in zcode.strings ])
    print('globals:', len(zcode.globals))
    print('constants:', len(zcode.constants))
    print('static strings:', len(zcode.strings), '/', 'unique:', len(strset))
    print('inline strings:', len(zcode.istrings))
    print('routines:', len(zcode.routines))
    print('objects:', len(zcode.objects))
    print('actions:', len(zcode.actions))

if opts.gamefile:
    print('reading %s...' % (opts.gamefile,))
    fl = open(opts.gamefile, 'rb')
    gamefile = fl.read()
    fl.close()
    print('length:', len(gamefile))

if opts.txdfile:
    print('reading TXD dump...')
    txdat = TXDData()
    txdat.readdump('gamedat/game-dump.txt')
    print('routines:', len(txdat.routines))
    print('strings:', len(txdat.strings))
    print('istrings:', len(txdat.istrings))

if opts.objdump:
    print('reading object dump...')
    objdat = ObjDumpData()
    objdat.readdump('gamedat/obj-dump.txt')
    print('objects:', len(objdat.objects))
    
if opts.dictdump:
    print('reading dict dump...')
    dictdat = DictDumpData()
    dictdat.readdump('gamedat/dict-dump.txt')
    print('dict words:', len(dictdat.words))
    
if opts.grammardump:
    print('reading grammar dump...')
    grammardat = GrammarDumpData()
    grammardat.readdump('gamedat/grammar-dump.txt')
    print('verbs:', len(grammardat.verbs))
    print('actions:', len(grammardat.actions))
    print('prepositions:', len(grammardat.prepositions))
    
if opts.gamedat:
    write_filenames('src/game/filenames.js')
    write_properties('src/game/properties.js')
    write_attributes('src/game/attributes.js')
    if opts.dictdump:
        write_dictwords('src/game/dictwords.js', dictdat)
    if opts.zilfile and opts.grammardump:
        write_actions('src/game/actions.js', zcode, grammardat)
    if opts.grammardump and opts.dictdump and opts.txdfile and opts.zilfile:
        write_grammar('src/game/grammar.js', grammardat, dictdat, zcode, txdat)
    if opts.zilfile:
        write_globals('src/game/globals.js', zcode)
        write_constants('src/game/constants.js', zcode)
    if opts.zilfile and opts.objdump:
        write_objects('src/game/objects.js', zcode, objdat)
    if opts.zilfile and opts.txdfile:
        write_routines('src/game/routines.js', zcode, txdat)
    if opts.zilfile and opts.txdfile and opts.objdump:
        write_strings('src/game/strings.js', zcode, txdat, objdat)
    if opts.zilfile:
        compute_room_distances('src/game/distances.js', zcode)

if opts.showglob:
    display_globals(zcode)

if opts.sourcelist:
    if not opts.zilfile:
        print('need -z gamesrc/zork1.zil')
    else:
        write_source_colored('src/game/source.js', zcode)
