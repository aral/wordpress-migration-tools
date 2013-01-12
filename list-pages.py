import parse_wordpress_export
import xml.etree.ElementTree as ET
# from StringIO import StringIO
# from bs4 import BeautifulSoup

# domain = 'aralbalkan.com'
# imagesFolder = '/images'
# downloadsFolder = '/downloads'
# uploadedMediaFolder = '/wp-content/uploads'

# Shorthand reference to the namespace.
wp = parse_wordpress_export

wp.parse()

for page in wp.pages:
	print ET.dump(page)