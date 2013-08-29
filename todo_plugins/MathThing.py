#!/usr/bin/python
import collections
import re
import tokenize as tokenizer
import token
import StringIO

#Debugging Decorators {{{
depth = 1 
def tokenizeDebug(func):
#    return func
    def nfunc(self,tokens):
        global depth
        print tokens,
        print ("  |"*depth)[:-1]+">",
        print self.__class__.__name__

        depth += 1
        try:
            ret = func(self,tokens)
        except Exception as e:
            depth -=1
            print tokens, 
            print ("  |"*depth)[:-1]+"X", e
            raise
        depth -=1
        print tokens,
        print ("  |"*depth)[:-1]+"<",
        print ret

        return ret
    return nfunc

def evalDebug(func):
#    return func
    def nfunc(self,scope):
        global depth

        print ("  |"*depth)[:-1]+">", self.__class__.__name__
        depth += 1
        try:
            ret = func(self,scope)
        except Exception as e:
            depth -= 1
            print ("  |"*depth)[:-1]+"X",e
            raise
        depth -= 1
        print ("  |"*depth)[:-1]+"<",ret
        return ret
    return nfunc

def breakOnException(func):
    return func
    def nfunc(*a,**b):
        try:
            return func(*a,**b)
        except Exception as e:
            print e
            import pdb; pdb.set_trace()
            func(*a,**b)
            raise
    return nfunc        
#}}}

#Tokenizer {{{
Token = collections.namedtuple("Token",["ttype","tval","start","end","lineno"])


class Tokenizer(object):
    def __init__(self, line):
        self.tokens = []
        self.state = []
        self.pos = 0
        self.skipTokens = [token.NEWLINE,token.INDENT,token.ENDMARKER,token.DEDENT,token.ERRORTOKEN,54]
        try:
            tokenizer.tokenize(StringIO.StringIO(line).readline, self.consumer)
        except:pass
        self.tokens.append(Token(0, "EOL", len(line),len(line)+1, line))

    def consumer(self, ttype, tval, start, end, lineno):
        if ttype in self.skipTokens:
            return
        self.tokens.append(Token(ttype, tval, start[1], end[1], lineno))

    def get(self):
        if self.pos == len(self.tokens):
            raise TokenizerException("Ran out of tokens.")
        
        token = self.tokens[self.pos]
#        print self,"get",token.tval
        self.pos += 1
        return token

    def unget(self):
        if self.pos == 0:
            raise TokenizerException("Tried to return tokens with nothing to return")
        self.pos -= 1
#        print self,"Unget"
        return self

    def pushState(self):
        self.state.append(self.pos)
        return self

    def popState(self):
        self.pos = self.state.pop()
        return self

    def discardState(self):
        self.state.pop()
        return self

    def __str__(self):
        vals = map(lambda tok:tok.tval,self.tokens) + [""]
        vals[self.pos] = "[{}]".format(vals[self.pos])
        return "{ "+" ".join(vals)+" }"
#}}}

class TokenizerException(Exception):pass
class ParseException(Exception):pass
class EvaluatorException(Exception):pass
class ExpressionNode(object):pass

#Operations {{{
@breakOnException
def nonZero(a):
    return bool(a)

@breakOnException
def uneg(a):
#    print "uneg",a
    return -1*a

@breakOnException
def power(a, b):
#    print "pow",a,b
    return a**b

@breakOnException
def mul(a, b):
#    print "mul",a,b
    if type(b) is list:
        return map(lambda item:mul(a,item),b)
    return a*b

@breakOnException
def div(a, b):
#    print "div",a,b
    return a/b

@breakOnException
def mod(a, b):
#    print "mod",a,b
    return a%b

@breakOnException
def add(a, b):
#    print "add",a,b
    if type(a) == list and type(b) != list:
        idx = int(b)
        if idx < 0 or idx >= len(a):
            raise EvaluatorException("Index out of bounds: "+str(a)+" at "+int(idx))
        return a[idx]
    return a+b

@breakOnException
def sub(a, b):
#    print "sub",a,b
    return a-b

@breakOnException
def call(a, b, scope):
#    print "call",a,b,"Scope:",scope.keys()
    trailer = b.evaluate(scope)
    if trailer is None:
        print "Error evaluating:",b
        return None

    if type(a) in [float, int, complex]:
        return mul(a,trailer)
    elif type(a) is list:
        if type(trailer) == float:
            trailer = [trailer]

        for idx in trailer:
            a = add(a,idx)
        return a
    else: #it's a function... i guess
        newScope = scope.copy()
        argVals = trailer
        if type(argVals) != list:
            argVals = [argVals]
        if len(a.argNames) > len(argVals):
            argVals += [0] * (len(a.argNames)-len(argVals))
        newScope.update(dict(zip(a.argNames,argVals)))
