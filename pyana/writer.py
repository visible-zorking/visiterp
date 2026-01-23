import json
import re

info_loaded = False

sourcefile_map = {}
sourcefile_binorder_map = {}
objnum_to_name = {}
objname_to_num = {}
propnum_to_name = {}
propname_to_num = {}
globname_to_num = {}
globnum_to_name = {}
globname_to_vartype = {}
attribute_list = []
property_list = []
propname_to_vartype = {}
funcname_to_argtypes = {}
mapextra_list = []

def load_gameinfo():
    global info_loaded
    if info_loaded:
        return
    pat = re.compile(r'(\S+)\s+(\S+)\s+(\S+)\s*(.*)?')
    fl = open('gamedat/game-info')
    for ln in fl.readlines():
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        match = pat.match(ln)
        typ, num, name = match.group(1), match.group(2), match.group(3)
        extra = match.group(4)
        num = 0 if num == '-' else int(num)
        if typ == 'SourceFile':
            val = chr(64+num)
            sourcefile_map[name] = val
            if extra:
                sourcefile_binorder_map[name] = int(extra)
        elif typ == 'Object':
            if name in objname_to_num:
                raise Exception('Object name repeats: %s' % (name,))
            objname_to_num[name] = num
            if num in objnum_to_name:
                raise Exception('Object num repeats: %s' % (num,))
            objnum_to_name[num] = name
        elif typ == 'Property':
            if name in propname_to_num:
                raise Exception('Property name repeats: %s' % (name,))
            propname_to_num[name] = num
            if num in propnum_to_name:
                raise Exception('Property num repeats: %s' % (num,))
            propnum_to_name[num] = name
            property_list.append( (num, name) )
            if extra:
                propname_to_vartype[name] = extra
        elif typ == 'Attribute':
            attribute_list.append( (num, name) )
        elif typ == 'Global':
            if name in globname_to_num:
                raise Exception('Global name repeats: %s' % (name,))
            globname_to_num[name] = num
            if num in globnum_to_name:
                raise Exception('Global num repeats: %s' % (num,))
            globnum_to_name[num] = name
            if extra:
                globname_to_vartype[name] = extra
        elif typ == 'RoutineType':
            argtypes = []
            for val in extra.split(' '):
                if not val:
                    continue
                if val == '-':
                    argtypes.append(None)
                    continue
                argtypes.append(val)
            funcname_to_argtypes[name] = argtypes
        elif typ == 'MapExtraConn':
            (dir, dest) = extra.split(' ')
            mapextra_list.append( (name, dir, dest) )
        else:
            raise Exception('bad game-info line: %s' % (typ,))
    fl.close()
    info_loaded = True

def sourceloc(tup=None, endtup=None, tok=None):
    if not info_loaded:
        raise Exception('sourcefile_map not loaded')
    if tok:
        tup = tok.pos
        endtup = tok.endpos
    if tup is None:
        return ''
    file, line, char = tup
    filekey = sourcefile_map[file]
    res = '%s:%d:%d' % (filekey, line, char,)
    if endtup:
        efile, eline, echar = endtup
        if file != efile:
            raise Exception('sourceloc span across files')
        res += ':%d:%d' % (eline, echar,)
    return res

def get_sourcefile_map():
    load_gameinfo()
    return sourcefile_map

def get_attributes():
    load_gameinfo()
    return attribute_list

def get_properties():
    load_gameinfo()
    return property_list

def sort_zcode_routines(ls, sourceorder):
    # Some games (Zork 1) compile routines in source-code order.
    # Others (Zork 2) do not, for reasons I have failed to figure out.
    # The game-info "SourceFile" lines can provide an explicit order;
    # if not, fall back to source-code order.
    fileorder = {}   # maps filename to order index (1-based)
    for (index, filename) in enumerate(sourceorder, start=1):
        fileorder[filename] = index
    for (filename, index) in sourcefile_binorder_map.items():
        fileorder[filename] = index
    # Within a file, functions are compiled in the order encountered.
    funcorder = { zfunc.name: index for (index, zfunc) in enumerate(ls) }
    def func(zfunc):
        filename = zfunc.rtok.pos[0]
        return (fileorder[filename], funcorder[zfunc.name])
    res = ls.copy()
    res.sort(key=func)
    return res

