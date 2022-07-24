from dataclasses import dataclass
import enum, sys

def Error(msg):
    print(msg)
    sys.exit(0)

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

xIntLimit = int("1" * 16, 2)
#origin address to store temps
xTempSpace = 10000

xCallStackIndex  = 19999
xCallStackOrigin = 20000


class cFalseCompiler:
    @dataclass
    class cCommand:
        xType : int
        xData : str = ""

    class cS1Inst:
        def __init__(self, *xInp):
            (self.xOp, self.xArg) = tuple(map(str, xInp)) + ((None,) if len(xInp) < 2 else ())
        
        def __str__(self):
            return f"{self.xOp} {self.xArg}".format()
        
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
        xFileIter = cFalseCompiler.IterGen(xInput)
        xOutputBuffer = []
        
        
        xChar = next(xFileIter)
        while True:
            xTempBuffer = ""

            if xChar is None: break
        
            if  xChar == "'":       xOutputBuffer += [cFalseCompiler.cCommand(xType = CE.PUTCHR, xData = next(xFileIter))]
            elif xChar.isalpha():   xOutputBuffer += [cFalseCompiler.cCommand(xType = CE.PUTREF, xData = xChar)]
            elif xChar in CM:       xOutputBuffer += [cFalseCompiler.cCommand(xType = CM[xChar])]
            
            elif xChar == '"':
                #eeehhh walrus operator aaaahhh 
                while ((xTemp:=next(xFileIter)) != '"'):
                    xTempBuffer += xTemp

                xOutputBuffer += [cFalseCompiler.cCommand(xType = CE.STRING, xData = xTempBuffer)]
            
            elif xChar.isdigit():
                while True:
                    xTempBuffer += xChar
                    xChar = next(xFileIter)
                    if not(xChar and xChar.isdigit()): break                    

                xOutputBuffer += [cFalseCompiler.cCommand(xType = CE.PUTINT, xData = int(xTempBuffer))]
                continue
            
            elif xChar == "[":
                xBracketLevel = 1
                while xBracketLevel:
                    xTempBuffer += xChar
                    xChar = next(xFileIter)
                    if xChar in "[]": xBracketLevel += {"[": 1, "]": -1}[xChar]
                    
                xOutputBuffer += [cFalseCompiler.cLambda(cFalseCompiler.Parse(xTempBuffer[1:]))]                
            
            elif xChar == "{":
                while next(xFileIter) != "}": pass
            
            xChar = next(xFileIter)
                    
                    
        return xOutputBuffer        

    def __init__(self):
        self.xInstList = [self.cS1Inst("got", "main")]
    
    #takes lambda allocates it in memory and returns reference (ir value)
    def AllocLambda(self, xLambdaCode):
        #each instruction takes two word of memory, that's why the *2 is needed
        xOrigin = len(self.xInstList) * 2
        
        self.xInstList += xLambdaCode + [
                #dec stack ptr
                self.cS1Inst("lDA", xCallStackIndex),
                self.cS1Inst("set", 1),
                self.cS1Inst("sub"),
                self.cS1Inst("sAD", xCallStackIndex),
                
                #pull from call stack push to main stack, then jump
                self.cS1Inst("clr"),
                self.cS1Inst("lPA", xCallStackIndex),
                self.cS1Inst("sRP", xCallStackIndex),
                self.cS1Inst("pha"),
                self.cS1Inst("ret"),
                
            
            ]
        
        return xOrigin

    #if xDoLambda is True this returns the origin address of the allocated lambda
    #if xDoLmabda is False this returns the self.xInstList
    def Compile(self, xTokens, xDoLambda = False): 
        #short handle
        cS1Inst = self.cS1Inst
        xInstBuffer = []
        """
               : (lambda: self.xStack.append(xToken.xData)),
            CE.PUTREF   : (lambda: self.xStack.append(ord(xToken.xData) - 97)),
    
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
    "!" : ,
    "?" : CE.COND,
    "#" : CE.WHILE,
    ":" : CE.STORE,
    ";" : CE.FETCH,
    "^" : CE.READ,
    "," : ,
    "." : CE.DEC,
    "ß" : CE.FLUSH,
"""
        for xTokenIter in xTokens:
            print(xTokenIter)
            if type(xTokenIter) is cFalseCompiler.cLambda:
                xInstBuffer += [
                        cS1Inst("clr"),
                        cS1Inst("set", self.Compile(xTokenIter.xContent, xDoLambda=True)),
                        cS1Inst("add"),
                        cS1Inst("pha"),
                    ]
            
            else:
                xInstBuffer += {
                    
                    CE.STRING : sum([[
                            cS1Inst("clr"),
                            cS1Inst("set", ord(x)),
                            cS1Inst("add"),
                            cS1Inst("putstr")]
                            for x in xTokenIter.xData
                        ], []) if type(xTokenIter.xData) is str else [],
                    CE.PUTCHR : [
                            cS1Inst("clr"),
                            cS1Inst("set", ord(xTokenIter.xData) if type(xTokenIter.xData) is str and len(xTokenIter.xData) == 1 else ""),
                            cS1Inst("add"),
                            cS1Inst("pha"),
                        ],
                    CE.PUTINT : [
                            cS1Inst("clr"),
                            cS1Inst("set", int(xTokenIter.xData) if type(xTokenIter.xData) is int else ""),
                            cS1Inst("add"),
                            cS1Inst("pha"),
                        ],
                    CE.DUP : [
                            cS1Inst("pla"),
                            cS1Inst("pha"),
                            cS1Inst("pha"),
                        ],
                    CE.DROP : [
                            cS1Inst("pla"),
                        ],
                    CE.SWAP : [
                            cS1Inst("pla"), cS1Inst("sAD", xTempSpace + 0),
                            cS1Inst("pla"), cS1Inst("sAD", xTempSpace + 1),
                            cS1Inst("lDA", xTempSpace + 0), cS1Inst("pha"),
                            cS1Inst("lDA", xTempSpace + 1), cS1Inst("pha"),
                        ],
                    CE.ROT : [
                            cS1Inst("pla"), cS1Inst("sAD", xTempSpace + 0),
                            cS1Inst("pla"), cS1Inst("sAD", xTempSpace + 1),
                            cS1Inst("pla"), cS1Inst("sAD", xTempSpace + 2),
                            cS1Inst("lDA", xTempSpace + 1), cS1Inst("pha"),
                            cS1Inst("lDA", xTempSpace + 2), cS1Inst("pha"),
                            cS1Inst("lDA", xTempSpace + 0), cS1Inst("pha"),
                        ],
                    
                    CE.WRITE : [
                            cS1Inst("pla"),
                            cS1Inst("putstr"),
                        ],
                    CE.EXEC : [
                            #push current ir as return address (+1 to reference the next command)
                            cS1Inst("set", (len(self.xInstList) + len(xInstBuffer) + 1) * 2),
                            cS1Inst("sRP", xCallStackIndex),

                            #inc stack ptr
                            cS1Inst("lDA", xCallStackIndex),
                            cS1Inst("set", 1),
                            cS1Inst("add"),
                            cS1Inst("sAD", xCallStackIndex),
                            
                            #use ret to jump to the lambda origin address ("I LOVE ABUSING S1ASM AND IM NOT MENTALLY ILL" - Jerma985)
                            cS1Inst("ret"),
                        ],
                    
                    
                    }[xTokenIter.xType]
                
            
        if xDoLambda:   return self.AllocLambda(xInstBuffer)
        else:           return self.xInstList + [cS1Inst("lab", "main")] + xInstBuffer
            
               
    @staticmethod
    def Main(xFile):
        xTokens = cFalseCompiler.Parse(xFile)
        return cFalseCompiler().Compile(xTokens)

if __name__ == '__main__':
    with open(sys.argv[1], "r") as xFile:
        xOut = cFalseCompiler.Main(xFile.read())
    
    print("\n".join(map(str, xOut)))
        
    #with open("build.s1", "r") as xFile:
    #    xFile.write(xOut)
        