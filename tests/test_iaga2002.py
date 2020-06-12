"""
..  codeauthor:: Charles Blais
"""

from pyiaga2002 import iaga2002


def test_iaga2002_convert():
    """
    Test IAGA2002 convertion
    """
    filename = 'tests/ott20181201vsec.sec.gz'
    print(iaga2002.read(filename))
    assert False
