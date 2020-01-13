import os
import sys
import argparse
import gzip
import errno    
import os
import logging

from obspy import read
import numpy

import pyiaga2002.iaga2002 as iaga2002


def __mkdir_p(path):
    '''Make directory recursive'''
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def __get_nrcan_archive_filename(trace, directory=''):
    '''See description'''
    return os.path.join(
        directory,
        trace.stats.starttime.strftime("%Y"),
        trace.stats.starttime.strftime("%m"),
        trace.stats.starttime.strftime("%d"),
        "{timestamp}.{network}.{station}.{location}.{channel}.mseed".format(
            timestamp = trace.stats.starttime.strftime("%Y%m%d"),
            network = trace.stats.network,
            station = trace.stats.station,
            location = trace.stats.location,
            channel = trace.stats.channel
        )
    )


def __is_empty(trace):
    '''
    Determine if the trace is empty
    '''
    if len(trace) == 0:
        logging.warning("Trace %s is empty, ignoring...", trace.get_id())
        return True
    if numpy.ma.is_masked(trace.data):
        if trace.data.all() is numpy.ma.masked:
            logging.warning("Trace %s is empty, ignoring...", trace.get_id())
            return True
    return False


def iaga2archive():
    '''
    Convert IAGA2002 directory structure of geomag
    to /arc/channel_archive structure.  The structure is
    as followed:

    YYYY/mm/dd/YYYYmmdd.NN.SSSS.LL.CCC.mseed

    where:
    YYYY = year
    mm = month
    dd = day
    NN = network code
    SS = station code
    LL = location code
    CCC = channel code
    '''
    parser = argparse.ArgumentParser(description='Read IAGA2002 directory structure and convert to miniSeed into NRCan archive')
    parser.add_argument('directory', help='IAGA2002 archive directory')
    parser.add_argument('--output', default=os.getcwd(), help='Output base directory (default: [filename].mseed)')
    parser.add_argument('--network', default='C2', help='Network code (default: C2)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbosity')
    args = parser.parse_args()

    # Set logging level
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)s \
            %(module)s %(funcName)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO if args.verbose else logging.WARNING)

    for root, subdirs, files in os.walk(args.directory):
        subdirs = subdirs
        for filename in files:
            logging.info("Reading content of %s", filename)
            if filename.endswith(".min.gz") or filename.endswith(".sec.gz"):
                fptr = gzip.open(os.path.join(root, filename), 'rb')
                stream = iaga2002.read(fptr)
                fptr.close()
            elif filename.endswith(".min") or filename.endswith(".sec"):
                stream = iaga2002.read(os.path.join(root, filename))
            else:
                logging.warning("Unknown filename format %s", filename)
                continue
            for trace in stream:
                # Don't do anything if empty
                if __is_empty(trace):
                    continue
                trace.stats.network = args.network
                output = __get_nrcan_archive_filename(trace, args.output)
                # MiniSeed can not store masked values
                trace = trace.split()
                __mkdir_p(os.path.dirname(output))
                logging.info("Writing converted IAGA2002 to %s", output)
                trace.write(output, format='MSEED', reclen=512, encoding='FLOAT32')


def iaga2mseed():
    '''
    Convert IAGA2002 file to miniSeed.

    Not trying to be fancy at all in this code since this is only used
    by operations to store IAGA2002 into miniSeed archive.  I don't expect
    anyone using this for other purposes as it should be the other way around.

    Information read from IAGA2002 header for miniSeed:
        network code = set by command line
        station code = IAGA CODE header
        location = Data Type header = (D0) definitive, (R0) all others
        channel =
        1. convert the delta to SEED code
        2. F
        3. orientation code (last element of column header)
        starttime = first time in data
        delta = difference between first and second time

    :author: Charles Blais
    '''
    import argparse
    
    parser = argparse.ArgumentParser(description='Read IAGA2002 file as miniSeed')
    parser.add_argument('filename', help='IAGA2002 file to convert')
    parser.add_argument('--output', default=None, help='Output file (default: [filename].mseed)')
    parser.add_argument('--network', default='C2', help='Network code (default: C2)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbosity')
    args = parser.parse_args()

    # Set logging level
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)s \
            %(module)s %(funcName)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO if args.verbose else logging.WARNING)

    # Set default filename
    output = args.output if args.output is not None else args.filename + '.mseed'

    logging.info("Reading content of %s", args.filename)
    if args.filename.endswith(".min.gz") or args.filename.endswith(".sec.gz"):
        fptr = gzip.open(args.filename, 'rb')
        stream = iaga2002.read(fptr)
        fptr.close()
    elif args.filename.endswith(".min") or args.filename.endswith(".sec"):
        stream = iaga2002.read(args.filename)
    else:
        logging.error("Unknown filename format %s", args.filename)
        return 1

    # Add network code to all traces
    for trace in stream:
        __is_empty(trace)
        trace.stats.network = args.network

    # Can not write masked array
    stream = stream.split()
    logging.info("Writing converted IAGA2002 to %s", output)
    stream.write(output, format='MSEED', reclen=512, encoding='FLOAT32')
