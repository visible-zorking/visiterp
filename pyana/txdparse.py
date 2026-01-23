import re

class String:
    @staticmethod
    def unescape(text, stripquotes=False):
        if stripquotes:
            if not (text.startswith('"') and text.endswith('"')):
                raise Exception('not quoted')
            text = text[ 1 : -1 ]
        text = text.replace('\\n', '\n')
        text = text.replace('\\t', '\t')
        text = text.replace('\\"', '\"')
        if '\\' in text:
            raise Exception('unknown escape')
        return text

    def __init__(self, addr, index, text, rtn=None):
        self.addr = addr
        self.index = index
        self.text = text
        self.rtn = rtn

    def __repr__(self):
        summary = self.text
        if len(summary) > 40:
            summary = summary[ : 40 ] + '...'
        rtnstr = ''
        if self.rtn:
            rtnstr = ' in rtn %X' % (self.rtn.addr,)
        return '<String %X%s: %r>' % (self.addr, rtnstr, summary,)

class Routine:
    def __init__(self, addr, argcount):
        self.addr = addr
        self.argcount = argcount
        self.opcodes = []
        self.istrings = []
        self.ismain = False
        self.action = None
        self.acverbs = []

    def __repr__(self):
        return '<Routine %X (%d args, %d opcodes)>' % (self.addr, self.argcount, len(self.opcodes),)

class TXDData:
    def __init__(self):
        self.routines = []
        self.strings = []
        self.istrings = []

    def readdump(self, filename):
        pat_routine = re.compile('^(Routine|Main routine) ([0-9a-f]+), ([0-9]+) local[s]?')
        pat_opcode = re.compile('^[ ]*([0-9a-f]+):[ ]+([A-Z0-9_]+)[ ]*(.*)$')
        pat_startrtns = re.compile('^\\[Start of code')
        pat_endrtns = re.compile('^\\[End of code')
        pat_text = re.compile('^([0-9a-f]+): S([0-9]+)[ ]+\"(.*)\"$')
        pat_starttext = re.compile('^\\[Start of text')
        pat_endtext = re.compile('^\\[End of text')
        pat_actiontype = re.compile('^[ ]*(Action|Pre-action) routine for:')
        pat_acverb = re.compile('^[ ]*verb: "([^"]*)"')
        pat_orphan = re.compile('^orphan code fragment:')
        with open(filename) as infl:
            rtn = None
            mode = None
            for ln in infl.readlines():
                ln = ln.rstrip()
                if pat_startrtns.match(ln):
                    mode = 'ROUTINES'
                    continue
                if pat_endrtns.match(ln):
                    mode = None
                    rtn = None
                    continue
                if pat_starttext.match(ln):
                    mode = 'TEXT'
                    continue
                if pat_endtext.match(ln):
                    mode = None
                    continue
                if mode == 'ROUTINES':
                    match = pat_routine.match(ln)
                    if match:
                        addr = int(match.group(2), 16)
                        argcount = int(match.group(3))
                        rtn = Routine(addr, argcount)
                        if match.group(1) == 'Main routine':
                            rtn.ismain = True
                        self.routines.append(rtn)
                        continue
                    match = pat_opcode.match(ln)
                    if match and rtn:
                        addr = int(match.group(1), 16)
                        rtn.opcodes.append(addr)
                        if match.group(2) in ('PRINT', 'PRINT_RET'):
                            text = String.unescape(match.group(3), stripquotes=True)
                            st = String(addr, None, text, rtn=rtn)
                            rtn.istrings.append(st)
                            self.istrings.append(st)
                        continue
                    match = pat_actiontype.match(ln)
                    if match and rtn:
                        rtn.action = match.group(1)
                        continue
                    match = pat_acverb.match(ln)
                    if match and rtn and rtn.action:
                        rtn.acverbs.append(match.group(1))
                        continue
                    match = pat_orphan.match(ln)
                    if match and rtn:
                        continue
                    if ln:
                        raise Exception('unrecognized line in routine: ' + ln)
                if mode == 'TEXT':
                    match = pat_text.match(ln)
                    if match:
                        addr = int(match.group(1), 16)
                        index = int(match.group(2))
                        text = String.unescape(match.group(3))
                        st = String(addr, index, text)
                        self.strings.append(st)


class Object:
    def __init__(self, num):
        self.num = num
        self.attrs = []
        self.propaddr = None
        self.desc = None
        self.parent = None
        self.sibling = None
        self.child = None
        self.props = {}

    def __repr__(self):
        return '<Object %d "%s">' % (self.num, self.desc,)

class ObjDumpData:
    def __init__(self):
        self.objects = []
        self.objmap = {}

    def readdump(self, filename):
        pat_objhead = re.compile('^[ ]*([0-9]+)[.][ ]*Attributes:(.*)')
        pat_propaddr = re.compile('^[ ]*Property address: ([0-9a-fA-F]+)')
        pat_tree = re.compile('^[ ]*Parent object:[ ]*([0-9]+)[ ]*Sibling object:[ ]*([0-9]+)[ ]*Child object:[ ]*([0-9]+)')
        pat_desc = re.compile('^[ ]*Description: "([^"]*)"')
        pat_prop = re.compile('^[ ]*\\[([0-9 ]+)\\]([ 0-9a-fA-F]*)')
        with open(filename) as infl:
            curobj = None
            for ln in infl.readlines():
                ln = ln.rstrip()
                match = pat_objhead.match(ln)
                if match:
                    curobj = Object(int(match.group(1)))
                    val = match.group(2).strip()
                    if val != 'None':
                        ls = val.split(',')
                        ls = [ int(val.strip()) for val in ls ]
                        curobj.attrs = ls
                    self.objects.append(curobj)
                    self.objmap[curobj.num] = curobj
                    continue
                match = pat_propaddr.match(ln)
                if match:
                    curobj.propaddr = int(match.group(1), 16)
                    continue
                match = pat_tree.match(ln)
                if match:
                    curobj.parent = int(match.group(1))
                    curobj.sibling = int(match.group(2))
                    curobj.child = int(match.group(3))
                    continue
                match = pat_desc.match(ln)
                if match:
                    curobj.desc = match.group(1)
                    continue
                match = pat_prop.match(ln)
                if match:
                    propnum = int(match.group(1).strip())
                    ls = match.group(2).split(' ')
                    ls = [ int(val, 16) for val in ls if val ]
                    curobj.props[propnum] = ls
                    continue
                
