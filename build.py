import os, re, glob

# Open app.conf and read all lines
with open('./curl_command/default/app.conf') as appconf:
  lines = appconf.readlines()

appconf.close()

# Get current version -> version = 1.0.0
for line in lines:
  if re.match('version', line):
    version = re.search(r'version\s?=\s?(\d\.\d\.\d)', line).group(1)

# Delete older build
for file in glob.glob('./dist/curl_command*'):
  os.remove(file)

# Copy App, delete uneccesary files and create .tar.gz
os.system('cp -R curl_command dist/')
os.system('find dist/curl_command -name ".*" -delete')
os.system('find dist/curl_command -name "*.pyc" -delete')
os.system('tar -zcf dist/curl_command-%s.tar.gz curl_command' % (version))
os.system('rm -rf dist/curl_command')

print 'App <curl_command-%s.tar.gz> successfully built!' % (version)