def write_filenames(filename):
    print('...writing filename data:', filename)
    load_gameinfo()

    keymap = dict()
    capmap = dict()
    revmap = dict()
    for name, key in sourcefile_map.items():
        keymap[name] = key
        revmap[key] = name
        sname, _, _ = name.rpartition('.')
        capmap[sname.upper()] = key
    
    fl = open(filename, 'w')
    fl.write('window.gamedat_sourcefile_keymap = ');
    json.dump(keymap, fl, separators=(',', ':'))
    fl.write(';\n')
    fl.write('window.gamedat_sourcefile_capkeymap = ');
    json.dump(capmap, fl, separators=(',', ':'))
    fl.write(';\n')
    fl.write('window.gamedat_sourcefile_revkeymap = ');
    json.dump(revmap, fl, separators=(',', ':'))
    fl.write(';\n')
    fl.close()

def interpret_dictflags(wd):
    prepnum = adjnum = verbnum = dirnum = None
    
    # The dict-flag rules are quite terrible. See Michael Ko
    # page 22.
    
    if 'P' in wd.flags:
        prepnum = wd.special[1]
    if 'A' in wd.flags:
        if (wd.special[0] & 0x03) == 0x02:
            adjnum = wd.special[1]
        elif wd.special[0] & 0x20:
            adjnum = wd.special[2]
        else:
            raise Exception('adj flag without bits')
    if 'V' in wd.flags:
        if (wd.special[0] & 0x03) == 0x01:
            verbnum = wd.special[1]
        elif wd.special[0] & 0x40:
            verbnum = wd.special[2]
        else:
            raise Exception('verb flag without bits')
    if 'D' in wd.flags:
        if (wd.special[0] & 0x03) == 0x03:
            dirnum = wd.special[1]
        elif wd.special[0] & 0x10:
            dirnum = wd.special[2]
        else:
            raise Exception('dir flag without bits')
    
    return (prepnum, adjnum, verbnum, dirnum)
    
def write_dictwords(filename, dictdat):
    print('...writing dictword data:', filename)

    ls = []
    for wd in dictdat.words:
        dat = { 'num': wd.num, 'text': wd.text, 'flags': wd.flags }
        prepnum, adjnum, verbnum, dirnum = interpret_dictflags(wd)
        if prepnum is not None:
            dat['prepnum'] = prepnum
        if adjnum is not None:
            dat['adjnum'] = adjnum
        if verbnum is not None:
            dat['verbnum'] = verbnum
        if dirnum is not None:
            dat['dirnum'] = dirnum
        ls.append(dat)

    fl = open(filename, 'w')
    fl.write('window.gamedat_dictwords = ');
    json.dump(ls, fl, separators=(',', ':'))
    fl.write(';\n')
    fl.close()

def write_strings(filename, zcode, txdat, objdat):
    print('...writing string data:', filename)
    load_gameinfo()

    objname_to_descloc = {}
    for obj in zcode.objects:
        if obj.desc:
            objname_to_descloc[obj.name] = obj.desctok

    strtext_to_pos = {}
    for st in zcode.strings:
        if st.text not in strtext_to_pos:
            strtext_to_pos[st.text] = []
        strtext_to_pos[st.text].append(st)

    istrtext_to_pos = {}
    for st in zcode.istrings:
        text = st.text.replace('.  ', '. ')
        text = text.replace('    ****', '   ****')
        tup = (st.rtn, text)
        if tup not in istrtext_to_pos:
            istrtext_to_pos[tup] = []
        istrtext_to_pos[tup].append(st)

    funcaddr_to_name = {}
    sortedroutines = sort_zcode_routines(zcode.routines, zcode.sourceorder)
    for zfunc, tfunc in zip(sortedroutines, txdat.routines):
        funcaddr_to_name[tfunc.addr] = zfunc.name
        
    ls = []
    for str in txdat.strings:
        posls = strtext_to_pos.get(str.text)
        posval = None
        if not posls:
            print('ERROR: missing str', str)
        else:
            if len(posls) == 1:
                posval = sourceloc(tok=posls[0])
            else:
                posval = [ sourceloc(tok=val) for val in posls ]
        ls.append([ str.addr, str.text, posval ])
    for str in txdat.istrings:
        fname = funcaddr_to_name[str.rtn.addr]
        tup = istrtext_to_pos.get((fname, str.text))
        if tup is not None:
            srctok = tup.pop(0)
            ls.append([ str.addr, str.text, sourceloc(tok=srctok), str.rtn.addr ])
    for obj in objdat.objects:
        if not obj.desc:
            continue
        oname = objnum_to_name[obj.num]
        srctok = objname_to_descloc.get(oname)
        ls.append([ obj.propaddr+1, obj.desc, sourceloc(tok=srctok), obj.num ])

    for tup, tls in istrtext_to_pos.items():
        if tls:
            print('ERROR: unused istrings: %s, "%s"' % tup)

    fl = open(filename, 'w')
    fl.write('window.gamedat_strings = ');
    json.dump(ls, fl, separators=(',', ':'))
    fl.write(';\n')
    fl.close()

