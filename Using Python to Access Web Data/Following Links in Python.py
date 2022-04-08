import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

count = int(input("Enter count: "))
position = int(input("Enter position: "))
url = input('Enter URL: ')

for j in range(count):
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')

    i = 0;

    # Retrieve all of the anchor tags
    tags = soup('a')

    for tag in tags:
        i += 1

        if i == position:
            print("retrieving:", url)
            url = tag.get("href", None)
            break

print(url)