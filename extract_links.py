
import re

def extract_links(filename):
    with open(filename, 'rb') as f:
        content = f.read()
        # Look for strings ending with _link, allowing for some widely used characters
        # We assume they are ASCII/UTF-8 encoded within the binary
        matches = re.findall(b'[a-zA-Z0-9_]+_link', content)
        unique_links = sorted(list(set([m.decode('utf-8') for m in matches])))
        return unique_links

links = extract_links('data/usd/spotmicro_with_imu_dc.usd')
print("Found links:")
for link in links:
    print(link)
