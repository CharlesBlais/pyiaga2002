"""
IAGA2002 library
================

Library for reading IAGA2002 files

..  codeauthor:: Charles Blais
"""
import re
import logging
import gzip
from typing import Union, List, TextIO


from obspy import Stream, Trace, UTCDateTime
import numpy as np

# User-contribute
import pyiaga2002.seed as seed


class IAGA2002FormatError(Exception):
    """Custom error for IAGA2002 format"""
    pass


def _get_station(line: str) -> str:
    """Get station code from line

    :param str line: line to parse station code
    :rtype: str
    :returns: station code
    """
    return line[23:-1].strip()


def _get_location(line: str) -> str:
    """Get location code from line

    :param str line: line to parse location code
    :rtype: str
    :returns: location code
    """
    if line[24:-1].strip() == 'definitive':
        return 'D0'
    elif line[24:-1].strip() == 'quasi-definitive':
        return 'Q0'
    elif line[24:-1].strip() == 'provisional':
        return 'A0'
    return 'R0'


def _get_components(line: str) -> List[str]:
    """Get components from line (last characters of last 4 blocks)

    :param str line: line to parse components
    :rtype: [str]
    :returns: components in code
    """
    return [block[-1] for block in line.split()[-5:-1]]


def read(
    filename: Union[str, TextIO],
    dtype=np.float32,
) -> Stream:
    """Read content of IAGA2002 into obspy Stream object

    The sampling rate will be determined by the content of the stream.
    The data type (for location) will be determined the header information.

    The naming convention follows the one described under:

    https://github.com/INTERMAGNET/miniseed-sncl/blob/master/SNCL.md

    :type filename: str or resource
    :param filename: file of IAGA2002 data

    :param dtype: numpy dtype (default: np.float32)

    :type: :class:`obspy.Stream`
    :returns: IAGA2002 to miniseed
    """
    if isinstance(filename, str):
        logging.info(f'Reading content of {filename}')
        fptr = gzip.open(filename, 'r') \
            if filename.endswith('gz') \
            else open(filename)
    elif hasattr(filename, 'read'):
        logging.debug('Received resource')
        fptr = filename
    else:
        raise ValueError('Unknown content sent for IAGA2002 reading')

    # Set defaults
    stream = Stream([
        Trace(np.array([], dtype=dtype)),
        Trace(np.array([], dtype=dtype)),
        Trace(np.array([], dtype=dtype)),
        Trace(np.array([], dtype=dtype))
    ])

    for line in fptr:
        try:
            line = line.decode('utf-8')  # type: ignore
        except (UnicodeDecodeError, AttributeError):
            pass
        line = line.strip()
        if line.startswith('IAGA CODE'):
            for trace in stream:
                trace.stats.station = _get_station(line)
        if line.startswith('Data Type'):
            for trace in stream:
                trace.stats.location = _get_location(line)
        # this is the header before data so we stop here
        if line.startswith('DATE'):
            components = _get_components(line)
            for idx in range(len(stream)):
                stream[idx].stats.channel = 'UF' + components[idx]
            break

    # Read data lines and convert them to obspy.Trace
    # Example of line:
    #   2014-12-01 00:00:00.000 335      1375.02  -2365.15  56033.84  99999.00
    for line in fptr:
        try:
            line = line.decode('utf-8')  # type: ignore
        except (UnicodeDecodeError, AttributeError):
            pass
        # if the data line contains stars (*) replace with 99999.00
        data = re.sub(r'[*]+', '99999.00', line).split()

        if len(data) != 7:
            logging.warning(f'The following line is incomplete, skip: {line}')
            continue

        # always the first line
        if len(stream[0].data) == 0:
            starttime = UTCDateTime("{0} {1}".format(*data))
            for trace in stream:
                trace.stats.starttime = starttime

        # always the second line
        # we can calculate the delta and its associated SEED code
        # we do this since HEADER in IAGA-2002 is known to me innacurate for
        # some institutes
        if len(stream[0].data) == 1:
            delta = UTCDateTime("{0} {1}".format(*data)) - \
                stream[0].stats.starttime
            if delta == 0:
                raise IAGA2002FormatError('Problem with the time in the file')
            seedcode = seed.get_bandcode(1.0/delta)
            for trace in stream:
                trace.stats.delta = delta
                trace.stats.channel = seedcode + trace.stats.channel[1:]

        # append the data to each stream
        for idx in range(len(stream)):
            stream[idx].data = np.append(
                stream[idx].data,
                np.array([float(data[idx+3])], dtype=np.float32))

    # Mask any invalid data
    for trace in stream:
        trace.data = np.ma.masked_where(trace.data >= 88888, trace.data)

    if isinstance(filename, str):
        fptr.close()
    return stream
