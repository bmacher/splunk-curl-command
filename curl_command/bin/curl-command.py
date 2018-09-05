#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Splunk specific dependencies
import sys, os
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators, splunklib_logger as logger

# Command specific dependencies
import requests
from requests.auth import HTTPDigestAuth

@Configuration(type='reporting')
class curlCommand(GeneratingCommand):
  url = Option(
		doc='''
		  **Syntax:** **url=***<url>*
		  **Description:** Target URL
    ''',
		require=True
  )
  paramMap = Option(
    doc='''
      **Syntax:** **paramMap=***<foo=bar,hello=world>*
		  **Description:** Parameters of URL
    ''',
    require=False,
  )
  auth = Option(
    doc='''
      **Syntax:** **auth=**<method,user,password>**
		  **Description:** Authentication at the endpoint with user credentials
    ''',
    require=False,
  )
  proxies = Option(
    doc='''
      **Syntax:** **proxy=***<http_proxy, https_proxy>*
		  **Description:** Proxies
    ''',
    require=False
  )
  unsetProxy = Option(
    doc='''
      **Syntax:** **useProxy=***<true/false>*
		  **Description:** Unset proxy during the session
    ''',
    require=False,
    validate=validators.Boolean()
  )
  timeout = Option(
    doc='''
      **Syntax:** **timeout=***<timeout>*
		  **Description:** Time to wait before the request is stopped
    ''',
    require=False,
    validate=validators.Integer(),
    default=10
  )
  output = Option(
    doc='''
      **Syntax:** **output=**<json/text>**
		  **Description:** Output format 
    ''',
    require=False,
    default='json'
  )
  
  def generate(self):
    url = self.url
    paramMap = self.parseParamMap(self.paramMap) if self.paramMap != None else None
    output = self.output
    proxies = self.parseParamMap(self.proxies) if self.proxies != None else None
    unsetProxy = self.unsetProxy
    timeout = self.timeout if self.timeout != None else None
    auth = self.parseAuth(self.auth) if self.auth != None else None
 
    # Unset proxy, if unsetProxy = True
    if unsetProxy == True:
      if 'HTTP' in os.environ.key():
        del os.environ['HTTP']
      if 'HTTPS' in os.environ.key():
        del os.environ['HTTPS']

    # Load data from REST API
    record = {}    
    try:
      request = requests.get(
        url,
        params=paramMap,
        proxies=proxies,
        timeout=timeout,
        auth=auth
      )

      # Choose right output format
      if output == 'json':
        record = request.json()
      else:
        record = {'reponse': request.content}

    except requests.exceptions.RequestException  as err:
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
      paramStr += param.replace('&#44;', ',') + '&'

    # Delete last &
    return paramStr[:-1]

  '''
    Parse proxy into python dict
    @proxy string: Comma separated proxies -> http,https
    @return dict
  '''
  def parseProxies(self, proxies):
    proxies = proxies.replace(' ', '').split(',')

    return {
      'http': proxies[0],
      'https' : proxies[1]
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
      return (auth[1], auth[2])
    elif auth[0].lower() == 'digest':
      return HTTPDigestAuth(auth[0], auth[1])

    # Return false in case of no valid method
    return False
    

dispatch(curlCommand, sys.argv, sys.stdin, sys.stdout, __name__)