#        print "Calling with scope:",newScope.keys()
        return a.call(newScope)
#End Operations}}}

#Parser {{{

class FunctionAssignmentExpression(ExpressionNode):#{{{
    def __init__(self):
        self.argNames = []
        self.funcBody = None
        self.funcName = None
        self.constructionScope = {}

    @tokenizeDebug
    def parse(self, tokens):
        tokens.pushState()

        self.funcName = tokens.get()
        if self.funcName.ttype != token.NAME:
            return CommaExpression().parse(tokens.popState())

        op = tokens.get()
        if op.tval =='=':
            return VariableAssignmentExpression().parse(tokens.popState())
        elif op.tval != '(':
            return CommaExpression().parse(tokens.popState())

        #First arg or ) 
        op = tokens.get()
        if op.ttype == token.NAME: # name [, name]* )
            self.argNames.append(op.tval)

            op = tokens.get() # , or ) ... hopefully
            while op.tval == ',':
                op = tokens.get() #Arg

                if op.ttype != token.NAME:
                    return CommaExpression().parse(tokens.popState())
                else: 
                    self.argNames.append(op.tval)

                op = tokens.get() #, or )

            if op.tval != ')': #we didn't 'end' with a ). eg: "f(x+..."
                return CommaExpression().parse(tokens.popState())
        elif op.tval == ')': #empty arg list
            pass
        else: # apparently a function call
            return CommaExpression().parse(tokens.popState())

        #We're ready for the '='
        op = tokens.get()
        if op.tval != '=': #How unfortunate, it IS a function call. "f(x,y)+..."
            return CommaExpression().parse(tokens.popState())

        self.funcBody = CommaExpression().parse(tokens)
        self.funcName = self.funcName.tval
        tokens.discardState()
        return self

    @evalDebug
    def evaluate(self,scope):
        scope[self.funcName] = self
        self.constructionScope = scope
        return self

    @evalDebug
    def call(self,scope):
        return self.funcBody.evaluate(dict(self.constructionScope,**scope))

    def __str__(self):
        return self.funcName+"("+",".join(self.argNames)+")="+str(self.funcBody) #+" {Scope:"+str(self.constructionScope)+"}"
#}}}

class VariableAssignmentExpression(ExpressionNode):#{{{
    def __init__(self):
        self.varName = None
        self.valExpr = None
        pass

    @tokenizeDebug
    def parse(self,tokens):
        tokens.pushState()

        name = tokens.get()
        if name.ttype != token.NAME:
            return CommaExpression().parse(tokens.popState())

        eq = tokens.get()
        if eq.tval != '=':
            return CommaExpression().parse(tokens.popState())

        self.varName = name.tval
        self.valExpr = CommaExpression().parse(tokens.discardState())

        return self

    @evalDebug
    def evaluate(self,scope):
        scope[self.varName] = self.valExpr.evaluate(scope)
        return scope[self.varName]

    def __str__(self):
        return self.varName +"="+str(self.valExpr)
#}}}

class CommaExpression(ExpressionNode):#{{{
    def __init__(self):
        self.exprs = []
    @tokenizeDebug
    def parse(self,tokens):
        expr = IfExpression().parse(tokens)
        if expr is None:
            return self
        self.exprs.append(expr)

        comma = tokens.get()
        while comma.tval == ',':
            exp = IfExpression().parse(tokens)
            if not exp:
                raise ParseException("Expected Additive expression after ','")

            self.exprs.append(exp)
            comma = tokens.get()

        tokens.unget()

        if len(self.exprs)==1:
            return self.exprs[0]

        return self

    @evalDebug
    def evaluate(self, scope):
        return map(lambda x:x.evaluate(scope), self.exprs)

    def __str__(self):
        return "("+",".join(map(str,self.exprs))+")"
#}}}

class IfExpression(ExpressionNode):#{{{
    def __init__(self):
        self.condition= None
        self.trueCase = None
        self.falseCase = None
    @tokenizeDebug
    def parse(self,tokens):
        nextExpr = ComparisonExpression
        tokens.pushState()
        if tokens.get().tval != 'if':
            return nextExpr().parse(tokens.popState())

        if tokens.get().tval != '(':
            raise ParseException("Expected '(' after if")

        self.condition = nextExpr().parse(tokens)

        if tokens.get().tval!= ')':
            raise ParseException("Expected ')' ")
        
        self.trueCase = nextExpr().parse(tokens)

        tokens.discardState()
        
        if tokens.get().tval == 'else':
            self.falseCase = nextExpr().parse(tokens)
        else:
            tokens.unget()

        return self
        

    @evalDebug
    def evaluate(self,scope):
        val = self.condition.evaluate(scope)
        if nonZero(val):
            return self.trueCase.evaluate(scope)
        if self.falseCase is not None:
            return self.falseCase.evaluate(scope)
        return 0

    def __str__(self):
        return "if({}) {} else {}".format(self.condition,self.trueCase,self.falseCase)
