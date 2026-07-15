from xml.dom.minidom import Node

def monkeyinsertcrufty(gameid):
    if gameid == 'deadline-r27-s831005':
        return True
    if gameid == 'starcross-r15-s820901':
        return True
    if gameid == 'suspended-mac-r8-s840521':
        return True

def monkeyskiptoken(lexer, tok):
    if tok.typ is TokType.DELIM and tok.val == '>' and tok.pos == ('people.zil', 149, 41) and lexer.monkeypatch.startswith('suspended-mac-r8-s840521'):
        return True
    if tok.typ is TokType.DELIM and tok.val == ')' and tok.pos == ('places.zil', 947, 1) and lexer.monkeypatch.startswith('witness-r23-s840925'):
        return True
    if tok.typ is TokType.DELIM and tok.val == '>' and tok.pos == ('places.zil', 947, 2) and lexer.monkeypatch.startswith('witness-r23-s840925'):
        return True
    return False

def monkeyadjustlex(lexer, ls):
    if lexer.monkeypatch == 'zork2-r48-s840904':
        if lexer.filename == 'zork2.zil':
            # Add a synthetic include at the end of the top file.
            pos = lexer.getpos()
            newtok = Token(TokType.GROUP, '<', pos, [
                Token(TokType.ID, 'IFILE', pos),
                Token(TokType.STR, 'CRUFTY', pos),
                Token(TokType.ID, 'T', pos),
            ])
            ls.append(newtok)
    if lexer.monkeypatch == 'starcross-r15-s820901':
        if lexer.filename == 'dungeon.zil':
            # Add a synthetic object at line 52 of dungeon.zil.
            pos = lexer.getpos()
            pos = ('dungeon.zil', 52, 0)
            endpos = ('dungeon.zil', 53, 0)
            newtok = Token(TokType.GROUP, '<', pos=pos, endpos=endpos, children=[
                Token(TokType.ID, 'OBJECT', pos),
                Token(TokType.ID, 'LADDER', pos),
            ])
            ls.append(newtok)
        if lexer.filename == 'verbs.zil':
            # Add a fake FSET?/TELL clause at line 1095 in the V-SHAKE
            # routine, between the "This seems to have no effect" and
            # "sounds like there is something inside" clauses.
            tok = ls[147]
            assert tok.children[1].val == 'V-SHAKE'
            condtok = tok.children[3]
            pos = ('verbs.zil', 1095, 0)
            endpos = ('verbs.zil', 1095, 1)
            newtok = Token(TokType.GROUP, '(', pos=pos, endpos=endpos, children=[
                Token(TokType.GROUP, '<', pos=pos, children=[
                    Token(TokType.ID, 'FSET?', pos),
                    Token.WithPrefix(',', TokType.ID, 'PRSO', pos),
                    Token.WithPrefix(',', TokType.ID, 'TAKEBIT', pos),
                ]),
                Token(TokType.GROUP, '<', pos=pos, children=[
                    Token(TokType.ID, 'TELL', pos),
                    Token(TokType.STR, "You don't have it!", pos),
                    Token(TokType.ID, 'CR', pos),
                ]),
            ])
            condtok.children.insert(2, newtok)
    if lexer.monkeypatch == 'witness-r23-s840925':
        if lexer.filename == 'people.zil':
            # Add a synthetic object at line 80 of people.zil.
            pos = lexer.getpos()
            pos = ('people.zil', 80, 0)
            endpos = ('people.zil', 81, 0)
            newtok = Token(TokType.GROUP, '<', pos=pos, endpos=endpos, children=[
                Token(TokType.ID, 'OBJECT', pos),
                Token(TokType.ID, 'DRIVEWAY-GATE', pos),
            ])
            ls.append(newtok)
    return ls

extracompiledstrings = []