def write_properties(filename):
    print('...writing property data:', filename)
    load_gameinfo()

    propls = [ { 'num':num, 'name':name } for (num, name) in property_list ]
    for obj in propls:
        val = propname_to_vartype.get(obj['name'])
        if val:
            obj['vartype'] = val
    
    fl = open(filename, 'w')
    fl.write('window.gamedat_properties = ');
    json.dump(propls, fl)
    fl.write(';\n')
    fl.close()
    
def write_attributes(filename):
    print('...writing attribute data:', filename)
    load_gameinfo()

    attrls = [ { 'num':num, 'name':name } for (num, name) in attribute_list ]

    fl = open(filename, 'w')
    fl.write('window.gamedat_attributes = ');
    json.dump(attrls, fl)
    fl.write(';\n')
    fl.close()
    
def write_actions(filename, zcode, grammardat):
    print('...writing actions:', filename)
    if len(zcode.actions) != len(grammardat.actions):
        raise Exception('action count mismatch')
    
    ls = []
    for ix, act in enumerate(zcode.actions):
        dat = { 'num': ix, 'name': act.name }
        gact = grammardat.actions[ix]
        assert gact.num == ix
        if gact.actionrtn:
            dat['acrtn'] = gact.actionrtn
        if gact.preactionrtn:
            dat['preacrtn'] = gact.preactionrtn
        ls.append(dat)

    fl = open(filename, 'w')
    fl.write('window.gamedat_actions = ');
    json.dump(ls, fl)
    fl.write(';\n')
    fl.close()

def interpret_locbits(val):
    # See constants in gparser.zil.
    ls = []
    if val & 128:
        ls.append('HELD')
    if val & 64:
        ls.append('CARRIED')
    if val & 32:
        ls.append('IN-ROOM')
    if val & 16:
        ls.append('ON-GROUND')
    if val & 8:
        ls.append('TAKE')
    if val & 4:
        ls.append('MANY')
    if val & 2:
        ls.append('HAVE')
    if val & 1:
        ls.append('???')
    return '(' + ' '.join(ls) + ')'
    
def write_grammar(filename, grammardat, dictdat, zcode, txdat):
    print('...writing grammar:', filename)
    load_gameinfo()

    attrnames = { num: attr for num, attr in attribute_list }
    prepwds = {}
    for prep in grammardat.prepositions:
        ls = [ prep.text ] + prep.synonyms
        prepwds[prep.num] = '/'.join(ls)
    verbwds = {}
    for wd in dictdat.words:
        prepnum, adjnum, verbnum, dirnum = interpret_dictflags(wd)
        if verbnum is not None:
            ### but which are the synonyms?
            verbwds[verbnum] = wd

    verbls = []
    
    for verb in grammardat.verbs:
        lines = []
        dat = { 'num': verb.num, 'addr': verb.addr, 'lines': lines }
        verbls.append(dat)
        addr = verb.addr + 1
        for gline in verb.lines:
            ls = [ verbwds[verb.num].text ]
            if gline.objcount >= 1:
                if gline.dobjprep:
                    ls.append(prepwds[gline.dobjprep])
                if gline.dobjattr:
                    ls.append('O:'+attrnames[gline.dobjattr])
                else:
                    ls.append('OBJ')
                if gline.dobjloc:
                    ls.append(interpret_locbits(gline.dobjloc))
            if gline.objcount >= 2:
                if gline.iobjprep:
                    ls.append(prepwds[gline.iobjprep])
                if gline.iobjattr:
                    ls.append('O:'+attrnames[gline.iobjattr])
                else:
                    ls.append('OBJ')
                if gline.iobjloc:
                    ls.append(interpret_locbits(gline.iobjloc))
            print('### %r -> %s' % (' '.join(ls), zcode.actions[gline.action].name,))
            linedat = { 'addr': addr, 'text': ' '.join(ls) }
            addr += 8
            lines.append(linedat)

    fl = open(filename, 'w')
    fl.write('window.gamedat_grammar = ');
    json.dump(verbls, fl, separators=(',', ':'))
    fl.write(';\n')
    fl.close()
    
