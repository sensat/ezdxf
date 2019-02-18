# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-18
from typing import TYPE_CHECKING
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from .dxfentity import base_class, SubclassProcessor, DXFEntity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from .dxfentity import DXFNamespace

__all__ = ['Block', 'EndBlk']

acdb_entity = DefSubclass('AcDbEntity', {
    'layer': DXFAttr(8, default='0'),
})

acdb_block_begin = DefSubclass('AcDbBlockBegin', {
    'name': DXFAttr(2),
    'name2': DXFAttr(3),
    'description': DXFAttr(4, default=''),
    'flags': DXFAttr(70, default=0),
    'base_point': DXFAttr(10, xtype=XType.any_point, default=Vector(0, 0, 0)),
    'xref_path': DXFAttr(1, default=''),
})


@register_entity
class Block(DXFEntity):
    """ DXF BLOCK entity """
    DXFTYPE = 'BLOCK'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_block_begin)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        processor.load_dxfattribs_into_namespace(dxf, acdb_entity.name)
        processor.load_dxfattribs_into_namespace(dxf, acdb_block_begin.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)

        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_entity.name)
        self.dxf.export_dxf_attribute(tagwriter, 'layer')
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_block_begin.name)

        self.dxf.export_dxf_attribs(tagwriter, ['name', 'flags', 'base_point', 'name2', 'xref_path'], force=True)
        self.dxf.export_dxf_attribute(tagwriter, 'description')
        # xdata and embedded objects export will be done by parent class


acdb_block_end = DefSubclass('AcDbBlockEnd', {})


@register_entity
class EndBlk(DXFEntity):
    """ DXF ENDBLK entity """
    DXFTYPE = 'ENDBLK'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_block_end)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        processor.load_dxfattribs_into_namespace(dxf, acdb_entity.name)
        processor.load_dxfattribs_into_namespace(dxf, acdb_block_end.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)

        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_entity.name)
        self.dxf.export_dxf_attribute(tagwriter, 'layer')
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_block_end.name)

        # xdata and embedded objects export will be done by parent class
