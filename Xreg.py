import xml.etree.ElementTree as ET 
import gdb
import struct
'''
peripherals(name, base address, description, registers(dictionary), size)
registsters(name, description, offset, reset value)

It'd better tells difference between the reset value

bugs
1. GPIOC, D, E, H... can't derive from GPIOB
2.
'''

class XregParser():
    def __init__(self):
        self.__isSvdLoaded = False

    def load_svd_file(self, filePath):
        self.__tree = ET.parse(filePath)
        self.__root = self.__tree.getroot()
        self.__periphDict = self.generate_periph_dict()
        self.__isSvdLoaded = True
        print "[Xreg] Load %s." % filePath

    def print_periph_dict(self):
        if self.__isSvdLoaded == True:
            print self.__periphDict
        else:
            print "[Xreg] SVD file has not been loaded."

    def generate_periph_dict(self):
        if self.__isSvdLoaded == True: # Avoid repeated load
            return self.__periphDict

        periphDict = dict()
        periphName = ""
        regName = ""
        for p in self.__root.iter("peripheral"):
            for i in p.findall("name"):
                periphName = i.text
                periphDict[periphName] = dict()
            for i in p.findall("description"):
                periphDict[periphName]["description"] = i.text
            for i in p.findall("baseAddress"):
                periphDict[periphName]["baseAddress"] = int(i.text, 0)
            for i in p.findall("addressBlock"):
                for j in i.findall("size"):
                    periphDict[periphName]["size"] = int(j.text, 0)
            periphDict[periphName]["register"] = dict()
            for r in p.iter("register"):
                for i in r.findall("name"):
                    regName = i.text
                    periphDict[periphName]["register"][regName] = dict()
                for i in r.findall("description"):
                    periphDict[periphName]["register"][regName]["description"] = i.text
                for i in r.findall("addressOffset"):
                    periphDict[periphName]["register"][regName]["addressOffset"] = int(i.text, 0)
                for i in r.findall("resetValue"):
                    periphDict[periphName]["register"][regName]["resetValue"] = int(i.text, 0)
        print "[Xreg] Periphal dictionary generated."
        return periphDict
    
    def get_reg_addr(self, periph, reg):
        return self.__periphDict[periph]["register"][reg]["addressOffset"] + self.__periphDict[periph]["baseAddress"]

    def is_reg_modified(self, periph, reg):
        pass

    def get_periph_description(self, periph, reg=None):
        if reg == None:
            return self.__periphDict[periph]["description"]
        else:
            return self.__periphDict[periph]["register"][reg]["description"]

    def print_reg(self, periph, val, reg=None):
        # if reg == None:
        print "0x%08x" % val

xp = XregParser()

class XregPrefixCommand(gdb.Command):
    "bla bla"
    def __init__(self):
        super(XregPrefixCommand, self).__init__("xreg", gdb.COMMAND_SUPPORT, gdb.COMPLETE_NONE, True)

class XregLoadCommand(gdb.Command):
    "bla bla"
    def __init__(self):
        super(XregLoadCommand, self).__init__("xreg load", gdb.COMMAND_SUPPORT, gdb.COMPLETE_FILENAME)

    def invoke(self, arg, from_tty):
        "load a svd file???"
        xp.load_svd_file(arg)

class XregShowCommand(gdb.Command):
    def __init__(self):
        super(XregShowCommand, self).__init__("xreg show", gdb.COMMAND_SUPPORT)

    def invoke(self, arg, from_tty):
        p, r = arg.split('_')
        addr = xp.get_reg_addr(p, r)
        buff = gdb.inferiors()[0].read_memory(addr, 4)
        val = struct.unpack("I", buff)[0]
        xp.print_reg(arg, val)
        
    def complete(self, arg, from_tty): # Auto-completion
        pass

XregPrefixCommand()
XregLoadCommand()
XregShowCommand()

if __name__ == "__main__":
    pass
    # xp = XregParser()
    # xp.load_svd_file("STM32L053x.svd")
    # print("0x%08x" % xp.get_reg_addr("TIM2", "CR2"))
    # xp.print_periph_dict()