#}}}

#}}}
class ComparisonExpression(ExpressionNode):#{{{
    def __init__(self):
        self.terms = []
        self.opDict = {
            "<":lambda x,y:x<y,
            "<=":lambda x,y:x<=y,
            ">":lambda x,y:x>y,
            ">=":lambda x,y:x>=y
        }
        pass

    @tokenizeDebug
    def parse(self,tokens):
        term = AdditiveExpression().parse(tokens)
        if term is None:
            raise ParseException("Expected additive expression")
        self.terms.append(term)
        op = tokens.get()
        while op.tval in self.opDict.keys():
            self.terms.append(op.tval)
            term = AdditiveExpression().parse(tokens)
            if term is None:
                raise ParseExpression("Expected additive expression")
            self.terms.append(term)
            op = tokens.get()
        tokens.unget()

        if len(self.terms) == 1:
            return self.terms[0]
        return self

    @evalDebug
    def evaluate(self,scope):
        left = self.terms[0].evaluate(scope)
        right = self.terms[2].evaluate(scope)
        op = self.terms[1]
        out = self.performOp(left,op,right)
        nextVal = 4
        while out and nextVal<len(self.terms):
            left = right
            op = self.terms[nextVal-1]
            right = self.terms[nextVal].evaluate(scope)
            nextVal += 2
            out = self.performOp(left,op,right)
        if out:
            return 1
        return 0
    def performOp(self, left, op, right):
        return self.opDict[op](left,right)
    def __str__(self):
        return "("+"".join(map(str,self.terms))+")"
        
#}}}

class AdditiveExpression(ExpressionNode):#{{{
    def __init__(self):
        self.terms = []
    @tokenizeDebug
    def parse(self,tokens):
        term = MultiplicativeExpression().parse(tokens)
        if term is None:
            raise ParseException("Expected multiplicative expression")

        self.terms.append(term)
        op = tokens.get()
        while op.tval in "+-":
            self.terms.append(op.tval)
            term = MultiplicativeExpression().parse(tokens)
            if term is None:
                raise ParseException("Expected multiplicative expression")

            self.terms.append(term)
            op = tokens.get()

        tokens.unget()

        if len(self.terms) == 1:
            return self.terms[0]
        return self

    @evalDebug
    def evaluate(self,scope):
        res = self.terms[0].evaluate(scope)
        for op, val in zip(self.terms[1::2], self.terms[2::2]):
            if op == '+':
                res = add(res, val.evaluate(scope))
            elif op == '-':
                res = sub(res, val.evaluate(scope))
            else:
                print "Invalid operation:",op
        return res
        pass

    def __str__(self):
        return "("+"".join(map(str,self.terms))+")"
#}}}

class MultiplicativeExpression(ExpressionNode):#{{{
    def __init__(self):
        self.factors = []
    @tokenizeDebug
    def parse(self,tokens):

        factor = UnaryExpression().parse(tokens)
        if factor is None:
            raise ParseException("Expected unary expression")

        self.factors.append(factor)

        op = tokens.get()
        while op.tval in "*/%":
            self.factors.append(op.tval)

            factor = UnaryExpression().parse(tokens)
            if factor is None:
                raise ParseException("Expected unary expression")

            self.factors.append(factor)
            op = tokens.get()

        tokens.unget()

        if len(self.factors) == 1:
            return self.factors[0]

        return self

    @evalDebug
    def evaluate(self,scope):
        res = self.factors[0].evaluate(scope)
        for op, val in zip(self.factors[1::2], self.factors[2::2]):
            if op == '*':
                res = mul(res, val.evaluate(scope))
            elif op == '/':
                res = div(res, val.evaluate(scope))
            elif op == '%':
                res = mod(res, val.evaluate(scope))
            else:
                print "Invalid operation:",op
        return res
    def __str__(self):
        return "("+"".join(map(str,self.factors))+")"
#}}}