def write_routines(filename, zcode, txdat):
    print('...writing routine data:', filename)
    load_gameinfo()

    if len(zcode.routines) != len(txdat.routines):
        raise Exception('routine length mismatch (%d vs %d)' % (len(zcode.routines), len(txdat.routines),))
    
    sortedroutines = sort_zcode_routines(zcode.routines, zcode.sourceorder)
    
    ls = []
    for zfunc, tfunc in zip(sortedroutines, txdat.routines):
        dat = {
            'name': zfunc.name,
            'addr': tfunc.addr,
            'sourceloc': sourceloc(tok=zfunc.rtok),
        }
        args = zfunc.args[ : zfunc.callargcount ]
        argtypes = funcname_to_argtypes.get(zfunc.name)
        if argtypes is None:
            argtypes = [ guessargtype(zfunc.name, arg, ix) for (ix, arg) in enumerate(args) ]
        if any(argtypes):
            dat['argtypes'] = argtypes
        ls.append(dat)

    fl = open(filename, 'w')
    fl.write('window.gamedat_routines = ');
    json.dump(ls, fl, separators=(',', ':'))
    fl.write(';\n')
    fl.close()

def guessargtype(funcname, argname, index):
    # This guesser may be Zork-specific. The display of MFLAG as well.
    ### Use source #DECL?
    if argname in ('O', 'OBJ', 'R', 'RM', 'ROOM'):
        return 'OBJ'
    if argname == 'STR':
        return 'STR'
    if argname == 'RTN':
        return 'RTN'
    if argname == 'RARG':
        return 'MFLAG'
    return None

def write_globals(filename, zcode):
    print('...writing globals data:', filename)
    load_gameinfo()
    found = set()
    ls = []
    for glo in zcode.globals:
        if glo.name in found:
            # Annoyingly, WON-FLAG and LUCKY appear twice (in Z1).
            # TODO: record two sourcelocs?
            continue
        found.add(glo.name)
        if glo.name not in globname_to_num:
            print('game-info missing global ' + glo.name)
            continue
        dat = {
            'name': glo.name,
            'num': globname_to_num[glo.name],
            'sourceloc': sourceloc(tok=glo.gtok),
        }
        if glo.name in globname_to_vartype:
            dat['vartype'] = globname_to_vartype[glo.name]
        ls.append(dat)

    fl = open(filename, 'w')
    fl.write('window.gamedat_globals = ');
    json.dump(ls, fl)
    fl.write(';\n')
    fl.close()

def display_globals(zcode):
    load_gameinfo()
    if not sourcefile_binorder_map:
        print('ERROR: --showglob requires order info for SourceFile')
        return
    print('* Globals (%d), in what we hope is their correct order:' % len(zcode.globals),)
    ls = zcode.globals.copy()
    def func(glob):
        if glob.name == 'LOW-DIRECTION':
            return (100, 1)
        if glob.name == 'PREPOSITIONS':
            return (101, 1)
        if glob.name == 'ACTIONS':
            return (102, 1)
        if glob.name == 'PREACTIONS':
            return (103, 1)
        if glob.name == 'VERBS':
            return (104, 1)
        if glob.name == 'HERE':
            return (-99, 1)
        if glob.name == 'SCORE':
            return (-98, 1)
        if glob.name == 'MOVES':
            return (-97, 1)
        pos = glob.gtok.pos
        return (-sourcefile_binorder_map[pos[0]], -pos[1])
    ls.sort(key=func)
    for index, glob in enumerate(ls):
        print('Global %d %s' % (index, glob.name,))
    print('...check BIGFIX vs LOW-DIRECTION, and the following ones too')
    print('...any global defined twice will muck up the ordering')
    
