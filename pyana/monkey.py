from xml.dom.minidom import Node

def monkeyinsertcrufty(gameid):
    if gameid == 'deadline-r27-s831005':
        return True
    if gameid == 'starcross-r15-s820901':
        return True
    if gameid == 'suspended-mac-r8-s840521':
        return True

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
            return True
    return False

def monkeyextrastrings():
    return extracompiledstrings

def monkeyadjuststringtext(text, gameid, rtn=None):
    text = text.replace('.  ', '. ')
    # Something about punctuation and spaces
    text = text.replace('    ****', '   ****')
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

