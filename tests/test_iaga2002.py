"""
..  codeauthor:: Charles Blais
"""

from pyiaga2002 import iaga2002
from obspy import UTCDateTime


def test_iaga2002_convert():
    """
    Test IAGA2002 convertion
    """
    filename = 'tests/ott20181201vsec.sec.gz'
    stream = iaga2002.read(filename)
    for trace in stream:
        assert trace.meta.station == 'OTT'
        assert trace.meta.location == 'R0'
        assert trace.meta.channel in ['LFX', 'LFY', 'LFZ', 'LFF']
        assert trace.meta.delta == 1
        assert trace.meta.starttime == UTCDateTime(2018, 12, 1)
