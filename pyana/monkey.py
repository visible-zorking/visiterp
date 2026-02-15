from zillex import Token, TokType

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
    return False

def monkeyextrastrings():
    return extracompiledstrings

def monkeyadjuststringtext(text, gameid):
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
    return text