def write_constants(filename, zcode):
    print('...writing constants data:', filename)
    ls = []
    for con in zcode.constants:
        dat = {
            'name': con.name,
            'value': con.value,
            'sourceloc': sourceloc(tok=con.ctok),
        }
        ls.append(dat)

    fl = open(filename, 'w')
    fl.write('window.gamedat_constants = ');
    json.dump(ls, fl, separators=(',', ':'))
    fl.write(';\n')
    fl.close()

def write_objects(filename, zcode, objdat):
    print('...writing object data:', filename)
    load_gameinfo()
    globalprop = propname_to_num.get('GLOBAL')
    ls = []
    map = {}
    for obj in zcode.objects:
        if obj.name not in objname_to_num:
            print('onum not found: %s "%s"' % (obj.name, obj.desc,))
            continue
        onum = objname_to_num[obj.name]
        if onum not in objdat.objmap:
            print('obj dump not found: %s' % (onum,))
            continue
        odump = objdat.objmap[onum]
        dat = {
            'onum':onum, 'name':obj.name, 'desc':obj.desc,
            'propaddr': odump.propaddr,
            'origparent': odump.parent,
            'sourceloc': sourceloc(tok=obj.objtok),
        }
        if obj.type == 'ROOM':
            dat['isroom'] = True
        if globalprop is not None and globalprop in odump.props:
            dat['scenery'] = odump.props[globalprop]
        ls.append(dat)
        map[dat['onum']] = dat

    for (onum, dat) in map.items():
        scenls = dat.get('scenery')
        if scenls:
            for val in scenls:
                idat = map[val]
                if 'iscenery' not in idat:
                    idat['iscenery'] = []
                idat['iscenery'].append(onum)
    
    fl = open(filename, 'w')
    fl.write('window.gamedat_objects = ');
    json.dump(ls, fl, separators=(',', ':'))
    fl.write(';\n')
    fl.close()

def compute_room_distances(filename, zcode):
    print('...writing room distances:', filename)
    load_gameinfo()
    map = zcode.mapconnections(mapextra_list)

    dat = {}

    try:
        for start in zcode.roomnames:
            dist = compute_distance_from(zcode, map, start)
            idist = dict([ (objname_to_num[key], val) for key, val in dist.items() ])
            dat[objname_to_num[start]] = idist
    except KeyError as ex:
        print('game-info missing rooms; cannot complete distances:', ex)
        
    fl = open(filename, 'w')
    fl.write('window.gamedat_distances = ');
    json.dump(dat, fl, separators=(',', ':'))
    fl.write(';\n')
    fl.close()

# This is cheesy, but we're going to trim down the error messages as
# much as possible.
notedmissing = set()
    
def compute_distance_from(zcode, map, fromroom):    
    reached = []
    reacheddist = {}
    todo = [ (fromroom, 0) ]
    while todo:
        (cur, dist) = todo.pop(0)
        if cur in reacheddist and reacheddist[cur] <= dist:
            continue
        reached.append(cur)
        reacheddist[cur] = dist
        for (dir, dest) in map[cur]:
            newdist = dist+1
            if dir == 'DISTANT':
                newdist = dist+1000
            todo.append( (dest, newdist) )

    if len(reached) != len(zcode.roomnames):
        missing = set(zcode.roomnames) - set(reached)
        newmissing = missing - notedmissing
        notedmissing.update(missing)
        newerr = ''
        if newmissing:
            if len(missing) == len(newmissing):
                newerr = ': %s' % ((' '.join(newmissing)),)
            else:
                newerr = ': above plus %s' % ((' '.join(newmissing)),)
        print('failed to reach all rooms from %s: missing %d%s' % (fromroom, len(missing), newerr))
    
    return reacheddist
    
