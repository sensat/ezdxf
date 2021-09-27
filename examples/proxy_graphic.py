# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
from ezdxf.lldxf.tags import Tags
from ezdxf.proxygraphic import load_proxy_graphic, ProxyGraphic
import logging
import ezdxf

logging.basicConfig(level=logging.ERROR)
DIR = Path("~/Desktop/outbox").expanduser()

DATA = """160
968
310
C80300000D000000540000002000000002000000033E695D8B227240B00D3CF1FB7B5540000000000000000082C85BAC2FDE7240FB1040429FB05740000000000000000000000000000000000000000000000000000000000000F03F5400000020000000020000004AF9442AE7FA60405A2D686189715A4000000000000000
310
00C0DC003571AE5F40043422DDA4515D40000000000000000000000000000000000000000000000000000000000000F03F64000000040000001EA72DF9806A69402CE3B4E7B59D34400000000000000000770FBC9D50855E4000000000000000000000000000000000000000000000F03FB634003D352CE93FB1DDE561C5C1
310
E33F00000000000000000418DC3967E1F83F000000000C0000001200000000000000D0000000260000001F8BC5F8B8B46A40197732241FF06140000000000000000000000000000000000000000000000000000000000000F03F0943D77B25BDEF3F417457E0C451C0BF00000000000000003100370032002C003400320000
310
00000006000000010000000000000000000440000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000000000000000000000000000000000000000000041007200690061006C00000061007200690061006C002E007400740066000000000000000C00000012000000FF7F0000
310
6400000004000000813C33FBB3606A400278BF21B8F4614000000000000000009AEFA7C64B37034000000000000000000000000000000000000000000000F03F0943D77B25BDEF3F437457E0C451C0BF0000000000000000182D4454FB210940000000000C00000010000000010000000C0000001700000000000000540000
310
0020000000020000001EA72DF9806A69402CE3B4E7B59D344000000000000000001EA72DF9806A69402CE3B4E7B59D3440000000000000000000000000000000000000000000000000000000000000F03F540000002000000002000000B296839B8D1A724001000000F06355400000000000000000B296839B8D1A72400100
310
0000F0635540000000000000000000000000000000000000000000000000000000000000F03F540000002000000002000000632D073753076140FFFFFFFF2F525A400000000000000000632D073753076140FFFFFFFF2F525A40000000000000000000000000000000000000000000000000000000000000F03F5400000020
310
000000020000000960E446A3456F405AF2DBF448AB604000000000000000000960E446A3456F405AF2DBF448AB6040000000000000000000000000000000000000000000000000000000000000F03F
"""

doc = ezdxf.new()
msp = doc.modelspace()

data = load_proxy_graphic(Tags.from_text(DATA))
proxy = ProxyGraphic(data, doc)

for index, size, name in proxy.info():
    print(f"Index: {index}, Size: {size}, Type: {name}")

for entity in proxy.virtual_entities():
    print(str(entity))
    doc.entitydb.add(entity)
    msp.add_entity(entity)

doc.saveas(DIR / "proxy.dxf")