def monkeyadjustifdef(tok, gameid, forscolor=False):
    if gameid == 'zork2-r48-s840904':
        if tok.typ is TokType.STR and tok.val == 'You must explain how to do that.':
            return True
        if tok.typ is TokType.STR and tok.val == 'Wasn\'t he a sailor?':
            return True
        if tok.typ is TokType.GROUP and tok.val == '<>' and len(tok.children) == 3 and tok.children[0].val == 'GLOBAL' and tok.children[1].val == 'DUMMY' and tok.pos[0] == 'gverbs.zil':
            if not forscolor:
                ltable = tok.children[2]
                # "Too late for that."
                extracompiledstrings.append(ltable.children[3])
                # "Have your eyes checked."
                extracompiledstrings.append(ltable.children[4])
            return True
    if gameid == 'zork3-r17-s840727':
        if tok.typ is TokType.STR and tok.val == 'You don\'t have that.':
            return True
    if gameid == 'suspended-mac-r8-s840521':
        if tok.typ is TokType.GROUP and tok.pos == ('robots.zil', 878, 2):
            # first CLC-TXT property
            if not forscolor:
                pltable = tok.children[1]
                # "They are carbon-based, organic mechanisms."
                extracompiledstrings.append(pltable.children[1])
                # "They are here to replace you. You must stop them at all costs."
                extracompiledstrings.append(pltable.children[2])
                # "I refer you to Gregory Franklin..."
                extracompiledstrings.append(pltable.children[3])
            return True
    if gameid == 'witness-r23-s840925':
        if tok.typ is TokType.GROUP and tok.pos == ('things.zil', 426, 1):
            # inlined routine SEEKING-DRINK?
            return True
        if tok.typ is TokType.GROUP and tok.pos == ('main.zil', 45, 1):
            # inlined routine MAIN-LOOP
            return True
        if tok.typ is TokType.GROUP and tok.pos == ('people.zil', 437, 15):
            # PHONG-F stanza not compiled in
            return True
    return False

def monkeyextrastrings():
    return extracompiledstrings

def monkeyadjuststringtext(text, gameid, rtn=None):
    text = text.replace('.  ', '. ')
    if gameid != 'planetfall-r37-s851003':
        # Something about punctuation and spaces (mostly)
        text = text.replace('    ****', '   ****')
    if gameid == 'zork1-r88-s840726':
        # My untabification
        if text.startswith('"     Flood'):
            text = text.replace('"     Flood', '"\tFlood')
        if text.startswith('         !!!!  '):
            text = text.replace('         !!!!  ', '\t  !!!! \t')
        if '          All-' in text:
            text = text.replace('          All-', '\t  All-')
    if gameid == 'zork3-r17-s840727':
        # Double-space is not always fixed
        text = text.replace('crumbling. To the southwest', 'crumbling.  To the southwest')
        text = text.replace('read them. The book', 'read them.  The book')
        text = text.replace('stay. The lake', 'stay.  The lake')
        text = text.replace('voices fading. After a', 'voices fading.  After a')
        text = text.replace('location. Interestingly', 'location.  Interestingly')
        text = text.replace('up for you. Then,', 'up for you.  Then,')
        text = text.replace('hills to the east. A path', 'hills to the east.  A path')
    if gameid == 'deadline-r27-s831005':
        # Extra trimming
        if text.startswith('Frobizz Pharm'):
            text = text[ : -1 ]
        if text.startswith(':\n\nDear Inspector,'):
            text = text[ : -1 ]
        # These characters are switched in the source and I don't know why.
        if text == '".' and rtn == 'ROURKE-F':
            text = '."'
    if gameid == 'starcross-r15-s820901':
        if text == 'Lose, lose!':
            text = '!'
    if gameid == 'suspended-mac-r8-s840521':
        # My untabification
        if text.startswith('FC INTERRUPT: Oh oh.'):
            text = text.replace('               NOVA', ' \t       NOVA')
    if gameid == 'witness-r23-s840925':
        # Extra trimming
        if text.startswith(':\n\nDear Detective:'):
            text = text[ : -1 ]
    return text

def monkeyadjustmapxml(doc, gameid):
    if gameid == 'starcross-r15-s820901':
        svgnod = doc.childNodes[1]
        groupls = []
        for nod in svgnod.childNodes:
            if nod.nodeName == 'g':
                groupls.append(nod)
        gnod = doc.createElement('g')
        gnod.appendChild(doc.createTextNode('\n  '))
        gnod.setAttribute('id', 'turntable')
        svgnod.appendChild(doc.createTextNode('\n'))
        svgnod.appendChild(gnod)
        svgnod.appendChild(doc.createTextNode('\n'))
        for nod in groupls:
            gnod.appendChild(nod)
            gnod.appendChild(doc.createTextNode('\n  '))
    return doc


# late imports
from zillex import Token, TokType

