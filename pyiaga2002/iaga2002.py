#!/usr/bin/env python
import sys
from obspy import Stream, Trace, UTCDateTime
from obspy.core.trace import Stats
import numpy as np

# User-contribute
import pyiaga2002.seed as seed

class IAGA2002FormatError(Exception):
    pass


def _get_station(line):
    '''Get station code from line'''
    return line[23:-1].strip()

def _get_location(line):
    '''Get location code from line'''
    return 'D0' if line[24:-1].strip() == 'definitive' else 'R0'

def _get_components(line):
    '''Get components from line (last characters of last 4 blocks)'''
    return [block[-1] for block in line.split()[-5:-1]]


def read(filename):
    '''Read content of IAGA2002 into obspy Stream object

    :param filename: file of IAGA2002 data

    :return: ~obspy.Stream
    '''
    if isinstance(filename, str):
        fptr = open(filename)
    else:
        fptr = filename

    # Set defaults
    stream = Stream([
        Trace(np.array([], dtype=np.float32)),
        Trace(np.array([], dtype=np.float32)),
        Trace(np.array([], dtype=np.float32)),
        Trace(np.array([], dtype=np.float32))
    ])
    dstarttime = stream[0].stats.starttime
    ddelta = stream[0].stats.delta

    for line in fptr:
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
        data = line.split()
        if len(data) != 7:
            raise IAGA2002FormatError("The following line is incomplete, aborting: %s" % line)
        # always the second line (we can calculate the delta and its associated SEED code)
        if stream[0].stats.starttime != dstarttime and stream[0].stats.delta == ddelta:
            delta = UTCDateTime("{0} {1}".format(*data)) - stream[0].stats.starttime
            seedcode = seed.get_bandcode(1.0/delta)
            for trace in stream:
                trace.stats.delta = delta
                trace.stats.channel = seedcode + trace.stats.channel[1:]
        # always the first line
        if stream[0].stats.starttime == dstarttime:
            starttime = UTCDateTime("{0} {1}".format(*data))
            for trace in stream:
                trace.stats.starttime = starttime
        # append the data to each stream
        for idx in range(len(stream)):
            stream[idx].data = np.append(stream[idx].data, np.array([float(data[idx+3])], dtype=np.float32))
    for trace in stream:
        if 99999 in trace.data:
            trace.data = np.ma.masked_values(trace.data, 99999.0)
    
    if isinstance(filename, str):
        fptr.close()
    return stream
