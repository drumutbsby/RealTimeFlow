# -*- coding: utf-8 -*-
"""pytest yardımcı: `sinyal_v2` paketini içe aktarılabilir kıl.

Testler hangi dizinden çağrılırsa çağrılsın (proje kökü veya sinyalizasyon_v2/),
bu dosyanın bulunduğu dizin sys.path'e eklenerek `import sinyal_v2` çalışır.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
