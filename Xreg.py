import xml.etree.ElementTree as ET 
import gdb
import struct
'''
TODO:
1. GPIOC, D, E, H... can't derive from GPIOB
2. Design a command to tells how the register is modified.

peripDict structure
{
    "PERIP1": {
        "baseAddress": number,
        "description": string,
        "size": number, # size in bit
        "registerList": [REG1, REG2, ...]
        "register": {
            "REG1": {
                "description": string,
                "addressOffset": number,
                "resetValue": number,
            }
            "REG2": {
                ...
            }
        }
    }
}
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
                try:
                    periphDict[periphName] = periphDict[p.attrib["derivedFrom"]] # Derived from another peripheral
                except KeyError:
                    periphDict[periphName] = dict()

                # if p.attrib["derivedFrom"] == None:
                #     periphDict[periphName] = dict()
                # else:
                #     print p.attrib["derivedFrom"]
                #     periphDict[periphName] = periphDict[p.attrib["derivedFrom"]] # Derived from another peripheral
            for i in p.findall("description"):
                periphDict[periphName]["description"] = i.text
            for i in p.findall("baseAddress"):
                periphDict[periphName]["baseAddress"] = int(i.text, 0)

            periphDict[periphName]["register"] = dict()
            periphDict[periphName]["registerList"] = []
            for r in p.iter("register"):
                for i in r.findall("name"):
                    regName = i.text
                    periphDict[periphName]["registerList"].append(regName)
                    periphDict[periphName]["register"][regName] = dict()
                for i in r.findall("description"):
                    periphDict[periphName]["register"][regName]["description"] = i.text
                for i in r.findall("addressOffset"):
                    periphDict[periphName]["register"][regName]["addressOffset"] = int(i.text, 0)
                for i in r.findall("resetValue"):
                    periphDict[periphName]["register"][regName]["resetValue"] = int(i.text, 0)
        print "[Xreg] Periphal dictionary generated."
        return periphDict
    
    def get_reg_addr(self, periph, reg=None):
        if reg == None:
            return self.__periphDict[periph]["baseAddress"]
        else:
            return self.__periphDict[periph]["register"][reg]["addressOffset"] + self.__periphDict[periph]["baseAddress"]

    def show_changes(self, periph, reg):
        pass

    def get_periph_description(self, periph, reg=None):
        if reg == None:
            return self.__periphDict[periph]["description"]
        else:
            return self.__periphDict[periph]["register"][reg]["description"]

    def print_reg(self, periph, val, reg=None):
        if reg != None:
            print "0x%08x" % val
        else:
            for i in range(self.get_reg_count(periph)):
                print "%s = 0x%08x" % (self.__periphDict[periph]["registerList"][i], val[i])
    
    @property
    def periph_list(self):
        return sorted(self.__periphDict.keys())

    def register_list(self, periph):
        return self.__periphDict[periph]["registerList"]
    
    def get_reg_count(self, periph):
        return len(self.__periphDict[periph]["registerList"]) 

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
        if '_' in arg:
            p, r = arg.split('_')
            regCount = 1
        else:
            p, r = arg, None
            regCount = xp.get_reg_count(p)
        addr = xp.get_reg_addr(p, r)
        buff = gdb.inferiors()[0].read_memory(addr, 4*regCount)
        val = struct.unpack("I"*regCount, buff)
        xp.print_reg(p, val, reg=r)
        
    def complete(self, arg, from_tty): # Auto-completion
        pass

class XregListCommand(gdb.Command):
    def __init__(self):
        super(XregListCommand, self).__init__("xreg list", gdb.COMMAND_SUPPORT)

    def invoke(self, arg, from_tty):
        if arg == "":
            for p in xp.periph_list:
                print "[Xreg] %s" % p
        elif arg in xp.periph_list:
            for r in xp.register_list(arg):
                print "[Xreg] %s" % r
        else:
            print "[Xreg] Given peripheral doesn't exist"

XregPrefixCommand()
XregLoadCommand()
XregShowCommand()
XregListCommand()

if __name__ == "__main__":
    pass