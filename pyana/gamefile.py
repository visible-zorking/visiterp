
class Gamefile:
    def __init__(self, filename):
        fl = open(filename, 'rb')
        self.mem = fl.read()
        fl.close()

        self.objtable = self.getword(0x0A)
        self.globaltable = self.getword(0x0C)
        
    def getbyte(self, addr):
        return self.mem[addr]

    def getword(self, addr):
        return self.mem[addr]*0x100 + self.mem[addr+1]
        
    def getglobal(self, index):
        return self.getword(self.globaltable+2*index)
    
    def getproptable(self, onum):
        objaddr = self.objtable + 31*2 + 9*(onum-1)
        propaddr = self.getword(objaddr + 7)
        
        textlen = self.getbyte(propaddr)
        addr = propaddr + (1 + 2*textlen)
        lastpnum = 65535

        res = []

        while True:
            val = self.getbyte(addr)
            if not val:
                break
            plen = (val >> 5) + 1
            pnum = (val & 0x1F)
            if pnum < lastpnum:
                values = self.mem[ addr+1 : addr+1+plen ]
                res.append( (pnum, values) )
                lastpnum = pnum
            addr += (1 + plen)

        res.reverse()
        return res
    
