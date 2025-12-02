#!/usr/bin/env python3

import re
import os
import sys
import glob

regex = r'<script type="text/javascript">var Tawk_API.*?</script>'

for path in glob.glob("www.metanoia-magazin.com/**/*.html", recursive=True):
    with open(path) as f:
        html = f.read()
    html_bak = str(html)
    html = re.sub(regex, "", html, flags=re.DOTALL)
    if html != html_bak:
        print(f"writing {path}")
        with open(path, "w") as f:
            f.write(html)

sys.exit()

# chat popup html:
r'''
<script type="text/javascript">var Tawk_API=Tawk_API||{}, Tawk_LoadStart=new Date();(function(){var s1=document.createElement("script"),s0=document.getElementsByTagName("script")[0];s1.async=true;s1.src='https://embed.tawk.to/64995a89cc26a871b024b540/1h3rgjaue';s1.charset='UTF-8';s1.setAttribute('crossorigin','*');s0.parentNode.insertBefore(s1,s0);})();</script>
'''
