#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Splunk specific dependencies
import sys, os
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators, splunklib_logger as logger

# Command specific dependencies
import requests
from requests.auth import HTTPDigestAuth
import json

@Configuration(type='reporting')
class curlCommand(GeneratingCommand):
  # Authorization : Bearer cn389ncoiwuencr
  url        = Option(require=True)
  paramMap   = Option(require=False)
  output     = Option(require=False, default='json')
  timeout    = Option(require=False, default=10, validate=validators.Integer())
  auth       = Option(require=False)
  headers    = Option(require=False)
  proxies    = Option(require=False)
  unsetProxy = Option(require=False, validate=validators.Boolean())
  
  def generate(self):
    url        = self.url
    paramMap   = self.parseParamMap(self.paramMap) if self.paramMap != None else None
    output     = self.output
    timeout    = self.timeout if self.timeout != None else None
    auth       = self.parseAuth(self.auth) if self.auth != None else None
    headers    = self.parseHeaders(self.headers) if self.headers != None else None
    proxies    = self.parseProxies(self.proxies) if self.proxies != None else None
    unsetProxy = self.unsetProxy
 
    # Unset proxy, if unsetProxy = True
    if unsetProxy == True:
      if 'HTTP' in os.environ.keys():
        del os.environ['HTTP']
      if 'HTTPS' in os.environ.keys():
        del os.environ['HTTPS']

    # Load data from REST API
    record = {}    
    try:
      request = requests.get(
        url,
        params=paramMap,
        auth=auth,
        headers=headers,
        timeout=timeout,
        proxies=proxies
      )

      # Choose right output format
      if output == 'json':
        record = request.json()
      else:
        record = {'reponse': request.content}

    except requests.exceptions.RequestException as err:
      record = ({"Error:": err})
    
    yield record

  ''' HELPERS '''
  '''
    Parse paramMap into python dict
    @paramMap string: Pattern 'foo=bar&hello=world, ...'
    @return dict
  '''
  def parseParamMap(self, paramMap):
    paramStr = ''

    # Check, if params contain \, or \= and replace it with placeholder
    paramMap = paramMap.replace(r'\,', '&#44;')
    paramMap = paramMap.split(',')

    for param in paramMap:
      paramStr += param.replace('&#44;', ',').strip() + '&'

    # Delete last &
    return paramStr[:-1]

  '''
    Parse proxy into python dict
    @proxy string: Comma separated proxies -> http,https
    @return dict
  '''
  def parseProxies(self, proxies):
    proxies = proxies.split(',')

    return {
      'http': proxies[0].strip(),
      'https' : proxies[1].strip()
    }

  '''
    Parse auth into python dict with correct method
    @proxy string: Comma separated auth params -> method,user,pass
    @return object/bool
  '''
  def parseAuth(self, auth):
    # Password could use commas, so just split 2 times
    auth = auth.rsplit(',', 2)

    # Use correcht auth method
    if auth[0].lower() == 'basic':
      return (auth[1].strip(), auth[2].strip())
    elif auth[0].lower() == 'digest':
      return HTTPDigestAuth(auth[0].strip(), auth[1].strip())

    # Return false in case of no valid method
    return False
    
  '''
    Convert headers string into dict
    @headers string: Headers as json string
    @return dict
  '''
  def parseHeaders(self, headers):
    # Replace single quotes with double quotes for valid json
    return json.loads(
      headers.replace('\'', '"')
    )

dispatch(curlCommand, sys.argv, sys.stdin, sys.stdout, __name__)