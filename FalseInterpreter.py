from dataclasses import dataclass
import enum, sys

def Error(msg):
    print(msg)
    sys.exit(0)

import msvcrt
getch = msvcrt.getch

class cCommandEnum(enum.Enum):
    PUTINT  = enum.auto()
    PUTCHR  = enum.auto()
    DUP     = enum.auto()
    DROP    = enum.auto()
    SWAP    = enum.auto()
    ROT     = enum.auto()
    PICK    = enum.auto()
    PLUS    = enum.auto()
    MINUS   = enum.auto()
    MUL     = enum.auto()
    DIV     = enum.auto()
    NEG     = enum.auto()
    AND     = enum.auto()
    OR      = enum.auto()
    NOT     = enum.auto()
    GREAT   = enum.auto()
    EQUAL   = enum.auto()
    #lambda has seperate class
    EXEC    = enum.auto()
    COND    = enum.auto()
    WHILE   = enum.auto()
    PUTREF  = enum.auto()
    STORE   = enum.auto()
    FETCH   = enum.auto()
    READ    = enum.auto()
    WRITE   = enum.auto()
    STRING  = enum.auto()
    DEC     = enum.auto()
    FLUSH   = enum.auto()

CE = cCommandEnum
CM = {
    "$" : CE.DUP,
    "%" : CE.DROP,
    "\\" : CE.SWAP,
    "@" : CE.ROT,
    "ø" : CE.PICK,
    "+" : CE.PLUS,
    "-" : CE.MINUS,
    "*" : CE.MUL,
    "/" : CE.DIV,
    "_" : CE.NEG,
    "&" : CE.AND,
    "|" : CE.OR,
    "~" : CE.NOT,
    ">" : CE.GREAT,
    "=" : CE.EQUAL,
    "!" : CE.EXEC,
    "?" : CE.COND,
    "#" : CE.WHILE,
    ":" : CE.STORE,
    ";" : CE.FETCH,
    "^" : CE.READ,
    "," : CE.WRITE,
    "." : CE.DEC,
    "ß" : CE.FLUSH,
    }

class cFalseInterpreter:

    @dataclass
    class cCommand:
        xType : int
        xData : str = ""

    class cLambda:
        def __init__(self, xContent : list):
            self.xContent = xContent
        
        def __str__(self):
            return "cLambda({})".format(', '.join(map(str, self.xContent)))


    @staticmethod
    def IterGen(xRaw):
        for x in xRaw:
            yield x
    
        yield None
        Error("Error: Invaild syntax at end of program")
    
    @staticmethod
    def Parse(xInput):
        xFileIter = cFalseInterpreter.IterGen(xInput)
        xOutputBuffer = []
        
        
        xChar = next(xFileIter)
        while True:
            xTempBuffer = ""

            if xChar is None: break
        
            if  xChar == "'":       xOutputBuffer += [cFalseInterpreter.cCommand(xType = CE.PUTCHR, xData = next(xFileIter))]
            elif xChar.isalpha():   xOutputBuffer += [cFalseInterpreter.cCommand(xType = CE.PUTREF, xData = xChar)]
            elif xChar in CM:       xOutputBuffer += [cFalseInterpreter.cCommand(xType = CM[xChar])]
            
            elif xChar == '"':
                #eeehhh walrus operator aaaahhh 
                while ((xTemp:=next(xFileIter)) != '"'):
                    xTempBuffer += xTemp

                xOutputBuffer += [cFalseInterpreter.cCommand(xType = CE.STRING, xData = xTempBuffer)]
            
            elif xChar.isdigit():
                while True:
                    xTempBuffer += xChar
                    xChar = next(xFileIter)
                    if not(xChar and xChar.isdigit()): break                    

                xOutputBuffer += [cFalseInterpreter.cCommand(xType = CE.PUTINT, xData = int(xTempBuffer))]
                continue
            
            elif xChar == "[":
                xBracketLevel = 1
                while xBracketLevel:
                    xTempBuffer += xChar
                    xChar = next(xFileIter)
                    if xChar in "[]": xBracketLevel += {"[": 1, "]": -1}[xChar]
                    
                xOutputBuffer += [cFalseInterpreter.cLambda(cFalseInterpreter.Parse(xTempBuffer[1:]))]                
            
            elif xChar == "{":
                while next(xFileIter) != "}": pass
            
            xChar = next(xFileIter)
                    
                    
        return xOutputBuffer
            
    def __init__(self):
        self.xStack = []
        self.xMem   = [None for x in range(256)]
    
    #OH MY GOD I LOVE C
    def Memset(self, xIndex, xData):
        self.xMem[xIndex] = xData
    
    def Interpret(self, xTokens):        
        for xToken in xTokens:
            
            if type(xToken) is cFalseInterpreter.cLambda:
                self.xStack.append(xToken)
            
            elif xToken.xType == CE.WHILE:
                xDo     = self.xStack.pop().xContent 
                xCond   = self.xStack.pop().xContent
                
                cFalseInterpreter.Interpret(self, xCond)
                while(self.xStack.pop()):                    
                    cFalseInterpreter.Interpret(self, xDo)
                    cFalseInterpreter.Interpret(self, xCond)
            
            elif xToken.xType == CE.ROT:
                n0 = self.xStack.pop()
                n1 = self.xStack.pop()
                n2 = self.xStack.pop()
                
                self.xStack.append(n1)
                self.xStack.append(n2)
                self.xStack.append(n0)
                #self.xStack += [n1, n2, n0]
            
            else:
