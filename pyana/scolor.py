from enum import StrEnum

from zillex import Lexer, TokType, dumptokens
from zillex import posLE, posGT
from zilana import ismonkeyskip, teststaticcond, ZRoutine
from writer import get_attributes, get_properties

gameid = None
compileconstants = {}
implicitids = set()
linkids = {}
loctoentity = {}

def prep_syntax_coloring(zcode):
    global gameid
    gameid = zcode.gameid
    compileconstants.update(zcode.compileconstants)
    
    # A global can be defined more than once (see LUCKY, WON-FLAG).
    # We just let one definition win.
    absorb_entities([ (glo, glo.gtok) for glo in zcode.globals ], dupcheck=False)
    absorb_entities([ (obj, obj.objtok) for obj in zcode.objects ])
    absorb_entities([ (rtn, rtn.rtok) for rtn in zcode.routines ])
    absorb_entities([ (con, con.ctok) for con in zcode.constants ], dupcheck=False)
    for (num, attr) in get_attributes():
        if attr in implicitids:
            raise Exception('symbol clash: %s' % (attr,))
        implicitids.add(attr)
    for (num, prop) in get_properties():
        implicitids.add('P?'+prop)

### special-case property names in a ROOM/OBJECT declaration
### (and special-special case the DIR TO lines)
        
def colorize_file(filename):
    # This is awkward. We just parsed the ZIL for the zcode object,
    # but we want to do it again for the syntax coloring. (The first
    # time we stripped out comments and conditional compilation, but
    # now we leave them in.) (Also, the original parsing might have
    # game-specific monkeypatches which we now want to omit.)
    
    lex = Lexer(filename, monkeypatch=None)
    tokls = lex.readfile(includes=False)
    #dumptokens(tokls, withpos=True)
    
    res = []
    colorize(tokls, res, None)
    #dumpcolors(res)
    lines = color_file_lines(filename, res)
    return lines

def absorb_entities(ls, dupcheck=True):
    for obj, tok in ls:
        if dupcheck and obj.name in linkids:
            raise Exception('symbol clash: %s' % (obj.name,))
        linkids[obj.name] = tok
        if tok:
            lockey = tok.posstr()
            if lockey in loctoentity:
                raise Exception('location clash (%s): %s' % (obj, lockey,))
            loctoentity[lockey] = obj

class Color(StrEnum):
    STR = 'STR'           # String
    ID = 'ID'             # Normal identifier (will link to def)
    IMPLID = 'IMPLID'     # Identifier with no definition (will open a tab)
    LOCALID = 'LOCALID'   # Local-variable identifier
    IDDEF = 'IDDEF'       # Identifier being defined
    DICT = 'DICT'         # Dictionary word
    COMMENT = 'COMMENT'   # Commented-out element
    IFNDEF = 'IFNDEF'     # Compiled-out element

def colorize(tokls, res, defentity):
    localids = set()
    if defentity and isinstance(defentity, ZRoutine):
        localids = set(defentity.args)
        
    for tok in tokls:
        if gameid is not None and ismonkeyskip(tok, gameid):
            res.append( (tok, Color.IFNDEF) )
            continue
        if tok.typ is TokType.STR:
            if tok.val in ('AUX', 'OPTIONAL', 'ARGS'):
                # not really a string
                continue
            res.append( (tok, Color.STR) )
            continue
        if tok.typ is TokType.ID:
            if tok.val in localids:
                res.append( (tok, Color.LOCALID) )
            elif tok.val in linkids:
                if defentity and defentity.name == tok.val:
                    res.append( (tok, Color.IDDEF) )
                else:
                    res.append( (tok, Color.ID) )
            elif tok.val in implicitids:
                res.append( (tok, Color.IMPLID) )
            continue
        
        if tok.typ is TokType.GROUP and tok.val == ';':
            res.append( (tok, Color.COMMENT) )
            continue
        
        if tok.typ is TokType.GROUP and tok.val == '%' and tok.children:
            ctok = tok.children[0]
            if ctok.matchform('COND', 0):
                colorize([ ctok.children[0] ], res, defentity)
                found = None
                for cgrp in ctok.children[ 1 : ]:
                    if found:
                        res.append( (cgrp, Color.IFNDEF) )
                        continue
                    found = teststaticcond(cgrp, compileconstants)
                    if found:
                        colorize([ cgrp ], res, defentity)
                    else:
                        res.append( (cgrp, Color.IFNDEF) )
                        continue
                continue
        if tok.typ is TokType.GROUP and tok.val == '()' and tok.children:
            if tok.children[0].idmatch(('SYNONYM', 'ADJECTIVE')):
                for subtok in tok.children[1:]:
                    if subtok.typ is TokType.ID:
                        res.append( (subtok, Color.DICT) )
                    if subtok.typ is TokType.GROUP and subtok.val == ';':
                        res.append( (subtok, Color.COMMENT) )
                continue
            if tok.children[0].idmatch('PSEUDO'):
                for subtok in tok.children[1:]:
                    if subtok.typ is TokType.STR:
                        res.append( (subtok, Color.DICT) )
                    if subtok.typ is TokType.ID and subtok.val in linkids:
                        res.append( (subtok, Color.ID) )
                continue
        if tok.matchform('BUZZ', 1):
            for subtok in tok.children[1:]:
                if subtok.typ is TokType.ID:
                    res.append( (subtok, Color.DICT) )
            continue
        if tok.matchform('SYNONYM', 1):
            for subtok in tok.children[1:]:
                if subtok.typ is TokType.ID:
                    res.append( (subtok, Color.DICT) )
            continue
        if tok.matchform('SYNTAX', 3):
            eqpos = 1
            for subtok in tok.children[1:]:
                if subtok.idmatch('='):
                    break
                if subtok.typ is TokType.ID and subtok.val != 'OBJECT':
                    res.append( (subtok, Color.DICT) )
                eqpos += 1
            colorize(tok.children[ eqpos+1 : ], res, defentity)
            continue
        
        if tok.children:
            subentity = defentity
            if not subentity:
                lockey = tok.posstr()
                if lockey in loctoentity:
                    subentity = loctoentity[lockey]
            colorize(tok.children, res, subentity)

def dumpcolors(ls):
    for (tok, color) in ls:
        print('%s: %s %s' % (color, tok.posstr(), tok, ))

def color_file_lines(filename, colorls):
    colorls = list(colorls)
    res = []
    
    with open(filename) as infl:
        col = colorls and colorls.pop(0)
        
        linenum = 1
        for ln in infl.readlines():
            ln = ln.rstrip()
            
            curline = []
            charnum = 1
            
            while charnum < 1+len(ln):
                lastcharnum = charnum
                while col and posLE(col[0].endpos, (linenum, charnum)):
                    col = colorls and colorls.pop(0)
                if not col:
                    charnum = 1+len(ln)
                    if lastcharnum < charnum:
                        curline.append( (None, ln[lastcharnum-1 : charnum-1]) )
                    continue
                
                _, colline, colchar = col[0].pos
                if posGT((colline, colchar), (linenum, charnum)):
                    if colline > linenum:
                        charnum = 1+len(ln)
                    else:
                        charnum = colchar
                    if lastcharnum < charnum:
                        curline.append( (None, ln[lastcharnum-1 : charnum-1]) )
                    continue
                
                _, colendline, colendchar = col[0].endpos
                if colendline > linenum:
                    charnum = 1+len(ln)
                else:
                    charnum = colendchar
                if lastcharnum < charnum:
                    curline.append( (col[1], ln[lastcharnum-1 : charnum-1]) )
                    
            res.append(curline)
            linenum += 1

    return res