class UnaryExpression(ExpressionNode):#{{{
    def __init__(self):
        self.sign = None
        self.val = None

    @tokenizeDebug
    def parse(self,tokens):
        sign = tokens.get()
        if sign.tval in "+-":
            self.sign = sign.tval
            self.val = UnaryExpression().parse(tokens)
            return self
        else:
            tokens.unget()
            return PowerExpression().parse(tokens)

    @evalDebug
    def evaluate(self,scope):
        if self.sign == '-':
            return uneg(self.val.evaluate(scope))
        return self.val.evaluate(scope)

    def __str__(self):
        return self.sign+"("+str(self.val)+")"
#}}}

class PowerExpression(ExpressionNode):#{{{
    def __init__(self):
        self.base = None
        self.exp = None

    @tokenizeDebug
    def parse(self,tokens):
        self.base = ValueExpression().parse(tokens)
        if not self.base:
            return

        op = tokens.get()
        if op.tval == '^' or op.tval == '**':
            self.exp = UnaryExpression().parse(tokens)
            if self.exp == None:
               raise ParseException("Expected expression after '"+op.tval+"' operator", op)
            return self
        tokens.unget()

        return self.base
    @evalDebug
    def evaluate(self,scope):
        b = self.base.evaluate(scope)
        e = self.exp.evaluate(scope)
        return power(b,e) 

    def __str__(self):
        return str(self.base)+"^("+str(self.exp)+")"
#}}}

class ValueExpression(ExpressionNode):#{{{
    def __init__(self):
        self.atom = None
        self.trailers = []

    @tokenizeDebug
    def parse(self,tokens):
        self.atom = Atom().parse(tokens)
        if self.atom == None:
            return

        trailer = Trailer().parse(tokens)
        while trailer is not None:
            self.trailers.append(trailer)
            trailer = Trailer().parse(tokens)

        if len(self.trailers) == 0:
            return self.atom
        return self

    def __str__(self):
        return str(self.atom)+"("+(")(".join(map(str,self.trailers))+")" if self.trailers else "")

    @evalDebug
    def evaluate(self, scope):
        res = self.atom.evaluate(scope)
        for trailer in self.trailers:
            res = call(res,trailer,scope)
        return res
#}}}

class Atom(ExpressionNode):#{{{
    def __init__(self):
            self.num = None
            self.var = None
    def atomize(self, val):
        if type(val) in [float, int]:
            self.num = val
            return self
        if isinstance(val, ExpressionNode):
            return val
    @tokenizeDebug
    def parse(self,tokens):
        op = tokens.get()
        if op.ttype == token.NUMBER:
            self.num = op
            self.var = None
            return self

        if op.ttype == token.NAME:
            self.num = None
            self.var = op
            return self
       
        if op.tval == '(':
            expr = Expression().parse(tokens)
            if expr == None:
                raise ParseException("Error parsing atom.")
            if tokens.get().tval != ")":
                raise ParseException("Expected )")
            return expr

        tokens.unget()
#        if op.tval == ')':
#            return CommaExpression() # Empty expression

        raise ParseException("Expected number, name, or sub expression",op)

    @evalDebug
    def evaluate(self,scope):
        if self.num is not None:
            return float(self.num.tval)
        if self.var is not None:
            if scope.has_key(self.var.tval):
                return scope[self.var.tval]
            else:
                raise EvaluatorException("Couldn't find variable or function: ",self.var)

    def __str__(self):
        return self.num.tval if self.num is not None else self.var.tval
#}}}

class Trailer(ExpressionNode):#{{{
    #This class has no evaluate function because a successful parse returns an Expression, not a Trailer.
    def __init__(self):
        self.arg = None
    @tokenizeDebug
    def parse(self,tokens):
        op = tokens.get()
        if op.tval == "(":
            if tokens.get().tval == ")":
                return CommaExpression()
            else:
                tokens.unget()
            self.arg = CommaExpression().parse(tokens)
            if tokens.get().tval != ")":
                raise ParseException("Expected )")
            return self.arg
        tokens.unget()
#}}}

class Expression(ExpressionNode): #{{{
    def __init__(self):
        pass
    @tokenizeDebug
    def parse(self,tokens):
        expr = FunctionAssignmentExpression().parse(tokens)
        n = tokens.get()
        if n.tval in [')', 'else']:
            tokens.unget()
            return expr

        if n.ttype != 0:
            raise ParseException("Expected end of expression.",n)
        return expr
#}}}

#}}}
class NativeFunction(FunctionAssignmentExpression):
    def __init__(self, name, args, func):
        self.funcName = name
        self.argNames = args
        self.func = func
        self.funcBody = "[Native Function]"
    def call(self,scope):
        return self.func(*map(scope.get,self.argNames))

    def evaluate(self,scope):
        scope[self.funcName] = self

