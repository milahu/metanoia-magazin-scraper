#!/usr/bin/env python3

import re
import os
import sys
import glob

regex = r'<div\s+class="cookie-permission-container".*?>\s*<div.*?>\s*<div.*?>\s*<div.*?>\s*.*?</div>\s*<div.*?>\s*.*?</div>.*?</div>.*?</div>.*?</div>'

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

# cookie popup html:
r'''
                                <div
            class="cookie-permission-container"
            data-cookie-permission="true">
            <div class="container">
                <div class="row align-items-center">

                                            <div class="col cookie-permission-content">
                            Diese Website verwendet Cookies, um eine bestmögliche Erfahrung bieten zu können. <a data-toggle="modal" data-url="/widgets/cms/c5c2c216b8f049519f2cd5c4f30e0c2a" href="../widgets/cms/c5c2c216b8f049519f2cd5c4f30e0c2a.html" title="Mehr Informationen">Mehr Informationen ...</a>
                        </div>
                    
                                            <div class="col-12 col-md-auto pr-2 ">
                                                            <span class="cookie-permission-button js-cookie-permission-button">
                                    <button
                                        type="submit"
                                        class="btn btn-primary">
                                        Ablehnen
                                    </button>
                                </span>
                            
                                                            <span class="js-cookie-configuration-button">
                                    <button
                                        type="submit"
                                        class="btn btn-primary">
                                        Konfigurieren
                                    </button>
                                </span>
                            
                                                                                                <span class="js-cookie-accept-all-button">
                                        <button
                                            type="submit"
                                            class="btn btn-primary">
                                            Alle Cookies akzeptieren
                                        </button>
                                    </span>
                                                                                    </div>
                                    </div>
            </div>
        </div>
'''
