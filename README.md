# Splunk | curl command
This app contains the search command "curl", which polls data from a REST API. The syntax is as follows, with the question mark indicating the optional Options.

```
| curl <url> <paramMap>? <output>? <timeout>? <auth>? <headers>? <proxies>? <unsetProxy>? <verify>?
```

#### Options in detail

Option | Type | Value
---- | ---- | ----
url | string | http://my_rest_api/endpoint
paramMap | string | param1=val1, param2=val2
output | string | json || text (default: jsont)
timeout | int | 0..∞
auth | string | Basic, User, Password
headers | json | {'option1': 'val1', 'option2': 'val2'}
proxies | string | http_proxy, https_proxy
unsetProxy | bool | true OR false (default: false)
verify | bool | true OR false (default: true)

#### Examples
Returns the data from the endpoint as json
```
| curl url="https://reqres.in/api/users"
```
Basic login at the Github API with reponse as plain text
```
| curl url="https://api.github.com/user" auth="basic, <user>, <password>" output=text
```
Access InfluxDB with token
```
| curl url="http://influx:3000/api/datasources/proxy/1/query" paramMap="db=statsdemo, q=show tag keys" headers="{'Authorization': 'Bearer <token>'}"
```
<br>
MIT License 

_Copyright © 2018 Benjamin Macher_