def includeMath(scope):
    import math
    def mymap(func,args):
        out = []
        _scope = {}
        for arg in args:
            if type(arg) != list:
                arg = [arg]
            for argName,val in zip(func.argNames,arg):
                _scope[argName] = val
            out.append(func.call(_scope))
        return out 
    NativeFunction("map",["func","list"],mymap).evaluate(scope)
    NativeFunction("range",["r"],lambda x:range(int(x))).evaluate(scope)

    NativeFunction("acos",["x"],math.acos).evaluate(scope)
    NativeFunction("acosh",["x"],math.acosh).evaluate(scope)
    NativeFunction("asin",["x"],math.asin).evaluate(scope)
    NativeFunction("asinh",["x"],math.asinh).evaluate(scope)
    NativeFunction("atan",["x"],math.atan).evaluate(scope)
    NativeFunction("atan2",["x","y"],math.atan2).evaluate(scope)
    NativeFunction("atanh",["x"],math.atanh).evaluate(scope)
    NativeFunction("ceil",["x"],math.ceil).evaluate(scope)
    NativeFunction("cos",["x"],math.cos).evaluate(scope)
    NativeFunction("cosh",["x"],math.cosh).evaluate(scope)
    NativeFunction("degrees",["x"],math.degrees).evaluate(scope)
    NativeFunction("exp",["x"],math.exp).evaluate(scope)
    NativeFunction("abs",["x"],math.fabs).evaluate(scope)
    NativeFunction("factorial",["x"],math.factorial).evaluate(scope)
    NativeFunction("floor",["x"],math.floor).evaluate(scope)
    NativeFunction("fmod",["x"],math.fmod).evaluate(scope)
    NativeFunction("frexp",["x"],math.frexp).evaluate(scope)
    NativeFunction("hypot",["x","y"],math.hypot).evaluate(scope)
    NativeFunction("isinf",["x"],math.isinf).evaluate(scope)
    NativeFunction("isnan",["x"],math.isnan).evaluate(scope)
    NativeFunction("ldexp",["x"],math.ldexp).evaluate(scope)
    NativeFunction("log",["x"],math.log).evaluate(scope)
    NativeFunction("log10",["x"],math.log10).evaluate(scope)
    NativeFunction("log1p",["x"],math.log1p).evaluate(scope)
    NativeFunction("modf",["x"],math.modf).evaluate(scope)
    NativeFunction("powmod",["b","e","m"],lambda b,e,m:pow(int(b),int(e),int(m))).evaluate(scope)
    NativeFunction("radians",["x"],math.radians).evaluate(scope)
    NativeFunction("sin",["x"],math.sin).evaluate(scope)
    NativeFunction("sinh",["x"],math.sinh).evaluate(scope)
    NativeFunction("sqrt",["x"],math.sqrt).evaluate(scope)
    NativeFunction("tan",["x"],math.tan).evaluate(scope)
    NativeFunction("tanh",["x"],math.tanh).evaluate(scope)
    NativeFunction("trunc",["x"],math.trunc).evaluate(scope)
    scope['pi'] = math.pi
    scope['e'] = math.e





scope = {}
def on_load(bot):
    global scope
    includeMath(scope)
def clean(val):
    if type(val) == float:
        return round(val,15)
    if type(val) == list:
        return "("+", ".join(map(lambda x:str(clean(x)),val))+")"
    return str(val)

   

def on_PRIVMSG(bot,sender,args):
    line = args[1]
    if line[0] != "%":
        return

    room = args[0]
    response = ""
    try:
        resp = Expression().parse(Tokenizer(line[1:])).evaluate(scope)
        scope['_'] = resp
        response = (sender.split("!")[0]+": {!s}").format(clean(resp))
    except Exception as e:
        try:
            errmsg = e.args[0]
            tok = e.args[1]
            response = tok.lineno
            response = errmsg+" "+response[:tok.start] + "{C4}" + tok.tval + "{}" + response[tok.end:]
        except:    
            response = str(e)
        
    bot.say(room,response)
        







if __name__ == "__main__":#{{{
    scope = {}
    includeMath(scope)

    i = raw_input("> ")
    while i:
        if i == '?':
            for k,v in scope.items():
                print k,"=>",v
        else:
            try:
                print "Tokenizing"
                ast = Expression().parse(Tokenizer(i))
                if ast is not None:
                    print "Evaluating"
                    val = ast.evaluate(scope)
                    print "=",clean(val)
                    scope['_']=val
            except (ParseException, EvaluatorException) as e:
                print "Exception:",e.args[0]
                tok = e.args[1]
                print "",tok.lineno
                print " "*tok.start,"^"*(tok.end-tok.start)
            except:
                raise 
        i = raw_input("> ")
        
#}}}
