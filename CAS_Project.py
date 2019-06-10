# coding: utf-8

# CS 203 Spring 2019
#
# Final Project - A Computer Algebra System
#
# Author:  Rafael Espericueta,  resperic@ucsc.edu


'''
The Evolution of a Simple CAS

First, the While language includes Arith as a subset, so we start with the data 
scructures from Assignment 1, with a bit of renaming and a new subtraction operation. 
To this was then added functionality to deal with Boolean expressions, with 
corresponding operators. Then the test for equality and less than for two arithmetic 
expressions was implemented, along with the structures and code needed for variables 
(for both arithmetic and boolean expressions) and the assignment operators. Finally
the sequence, the if-then-else, and the namesake while operator are all implemented.

For the second part of that assignment, I extend While to include floating-point 
numbers, division, as well as exponentials, logarithms, sine, cosine, and even the
GCD function implementing Euclid's algorithm as shown in the lecture.

All this seemed like the beginnings of a simple computer algebra system, so I built
my CAS on this starting point, by adding algebraic ASTs, a Solve function, and 
a derivative operator. 

'''


# We need some functions from "math" to implement the corresponding functions 
# in this extention of the While language.
from math import sin, cos, exp, log
from copy import deepcopy

###################################################################################
# 
# Data Structures
# 
# The following classes essentially constitute my data structures used to implement 
# the abstract syntax trees (AST) of Arith, but with subtraction and some renaming.
#

#
# Syntax tree node structure to hold AST for arithmetic expressions.
#

class Expr:
    def __init__(self):
        pass

class AConst(Expr):    # integer valued
    def __init__(self, value):
        Expr.__init__(self)
        self.arg1 = value

class FConst(Expr):    # floating-point valued
    def __init__(self, value):
        Expr.__init__(self)
        self.arg1 = value
        
