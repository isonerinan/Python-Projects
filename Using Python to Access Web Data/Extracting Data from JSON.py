import json
import urllib.request, urllib.parse, urllib.error
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = input("Enter URL: ")
print ("Retrieving", url)

html = urllib.request.urlopen(url)
data = html.read().decode()
print("Retrieved",len(data),"characters")

info = json.loads(data)
print('User count:', len(info))
sum = 0

for item in info["comments"]:
    sum += item["count"]

print("Sum:", sum)