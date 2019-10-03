#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Splunk specific dependencies
import sys, os
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators, splunklib_logger as logger

# Command specific dependencies
import requests
from requests.auth import HTTPDigestAuth
import json

# TODO's
# - paramMap auf payload umstellen -> aber backward compatible
# - Error handling auf raise XY umstellen
#   - https://www.tutorialspoint.com/python/python_exceptions.htm
# - Add logging via logger
# - Do not delete older builds


@Configuration(type='reporting')
class curlCommand(GeneratingCommand):
  url        = Option(require=True)
  method     = Option(require=False, default='get')
  payload    = Option(require=False)
  output     = Option(require=False, default='json')
  timeout    = Option(require=False, default=10, validate=validators.Integer())
  auth       = Option(require=False)
  headers    = Option(require=False)
  proxies    = Option(require=False)
  unsetProxy = Option(require=False, validate=validators.Boolean())
  verify     = Option(require=False, default=True, validate=validators.Boolean())
  
  # Deprecated
  paramMap   = Option(require=False)
  # /Deprecated
  
  def generate(self):
    url        = self.url
    method     = self.method
    payload    = self.parseJSONStrToJSON(self.payload) if self.payload != None else None
    output     = self.output
    timeout    = self.timeout if self.timeout != None else None
    auth       = self.parseAuth(self.auth) if self.auth != None else None
    headers    = self.parseJSONStrToJSON(self.headers) if self.headers != None else None
    proxies    = self.parseProxies(self.proxies) if self.proxies != None else None
    unsetProxy = bool(self.unsetProxy)
    verify     = bool(self.verify)
    
    # Deprecated
    paramMap   = self.parseParamMap(self.paramMap) if self.paramMap != None else None

    if payload == None:
      payload = paramMap
    # /Deprecated

    # Unset proxy, if unsetProxy = True
    if unsetProxy == True:
      if 'HTTP' in os.environ.keys():
        del os.environ['HTTP']
      if 'HTTPS' in os.environ.keys():
        del os.environ['HTTPS']

    # Load data from REST API
    event = {}    
    try:
      if method == 'get':      
        request = requests.get(
          url,
          params=payload,
          auth=auth,
          headers=headers,
          timeout=timeout,
          proxies=proxies,
          verify=verify
        )
      elif method == 'post':
        request = requests.post(
          url,
          data=payload,
          auth=auth,
          headers=headers,
          timeout=timeout,
          proxies=proxies,
          verify=verify
        )
      else:
        raise ValueError('Only get and post are valid methods.')

      # Choose right output format
      if output == 'json':
        event = request.json()
      else:
        event = {'reponse': request.content}

    except requests.exceptions.RequestException as err:
      event = ({"Error:": err})
    
    yield event

  ''' HELPERS '''
  '''
    Convert headers string into dict
    :headers string: Headers as json string
    :return dict
  '''
  def parseJSONStrToJSON(self, headers):
    # Replace single quotes with double quotes for valid json
    return json.loads(
      headers.replace('\'', '"')
    )

  '''
    Parse proxy into python dict
    :proxy string: Comma separated proxies -> http,https
    :return dict
  '''
  def parseProxies(self, proxies):
    proxies = proxies.split(',')

    return {
      'http': proxies[0].strip(),
      'https' : proxies[1].strip()
    }

  '''
    Parse auth into python dict with correct method
    :proxy string: Comma separated auth params -> method,user,pass
    :return object/bool
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


  ''' DEPRECATED '''

  '''
    Parse paramMap into python dict
    :paramMap string: Pattern 'foo=bar, hello=world, ...'
    :return dict
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

dispatch(curlCommand, sys.argv, sys.stdin, sys.stdout, __name__)
