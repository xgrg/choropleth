#!/usr/bin/env python
# -*- coding: utf-8 -*-

def parse_function(f):
   import string

   # trim leading @ and remove spaces
   f = f[f.find('@')+1:].lower()
   f = ''.join([each for each in f if each != ' '])
   assert(f.count('(') == f.count(')'))

   def find(f, char):
      res = []
      last = 0
      while last != -1:
         last = f.find(char, last)
         if last != -1:
            res.append(f.find(char, last))
      return res

   # if no function at all (lowest level) return the string as an end parameter
   if f.count('(') == 0:
      try:
         return string.atoi(f)
      except ValueError:
         return f

   else:
      #parse function and solve inner function
      fname, endf = f[:f.find('(')], f[f.find('(') + 1:]
      depth = 1
      parend = 0
      params = []
      comma = -1

      while parend < len(endf):
         if endf[parend] == '(': depth = depth + 1
         elif endf[parend] == ')': depth = depth - 1
         elif endf[parend] == ',' and depth == 1:
            prev_comma = comma
            comma = parend
            params.append(endf[prev_comma + 1:comma])
         parend = parend + 1

      parsed_params = [parse_function(p) for p in params]
      parsed_params.append(parse_function(endf[comma+1:-1]))
      res = [fname]
      res.extend(parsed_params)
      return tuple(res)

def solve_function(operations, model = None):

   fname = operations[0]
   params = []
   for o in operations[1:]:
      if isinstance(o, tuple):
         params.append(solve_function(o, model = model))
      elif isinstance(o, int):
         params.append(o)
      elif isinstance(o, basestring):
         if '.' in o:
            obj, prop = o.split('.')
            params.append(model[obj][prop])
         else:
            params.append(o)
      else:
         raise Exception('Operation type not recognized : %s (%s)'%(o, type(o)))

   if fname == 'add':
      res = 0
      for p in params:
         res += p
      return res
   elif fname == 'value':
      if len(params) !=1: raise Exception('Function VALUE should have 1 parameter (%s given)'%len(params))
      return params[0]
   elif fname == 'append':
      if len(params) !=2: raise Exception('Function APPEND should have 2 parameters (%s given)'%len(params))
      assert(isinstance(params[0], list))
      t = list(set(params[0]))
      t.append(params[1])
      return t
   elif fname == 'remove':
      if len(params) !=2: raise Exception('Function REMOVE should have 2 parameters (%s given)'%len(params))
      assert(isinstance(params[0], list))
      t = list(set(params[0]))
      t.remove(params[1])
      return t


   raise Exception('Operation type not recognized : %s'%o)
