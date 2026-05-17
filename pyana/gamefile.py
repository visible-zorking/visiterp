
class Gamefile:
    def __init__(self, filename):
        fl = open(filename, 'rb')
        self.mem = fl.read()
        fl.close()

    def getbyte(self, addr):
        return self.mem[addr]

    def getword(self, addr):
        return self.mem[addr]*0x100 + self.mem[addr+1]
        