class Add(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1
        self.arg2 = arg2

class Sub(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1
        self.arg2 = arg2
        
class Mul(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1
        self.arg2 = arg2

## The following extend the While interpteter
class Div(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1   # dividend
        self.arg2 = arg2   # divisor
        
class Exp(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1    # base
        self.arg2 = arg2    # exponent
        
class Log(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1    # base
        self.arg2 = arg2    # exponent
        
class Sin(Expr):
    def __init__(self, arg1):
        Expr.__init__(self)
        self.arg1 = arg1
    
class Cos(Expr):
    def __init__(self, arg1):
        Expr.__init__(self)
        self.arg1 = arg1
        
class GCD(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1
        self.arg2 = arg2
        

# Unbound versions of the above are algebraic expressions.

        
class uAdd(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1
        self.arg2 = arg2

class uSub(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1
        self.arg2 = arg2
        
class uMul(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1
        self.arg2 = arg2

## The following are for unbound expressions
        
class uDiv(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1   # dividend
        self.arg2 = arg2   # divisor
        
class uRec(Expr):    # 1/x, the reciprocal
    def __init__(self, arg1):
        Expr.__init__(self)
        self.arg1 = arg1   # divisor
        
class uExp(Expr):
    def __init__(self, arg1):
        Expr.__init__(self)
        self.arg1 = arg1    # exponent

class uPow(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1    # base
        self.arg2 = arg2    # exponent
        
class uLn(Expr):
    def __init__(self, arg1):
        Expr.__init__(self)
        self.arg1 = arg1
        
class uSin(Expr):
    def __init__(self, arg1):
        Expr.__init__(self)
        self.arg1 = arg1
    
class uCos(Expr):
    def __init__(self, arg1):
        Expr.__init__(self)
        self.arg1 = arg1


#
# To the above we must add some additional data structures to instantiate the While language.
#
            
# Arithmetic variable stores:  {name: val,}
Store = dict()

#
# Syntax tree node structure to hold AST for an Boolean expressions.
#

class BConst(Expr):
    def __init__(self, value):
        Expr.__init__(self)
        self.arg1 = value     # True or False
        
class Not(Expr):
    def __init__(self, arg1):
        Expr.__init__(self)
        self.arg1 = arg1
        
class And(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1
        self.arg2 = arg2
        
class Or(Expr):
    def __init__(self, arg1, arg2):
        Expr.__init__(self)
        self.arg1 = arg1
        self.arg2 = arg2

#
# Syntax tree node structure to hold AST for comparing arithmetic expressions
#
class IsEqual(Expr):
    def __init__(self, aexp1, aexp2):
        Expr.__init__(self)
        self.arg1 = aexp1
        self.arg2 = aexp2

class IsLess(Expr):
    def __init__(self, aexp1, aexp2):
        Expr.__init__(self)
        self.arg1 = aexp1
        self.arg2 = aexp2

#
# Syntax tree node structure to hold AST for commands.
#           
class Comm:
    def __init__(self):
        pass

# The skip command doesn't do much!  
class Skip(Comm):
    def __init__(self):
        Comm.__init__(self)
            
# Assign an arithmetic expression to a variable.
class Assign(Comm):
    def __init__(self, name, aexp):
        Comm.__init__(self)
        # The 1st argument must be a string, the name of the variable assigned.
        if isinstance(name, str):
            self.arg1 = name
            self.arg2 = aexp    # aexp may be the name of a variable

# Sequentially execute command1 followed by command2.
class Seq(Comm):
    def __init__(self, command1, command2):
        Comm.__init__(self)
        # These arguments are commands.
        self.arg1 = command1
        self.arg2 = command2

# If * then ** else ***.
class IfThen(Comm):
    def __init__(self, condition, command1, command2):
        Comm.__init__(self)
        self.arg1 = condition   # Boolean
        self.arg2 = command1
        self.arg3 = command2
        
# While loop
class While(Comm):
    def __init__(self, condition, command):
        Comm.__init__(self)
        self.arg1 = condition   # Boolean
        self.arg2 = command
        
                
#############################################################################
#
# Evaluation Function
# 

# Function that evaluates While syntax trees. The output is an integer or a Boolean.
def Eval(t):
    ''' Input: an AST for an arithmetic expression
        Output: the value of this arithmetic expression '''
        
    # If t is an integer or a Boolean, or a float, simply return it.
    if isinstance(t, int) or isinstance(t, bool) or isinstance(t, float): return t
    
    # If t is a variable name, return its value.
    if isinstance(t, str):
        if t in Store:  
            return Eval(Store[t])
        else:
            print('ERROR: Variable "' + t + "' is undefined")

    # Fetch the class name of this operator.
    op = t.__class__.__name__
    
    # Rename the operation's arguments to simplify the code.
    if hasattr(t, 'arg1'):  
        arg1 = t.arg1
    if hasattr(t, 'arg2'):  
        arg2 = t.arg2
    if hasattr(t, 'arg3'):  
        arg3 = t.arg3

    if (op == 'AConst') or (op == 'BConst') or (op == 'FConst'):
        return Eval(arg1)

    elif op == 'Skip':
        return
    
    elif op == 'Seq':  
        Eval(arg1)
        Eval(arg2)
        return
    
    elif op == 'Assign':
        # Store the value of this variable.
        Store[arg1] = Eval(arg2)
        return Store[arg1]
    
    elif op == 'Add' or op == 'uAdd':
        return Eval(arg1) + Eval(arg2)
    
    elif op == 'Sub' or op == 'uSub':
        return Eval(arg1) - Eval(arg2)
    
    elif op == 'Mul' or op == 'uMul':
        return Eval(arg1) * Eval(arg2)
    
    elif op == 'Div' or op == 'uDiv':
        return Eval(arg1) / Eval(arg2)
    
    elif op == 'Exp' or op == 'uExp':
        return Eval(arg1)**Eval(arg2)
    
    elif op == 'uLn':
        return log(Eval(arg1))
    
    elif op == 'Log':
        return log(Eval(arg1)) / log(Eval(arg2))
    
    elif op == 'Sin':
        return sin(Eval(arg1))
    
    elif op == 'Cos':
        return cos(Eval(arg1))
    
    elif op == 'Not':
        return not Eval(arg1)
    
    elif op == 'And':
        return Eval(arg1) & Eval(arg2)
    
    elif op == 'Or':
        return Eval(arg1) | Eval(arg2)
    
    elif op == 'IsEqual':
        if Eval(arg1) == Eval(arg2):
            return True
        else:
            return False
        
    elif op == 'IsLess':
        if Eval(arg1) < Eval(arg2):
            return True
        else:
            return False
        
    elif op == 'IfThen':
        if Eval(arg1):
            return Eval(arg2)
        else:
            return Eval(arg3)
        
    elif op == 'While':
        while Eval(arg1):
            Eval(arg2)
        return
    
    elif op == 'GCD':
        # Initialize inputs
        #
        # NOTE: this operation has a side effect of deleting any variables
        # with names 'nnn' or 'mmm'.
        Eval(Assign('nnn', arg1));  Eval(Assign('mmm', arg2))

        # Define GCD program (implementation of Euclid's algorithm)
        Eval(While(Not(IsEqual('nnn', 'mmm')),
                   IfThen(IsLess('nnn', 'mmm'),
                          Assign('mmm', Sub('mmm', 'nnn')),
                          Assign('nnn', Sub('nnn', 'mmm'))
                          )
                   )
            )
        temp = Store['nnn']
        # Cleanup
        del Store['nnn']; del Store['mmm']
        return temp
    
    else:
        print('ERROR:', op, ' not a valid operation')


def isnumber(x):
    ''' if x is numeric return True, else return False '''
    if isinstance(x, (int, float)):
        return True
    else:
        return False
    
    
#############################################################################
#
# Derivative Operator
# 

# Function that takes the derivative of unbound function ASTs. The output is a function AST.
# Ints and floats as well as arithmetic expressions are interpreted as constant functions.
def D(t, x):
    ''' Input: an AST for an function tree
        Output: a function tree equal to the derivative of the input tree '''
        
    # If t is an integer or a float, simply return the zero function.
    if isnumber(t): return 0
    
    
    # If t is a bound variable, return the zero function.
    if isinstance(t, str):
        if t in Store:  
            return 0    # the derivative of a constant is 0
        else:
            if t == x:
                return 1     # d/dx x = 1
            else:
                return 0     # d/dx y = 0   (y is not a function of x)

    # Fetch the class name of this operator.
    op = t.__class__.__name__
    
    # Rename the operation's arguments to simplify the code.
    if hasattr(t, 'arg1'):  
        arg1 = t.arg1
    if hasattr(t, 'arg2'):  
        arg2 = t.arg2
    #if hasattr(t, 'arg3'):  
    #    arg3 = t.arg3

    if (op == 'AConst') or (op == 'FConst'):
        return 0

    elif op == 'uPow':
        # If possible, simplify exponent.
        if isnumber(arg2) or (arg2.__class__.__name__ in ('AConst', 'FConst')): 
            exponent = Eval(Sub(arg2, 1))
        else:
            print('ERROR: Exponent not numeric')
        # Applying the chain rule.
        Dinside = D(arg1, x)
        if Dinside == 1:
            return uMul(arg2, uPow(arg1, exponent))
        else:
            return uMul(uMul(arg2, uPow(arg1, exponent)), Dinside)
    
    elif op == 'uAdd':
        return uAdd(D(arg1, x), D(arg2, x))
    
    elif op == 'uSub':
        return uSub(D(arg1, x), D(arg2, x))
    
    elif op == 'uMul':
        # D(c*f(x)) = c*(Df)(x), assuming c constant
        if isnumber(arg1) or arg1 in Store:
            return uMul(arg1, D(arg2, x))
        elif isnumber(arg2) or arg2 in Store:
                return uMul(arg2, D(arg1, x))
        else: 
            # Product Rule
            return uAdd(uMul(D(arg1, x), arg2), uMul(arg1, D(arg2, x)))
    
    elif op == 'uDiv':
        return uDiv(uSub(uMul(D(arg1, x), arg2), uMul(arg1, D(arg2, x))), uPow(arg2, 2))
    
    elif op == 'uExp':
        # Applying the chain rule.
        inside = D(arg1, x)
        if inside == 1:
            return uExp(arg1)
        else:
            return uMul(uExp(arg1), inside)
    
    elif op == 'uLn':
        # Applying the chain rule.
        return uDiv(D(arg1, x), arg1)
    
    elif op == 'uSin':
        # Applying the chain rule.
        inside = D(arg1, x)
        if inside == 1:
            return uCos(arg1)
        else:
            return uMul(uCos(arg1), inside)
    
    elif op == 'uCos':
        # Applying the chain rule.
        inside = D(arg1, x)
        if inside == 1:
            return uMul(-1, uSin(arg1))
        else:
            return uMul(uMul(-1, uSin(arg1)), inside)

    else:
        print('ERROR:', op, ' not a valid operation')
        
        
def Same(e1, e2):
    ''' Returns true if e1 == e2 in the literal sense '''
    if isnumber(e1) and isnumber(e2):
        if e1 == e2:
            return True
        else:
            return False
    elif isinstance(e1, str) and isinstance(e2, str):
        if e1 == e2:
            return True
        else:
            return False
    elif e1.__class__.__name__ == e2.__class__.__name__:
        return True
    return False

def SameClass(e1, e2):
    ''' Returns true if e1 has same class name as e2 '''
    if isnumber(e1) and isnumber(e2): 
        return False
    elif isinstance(e1, str) and isinstance(e2, str):
        return False
    elif e1.__class__.__name__ == e2.__class__.__name__:
        return True
    return False
    

def Simp(e):
    ''' Simplify a u-expression '''
    
    # Make a deep copy of e.
    ex = deepcopy(e)
    
    # Base cases - at a leaf
    if isnumber(ex):
        return ex
    if isinstance(ex, str):
        if ex in Store:
            ex = Store[ex]
            return ex
        else:
            return ex
   
    if hasattr(ex, 'arg1') and not hasattr(ex, 'arg2'):
        ex.arg1 = Simp(ex.arg1)
        return ex
    
    if hasattr(ex, 'arg1') and hasattr(ex, 'arg2'):
        
        if ex.__class__.__name__ == 'uAdd':
            ex.arg1, ex.arg2 = rSimp(ex.arg1), rSimp(ex.arg2)
            if ex.arg1 == 0:
                ex = ex.arg2
            elif ex.arg2 == 0:
                ex = ex.arg1
            elif isnumber(ex.arg1) and isnumber(ex.arg2):
                ex = ex.arg1 + ex.arg2
            
            # x + x = 2*x
            elif isinstance(ex.arg1, str) and ex.arg1 == ex.arg2:
                ex = uMul(2, ex.arg1)
                
            # x + (0-z)*y = x - y*z
            elif ex.__class__.__name__ == 'uAdd' and ex.arg2.__class__.__name__ == 'uSub' \
                 and ex.arg2.arg2.__class__.__name__ == 'uMul' and ex.arg2.arg1 == 0:
                ex = uSub(ex.arg1, uMul(ex.arg2.arg2.arg1, ex.arg2.arg2.arg2))
            
            # (0-z)*y + x = x - y*z
            elif ex.__class__.__name__ == 'uAdd' and ex.arg1.__class__.__name__ == 'uSub' \
                 and ex.arg1.arg2.__class__.__name__ == 'uMul' and ex.arg1.arg1 == 0:
                ex = uSub(ex.arg2, uMul(ex.arg1.arg2.arg1, ex.arg1.arg2.arg2))
                
            # (x+a) + b = x + (a+b)
            elif ex.arg1.__class__.__name__ == 'uAdd' and isnumber(ex.arg2):
                args = [ex.arg1.arg1, ex.arg1.arg2, ex.arg2]
                numeric = [e for e in args if isnumber(e)]
                nonumeric = [e for e in args if not isnumber(e)]
                if len(numeric) == 2:
                    ex.arg1.arg1, ex.arg1.arg2, ex.arg2 = numeric[0], numeric[1], nonumeric[0]
                    ex.arg1, ex.arg2 = rSimp(ex.arg1), rSimp(ex.arg2)
            
            # a + (x+b) = x + (a+b)
            elif ex.arg2.__class__.__name__ == 'uAdd' and isnumber(ex.arg1):
                args = [ex.arg2.arg1, ex.arg2.arg2, ex.arg1]
                numeric = [e for e in args if isnumber(e)]
                nonumeric = [e for e in args if not isnumber(e)]
                if len(numeric) == 2:
                    ex.arg1.arg1, ex.arg1.arg2, ex.arg2 = numeric[0], numeric[1], nonumeric[0]
                    ex.arg1, ex.arg2 = rSimp(ex.arg1), rSimp(ex.arg2)
                    
            # (x-a) + b = x + (b-a)   or   = x - (a - b)
            elif ex.arg1.__class__.__name__ == 'uSub' and isnumber(ex.arg1.arg2) and isnumber(ex.arg2):
                if ex.arg2 - ex.arg1.arg2 >= 0:
                    ex = rSimp(uAdd(ex.arg1.arg1, uSub(ex.arg2, ex.arg1.arg2)))
                else:
                    ex = rSimp(uSub(ex.arg1.arg1, uSub(ex.arg1.arg2, ex.arg2)))
            
            # a + (x-b) = x + (a-b)   or  = x - (b-a)
            elif ex.arg2.__class__.__name__ == 'uSub' and isnumber(ex.arg1) and isnumber(ex.arg2.arg2):
                if ex.arg1 - ex.arg2.arg2 >= 0:
                    ex = rSimp(uAdd(ex.arg2.arg1, uSub(ex.arg1, ex.arg2.arg2)))
                else:
                    ex = rSimp(uSub(ex.arg2.arg1, uSub(ex.arg2.arg2, ex.arg1)))
                    
            # (a-x) + b = (a+b) - x 
            elif ex.arg1.__class__.__name__ == 'uSub' and isnumber(ex.arg1.arg1) and isnumber(ex.arg2):
                ex = rSimp(uSub(uAdd(ex.arg1.arg1, ex.arg2), ex.arg1.arg2))
            
            # a + (b-x) = (a+b) - x 
            elif ex.arg2.__class__.__name__ == 'uSub' and isnumber(ex.arg1) and isnumber(ex.arg2.arg1):
                ex = rSimp(uSub(uAdd(ex.arg1, ex.arg2.arg1), ex.arg2.arg2))
                    
            # (x+2) + (y+3) = (x+y) + 5
            elif ex.arg1.__class__.__name__ == 'uAdd' and ex.arg2.__class__.__name__ == 'uAdd':
                args = [ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2]
                numeric = [e for e in args if isnumber(e)]
                nonumeric = [e for e in args if not isnumber(e)]
                if len(numeric) == 2:
                    ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2 = numeric[0], numeric[1], nonumeric[0], nonumeric[1]
                    ex.arg1, ex.arg2 = rSimp(ex.arg1), rSimp(ex.arg2)
            # (x+2) + (y+3) = (x+y) + 5
            elif ex.arg1.__class__.__name__ == 'uAdd' and ex.arg2.__class__.__name__ == 'uAdd':
                args = [ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2]
                numeric = [e for e in args if isnumber(e)]
                nonumeric = [e for e in args if not isnumber(e)]
                if len(numeric) == 2:
                    ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2 = numeric[0], numeric[1], nonumeric[0], nonumeric[1]
                    ex.arg1, ex.arg2 = rSimp(ex.arg1), rSimp(ex.arg2)
                    
            # (x-2) + (y+3) = (x+y) + (3-2)  or  (x-3) + (y+2) = (x+y) - (3-2)
            elif ex.arg1.__class__.__name__ == 'uSub' and ex.arg2.__class__.__name__ == 'uAdd':
                args = [ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2]
                numeric = [e for e in args if isnumber(e)]
                nonumeric = [e for e in args if not isnumber(e)]
                if len(numeric) == 2:
                    if numeric[1] >= numeric[0]:
                        ex.arg1 = uAdd(nonumeric[0], nonumeric[1])
                        ex.arg2 = uSub(numeric[1], numeric[0])
                    else:
                        ex = uSub(uAdd(nonumeric[0], nonumeric[1]), uSub(numeric[0], numeric[1]))
                        
            # (x+3) + (y-2) = (x+y) + (3-2)    or   (x+2) + (y-3) = (x+y) - (3-2)
            elif ex.arg1.__class__.__name__ == 'uAdd' and ex.arg2.__class__.__name__ == 'uSub':
                args = [ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2]
                numeric = [e for e in args if isnumber(e)]
                nonumeric = [e for e in args if not isnumber(e)]
                if len(numeric) == 2:
                    if numeric[0] >= numeric[1]:
                        ex.arg1 = uAdd(nonumeric[0], nonumeric[1])
                        ex.arg2 = uSub(numeric[0], numeric[1])
                    else:
                        ex = uSub(uAdd(nonumeric[0], nonumeric[1]), uSub(numeric[1], numeric[0]))  
                    
            # (x+a) + (y+b) = (x+y) + (a+b)
            elif ex.arg1.__class__.__name__ == 'uAdd' and ex.arg2.__class__.__name__ == 'uAdd':
                args = [ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2]
                numeric = [e for e in args if isnumber(e)]
                nonumeric = [e for e in args if not isnumber(e)]
                if len(numeric) == 2:
                    ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2 = nonumeric[0], nonumeric[1], numeric[0], numeric[1]
                    ex.arg1, ex.arg2 = rSimp(ex.arg1), rSimp(ex.arg2)
 
            # (x-a) + (y-b) = (x+y) - (a+b)
            elif ex.arg1.__class__.__name__ == 'uSub' and ex.arg2.__class__.__name__ == 'uSub' \
                and isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg2):
                args = [ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2]
                numeric = [e for e in args if isnumber(e)]
                nonumeric = [e for e in args if not isnumber(e)]
                if len(numeric) == 2:
                    ex = uSub(uAdd(nonumeric[0], nonumeric[1]), uAdd(numeric[0], numeric[1]))
                    
            # (a-x) + (y-b) = (y-x) + (a-b)     or   = (y-x) - (b-a)     
            elif ex.arg1.__class__.__name__ == 'uSub' and ex.arg2.__class__.__name__ == 'uSub' \
                and isnumber(ex.arg1.arg1) and isnumber(ex.arg2.arg2):
                args = [ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2]
                numeric = [e for e in args if isnumber(e)]
                nonumeric = [e for e in args if not isnumber(e)]
                if len(numeric) == 2:
                    if numeric[0] >= numeric[1]:
                        ex = uAdd(uSub(nonumeric[1], nonumeric[0]), uSub(numeric[0], numeric[1]))
                    else:
                        ex = uSub(uSub(nonumeric[1], nonumeric[0]), uSub(numeric[1], numeric[0]))
                        
            # (x-a) + (b-y) = (x-y) + (b-a)     or   = (x-y) - (a-b)     
            elif ex.arg1.__class__.__name__ == 'uSub' and ex.arg2.__class__.__name__ == 'uSub' \
                and isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg1):
                args = [ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2]
                numeric = [e for e in args if isnumber(e)]
                nonumeric = [e for e in args if not isnumber(e)]
                if len(numeric) == 2:
                    if numeric[1] >= numeric[0]:
                        ex = uAdd(uSub(nonumeric[0], nonumeric[1]), uSub(numeric[1], numeric[0]))
                    else:
                        ex = uSub(uSub(nonumeric[0], nonumeric[1]), uSub(numeric[0], numeric[1]))
                        
            # (a-x) + (b-y) = (a+b) - (x+y)  
            elif ex.arg1.__class__.__name__ == 'uSub' and ex.arg2.__class__.__name__ == 'uSub' \
                and isnumber(ex.arg1.arg1) and isnumber(ex.arg2.arg1):
                args = [ex.arg1.arg1, ex.arg1.arg2, ex.arg2.arg1, ex.arg2.arg2]
                numeric = [e for e in args if isnumber(e)]
                nonumeric = [e for e in args if not isnumber(e)]
                if len(numeric) == 2:
                    ex = rSimp(uSub(uAdd(numeric[0], numeric[1]), uAdd(nonumeric[0], nonumeric[1])))
                    
            # 2*x + x = 3*x   and   x + 2*x = 3*x
            elif ex.arg1.__class__.__name__== 'uMul' and ex.arg2.__class__.__name__ != 'uMul':
                if Same(ex.arg1.arg2, ex.arg2):
                    if isnumber(ex.arg1.arg1):
                        a, b, x = ex.arg1.arg1, 1, ex.arg2
                        ex = rSimp(uMul(uAdd(a, b), x))
                elif Same(ex.arg1.arg1, ex.arg2):
                    if isnumber(ex.arg1.arg2):
                        a, b, x = ex.arg1.arg2, 1, ex.arg2
                        ex = rSimp(uMul(uAdd(a, b), x))
            
            elif ex.arg2.__class__.__name__== 'uMul' and ex.arg1.__class__.__name__ != 'uMul':
                if Same(ex.arg1, ex.arg2.arg2):
                    if isnumber(ex.arg2.arg1):
                        a, b, x = ex.arg2.arg1, 1, ex.arg1
                        ex = rSimp(uMul(uAdd(a, b), x))
                elif Same(ex.arg1, ex.arg2.arg1):
                    if isnumber(ex.arg2.arg2):
                        a, b, x = ex.arg2.arg2, 1, ex.arg1
                        ex = rSimp(uMul(uAdd(a, b), x))
            
            # ax + bx = (a + b)*x      
            elif ex.arg1.__class__.__name__== 'uMul' and ex.arg2.__class__.__name__== 'uMul':
                if Same(ex.arg1.arg2, ex.arg2.arg2):
                    if isnumber(ex.arg1.arg1) and isnumber(ex.arg2.arg1):
                        a, b, x = ex.arg1.arg1, ex.arg2.arg1, ex.arg1.arg2
                        ex = rSimp(uMul(uAdd(a, b), x))
                elif Same(ex.arg1.arg1, ex.arg2.arg2):
                    if isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg1):
                        a, b, x = ex.arg1.arg2, ex.arg2.arg1, ex.arg1.arg1
                        ex = rSimp(uMul(uAdd(a, b), x))
                elif Same(ex.arg1.arg2, ex.arg2.arg1):
                    if isnumber(ex.arg1.arg1) and isnumber(ex.arg2.arg2):
                        a, b, x = ex.arg1.arg1, ex.arg2.arg2, ex.arg1.arg2
                        ex = rSimp(uMul(uAdd(a, b), x))
                elif Same(ex.arg1.arg1, ex.arg2.arg1):
                    if isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg2):
                        a, b, x = ex.arg1.arg2, ex.arg2.arg2, ex.arg1.arg1
                        ex = rSimp(uMul(uAdd(a, b), x))
                    

        elif ex.__class__.__name__ == 'uSub':
            ex.arg1, ex.arg2 = rSimp(ex.arg1), rSimp(ex.arg2)
            if ex.arg2 == 0:
                ex = ex.arg1
            # Negative numbers like -3 are represented as 0 - 3.
            elif isnumber(ex.arg1) and isnumber(ex.arg2):
                if ex.arg1 >= ex.arg2:
                    ex = ex.arg1 - ex.arg2
                else:
                    ex.arg2 -= ex.arg1
                    ex.arg1 = 0
            # 'x' - 'x' = 0
            elif isinstance(ex.arg1, str) and isinstance(ex.arg2, str) and ex.arg1 == ex.arg2:
                ex = 0
                
            # x - (0-z)*y = x + y*z    or   x - y*(0-z) = x + y*z
            elif ex.arg2.__class__.__name__ == 'uMul':
                if ex.arg2.arg1.__class__.__name__ == 'uSub' and ex.arg2.arg1.arg1 == 0:
                    x, y, z = ex.arg1, ex.arg2.arg2, ex.arg2.arg1.arg2
                    ex = uAdd(x, uMul(y, z))
                elif ex.arg2.arg2.__class__.__name__ == 'uSub' and ex.arg2.arg2.arg1 == 0:
                    x, y, z = ex.arg1, ex.arg2.arg1, ex.arg2.arg2.arg2
                    ex = uAdd(x, uMul(y, z))
                
            # (x + a) - b = x + (a - b)
            elif ex.arg1.__class__.__name__ == 'uAdd' and isnumber(ex.arg2):
                if isnumber(ex.arg1.arg2):
                    a, b, x = ex.arg1.arg2, ex.arg2, ex.arg1.arg1
                    ex = uAdd(x, uSub(a, b))
                elif isnumber(ex.arg1.arg1):
                    a, b, x = ex.arg1.arg1, ex.arg2, ex.arg1.arg2
                    ex = uAdd(x, uSub(a, b))
            
            # a - (b - x) = x + (a - b)
            elif ex.arg2.__class__.__name__ == 'uSub' and isnumber(ex.arg1) and isnumber(ex.arg1.arg1):
                    a, b, x = ex.arg1, ex.arg2.arg1, ex.arg2.arg2
                    ex = uAdd(x, uSub(a, b))
                    
            # (x - a) - b = x - (a + b) 
            elif ex.arg1.__class__.__name__ == 'uSub' and isnumber(ex.arg1.arg2) and isnumber(ex.arg2):
                a, b, x = ex.arg1.arg2, ex.arg2, ex.arg1.arg1
                ex = uSub(x, uAdd(a, b))
                    
            # (a - x) - b = (a - b) - x 
            elif ex.arg1.__class__.__name__ == 'uSub' and isnumber(ex.arg1.arg1) and isnumber(ex.arg2):
                a, b, x = ex.arg1.arg1, ex.arg2, ex.arg1.arg2
                ex = rSimp(uSub(uSub(a, b), x))
                    
            # (x + a) - (y + b) = (x - y) + (a - b)
            elif ex.arg1.__class__.__name__ == 'uAdd' and ex.arg2.__class__.__name__ == 'uAdd':
                
                if isnumber(ex.arg1.arg1) and isnumber(ex.arg2.arg1):
                    a, b, x, y = ex.arg1.arg1, ex.arg2.arg1, ex.arg1.arg2, ex.arg2.arg2
                    if a - b >= 0:
                        ex = rSimp(uAdd(uSub(x, y)), uSub(a, b))
                    else:
                        ex = rSimp(uSub(uSub(x, y), uSub(b, a)))
                        
                elif isnumber(ex.arg1.arg1) and isnumber(ex.arg2.arg2):
                    a, b, x, y = ex.arg1.arg1, ex.arg2.arg2, ex.arg1.arg2, ex.arg2.arg1
                    if a - b >= 0:
                        ex = rSimp(uAdd(uSub(a, b), uSub(x, y)))
                    else:
                        ex = rSimp(uAdd(uSub(b, a), uSub(x, y)))
                        
                elif isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg1):
                    a, b, x, y = ex.arg1.arg2, ex.arg2.arg1, ex.arg1.arg1, ex.arg2.arg2
                    if a - b >= 0:
                        ex = rSimp(uAdd(uSub(a, b), uSub(x, y)))
                    else:
                        ex = rSimp(uAdd(uSub(b, a), uSub(x, y)))
                        
                elif isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg2):
                    a, b, x, y = ex.arg1.arg2, ex.arg2.arg2, ex.arg1.arg1, ex.arg2.arg1
                    if a - b >= 0:
                        ex = rSimp(uAdd(uSub(a, b), uSub(x, y)))
                    else:
                        ex = rSimp(uAdd(uSub(b, a), uSub(x, y)))
                    
            # (x - a) - (y + b) = (x - y) - (a + b)
            elif ex.arg1.__class__.__name__ == 'uSub' and ex.arg2.__class__.__name__ == 'uAdd':
                if isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg1):
                    a, b, x, y = ex.arg1.arg2, ex.arg2.arg1, ex.arg1.arg1, ex.arg2.arg2
                    ex = rSimp(uSub(uSub(x, y), uAdd(a, b)))
                elif isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg2):
                    a, b, x, y = ex.arg1.arg2, ex.arg2.arg2, ex.arg1.arg1, ex.arg2.arg1
                    ex = rSimp(uSub(uSub(x, y), uAdd(a, b)))
      
            # (x + a) - (y - b) = (x - y) + (a + b)    or   (a + x) - (y - b) = (x - y) + (a + b)
            elif ex.arg1.__class__.__name__ == 'uAdd' and ex.arg2.__class__.__name__ == 'uSub':
                if isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg2):
                    a, b, x, y = ex.arg1.arg2, ex.arg2.arg2, ex.arg1.arg1, ex.arg2.arg1
                    ex = rSimp(uAdd(uSub(x, y), uAdd(a, b)))
                elif isnumber(ex.arg1.arg1) and isnumber(ex.arg2.arg2):
                    a, b, x, y = ex.arg1.arg1, ex.arg2.arg2, ex.arg1.arg2, ex.arg2.arg1
                    ex = rSimp(uAdd(uSub(x, y), uAdd(a, b)))
 
             
            elif ex.arg1.__class__.__name__ == 'uSub' and ex.arg2.__class__.__name__ == 'uSub':
                # (x - a) - (y - b) = (x - y) + (b - a)
                if isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg2):
                    a, b, x, y = ex.arg1.arg2, ex.arg2.arg2, ex.arg1.arg1, ex.arg2.arg1
                    if b >= a:
                        ex = rSimp(uAdd(uSub(x, y), uSub(b, a)))
                    else:
                        ex = rSimp(uSub(uSub(x, y), uSub(a, b)))
                # (x - a) - (b - y) = (x + y) - (a + b)
                elif isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg1):
                    a, b, x, y = ex.arg1.arg2, ex.arg2.arg1, ex.arg1.arg1, ex.arg2.arg2
                    ex = rSimp(uSub(uAdd(x, y), uAdd(a, b)))
                # (a - x) - (y - b) = (a + b) - (x + y)
                elif isnumber(ex.arg1.arg1) and isnumber(ex.arg2.arg2):
                    a, b, x, y = ex.arg1.arg1, ex.arg2.arg2, ex.arg1.arg2, ex.arg2.arg1
                    ex = rSimp(uSub(uAdd(a, b), uAdd(x, y)))
                # (a - x) - (b - y) = (y - x) + (a - b)
                elif isnumber(ex.arg1.arg1) and isnumber(ex.arg2.arg1):
                    a, b, x, y = ex.arg1.arg1, ex.arg2.arg1, ex.arg1.arg2, ex.arg2.arg2
                    if a >= b:
                        ex = rSimp(uAdd(uSub(y, x), uSub(a, b)))
                    else:
                        ex = rSimp(uSub(uSub(y, x), uSub(b, a)))
                    
            # a*x - x = (a-1)*x   and   x - a*x = 0 - (a-1)*x
            elif ex.arg1.__class__.__name__== 'uMul':
                if Same(ex.arg1.arg2, ex.arg2):
                    if isnumber(ex.arg1.arg1):
                        a, b, x = ex.arg1.arg1, 1, ex.arg2
                        ex = rSimp(uMul(uSub(a, b), x))
                elif Same(ex.arg1.arg1, ex.arg2):
                    if isnumber(ex.arg1.arg2):
                        a, b, x = ex.arg1.arg2, 1, ex.arg2
                        ex = rSimp(uMul(uSub(a, b), x))
                elif hasattr(ex.arg2, 'arg2') and Same(ex.arg1, ex.arg2.arg2):
                    if isnumber(ex.arg2.arg1):
                        a, b, x = ex.arg2.arg1, 1, ex.arg1
                        ex = rSimp(uMul(uSub(b, a), x))
                elif hasattr(ex.arg2, 'arg1') and Same(ex.arg1, ex.arg2.arg1):
                    if isnumber(ex.arg2.arg2):
                        a, b, x = ex.arg2.arg2, 1, ex.arg1
                        ex = rSimp(uMul(uSub(b, a), x))
            
            # a*x - b*x = (a - b)*x
            elif SameClass(ex.arg1, ex.arg2) and ex.arg1.__class__.__name__== 'uMul':
                if Same(ex.arg1.arg2, ex.arg2.arg2):
                    if isnumber(ex.arg1.arg1) and isnumber(ex.arg2.arg1):
                        a, b, x = ex.arg1.arg1, ex.arg2.arg1, ex.arg1.arg2
                        ex = rSimp(uMul(uSub(a, b), x))
                elif Same(ex.arg1.arg1, ex.arg2.arg2):
                    if isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg1):
                        a, b, x = ex.arg1.arg2, ex.arg2.arg1, ex.arg1.arg1
                        ex = rSimp(uMul(uSub(a, b), x))
                elif Same(ex.arg1.arg2, ex.arg2.arg1):
                    if isnumber(ex.arg1.arg1) and isnumber(ex.arg2.arg2):
                        a, b, x = ex.arg1.arg1, ex.arg2.arg2, ex.arg1.arg2
                        ex = rSimp(uMul(uAdd(a, b), x))
                elif Same(ex.arg1.arg1, ex.arg2.arg1):
                    if isnumber(ex.arg1.arg2) and isnumber(ex.arg2.arg2):
                        a, b, x = ex.arg1.arg2, ex.arg2.arg2, ex.arg1.arg1
                        ex = rSimp(uMul(uAdd(a, b), x))

        elif ex.__class__.__name__ == 'uMul':
            ex.arg1, ex.arg2 = Simp(ex.arg1), Simp(ex.arg2)
            # 0*a = 0
            if ex.arg1 == 0 or ex.arg2 == 0:
                ex = 0
            # 1*a = a
            elif ex.arg1 == 1:
                ex = ex.arg2
            elif ex.arg2 == 1:
                ex = ex.arg1
            elif isnumber(ex.arg1) and isnumber(ex.arg2):
                ex = ex.arg1 * ex.arg2
            
            # (0-y) * x = 0 - x*y   or   x * (0-y) = 0 - x*y
            elif ex.arg1.__class__.__name__ == 'uSub' and ex.arg1.arg1 == 0:
                ex = uSub(0, uMul(ex.arg2, ex.arg1.arg2))
            elif ex.arg2.__class__.__name__ == 'uSub' and ex.arg2.arg1 == 0:
                ex = uSub(0, uMul(ex.arg1, ex.arg2.arg2))
            
            # Prefer cannonical 2*x rather than x*2.
            elif not isnumber(ex.arg1) and isnumber(ex.arg2):
                ex.arg1, ex.arg2 = ex.arg2, ex.arg1
                
            # a*(b*x) = (a*b)*x
            elif isnumber(ex.arg1) and ex.arg2.__class__.__name__ == 'uMul' and isnumber(ex.arg2.arg1):
                ex = uMul(uMul(ex.arg1, ex.arg2.arg1), ex.arg2.arg2)
            # a*(x*b) = (a*b)*x 
            elif isnumber(ex.arg1) and ex.arg2.__class__.__name__ == 'uMul' and isnumber(ex.arg2.arg2):
                ex = uMul(uMul(ex.arg1, ex.arg2.arg2), ex.arg2.arg1)
            # (a*x)*b = (a*b)*x
            elif isnumber(ex.arg2) and ex.arg1.__class__.__name__ == 'uMul' and isnumber(ex.arg1.arg1):
                ex = uMul(uMul(ex.arg2, ex.arg1.arg1), ex.arg1.arg2)
            # (x*a)*b = (a*b)*x
            elif isnumber(ex.arg2) and ex.arg1.__class__.__name__ == 'uMul' and isnumber(ex.arg1.arg2):
                ex = uMul(uMul(ex.arg2, ex.arg1.arg2), ex.arg1.arg1)
                
        elif ex.__class__.__name__ == 'uDiv':
            ex.arg1, ex.arg2 = Simp(ex.arg1), Simp(ex.arg2)
            # a/0 = Undefined
            if ex.arg2 == 0:
                print('ERROR: Division by 0')
                ex = 'Infinity'
            # a/1 = a
            elif ex.arg2 == 1:
                ex = ex.arg1
            # a/a = 1
            elif isnumber(ex.arg1) and isnumber(ex.arg2) and ex.arg1 == ex.arg2:
                ex = 1
            elif isinstance(ex.arg1, str) and isinstance(ex.arg2, str) and ex.arg1 == ex.arg2:
                ex = 1
            # 1/(1/a) = a
            elif ex.arg1 == 1 and ex.arg2.__class__.__name__ == 'uDiv' and ex.arg2.arg1 == 1:
                ex = ex.arg2.arg2
                    
        elif ex.__class__.__name__ == 'uPow':
            ex.arg1, ex.arg2 = rSimp(ex.arg1), rSimp(ex.arg2)
            if ex.arg1 == 0:
                ex = 0
            elif ex.arg1 == 1 or ex.arg2 == 0:
                ex = 1
            elif ex.arg2 == 1:
                ex = ex.arg1
            elif isnumber(ex.arg1) and (ex.arg1 > 0) and isnumber(ex.arg2):
                ex = ex.arg1 ** ex.arg2
                
        elif ex.__class__.__name__ == 'uExp':
            ex.arg1 = rSimp(ex.arg1)
            if ex.arg1 == 0:
                return 1
            elif ex.arg1.__class__.__name__ == 'uLn':
                ex = ex.arg1.arg1
                
        elif ex.__class__.__name__ == 'uLn':
            ex.arg1 = rSimp(ex.arg1)
            if ex.arg1 == 1:
                return 0
            elif ex.arg1.__class__.__name__ == 'uExp':
                ex = ex.arg1.arg1
                
    return ex


def rSimp(ex):
    # Repeatedly simplify ex until convergence.
    exx = Simp(ex)
    while not Eq(ex, exx):
        ex, exx = exx, Simp(exx)
    return exx


def Eq(a, b):
    ''' Check if two expression trees are isomorphic '''
    # Base cases - at a leaf
    if isnumber(a) and isnumber(b):
        if a == b:
            return True
        else:
            return False
    
    # Both a and b must be either numeric or not numeric.
    elif isnumber(a) != isnumber(b):
        return False
    
    # If one node is a string but not the other, the ASTs are different.
    elif (isinstance(a, str) and not isinstance(b, str)) or (not isinstance(a, str) and isinstance(b, str)):
        return False
    
    # If both nodes are strings, they must be the same string.
    elif isinstance(a, str) and isinstance(b, str):
        if a != b:
            return False
    
    # If these nodes are of different classes, the ASTs are different.
    elif a.__class__.__name__ != b.__class__.__name__:
        return False

    # If both nodes have a first argument...
    elif hasattr(a, 'arg1') and hasattr(b, 'arg1'):
        
        # These arguments must be equal.
        if not Eq(a.arg1, b.arg1):
            return False
        
        # These nodes must both have a second argument or neither has.
        elif hasattr(a, 'arg2') != hasattr(b, 'arg2'):
            return False
        
        # If they both have a second argument, these arguments must be equal.
        elif hasattr(a, 'arg2'):
            if not Eq(a.arg2, b.arg2):
                return False
    return True
    

def Flatten(e):
    ''' Input is an AST, output is a flattened tree. '''
    nodes = []
    stack = [e]
    while stack:
        cur_node = stack[0]
        stack = stack[1:]
        nodes.append(cur_node) 
        cur_node_children = []
        if hasattr(cur_node, 'arg1'):
            cur_node_children.append(cur_node.arg1)
        if hasattr(cur_node, 'arg2'):
            cur_node_children.append(cur_node.arg2)
        cur_node_children.reverse()
        for child in cur_node_children:
            stack.insert(0, child)
    for i in range(len(nodes)):
        if isnumber(nodes[i]):
            i += 1
            continue
        elif isinstance(nodes[i], str):
            i += 1
            continue
        # Replace ops with conventional notation.
        nam = nodes[i].__class__.__name__ 
        if nam in {'aConst', 'fConst'}:
            nodes[i] = Eval(nodes[i])
        if nam == 'uAdd':
            nodes[i] = '+'
        elif nam == 'uSub':
            nodes[i] = '-'
        elif nam == 'uMul':
            nodes[i] = '*'
        elif nam == 'uPow':
            nodes[i] = '^'
        elif nam == 'uDiv':
            nodes[i] = '/'
        elif nam == 'uExp':
            nodes[i] = 'e^'
        elif nam == 'uLn':
            nodes[i] = 'ln'
        elif nam == 'uSin':
            nodes[i] = 'sin'
        elif nam == 'uCos':
            nodes[i] = 'cos'
            
        i += 1

    return nodes


def AlgExp(es):
    ''' Input is a flattened AST tree. Output is the algebraic expression '''
    
    def simplify(e):
        e = rSimp(e)
        if isnumber(e):  e = str(e)
        return e
    
    if isnumber(es):  return str(e)
    if len(es) == 1 and isnumber(es[0]): return str(es[0])
        
    m = len(es)
    i = 0
    for i in range(m-1, -1, -1):
        if es[i] not in {'+', '-', '*', '/', '^', 'e^', 'ln', 'sin', 'cos'}: 
            continue
        op = es[i]
        if op in {'+','-'}:
            arg2 = es.pop(i + 2); arg1 = es.pop(i + 1)
            arg1, arg2 = simplify(arg1), simplify(arg2)
            es[i] = '(' + arg1 + op + arg2 + ')'
            ## print(es)
        elif op in {'*', '/'}:
            arg2 = es.pop(i + 2); arg1 = es.pop(i + 1)
            arg1, arg2 = simplify(arg1), simplify(arg2)
            es[i] = arg1 + op + arg2
            ## print(es)
        elif op == '^':
            arg2 = es.pop(i + 2); arg1 = es.pop(i + 1)
            arg1, arg2 = simplify(arg1), simplify(arg2)
            es[i] = arg1 + op + arg2 
            ## print(es)
        elif op in {'e^','ln', 'sin', 'cos'}:
            arg1 = es.pop(i + 1)
            arg1 = simplify(arg1)
            if arg1[0] == '(' and arg1[-1] == ')':
                es[i] = op + arg1
            else:
                es[i] = op + '(' + arg1 + ')'
            ## print(es)
    expr = es[0]
    lp, rp = '(', ')'
    if expr[0] == lp and expr[-1] == rp:
        if not ((lp in expr[1:]) and (expr[1:].index(rp) < expr[1:].index(lp))):
            expr = expr[1: -1]
    ## print(); print(expr)
    return expr


def Examine(e):
    ''' This prints out an AST, for debugging purposes'''
    print('.'*40)
    # Base cases - at a leaf
    if isnumber(e):
        print(e)
    elif isinstance(e, str):
        if e in Store:
            print(Store[e])
        else:
            print(e)
    else: 
        if e != None:
            print(e)
        else:
            print('?? Why was Examine(None) called ??')
    if hasattr(e, 'arg1'):  
        if e.arg1 == None:
            print('?? ', e, ' has an arg1 == None ??')
        else:
            Examine(e.arg1)
    if hasattr(e, 'arg2'):  
        if e.arg1 == None:
            print('?? ', e, ' has an arg2 == None ??')
        else:
            Examine(e.arg2)


def Depth(x, ex):
    ''' Input x = variable, ex = AST.  Returns the shallowest depth of x in AST ex,
        or 0 if x doesn't occur in ex.  '''
    if x == ex:
        return 1
    elif hasattr(ex, 'arg1'):
        depth = [Depth(x, ex.arg1),]
        if hasattr(ex, 'arg2'):
            depth.append(Depth(x, ex.arg2))
        depth = list(set(depth))
        if len(depth) == 1 and 0 in depth:
            return 0
        if 0 in depth:  
            depth.pop(depth.index(0))
        return 1 + min(depth)
    else:
        return 0
         

def Solve(ex1, ex2, x):
    ''' Solves the equation e1 = e2 for variable x, where e1 and e2 are algebraic ASTs '''
    e1, e2 = deepcopy(rSimp(ex1)), deepcopy(rSimp(ex2))
    
    # If the variable to be solved for is on the right side of the equal sign,
    # but not on the left, switch sides, so the variable to be solved for is 
    # always on the right.
    if Depth(x, e1) == 0 and Depth(x, e2) > 0:  return Solve(e2, e1, x)
    
    if Depth(x, e1) == 1 and not Depth(x, e2):
        return e2
    elif Depth(x, e1) == 2 and not Depth(x, e2):
        # x + a = b
        if e1.__class__.__name__ == 'uAdd':
            if e1.arg1 == x:
                return uSub(e2, e1.arg2)
            elif e1.arg2 == x:
                return uSub(e2, e1.arg1)
        # x - a = b   or   a - x = b
        elif e1.__class__.__name__ == 'uSub':
            if e1.arg1 == x:
                return uAdd(e2, e1.arg2)
            elif e1.arg2 == x:
                return uSub(e1.arg1, e2)
        # a*x = b
        elif e1.__class__.__name__ == 'uMul':
            if e1.arg1 == x:
                return uDiv(e2, e1.arg2)
            elif e1.arg2 == x:
                return uDiv(e2, e1.arg1)
        # x/a = b
        elif e1.__class__.__name__ == 'uDiv':
            if e1.arg1 == x:
                return uMul(e2, e1.arg2)
            elif e1.arg2 == x:
                return uDiv(e1.arg1, e2)
        elif e1.__class__.__name__ == 'uExp':
            return uLn(e2)
        elif e1.__class__.__name__ == 'uLn':
            return uExp(e2)
        
    elif Depth(x, e1) > 2 and not Depth(x, e2):
        
        if e1.__class__.__name__ == 'uAdd':
            if Depth(x, e1.arg1) > 1 and Depth(x, e1.arg2) == 0:
                return Solve(e1.arg1, uSub(e2, e1.arg2), x)
            elif Depth(x, e1.arg1) == 0 and Depth(x, e1.arg2) > 1:
                return Solve(e1.arg2, uSub(e2, e1.arg1), x)
        
        elif e1.__class__.__name__ == 'uSub':
            if Depth(x, e1.arg1) > 1 and Depth(x, e1.arg2) == 0:
                return Solve(e1.arg1, uAdd(e2, e1.arg2), x)
            elif Depth(x, e1.arg1) == 0 and Depth(x, e1.arg2) > 1:
                return Solve(e1.arg2, uSub(e1.arg1, e2), x)
            
        elif e1.__class__.__name__ == 'uMul':
            if Depth(x, e1.arg1) > 1 and Depth(x, e1.arg2) == 0:
                return Solve(e1.arg1, uDiv(e2, e1.arg2), x)
            elif Depth(x, e1.arg1) == 0 and Depth(x, e1.arg2) > 1:
                return Solve(e1.arg2, uDiv(e2, e1.arg1), x)
    
        elif e1.__class__.__name__ == 'uDiv':
            if Depth(x, e1.arg1) > 1 and Depth(x, e1.arg2) == 0:
                return Solve(e1.arg1, uMul(e2, e1.arg2), x)
            elif Depth(x, e1.arg1) == 0 and Depth(x, e1.arg2) > 1:
                return Solve(e1.arg2, uDiv(e1.arg1, e2), x)
            
        elif e1.__class__.__name__ == 'uExp' and Depth(x, e1.arg1) > 1:
            return Solve(e1.arg1, uLn(e2), x)
        
        elif e1.__class__.__name__ == 'uLn' and Depth(x, e1.arg1) > 1:
            return Solve(e1.arg1, uExp(e2), x)
    
    elif Depth(x, e1) >= 2 and Depth(x, e2) == 1:
        
        # NOTE: Depth(x, e2) == 1   ==>   e2 == x.
        if e1.__class__.__name__ == 'uAdd':
            if Depth(x, e1.arg2) == 0:
                return Solve(uSub(e1.arg1, x), uSub(0, e1.arg2), x)
            elif Depth(x, e1.arg1) == 0:
                return Solve(uSub(e1.arg2, x), uSub(0, e1.arg1), x)
            
        elif e1.__class__.__name__ == 'uSub':
            if Depth(x, e1.arg2) == 0:
                return Solve(uSub(e1.arg1, x), e1.arg2, x)
            elif Depth(x, e1.arg1) == 0:
                return Solve(uAdd(e1.arg2, x), e1.arg1, x)
            
        elif e1.__class__.__name__ == 'uMul':
            if Depth(x, e1.arg2) == 0:
                return Solve(uSub(e1.arg1, x), uDiv(1, e1.arg2), x)
            elif Depth(x, e1.arg1) == 0:
                return Solve(uSub(e1.arg2, x), uDiv(1, e1.arg1), x)
            
        elif e1.__class__.__name__ == 'uDiv':
            if Depth(x, e1.arg2) == 0:
                return Solve(uSub(e1.arg1, x), e1.arg2, x)
            elif Depth(x, e1.arg1) == 0:
                return Solve(uMul(e1.arg2, x), e1.arg1, x)
                
    elif Depth(x, e1) == 3 and Depth(x, e2) == 3:
        if e1.__class__.__name__ == 'uAdd' and e2.__class__.__name__ == 'uAdd':
            if e1.arg1.__class__.__name__ == 'uMul' and e2.arg1.__class__.__name__ == 'uMul':
                if e1.arg1.arg2 == x and e2.arg1.arg2 == x:
                    a, b, c, d = e1.arg1.arg1, e1.arg2, e2.arg1.arg1, e2.arg2 
                    return Solve(uMul(uSub(a, c), x), uSub(d, b), x)
                elif e1.arg1.arg2 == x and e2.arg1.arg1 == x:
                    e2.arg1.arg1, e2.arg1.arg2 = e2.arg1.arg2, e2.arg1.arg1
                    return Solve(e1, e2, x)
                elif e1.arg1.arg1 == x and e2.arg1.arg2 == x:
                    e1.arg1.arg1, e1.arg1.arg2 = e1.arg1.arg2, e1.arg1.arg1
                    return Solve(e1, e2, x)
                elif e1.arg1.arg1 == x and e2.arg1.arg1 == x:
                    e1.arg1.arg1, e1.arg1.arg2 = e1.arg1.arg2, e1.arg1.arg1
                    e2.arg1.arg1, e2.arg1.arg2 = e2.arg1.arg2, e2.arg1.arg1
                    return Solve(e1, e2, x)
                
        

### ############# #
## ### TESTS ### ##
# ############# ###

#
# Tests of Arithmetic Simplification 
#             
print(); print('Tests of arithmetic simplification'); print()

Store['x'] = 5
Store['y'] = 5
if Eq(Simp('x'), Simp('y')) == True:
    print('Test 1 passed!')
else:
    print("ERROR: two equal variables, but Eq thinks they aren't")
    
if Eq(uMul(1,4), uAdd(1,4)) == False:
    print('Test 2 passed!')
else: 
    print("ERROR: two different operations Eq thinks are equal")

if Eq(uMul(1,4), uMul(2,3)) == False:
    print('Test 3 passed!')
else: 
    print("ERROR: two different expressions Eq thinks are equal")
    
if Eq(uMul(1,4), uMul(2,2)) == False:
    print('Test 4 passed!')
else: 
    print("ERROR: two different expressions Eq thinks are equal")
    
if Eq(Simp(uMul(1,4)), Simp(uMul(2,2))) == True:
    print('Test 5 passed!')
else: 
    print("ERROR: two equal expressions Eq thinks aren't")
    
if 'x' in Store:
    del Store['x']
e1 = uPow('x', 3)
e2 = uPow('x', 3)
if Eq(e1, e2):
    print('Test 6 passed!')
else:
    print("ERROR: two equal expressions Eq thinks aren't")

if 'x' in Store:
    del Store['x']
e1 = D(uPow('x', 3), 'x')
e2 = D(uPow('x', 3), 'x')
if Eq(e1, e2):
    print('Test 7 passed!')
else:
    print("ERROR: two equal expressions Eq thinks aren't")

A = D(uMul(uAdd('y', 3), uPow('y', 2)), 'y')
B = D(uMul(uAdd('y', 3), uPow('y', 2)), 'y')
if Eq(e1, e2):
    print('Test 8 passed!')
else:
    print("ERROR: two equal expressions Eq thinks aren't")

Store['x'] = 2
e = uPow('x',1)
if rSimp(e) == 2:
    print('Test 9 passed!')
else:
    print("ERROR: expression simplified incorrectly")

e = uAdd(1, 3)
if Simp(e) == 4:
    print('Test A passed!')
else:
    print("ERROR: expression simplified incorrectly")

e = uMul(0, uPow(5, 3))
if rSimp(e) == 0:
    print('Test B passed!')
else:
    print("ERROR: expression simplified incorrectly")

Store['x'] = 3
e = uAdd('x', 2)
if Simp(e) == 5:
    print('Test C passed!')
else:
    print("ERROR: expression simplified incorrectly")

#
# Tests of Flatten and AlgExp
#             
print(); print('Tests of Flatten and AlgExp'); print()  
      
Store = dict()   
e = uMul(uLn('a'), uPow('b', 'c'))
if AlgExp(Flatten(rSimp(e))) == 'ln(a)*b^c':
    print('Test D passed!')
else:
    print("ERROR: Incorrect output from AlgExp(Flatten(e))")
    
e = uExp(uAdd('c', uDiv('d','b')))
if AlgExp(Flatten(rSimp(e))) == 'e^(c+d/b)':
    print('Test E passed!')
else:
    print("ERROR: Incorrect output from AlgExp(Flatten(e))")
    
Store = dict()
e = uExp(uDiv(uAdd('c','d'),'b'))
if AlgExp(Flatten(rSimp(e))) == 'e^((c+d)/b)':
    print('Test F passed!')
else:
    print("ERROR: Incorrect output from AlgExp(Flatten(e))")
    
Store = dict()
e = uAdd(uMul(uLn('a'), uExp(uAdd('c', uDiv('d','e')))), uPow('b','g'))
if AlgExp(Flatten(rSimp(e))) == 'ln(a)*e^(c+d/e)+b^g':
    print('Test 10 passed!')
else:
    print("ERROR: Incorrect output from AlgExp(Flatten(e))")


#
# Tests of Algebraic Simplification
#
print(); print('Tests of Algebraic Simplification'); print()
    
# 2*z + 3*z = 5*z
Store = dict()
e = uAdd(uMul(2, 'z'), uMul(3, 'z'))
if AlgExp(Flatten(rSimp(e))) == '5*z':
    print('Test 11 passed!')
else:
    print("ERROR: expression simplified incorrectly")

# (0-x) * y = 0 - x*y
e = uMul(uSub(0,'x'), 'y')
if AlgExp(Flatten(rSimp(e))) == '0-y*x':
    print('Test 12 passed!')
else:
    print("ERROR: expression simplified incorrectly")
    
# x + (0-y)*z = x - z*y
Store = dict()
flag = True
e = uAdd('x', uMul(uSub(0,'y'), 'z'))
if AlgExp(Flatten(rSimp(e))) != 'x-z*y': flag = False
# (0-y)*z + x = x - z*y
Store = dict()
e = uAdd(uMul(uSub(0,'y'), 'z'), 'x')
if flag and AlgExp(Flatten(rSimp(e))) == 'x-z*y':
    print("Test 13 passed!")
else:
    print("ERROR: expression simplified incorrectly")
    
# (x-a) + b = x + (b-a)
Store = dict()
e = uAdd(uSub('x', 4), 7)
if AlgExp(Flatten(rSimp(e))) == 'x+3':
    print('Test 14 passed!')
else:
    print("ERROR: expression simplified incorrectly")
e = uAdd(uSub('x', 7), 4)
if AlgExp(Flatten(rSimp(e))) == 'x-3':
    print('Test 15 passed!')
else:
    print("ERROR: expression simplified incorrectly")
    
# a + (x-b) = x + (a-b)
Store = dict()
e = uAdd(7, uSub('x', 4))
if AlgExp(Flatten(rSimp(e))) == 'x+3':
    print('Test 16 passed!')
else:
    print("ERROR: expression simplified incorrectly")
e = uAdd(4, uSub('x', 7))
if AlgExp(Flatten(rSimp(e))) == 'x-3':
    print('Test 17 passed!')
else:
    print("ERROR: expression simplified incorrectly")

# (a-x) + b = (a+b) - x  
Store = dict()
e = uAdd(uSub(5, 'x'), 7)
if AlgExp(Flatten(rSimp(e))) == '12-x':
    print('Test 18 passed!')
else:
    print("ERROR: expression simplified incorrectly")
    
# 2 + (3-x) = (2+3) - x    
Store = dict()
e = uAdd(2, uSub(3, 'x'))
if AlgExp(Flatten(rSimp(e))) == '5-x':
    print('Test 19 passed!')
else:
    print("ERROR: expression simplified incorrectly")

# (x-2) + (x+3) = 2x + 1   
e = uAdd(uSub('x', 2), uAdd('x', 3))
if AlgExp(Flatten(rSimp(e))) == '2*x+1':
    print('Test 1A passed!')
else:
    print("ERROR: expression simplified incorrectly")
    
# (x+3) + (x-2) = 2x + 1   
e = uAdd(uSub('x', 2), uAdd('x', 3))
if AlgExp(Flatten(rSimp(e))) == '2*x+1':
    print('Test 1B passed!')
else:
    print("ERROR: expression simplified incorrectly")
    
# (x-3) + (x+2) = 2x - 1   
e = uAdd(uSub('x', 3), uAdd('x', 2))
if AlgExp(Flatten(rSimp(e))) == '2*x-1':
    print('Test 1C passed!')
else:
    print("ERROR: expression simplified incorrectly")
    
# (x+2) + (x-3) = 2x - 1   
e = uAdd(uAdd('x', 2), uSub('x', 3))
if AlgExp(Flatten(rSimp(e))) == '2*x-1':
    print('Test 1D passed!')
else:
    print("ERROR: expression simplified incorrectly")
    
# (x-4) + (x-3) = 2x - 7
e = uAdd(uSub('x', 4), uSub('x', 3))
if AlgExp(Flatten(rSimp(e))) == '2*x-7':
    print('Test 1E passed!')
else:
    print("ERROR: expression simplified incorrectly") 
    
# (7-x) + (x-3) = 4
e = uAdd(uSub(7, 'x'), uSub('x', 3))
if AlgExp(Flatten(rSimp(e))) == '4':
    print('Test 1F passed!')  
else:
    print("ERROR: expression simplified incorrectly") 
    
# (2*x-3) + (5-x) = 2
e = uAdd(uSub(uMul(2, 'x'), 3), uSub(5, 'x'))
if AlgExp(Flatten(rSimp(e))) == 'x+2':
    print('Test 20 passed!')  
else:
    print("ERROR: expression simplified incorrectly")

# (3-x) + (5-x) = 8 - 2*x
e = uAdd(uSub(3, 'x'), uSub(5, 'x'))
if AlgExp(Flatten(rSimp(e))) == '8-2*x':
    print('Test 21 passed!')  
else:
    print("ERROR: expression simplified incorrectly")
    
    
#
# Tests of Derivative Calculations
#
print(); print('Tests of Derivative Calculations'); print()

# The power rule
if 'x' in Store: del Store['x']
e = D(D(uPow('x',3),'x'),'x')
if AlgExp(Flatten(rSimp(e))) == '6*x':
    print('Test 22 passed!')
else:
    print("ERROR: expression simplified incorrectly")

# The derivative of a constant function.
Store = dict()
if D(5, 'x') == 0:
    print('Test 23 passed!')
else:
    print('Error: D(constant) != 0')
if D(Eval(Assign('y', 3)), 'x') == 0:
    print('Test 24 passed!')
else:
    print('Error: D(constant) != 0')
    
# The derivative of x w.r.t x.
Store = dict()
if D('x', 'x') == 1:
    print('Test 25 passed!')
else:
    print('Error: D(x, x) != 1')
    
# The (partial) derivative of y w.r.t x.
Store = dict()
if D('y', 'x') == 0:
    print('Test 26 passed!')
else:
    print('Error: D(y, x) != 0')
    
# The power rule
Store = dict()
ex = D(uPow('x', 3), 'x')
if AlgExp(Flatten(ex)) == '3*x^2':
    print('Test 27 passed!')
else:
    print('Error: D(x^3) != 3x^2')

# The power rule
Store = dict()
e = D(D(uPow('x', 5), 'x'), 'x')
if AlgExp(Flatten(rSimp(e))) == '20*x^3':
    print('Test 28 passed!')
else:
    print('Error: D(D(x^5)) != 20x^3')  

# The chain rule
Store = dict()
e = uPow(uSin('x'), 3)
ex = D(e, 'x')
if AlgExp(Flatten(ex)) == '3*sin(x)^2*cos(x)':
    print('Test 29 passed!')
else:
    print('Error: D(sin(x)^3) != 3*sin(x)^2*cos(x)')

Store = dict()
e = uAdd(uAdd('x', 3), 4)  
if AlgExp(Flatten(rSimp(e))) ==  '7+x':
    print('Test 2A passed!')
else:
    print('ERROR: Combining like terms in adding an add')

# The product rule
Store = dict()
e = D(uMul(uAdd('x', 3), uAdd('x', 2)), 'x') 
if AlgExp(Flatten(rSimp(e))) == '5+2*x':
    print('Test 2B passed!')
else:
    print('ERROR: Combining like terms in adding an add')
    

#
# Tests of Solving Equations
#
print(); print('Tests of Solving Equations'); print()

# sin(y) + x = ln(1 + e^2)
Store = dict()
e1, e2 = uAdd(uSin('y'), 'x'), uLn(uAdd(1,uExp(2)))
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == 'ln(1+e^(2))-sin(y)':
    print('Test 2C passed!')
else:
    print("ERROR: sin(y) + x = ln(1 + e^2) solved incorrectly")

# sin(y) - x = ln(1 + e^2)
Store = dict()
e1, e2 = uSub(uSin('y'), 'x'), uLn(uAdd(1,uExp(2)))
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == 'sin(y)-ln(1+e^(2))':
    print('Test 2D passed!')
else:
    print("ERROR: sin(y) - x = ln(1 + e^2) solved incorrectly")

# sin(y) * x = ln(1 + e^2)
Store = dict()
e1, e2 = uMul(uSin('y'), 'x'), uLn(uAdd(1,uExp(2)))
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == 'ln(1+e^(2))/sin(y)':
    print('Test 2E passed!')
else:
    print("ERROR: sin(y) - x = ln(1 + e^2) solved incorrectly")

# sin(y)/x = ln(1 + e^2)
Store = dict()
e1, e2 = uDiv(uSin('y'), 'x'), uLn(uAdd(1,uExp(2)))
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == 'sin(y)/ln(1+e^(2))':
    print('Test 2F passed!')
else:
    print("ERROR: sin(y)/x = ln(1 + e^2) solved incorrectly")

# e^x = 1 + e^2
Store = dict()
e1, e2 = uExp('x'), uAdd(1,uExp(2))
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == 'ln(1+e^(2))':
    print('Test 30 passed!')
else:
    print("ERROR: e^x = 1 + e^2 solved incorrectly")

# ln(x) = 2 + sin(y)
Store = dict()
e1, e2 = uLn('x'), uAdd(2,uSin('y'))
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == 'e^(2+sin(y))':
    print('Test 31 passed!')
else:
    print("ERROR: ln(x) = 2 + sin(y) solved incorrectly")

# 2 + sin(y) = ln(x)
Store = dict()
e2, e1 = uLn('x'), uSub(3,uCos('y'))
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == 'e^(3-cos(y))':
    print('Test 32 passed!')
else:
    print("ERROR: 2 + sin(y) = ln(x) solved incorrectly")

# a*x + b = c
Store = dict()
e1, e2 = uAdd(uMul('a', 'x'), 'b'), 'c'
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == '(c-b)/a':
    print('Test 33 passed!')
else:
    print("ERROR: a*x + b = c solved incorrectly")

# e^b = a + ln(x)
Store = dict()
e1, e2 = uExp('b'), uAdd(uLn('x'), 'a')
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == 'e^(e^(b)-a)':
    print('Test 34 passed!')
else:
    print("ERROR: e^b = a + ln(x) solved incorrectly")

# e^b = a - ln(x)
Store = dict()
e1, e2 = uExp('b'), uSub('a', uLn('x'))
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == 'e^(a-e^(b))':
    print('Test 35 passed!')
else:
    print("ERROR: e^b = a - ln(x) solved incorrectly")

# d = a*ln(x) + b
Store = dict()
e1, e2 = uAdd(uMul('a', uLn('x')), 'b'), 'd'
sol = rSimp(Solve(e2, e1, 'x'))
if AlgExp(Flatten(sol)) == 'e^((d-b)/a)':
    print('Test 36 passed!')
else:
    print("ERROR: d = a*ln(x) + b solved incorrectly")

# 2 = ln(1 + e^x)
Store = dict()
e1, e2 = 2, uLn(uAdd(1, uExp('x')))
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == 'ln(e^(2)-1)':
    print('Test 37 passed!')
else:
    print("ERROR: 2 = ln(1 + e^x) solved incorrectly")
    
# ln(1 + e^(2 + ln(x))) = 3 
Store = dict()
e1, e2 = uLn(uAdd(1, uExp(uAdd(2, uLn('x'))))), 3
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == 'e^(ln(e^(3)-1)-2)':
    print('Test 38 passed!')
else:
    print("ERROR: ln(1 + e^(2 + ln(x))) = 3 solved incorrectly")

# a*x + b = c*x + d
Store = dict()
e1, e2 = uAdd(uMul('a', 'x'), 'b'), uAdd(uMul('c', 'x'), 'd')
sol = rSimp(Solve(e1, e2, 'x'))
if AlgExp(Flatten(sol)) == '(d-b)/(a-c)':
    print('Test 39 passed!')
else:
    print("ERROR: a*x + b = c*x + d solved incorrectly")   
   

################################################################################################################

#
# Test Cases for While Interpreter
#
print(); print('Test Cases for While Interpreter');  print()

# Create an AST for a constant ARITH expression.
Ex = FConst(42.1)
# Evaluate this AST
if Eval(Ex) == 42.1:
    print('Test passed!')
else:
    print('Error interpreting a CONST')

# HELPER FUNCTION for testing floating point operations
from math import isclose

# Create an AST for the ARITH expression, 42.3 + 24.3
Ex = Add(FConst(42.3), FConst(24.3))

# Evaluate this AST
if isclose(Eval(Ex), 66.6):
    print('Test passed!')
else:
    print('Error interpreting +')

# Create an AST for the ARITH expression 4*5.
Ex = Mul(FConst(4.2), FConst(5.1))

# Evaluate this AST
if isclose(Eval(Ex), 21.42):
    print('Test passed!')
else:
    print('Error interpreting *')


# Now some less trivial cases!   :)
    
# Test case:  a*b + c*d  
# for all values of a,b,c,d in [-2.3,-1.8,-0.6,-0.2,-1.0, 0.2, 0.4, 0.6, 1.8, 2.4].
    
R = [-2.3,-1.8,-0.6,-0.2,-1.0, 0.2, 0.4, 0.6, 1.8, 2.4]
error_flag = False
for a in R:
    for b in R:
        for c in R:
            for d in R:
                result = b*sin(a) + c*log(d**2)/log(3)    # to check EVAL output
                
                # Create the AST for a*b + c*d.
                Ex = Add(Mul(Sin(FConst(a)), FConst(b)), Mul(FConst(c), Log(Exp(FConst(d), AConst(2)), AConst(3))))

                if not isclose(Eval(Ex), result):
                    print('Error interpreting  a*b + c*d')
                    error_flag = True

if not error_flag:  print('All', len(R)**4, 'test cases passed!!')


# Test case:  a*(b + (c*sin(c))**d) / (b*d)  
# for all values of a,b,c,d in R.
error_flag = False
for a in R:
    for b in R:
        for c in R:
            for d in R:
                result = a*(b + (c*sin(c))**d) / (b*d)      # to check EVAL output
                
                # Create the AST for a*(b + c) + b*d .
                Ex = Div(Mul(FConst(a), Add(FConst(b), Exp(Mul(FConst(c), Sin(FConst(c))), FConst(d)) )), Mul(FConst(b), FConst(d)))

                if not isclose(Eval(Ex), result):
                    print('Error interpreting  a*(b + (c*sin(c))**d) / (b*d) ')
                    print(Eval(Ex), result)
                    error_flag = True

if not error_flag:  print('All', len(R)**4, 'test cases passed!!')


#
# Tests of While Interpreter Commands
#
print(); print('Tests of While Interpreter Commands');  print()

#  Test cases for the assignment command and arithmetic variables (stored in Store),
#  as well as Boolean expressions involving arithmetic variables.

Store = dict()  # clear/initialize Store

# Assign a value to variable 'd'
Eval(Assign('d', AConst(1)))
if Eval(Store['d']) != 1:  
    print("ERROR: problem assigning value 1 to variable 'd' ")
else:
    print('Test passed!')
    
Eval(Assign('d', FConst(2.3)))
if Eval(Store['d']) != 2.3:  
    print("ERROR: problem reassigning value 2.3 to variable 'd' ")
else:
    print('Test passed!')

# Incrementing a variable
Eval(Assign('d', Add('d', AConst(1))))
if Eval(Store['d']) != 3.3:  
    print("ERROR: problem reassigning value 2 to variable 'd' ")
else:
    print('Test passed!')

# Assigning a more complex arithmetic expression to variable 'c'
Eval(Assign('c', Sub(Mul(AConst(2), FConst(5.4)), Add(FConst(4.7), AConst(1)))))
if not isclose(Eval(Store['c']), 5.1):  
    print("ERROR: problem reassigning value 2 to variable 'd' ")
else:
    print('Test passed!')


# Evaluating Boolean expressions involving variables
Eval(Assign('c', AConst(5)))
if not Eval(IsEqual('c', AConst(5))): 
    print("ERROR: problem evaluating equality with a variable")
else:
    print('Test passed!')
    
if not Eval(IsLess('d', 'c')): 
    print("ERROR: problem evaluating inequality with variables")
else:
    print('Test passed!')
    
if not Eval(IsLess('c', Add('d', FConst(4.9)))): 
    print("ERROR: problem evaluating inequality with variables")
else:
    print('Test passed!')

# Test case for Skip command
if Eval(Skip()) is None:   # Does nothing, as expected
    print('Test passed!')
else:
    print("ERROR: Skip() didn't")


# Test cases for Seq command

Eval(Seq(Skip(), Assign('b', FConst(10.4))))
if Eval(Store['b']) != 10.4:
    print("ERROR: problem evaluating Seq command")
else:
    print('Test passed!')
    
Eval(Seq(Assign('a', FConst(7.7)), Assign('e', AConst(17))))
if Eval(Store['a']) != 7.7 or Eval(Store['e']) != 17:
    print("ERROR: problem evaluating Seq command")
else:
    print('Test passed!')

Eval(Assign('a', FConst(1.2))); Eval(Assign('b', FConst(3.4))); Eval(Assign('c', FConst(5.6)))
Eval(Seq(Assign('a', 'b'), Assign('b', 'c')))
if Eval(Store['a']) != 3.4 or Eval(Store['b']) != 5.6:
    print("ERROR: problem evaluating Seq command")
else:
    print('Test passed!')
   
Eval(Assign('a', FConst(1.1))); Eval(Assign('b', FConst(2.2))); Eval(Assign('c', FConst(3.3)));
Eval(Seq(Assign('a', 'b'), Assign('c', 'a')))
if Eval(Store['a']) != 2.2 or Eval(Store['b']) != 2.2 or Eval(Store['c']) != 2.2:
    print("ERROR: problem evaluating Seq command")
else:
    print('Test passed!')

Eval(Assign('a', FConst(1.6))); Eval(Assign('b', FConst(5.9))); Eval(Assign('c', FConst(2.1))); Eval(Assign('d', FConst(7.9)))
Eval(Seq(Seq(Assign('a', 'b'), Assign('c', 'a')), Assign('d', 'c')))
if Eval(Store['a']) != 5.9 or Eval(Store['b']) != 5.9 or Eval(Store['c']) != 5.9 or Eval(Store['d']) != 5.9:
    print("ERROR: problem evaluating Seq command")
else:
    print('Test passed!')


# Test cases for IfThen command

t, c1, c2 = BConst(True), AConst(1), AConst(2)
if Eval(IfThen(t, c1, c2)) != 1:  
    print("ERROR: problem evaluating IfThen command")
else:
    print('Test passed!')
  
f = BConst(False)
if Eval(IfThen(f, c1, c2)) != 2:  
    print("ERROR: problem evaluating IfThen command")
else:
    print('Test passed!')

b, a1, a2 = Or(t, f), Mul(FConst(2.2), AConst(3)), Add(AConst(2), FConst(3))
if not isclose(Eval(IfThen(b, a1, a2)), 6.6):
    print("ERROR: problem evaluating IfThen command")
else:
    print('Test passed!')

x1, x2 = FConst(1.3), AConst(3)
b, x, y = And(t, f), Assign('x', Mul(x1, x2)), Assign('y', Add(x1, x2))
if not isclose(Eval(IfThen(b, x, y)), 4.3):
    print("ERROR: problem evaluating IfThen command")
else:
    print('Test passed!')

b = Not(b)
if not isclose(Eval(IfThen(b, x, y)), 3.9):
    print("ERROR: problem evaluating IfThen command")
else:
    print('Test passed!')


# Test cases for While command

# Initialize values for loop.
Eval(Assign('x', AConst(0)))  # set variable x = 0
# Loop away!
# Increment variable x while it's less than 5.
Eval(While(IsLess('x', AConst(5)), Assign('x', Add('x', AConst(1)))))
# So after the loop, variable x should equal 5.
if Store['x'] != 5:
    print("ERROR: problem evaluating While command")
else:
    print('Test passed!')


#
# Tests of GCD algorithm
#
print(); print('Tests of GCD algorithm'); print()

# In this extension of While, Euclid's algorithm has been implemented as an operation.
    
if Eval(GCD(AConst(15), AConst(20))) != 5:
    print("ERROR: problem running GCD operation")
else:
    print('Test passed!')

if Eval(GCD(AConst(26502), AConst(54282))) != 6:
    print("ERROR: problem running GCD operation")
else:
    print('Test passed!')

if Eval(GCD(AConst(408), AConst(425))) != 17:
    print("ERROR: problem running GCD operation")
else:
    print('Test passed!')
    
if Eval(GCD(AConst(22220), AConst(19089))) != 101:
    print("ERROR: problem running GCD operation")
else:
    print('Test passed!')

