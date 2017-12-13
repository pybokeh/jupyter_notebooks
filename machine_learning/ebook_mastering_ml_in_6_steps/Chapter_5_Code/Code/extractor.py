#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

# __all__ = ['Extractor']

class SOPTriplet(object):
  def __init__(self):
    self.subject = None
    self.predicate = None
    self.object = None

class SOPExtractor(object):
  def __init__(self, chunker):
    self.chunker = chunker
    self.sop_triplet = SOPTriplet()
    self._NP_subtrees = []
    self._VP_subtrees = []  

    self.NOUNS = ['NN', 'NNP', 'NNPS', 'NNS']
    self.VERBS = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    self.ADJECTIVES = ['JJ', 'JJR']
  
  def _do_with_penn_sub_tree(self, tree, needles, visitor, path=()):    
    for k in tree:
      if k in needles:        
        visitor(path, tree[k])
      elif type(tree[k]) != dict:
        pass
      else:
        self._do_with_penn_sub_tree(tree[k], needles, visitor, path+(k,)) 

  # visitors
  def _cout(self, path, element):
    print path, element 

  def _save_NP_subtree(self, path, element):
    self._NP_subtrees.append(dict(path=path, tree=element))

  def _save_VP_subtree(self, path, element):
    self._VP_subtrees.append(dict(path=path, tree=element))

  def _extract_predicate(self, path, element):
    if self.sop_triplet.predicate:
      if len(self.sop_triplet.predicate['path']) < len(path):
        self.sop_triplet.predicate = dict(path=path, tree=element)
    else:
      self.sop_triplet.predicate = dict(path=path, tree=element)

  def _extract_object(self, path, element):
    if not self.sop_triplet.object and (path[0] in ['NP', 'PP'] or path[0] == 'ADJP'):
      self.sop_triplet.object = element
    
  def extract(self, sentence):
    self.sop_triplet = SOPTriplet()
    self._NP_subtrees = []
    self._VP_subtrees = []

    penn = self.chunker.chunk_string(sentence, json_response=False)   
    
    self._do_with_penn_sub_tree(penn, 'NP', self._save_NP_subtree)    
    self._do_with_penn_sub_tree(penn, 'VP', self._save_VP_subtree) 

    # extract subject
    try:
      NP_subtree = None
      for t in self._NP_subtrees:
        path, tree = t['path'], t['tree']
        if path[-1] == 'S':
          NP_subtree = tree
          break
      for k,v in NP_subtree.items():
        if k in self.NOUNS:
          self.sop_triplet.subject = v
          break
    except (AttributeError, KeyError, TypeError):
      pass

    # extract predicate          
    try:
      VP_subtree = None
      for t in self._VP_subtrees:
        path, tree = t['path'], t['tree']
        if path[-1] == 'S':
          VP_subtree = tree
          break
      self._do_with_penn_sub_tree(VP_subtree, self.VERBS, self._extract_predicate)      
      parent = VP_subtree
      for p in self.sop_triplet.predicate['path']:
        parent = VP_subtree[p]
      self.sop_triplet.predicate = self.sop_triplet.predicate['tree']
    except (AttributeError, KeyError, TypeError):
      pass

    # extract object
    try:         
      self._do_with_penn_sub_tree(parent, self.NOUNS, self._extract_object) 
      if not self.sop_triplet.object:
        self._do_with_penn_sub_tree(parent, self.ADJECTIVES, self._extract_object)            
    except (AttributeError, KeyError, TypeError, UnboundLocalError):
      pass

    return self.sop_triplet

  def close(self):
    self.chunker.close()    