#    "^" : CE.READ,
#    "," : CE.WRITE,
#    "ß" : CE.FLUSH,
                {
                    CE.PUTINT   : (lambda: self.xStack.append(xToken.xData)),
                    CE.PUTCHR   : (lambda: self.xStack.append(ord(xToken.xData))),
                    CE.PUTREF   : (lambda: self.xStack.append(ord(xToken.xData) - 97)),
                    CE.STORE    : (lambda: self.Memset(self.xStack.pop(), self.xStack.pop())),
                    CE.FETCH    : (lambda: self.xStack.append(self.xMem[self.xStack.pop()])),

                    CE.DUP  : (lambda: self.xStack.append(self.xStack[-1])),
                    CE.DROP : (lambda: self.xStack.pop()),
                    CE.SWAP : lambda: (self.xStack.append(self.xStack[-2]), self.xStack.pop(-3)),
                    CE.PICK : lambda: None,
                    CE.PLUS : (lambda: self.xStack.append(self.xStack.pop(-2) + self.xStack.pop(-1))),
                    CE.MINUS: (lambda: self.xStack.append(self.xStack.pop(-2) - self.xStack.pop(-1))),
                    CE.MUL  : (lambda: self.xStack.append(self.xStack.pop(-2) * self.xStack.pop(-1))),
                    CE.DIV  : (lambda: self.xStack.append(self.xStack.pop(-2) / self.xStack.pop(-1))),
                    CE.NEG  : (lambda: self.xStack.append(-self.xStack.pop())),
                    CE.AND  : (lambda: self.xStack.append(self.xStack.pop() & self.xStack.pop())),
                    CE.OR   : (lambda: self.xStack.append(self.xStack.pop() | self.xStack.pop())),
                    CE.NOT  :  lambda: self.xStack.append(1 if self.xStack.pop() == 0 else 0),
                    CE.GREAT: (lambda: self.xStack.append(1 if self.xStack.pop(-2) >  self.xStack.pop(-1) else 0)),
                    CE.EQUAL: (lambda: self.xStack.append(1 if self.xStack.pop(-2) == self.xStack.pop(-1) else 0)),
                    CE.EXEC : (lambda: self.Interpret(self.xStack.pop().xContent)),
                    CE.COND : (lambda: self.Interpret(self.xStack.pop(-1).xContent) if self.xStack.pop(-2) else self.xStack.pop(-1)),
                    
                    CE.DEC      : (lambda: print(self.xStack.pop(), end = "")),
                    CE.STRING   : (lambda: print(xToken.xData, end = "")),
                    CE.READ     : (lambda: self.xStack.append(ord(getch()))),
                    CE.WRITE    : (lambda: print(chr(self.xStack.pop()), end = "")),
                    
                }[xToken.xType]()
            
            #print(xToken, "\t", self.xStack)
               
    @staticmethod
    def Main(xFile):
        xTokens = cFalseInterpreter.Parse(xFile)
        cFalseInterpreter().Interpret(xTokens)

if __name__ == '__main__':
    with open(sys.argv[1], "r") as xFile:
        cFalseInterpreter.Main(xFile.read())