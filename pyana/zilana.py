from zillex import Token, TokType
from zillex import tokIN
from monkey import monkeyadjustifdef, monkeyextrastrings

class ZObject:
    def __init__(self, name, flag, desc, desctok, objtok):
        self.name = name
        self.type = flag
        self.desc = desc
        self.desctok = desctok
        self.objtok = objtok

    def __repr__(self):
        desc = (self.desc or '')
        return '<Z%s %s "%s">' % ('Room' if self.type == 'ROOM' else 'Object', self.name, desc,)

class ZString:
    def __init__(self, text, pos, endpos, rtn=None):
        self.text = text
        self.pos = pos
        self.endpos = endpos
        self.rtn = rtn

    def __repr__(self):
        summary = self.text
        if len(summary) > 40:
            summary = summary[ : 40 ] + '...'
        rtnstr = ''
        if self.rtn:
            rtnstr = '%s:' % (self.rtn,)
        return '<ZString %s"%s">' % (rtnstr, summary)
    
class ZGlobal:
    def __init__(self, name, gtok):
        self.name = name
        self.gtok = gtok
        self.valtok = None

    def __repr__(self):
        return '<ZGlobal %s>' % (self.name,)
    
class ZConstant:
    def __init__(self, name, value, ctok):
        self.name = name
        self.value = value
        self.ctok = ctok

    def __repr__(self):
        return '<ZConstant %s %d>' % (self.name, self.value,)
    
class ZRoutine:
    def __init__(self, name, callargcount, args, rtok, argstok):
        self.name = name
        self.callargcount = callargcount
        self.args = args
        self.rtok = rtok
        self.argstok = argstok

    def __repr__(self):
        return '<ZRoutine %s>' % (self.name,)
    
class ZVerb:
    def __init__(self, name):
        self.name = name
        self.vtoks = []

    def __repr__(self):
        return '<ZVerb %s>' % (self.name,)
    
def markcomments(ls):
    def setcomment(tok):
        tok.comment = True

    for tok in ls:
        if tok.typ is TokType.GROUP and tok.val == ';':
            tok.itertree(setcomment)
            continue
        if tok.typ is TokType.GROUP:
            markcomments(tok.children)

def findsetg(ls):
    # Find all top-level <SETG> constant definitions.
    map = {}
    for tok in ls:
        if tok.matchform('SETG', 2):
            idtok = tok.children[1]
            if idtok.typ is TokType.ID:
                valtok = tok.children[2]
                if valtok.typ is TokType.NUM:
                    constval = valtok.num
                elif valtok.typ is TokType.STR:
                    # ZIL conventionally has a SETG constant
                    # SIBREAKS which is a string. We're just gonna
                    # handwave that.
                    constval = 0
                elif valtok.typ is TokType.GROUP and not valtok.children:
                    constval = 0
                else:
                    raise Exception('SETG has no value: %s' % (idtok.val,))
                map[idtok.val] = constval
    return map
            
def stripcomments(ls):
    # Remove all commented-out elements from ls.
    newls = []
    for tok in ls:
        if tok.typ is TokType.GROUP and tok.val == ';':
            continue
        newls.append(tok)
        if tok.typ is TokType.GROUP:
            stripcomments(tok.children)
    ls.clear()
    ls.extend(newls)

def stripifdefs(ls, compileconstants, gameid=None):
    # Remove all compiled-out %<COND...> elements from ls.
    newls = []
    for tok in ls:
        if gameid is not None and monkeyadjustifdef(tok, gameid):
            continue
        if tok.typ is TokType.GROUP and tok.val == '%' and tok.children:
            ctok = tok.children[0]
            if ctok.matchform('COND', 0):
                found = None
                for cgrp in ctok.children[ 1 : ]:
                    found = teststaticcond(cgrp, compileconstants)
                    if found:
                        break
                if found:
                    newls.append(found)
                continue
        newls.append(tok)
        if tok.typ is TokType.GROUP:
            stripifdefs(tok.children, compileconstants, gameid=gameid)
    ls.clear()
    ls.extend(newls)

def teststaticcond(cgrp, compileconstants):
    if cgrp.typ is TokType.GROUP and cgrp.val == '()' and len(cgrp.children) == 2:
        condgrp = cgrp.children[0]
        resgrp = cgrp.children[1]
    else:
        raise Exception('teststaticcond: not a group')

    def evalstaticcond(condgrp):
        if condgrp.matchform('OR', 2):
            for subcond in condgrp.children[1:]:
                if evalstaticcond(subcond):
                    return True
            return False
        if condgrp.typ is TokType.ID and condgrp.val == 'T':
            return True
        if condgrp.matchform('GASSIGNED?', 1):
            # This tests whether a symbol is globally assigned. To date,
            # we only check PREDGEN this way, and it suffices to hardwire
            # it "true". In the future we may need to be more clever.
            return True
        if condgrp.matchform('==?', 2):
            keytok = condgrp.children[1]
            valtok = condgrp.children[2]
            if keytok.typ is TokType.GROUP and keytok.val == "," and keytok.children:
                kidtok = keytok.children[0]
                if kidtok.typ is TokType.ID:
                    if kidtok.val not in compileconstants:
                        raise Exception('compile-time COND for unknown constant: %s' % (kidtok.val,))
                    if valtok.typ is not TokType.NUM:
                        raise Exception('compile-time COND for non-numeric constant: %s' % (kidtok.val,))
                    return (valtok.num == compileconstants[kidtok.val])
        return False

    if evalstaticcond(condgrp):
        return resgrp
    else:
        return None