class DictWord:
    def __init__(self, num, addr, text, special, flags):
        self.num = num
        self.addr = addr
        self.text = text
        self.special = special
        self.flags = flags
    
    def __repr__(self):
        return '<DictWord %d "%s">' % (self.num, self.text,)

class DictDumpData:
    def __init__(self):
        self.words = []
    
    def readdump(self, filename):
        pat_word = re.compile(r'\[\s*([0-9]+)\] @ [$]([0-9a-f]+)\s+([^ ]+)\s+\[([0-9a-f ]+)\]([a-z<> ]*)')
        with open(filename) as infl:
            for ln in infl.readlines():
                match = pat_word.match(ln.strip())
                if match:
                    num = int(match.group(1))
                    addr = int(match.group(2), 16)
                    text = match.group(3)
                    text = text.replace('\\"', '\"')
                    flags = ''
                    for flag in match.group(5).split():
                        if flag == '<verb>':
                            flags += 'V'
                        elif flag == '<adj>':
                            flags += 'A'
                        elif flag == '<special>':
                            flags += 'S'
                        elif flag == '<noun>':
                            flags += 'N'
                        elif flag == '<prep>':
                            flags += 'P'
                        elif flag == '<dir>':
                            flags += 'D'
                        else:
                            raise Exception('bad flag ' + flag)
                    valls = match.group(4).split()
                    special = [ int(val, 16) for val in valls ]
                    self.words.append(DictWord(num, addr, text, special, flags))

class VerbGrammar:
    def __init__(self, num):
        self.num = num
        self.lines = []

    def __repr__(self):
        return '<VerbGrammar %d (%d)>' % (self.num, len(self.lines),)
                    
class Action:
    def __init__(self, num, preactionrtn, actionrtn):
        self.num = num
        self.preactionrtn = preactionrtn
        self.actionrtn = actionrtn

    def __repr__(self):
        return '<Action %d pre=%d rtn=%d>' % (self.num, self.preactionrtn, self.actionrtn)

class Preposition:
    def __init__(self, num, textls):
        self.num = num
        self.text = textls[0]
        self.synonyms = textls[ 1 : ]
    
    def __repr__(self):
        synstr = ''
        if self.synonyms:
            ls = [ '"'+val+'"' for val in self.synonyms ]
            synstr = ' (' + ', '.join(ls) + ')'
        return '<Preposition %d "%s"%s>' % (self.num, self.text, synstr)

class GrammarDumpData:
    def __init__(self):
        self.verbs = []
        self.actions = []
        self.prepositions = []

    def readdump(self, filename):
        pat_sect = re.compile('.*[*][*][*][*]\\s*([^*]+)\\s*[*][*][*][*]')
        pat_prep = re.compile('\\s*([0-9]+)[.]\\s+(.*)')
        pat_action = re.compile('\\s*([0-9]+)[.]\\s+([0-9a-f]+)\\s+([0-9a-f]+)\\s*verb:')
        pat_verbstart = re.compile('\\s*([0-9]+)[.]\\s+([0-9]+) (entry|entries), verb = (.*)')
        pat_verbline = re.compile('\\s*\\[([^]]+)\\]')
        
        section = None
        curverb = None
        lastcount = None
        
        with open(filename) as infl:
            for ln in infl.readlines():
                match = pat_sect.match(ln)
                if match:
                    val = match.group(1).strip()
                    if val == 'Parse tables':
                        section = 'parse'
                        continue
                    if val == 'Verb action routines':
                        section = 'action'
                        continue
                    if val == 'Prepositions':
                        section = 'prep'
                        continue
                    raise Exception('bad section')
                
                if section == 'prep':
                    match = pat_prep.match(ln)
                    if match:
                        prepnum = int(match.group(1))
                        prepls = []
                        ls = match.group(2).split(',')
                        for val in ls:
                            val = val.strip()
                            if val.startswith('synonyms ='):
                                val = val[ 10 : ].strip()
                            if not (val.startswith('"') and val.endswith('"')):
                                raise Exception('preposition is not quoted')
                            val = val[ 1 : -1 ]
                            prepls.append(val)
                        self.prepositions.append(Preposition(prepnum, prepls))
                        
                if section == 'action':
                    match = pat_action.match(ln)
                    if match:
                        actnum = int(match.group(1))
                        prefunc = int(match.group(2), 16)
                        func = int(match.group(3), 16)
                        self.actions.append(Action(actnum, prefunc, func))
                        
                if section == 'parse':
                    match = pat_verbstart.match(ln)
                    if match:
                        if curverb and lastcount != len(curverb.lines):
                            raise Exception('line count mismatch')
                        verbnum = int(match.group(1))
                        lastcount = int(match.group(2))
                        curverb = VerbGrammar(verbnum)
                        self.verbs.append(curverb)
                        continue
                    match = pat_verbline.match(ln)
                    if match:
                        val = match.group(1)
                        ls = val.split(' ')
                        bls = [ int(val.strip(), 16) for val in ls ]
                        if len(bls) != 8:
                            raise Exception('bad grammar line length')
                        curverb.lines.append(bls)
                        
