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
        
        #takes list of tuples, converts to list of cS1Inst instances
        @staticmethod
        def List2Self(xList):
            return [cFalseCompiler.cS1Inst(*list(x)) for x in xList]
        
        def __str__(self):
            return f"{self.xOp} {'' if self.xArg is None else self.xArg}".format()

    class cS1InstList:
        def __init__(self, x = []):
            self.xContent : List[cS1Inst] = x[:]
            
        @staticmethod
        def List2Self(xList): 
            return cFalseCompiler.cS1InstList(cFalseCompiler.cS1Inst.List2Self(xList))
        
        def __iadd__(self, xOther):
            self.xContent += xOther.xContent
            return self
        
        def __add__(self, xOther):
            return cFalseCompiler.cS1InstList(self.xContent + xOther.xContent)
        
        def __getitem__(self, xIndex):
            return self.xContent[xIndex]
        
        def __len__(self):
            return len([x for x in self.xContent if x.xOp != "lab"])
    
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
        self.xTempLabelGen = self.TempLabelGen()
        self.xInstList = self.cS1InstList.List2Self([
                ("set", xCallStackOrigin),
                ("sRD", xCallStackIndex),
                ("got", "main"),
                ("lab", "mul"),
                ("clr",),
                ("sAD", xTempSpace + 2),
                ("pla",),
                ("sAD", xTempSpace + 10),
                ("pla",),
                ("sAD", xTempSpace + 0),
                ("pla",),
                ("sAD", xTempSpace + 1),
                ("lab", "muloop"),
                ("lDA", xTempSpace + 0),
                ("jm0", "mulexit"),
                ("set", 1),
                ("sub",),
                ("sAD", xTempSpace + 0),
                ("lDA", xTempSpace + 2),
                ("lDR", xTempSpace + 1),
                ("add",),
                ("sAD", xTempSpace + 2),
                ("got", "muloop"),
                ("lab", "mulexit"),
                ("lDA", xTempSpace + 2),
                ("pha",),
                ("lDA", xTempSpace + 10),
                ("pha",),
                ("ret",),
            ])
        self.xLabelTracker = []
                    
    #takes lambda allocates it in memory and returns reference (ir value)
    def AllocLambda(self, xLambdaCode):
        #each instruction takes two word of memory, that's why the *2 is needed
        xOrigin = len(self.xInstList) * 2
        
        self.xInstList += xLambdaCode + self.cS1InstList([
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
                
            
            ])
        
        return xOrigin

    def TempLabelGen(self):
        xId2Lab = lambda x: f"temp{x}".format(x)
        xId = 0
        while True:
            while xId2Lab(xId) in self.xLabelTracker:
                xId += 1
                
            xLab = xId2Lab(xId)
            self.xLabelTracker.append(xLab)
            yield xLab

    #if xDoLambda is True this returns the origin address of the allocated lambda
    #if xDoLmabda is False this returns the self.xInstList
    def Compile(self, xTokens, xDoLambda = False): 
        #short handle
        cS1Inst = self.cS1Inst
        xInstBuffer = self.cS1InstList()
        """    
    "ø" : CE.PICK,
    
    "*" : ,
    "/" : CE.DIV,
    "_" : CE.NEG,
    "&" : CE.AND,
    "|" : CE.OR,
    "~" : ,
    ">" : ,
    "=" : ,
    "!" : ,
    "?" : ,
    "#" : ,
    ":" : ,
    ";" : ,
    "^" : CE.READ,
    "," : ,
    "." : ,
    "ß" : CE.FLUSH,
"""
        for xTokenIter in xTokens:
            if type(xTokenIter) is cFalseCompiler.cLambda:
                xInstBuffer += cFalseCompiler.cS1InstList([
                    cS1Inst("clr"),
                    cS1Inst("set", self.Compile(xTokenIter.xContent, xDoLambda=True)),
                    cS1Inst("add"),
                    cS1Inst("pha"),
                ])

            else:                
                xTempLab = [next(self.xTempLabelGen) for x in range(10)]
                xInstBuffer += cFalseCompiler.cS1InstList({
                    
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
                    CE.PUTREF : [
                            cS1Inst("clr"),
                            cS1Inst("set", ord(xTokenIter.xData) - 97 if type(xTokenIter.xData) is str and len(xTokenIter.xData) == 1 else ""),
                            cS1Inst("add"),
                            cS1Inst("pha"),                        
                        ],
                    CE.STORE : [
                            cS1Inst("pla"),
                            cS1Inst("sAD", xTempSpace + 0),
                            cS1Inst("pla"),
                            cS1Inst("sAP", xTempSpace + 0),
                        ],
                    CE.FETCH : [
                            cS1Inst("pla"),
                            cS1Inst("sAD", xTempSpace + 0),
                            cS1Inst("lPA", xTempSpace + 0),
                            cS1Inst("pha")
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
                            #push current ir as return address (+7 to reference the next command)
                            cS1Inst("set", (len(self.xInstList) + len(xInstBuffer) + 7) * 2), #1
                            cS1Inst("sRP", xCallStackIndex),    #2

                            #inc stack ptr
                            cS1Inst("lDA", xCallStackIndex),    #3
                            cS1Inst("set", 1),                  #4
                            cS1Inst("add"),                     #5
                            cS1Inst("sAD", xCallStackIndex),    #6
                            
                            #use ret to jump to the lambda origin address ("I LOVE ABUSING S1ASM AND IM NOT MENTALLY ILL" - Jerma985)
                            cS1Inst("ret"),                     #7
                        ],
                    CE.PLUS : [
                            cS1Inst("pla"),
                            cS1Inst("sAD", xTempSpace),
                            cS1Inst("lDR", xTempSpace),
                            cS1Inst("pla"),
                            cS1Inst("add"),
                            cS1Inst("pha"),                            
                        ],
                    CE.MINUS : [
                            cS1Inst("pla"),
                            cS1Inst("sAD", xTempSpace),
                            cS1Inst("lDR", xTempSpace),
                            cS1Inst("pla"),
                            cS1Inst("sub"),
                            cS1Inst("pha"),                            
                        ],
                    CE.MUL : [
                            cS1Inst("jmS", "mul"),
                        ],
                    CE.NOT : [
                            cS1Inst("pla"),
                            cS1Inst("not"),
                            cS1Inst("pha"),
                        ],
                    CE.GREAT : [
                            cS1Inst("pla"),
                            cS1Inst("sAD", xTempSpace + 0),
                            cS1Inst("lDR", xTempSpace + 0),
                            cS1Inst("pla"),
                            cS1Inst("jmG", xTempLab[0]),
                            cS1Inst("clr"),
                            cS1Inst("got", xTempLab[1]),
                            cS1Inst("lab", xTempLab[0]),
                            cS1Inst("clr"),
                            cS1Inst("set", xIntLimit),
                            cS1Inst("add"),
                            cS1Inst("lab", xTempLab[1]),
                            cS1Inst("pha"),
                        ],
                    CE.EQUAL : [
                            cS1Inst("pla"),
                            cS1Inst("sAD", xTempSpace + 0),
                            cS1Inst("lDR", xTempSpace + 0),
                            cS1Inst("pla"),
                            cS1Inst("jmA", xTempLab[0]),
                            cS1Inst("clr"),
                            cS1Inst("got", xTempLab[1]),
                            cS1Inst("lab", xTempLab[0]),
                            cS1Inst("clr"),
                            cS1Inst("set", xIntLimit),
                            cS1Inst("add"),
                            cS1Inst("lab", xTempLab[1]),
                            cS1Inst("pha"),
                        ],                    
                    CE.COND : [
                            cS1Inst("pla"),                     #1
                            cS1Inst("sAD", xTempSpace + 0),     #2
                            cS1Inst("pla"),                     #3     
                            cS1Inst("jm0", xTempLab[0]),        #4
                            cS1Inst("lDA", xTempSpace + 0),     #5
                            cS1Inst("pha"),                     #6
                            cS1Inst("set", (len(self.xInstList) + len(xInstBuffer) + 13) * 2), #7
                            cS1Inst("sRP", xCallStackIndex),    #8
                            cS1Inst("lDA", xCallStackIndex),    #9
                            cS1Inst("set", 1),                  #10
                            cS1Inst("add"),                     #11
                            cS1Inst("sAD", xCallStackIndex),    #12                     
                            cS1Inst("ret"),                     #13
                            cS1Inst("lab", xTempLab[0]),        #(doesn't count because lab)
                        ],
                    CE.WHILE : [
                            cS1Inst("pla"),                     #1
                            cS1Inst("sAD", xTempSpace + 0),     #2
                            cS1Inst("pla"),                     #3
                            cS1Inst("sAD", xTempSpace + 1),     #4
                            
                            cS1Inst("lab", xTempLab[0]),        #5
                            cS1Inst("lDA", xTempSpace + 0),     #6
                            cS1Inst("pha"),                     #7
                            
                            cS1Inst("set", (len(self.xInstList) + len(xInstBuffer) + 14) * 2), #8
                            cS1Inst("sRP", xCallStackIndex),    #9
                            cS1Inst("lDA", xCallStackIndex),    #10
                            cS1Inst("set", 1),                  #11
                            cS1Inst("add"),                     #12
                            cS1Inst("sAD", xCallStackIndex),    #13
                            cS1Inst("ret"),                     #14

                            cS1Inst("jm0", xTempLab[1]),        #15
                            cS1Inst("lDA", xTempSpace + 1),     #16
                            cS1Inst("pha"),                     #17    
                            
                            cS1Inst("set", (len(self.xInstList) + len(xInstBuffer) + 24) * 2), #18
                            cS1Inst("sRP", xCallStackIndex),    #19
                            cS1Inst("lDA", xCallStackIndex),    #20
                            cS1Inst("set", 1),                  #21
                            cS1Inst("add"),                     #22
                            cS1Inst("sAD", xCallStackIndex),    #23
                            cS1Inst("ret"),                     #24
                            
                            cS1Inst("got", xTempLab[0]),
                            cS1Inst("lab", xTempLab[1]),


                        
                        ],
                    CE.DEC : [
                            cS1Inst("pla"),
                            cS1Inst("sAD", xTempSpace + 0),
                            cS1Inst("out", xTempSpace + 0),
                        
                        ],
                    
                    
                    }[xTokenIter.xType])
                
                
        
        if xDoLambda:   return self.AllocLambda(xInstBuffer)
        else:           return self.xInstList + self.cS1InstList([cS1Inst("lab", "main")]) + xInstBuffer + self.cS1InstList([cS1Inst("brk")])
            
               
    @staticmethod
    def Main(xFile):
        xTokens = cFalseCompiler.Parse(xFile)
        #print("\n".join(map(str, xTokens)))
        return cFalseCompiler().Compile(xTokens)

if __name__ == '__main__':
    with open(sys.argv[1], "r") as xFile:
        xOutInsts = cFalseCompiler.Main(xFile.read())
            
    with open("build.s1", "w") as xFile:
        xFile.write("\n".join(map(str, xOutInsts)))
        