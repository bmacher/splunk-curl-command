#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Splunk specific dependencies
import sys
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators, splunklib_logger as logger

# Command specific dependencies
import requests

@Configuration(type='reporting')
class curlCommand(GeneratingCommand):
  # ToDo add options: useproxy, unsetproxy(true/false), output(json/text), header(json), timeout
  url = Option(
		doc='''
		**Syntax:** **url=***<url>*
		**Description:** Target URL''',
		require=True
  )
  paramMap = Option(
    doc='''
    **Syntax:** **paramMap=***foo=bar,hello=world*
		**Description:** Parameters of URL''',
    require=False,
  )
  
  def generate(self):
    # --- Bind arguments ---
    url = self.url
    paramMap = self.parseParamMap(self.paramMap) if self.paramMap != None else None

    # Load data from REST API
    res = {}    
    try:
      req = requests.get(url, params=paramMap)
      res = req.json()
    except requests.exceptions.RequestException  as err:
      res = ({"Error:": err})
    
    yield res

  '''
    Parse paramMap into python dict
    @paramMap string: Pattern 'foo=bar&hello=world, ...'
    @return dict
    
    # ToDo: Handle cases in which a parameter occurs n>1 times
  '''
  def parseParamMap(self, paramMap):
    try:
      return dict(paramMap.split('=') for paramMap in paramMap.split(','))
    except:
      return {'Error': 'Could not parse paramMap! Use pattern foo=bar, hello=world'}

dispatch(curlCommand, sys.argv, sys.stdin, sys.stdout, __name__)