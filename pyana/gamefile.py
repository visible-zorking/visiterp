
class Gamefile:
    def __init__(self, filename):
        fl = open(filename, 'rb')
        self.mem = fl.read()
        fl.close()

        self.globaladdr = self.getword(0x0C)
        
    def getbyte(self, addr):
        return self.mem[addr]

    def getword(self, addr):
        return self.mem[addr]*0x100 + self.mem[addr+1]
        
    def getglobal(self, index):
        return self.getword(self.globaladdr+2*index)
    
