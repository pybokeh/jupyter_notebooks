#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import simplejson as json
import pyparsing
from jpype import *

class PennTreebackChunker(object):
  def __init__(self):
    path = os.path.realpath(__file__)
    path = path[:path.rfind(os.sep)] + os.sep + 'jars'
    classpath = os.pathsep.join(path+os.sep+jar for jar in os.listdir(path))
    startJVM(getDefaultJVMPath(), "-Djava.class.path=%s" % classpath)    
    String = JClass("java.lang.String")
    self.StringReader = JClass("java.io.StringReader")
    self.StringWriter = JClass("java.io.StringWriter")
    self.PrintWriter = JClass("java.io.PrintWriter")
    PTBTokenizer = JClass("edu.stanford.nlp.process.PTBTokenizer")
    LexicalizedParser = JClass("edu.stanford.nlp.parser.lexparser.LexicalizedParser")
    CoreLabelTokenFactory = JClass("edu.stanford.nlp.process.CoreLabelTokenFactory")
    self.TreePrint = JClass("edu.stanford.nlp.trees.TreePrint")
    self.tokenizerFactory = PTBTokenizer.factory(CoreLabelTokenFactory(), "")
    self.lp = LexicalizedParser.loadModel()
    self.penn_treebank_expr = pyparsing.nestedExpr('(', ')')

  def _nestedlist2dict(self, d, l):
    if not l[0] in d:
      d[l[0]] = {}
    for v in l[1:]:
      if type(v) == list:
        self._nestedlist2dict(d[l[0]],v)
      else:
        d[l[0]] = v

  def chunk_string(self, sentence, json_response=False):
    rawWords = self.tokenizerFactory.getTokenizer(self.StringReader(sentence)).tokenize()
    parse = self.lp.apply(rawWords)
    stringWriter = self.StringWriter()
    tp = self.TreePrint("oneline")
    tp.printTree(parse, self.PrintWriter(stringWriter))
    penn = stringWriter.toString()
    penn = self.penn_treebank_expr.parseString(penn).asList()[0]
    penn_str = {}
    self._nestedlist2dict(penn_str, penn)
    return json.dumps(penn_str) if json_response else penn_str

  def close(self):
    shutdownJVM()
