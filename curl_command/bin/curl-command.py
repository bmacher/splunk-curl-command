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
    **Syntax:** **url=***<url>*
		**Description:** Target URL''',
    require=False,
  )
  
  def generate(self):
    # --- Bind arguments ---
    url = self.url
    # Pattern foo=bar, bar=foo, ...
    paramMap = self.paramMap
    
    if paramMap != None:
      paramMap = paramMap.replace(' ', '')
      # Parse paramMap and catch error
      try:
        paramMap = dict(paramMap.split('=') for paramMap in paramMap.split(','))
      except:
        yield {'Error': 'Could not parse paramMap! Use pattern foo=bar, hello=world'}
        # Stop command
        return

      # Modify url with parameters
      url += '?' + '&'.join('{}={}'.format(param, val) for param, val in paramMap.items())

    # Load data from REST API
    res = {}    
    try:
      req = requests.get(url)
      res = req.json()
    except requests.exceptions.RequestException  as err:
      res = ({"Error:": err})
    
    yield {'url': url}

dispatch(curlCommand, sys.argv, sys.stdin, sys.stdout, __name__)