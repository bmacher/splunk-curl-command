from requests.auth import HTTPDigestAuth
auth="digest,b,c"


def parseAuth(auth):
    # Password could use commas, so just split 2 times
    auth = auth.rsplit(',', 2)

    if auth[0].lower() == 'basic':
      return (auth[1], auth[2])
    elif auth[0].lower() == 'digest':
      return HTTPDigestAuth(auth[0], auth[1])
    else:
      return False

print parseAuth(auth)