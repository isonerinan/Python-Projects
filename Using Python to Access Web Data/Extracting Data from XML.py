import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = input("Enter URL: ")
print ("Retrieving", url)

html = urllib.request.urlopen(url)
data = html.read()
print("Retrieved",len(data),"characters")

tree = ET.fromstring(data)
commentTag = tree.findall('comments/comment')
count = len(commentTag)
sum = 0

for comment in commentTag:
    sum += int(comment.find('count').text)

print("Count:", count)
print("Sum:", sum)