class Zcode:
    def __init__(self, tokls, gameid=None, compileconstants={}):
        self.tokls = tokls
        self.gameid = gameid
        self.compileconstants = compileconstants
        self.globals = []
        self.constants = []
        self.strings = []
        self.istrings = []
        self.routines = []
        self.objects = []
        self.roomnames = []
        self.verbs = []
        self.verbmap = {}
        self.attrnameset = set()
        self.directions = []
        self.directionset = set()
        self.sourceorder = []

    def build(self):
        self.findsourceorder()
        self.findinitial()
        self.findall()
        self.findextra()

    def findsourceorder(self):
        # Get a list of all source files, in the order they were included
        fileset = set()
        for tok in self.tokls:
            filename = tok.pos[0]
            if filename not in fileset:
                fileset.add(filename)
                self.sourceorder.append(filename)

    def findextra(self):
        # In case any strings were found in the game dump but not the source
        for strtok in monkeyextrastrings():
            self.strings.append(ZString(strtok.val, strtok.pos, strtok.endpos))

    def findinitial(self):
        # Some globals are generated by the compiler.
        self.globals.append(ZGlobal('LOW-DIRECTION', None))
        self.globals.append(ZGlobal('VERBS', None))
        self.globals.append(ZGlobal('ACTIONS', None))
        self.globals.append(ZGlobal('PREACTIONS', None))
        self.globals.append(ZGlobal('PREPOSITIONS', None))

    def findall(self):
        # Parse all the source
        for tok in self.tokls:
            if tok.matchform('GLOBAL', 1):
                idtok = tok.children[1]
                zglob = None
                if idtok.typ is TokType.ID:
                    zglob = ZGlobal(idtok.val, tok)
                    self.globals.append(zglob)
                    tok.defentity = zglob
                else:
                    raise Exception('Global has no name')
                if len(tok.children) >= 3:
                    globtok = tok.children[2]
                    zglob.valtok = globtok
                    if globtok.typ is TokType.STR:
                        self.strings.append(ZString(globtok.val, globtok.pos, globtok.endpos))
                    if globtok.typ is TokType.GROUP and globtok.children:
                        if globtok.children[0].val in ('TABLE', 'LTABLE'):
                            self.findstringsintok(globtok)
            if tok.matchform('CONSTANT', 2) or tok.matchform('SETG', 2):
                # SETG is for compile-time constants like ZORK-NUMBER and
                # DEBUG. We'll put them in the regular constant table.
                # (This duplicates the logic of findsetg() above. Sorry.)
                setg = (tok.children[0].val == 'SETG')
                idtok = tok.children[1]
                if idtok.typ is TokType.ID:
                    valtok = tok.children[2]
                    if valtok.typ is TokType.NUM:
                        constval = valtok.num
                    elif valtok.typ is TokType.STR:
                        if setg:
                            # ZIL conventionally has a SETG constant
                            # SIBREAKS which is a string. We're just gonna
                            # handwave that.
                            constval = 0
                        else:
                            raise Exception('Constant strings not supported: %s "%s"' % (idtok.val, valtok.val))
                    elif valtok.typ is TokType.GROUP and not valtok.children:
                        constval = 0
                    else:
                        raise Exception('Constant has no value: %s' % (idtok.val,))
                    zconst = ZConstant(idtok.val, constval, tok)
                    self.constants.append(zconst)
                    tok.defentity = zconst
                else:
                    raise Exception('Constant has no name')
            if tok.matchform('DIRECTIONS', 1):
                if self.directions:
                    raise Exception('Directions encountered twice')
                self.directions = [ dirtok.val for dirtok in tok.children[ 1 : ] ]
                self.directionset = set(self.directions)
            if tok.matchform('ROUTINE', 2):
                idtok = tok.children[1]
                if idtok.typ is TokType.ID:
                    argstok = tok.children[2]
                    callargcount, args = self.parseroutineargs(idtok.val, argstok)
                    rtn = ZRoutine(idtok.val, callargcount, args, tok, argstok)
                    self.routines.append(rtn)
                    tok.defentity = rtn
                    self.findstringsinroutine(tok, rtn)
            if tok.typ is TokType.GROUP and tok.val == "'" and tok.children[0].matchform('ROUTINE', 2):
                qtok = tok.children[0]
                idtok = qtok.children[1]
                if idtok.typ is TokType.ID:
                    argstok = qtok.children[2]
                    callargcount, args = self.parseroutineargs(idtok.val, argstok)
                    rtn = ZRoutine(idtok.val, callargcount, args, qtok, argstok)
                    self.routines.append(rtn)
                    qtok.defentity = rtn
                    self.findstringsinroutine(qtok, rtn)
            isobj = tok.matchform('OBJECT', 1)
            isroom = tok.matchform('ROOM', 1)
            if isobj or isroom:
                flag = 'ROOM' if isroom else 'OBJ'
                desc = None
                desctok = None
                idtok = tok.children[1]
                if idtok.typ is TokType.ID:
                    for proptok in tok.children[2:]:
                        if proptok.matchgroup(('DESC', 'LDESC', 'FDESC', 'TEXT'), 1):
                            if proptok.children[1].typ is TokType.STR:
                                strtok = proptok.children[1]
                                if proptok.children[0].val == 'DESC':
                                    desc = strtok.val
                                    desctok = strtok
                                else:
                                    self.strings.append(ZString(strtok.val, strtok.pos, strtok.endpos))
                        if proptok.matchgroup(self.directionset, 1):
                            self.findstringsintok(proptok)
                        if proptok.matchgroup('FLAGS', 1):
                            attrnames = [ atok.val for atok in proptok.children[1:] if atok.typ is TokType.ID ]
                            self.attrnameset.update(attrnames)
                    newobj = ZObject(idtok.val, flag, desc, desctok, tok)
                    self.objects.append(newobj)
                    tok.defentity = newobj
                    if isroom:
                        self.roomnames.append(idtok.val)
            if tok.matchform('SYNTAX', 3):
                eqpos = None
                for ix in range(len(tok.children)):
                    if tok.children[ix].idmatch('='):
                        eqpos = ix
                        break
                if eqpos:
                    verbtok = tok.children[eqpos+1]
                    if verbtok.idmatch(lambda val: val.startswith('V-')):
                        val = verbtok.val[ 2 : ]
                        verb = self.verbmap.get(val)
                        if not verb:
                            verb = ZVerb(val)
                            self.verbs.append(verb)
                            self.verbmap[val] = verb
                        verb.vtoks.append(tok)
                        

    def findstringsintok(self, tok):
        for stok in tok.children:
            if stok.typ is TokType.STR:
                if stok.val:
                    self.strings.append(ZString(stok.val, stok.pos, stok.endpos))
            if stok.typ is TokType.GROUP and stok.val == '<>' and stok.children:
                self.findstringsintok(stok)
        
    def findstringsinroutine(self, tok, rtn):
        rname = rtn.name
        for stok in tok.children:
            if stok.typ is TokType.STR:
                if stok.val == '':
                    continue
                if tokIN(stok, rtn.argstok) and stok.val in ('AUX', 'OPTIONAL'):
                    continue
                self.strings.append(ZString(stok.val, stok.pos, stok.endpos, rname))
            if stok.typ is TokType.GROUP and stok.val in ('<>', '()', "'") and stok.children:
                if stok.children[0].typ is TokType.ID and stok.children[0].val in ('TELL', 'PRINTI'):
                    self.findstringsintell(stok, rtn)
                else:
                    self.findstringsinroutine(stok, rtn)

    def parseroutineargs(self, funcname, tok):
        if tok.typ is not TokType.GROUP:
            raise Exception('%s: args group is not a group: %s' % (funcname, tok,))
        args = []
        callargcount = None
        for atok in tok.children:
            if atok.typ is TokType.STR:
                if atok.val == 'AUX':
                    callargcount = len(args)
                continue
            if atok.typ is TokType.ID:
                args.append(atok.val)
                continue
            if atok.typ is TokType.GROUP and atok.val == '()' and atok.children:
                gatok = atok.children[0]
                if gatok.typ is TokType.ID:
                    args.append(gatok.val)
                continue
        if callargcount is None:
            callargcount = len(args)
        return callargcount, args

    def findstringsintell(self, tok, rtn):
        rname = rtn.name
        for stok in tok.children:
            if stok.typ is TokType.STR:
                self.istrings.append(ZString(stok.val, stok.pos, stok.endpos, rname))
            if stok.typ is TokType.GROUP and stok.val == '<>':
                self.findstringsinroutine(stok, rtn)
            
    def mapconnections(self, extraconn=[]):
        exitmap = dict()
        for room in self.roomnames:
            exitmap[room] = []
            
        for tok in self.tokls:
            if tok.matchform('ROOM', 1):
                room = tok.children[1].val
                for prop in tok.children[2:]:
                    if prop.typ is TokType.GROUP and prop.val == '()' and len(prop.children) >= 3:
                        itok = prop.children[0]
                        totok = prop.children[1]
                        desttok = prop.children[2]
                        if itok.typ is TokType.ID and itok.val in self.directionset:
                            if totok.typ is TokType.ID and totok.val == 'TO':
                                if desttok.typ is TokType.ID and desttok.val in exitmap:
                                    #print(room, itok.val, desttok.val)
                                    exitmap[room].append( (itok.val, desttok.val) )

        if extraconn:
            for room, dir, dest in extraconn:
                exitmap[room].append( (dir, dest) )

        return exitmap
        
                        
