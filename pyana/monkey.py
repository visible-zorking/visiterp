from zillex import Token, TokType

def monkeyadjustlex(lexer, ls):
    if lexer.monkeypatch == 'zork2-r48-s840904':
        if lexer.filename == 'zork2.zil':
            #### on the end is probably fine?
            pos = None
            for ix, tok in enumerate(ls):
                if tok.matchform('IFILE', 1) and tok.children[1].val == 'GGLOBALS':
                    pos = ix
                    break
            if pos is not None:
                tok = ls[pos]
                newtok = Token(TokType.GROUP, '<', tok.pos, [
                    Token(TokType.ID, 'IFILE', tok.pos),
                    Token(TokType.STR, 'CRUFTY', tok.pos),
                    Token(TokType.ID, 'T', tok.pos),
                ])
                ls.insert(pos, newtok)
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

