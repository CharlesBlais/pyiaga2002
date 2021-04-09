"""
..  codeauthor:: Charles Blais
"""
import argparse
import logging

import pyiaga2002.iaga2002 as iaga2002


def main():
    """
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
    """
    parser = argparse.ArgumentParser(
        description='Read IAGA2002 file as miniSeed')
    parser.add_argument(
        'filename',
        help='IAGA2002 file to convert')
    parser.add_argument(
        '--output',
        default=None,
        help='Output file (default: [filename].mseed)')
    parser.add_argument(
        '--network',
        default='XX',
        help='Network code (default: XX)')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbosity')
    args = parser.parse_args()

    # Set logging level
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)s \
            %(module)s %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO if args.verbose else logging.WARNING)

    # Set default filename
    output = args.output if args.output is not None \
        else f'{args.filename}.mseed'

    stream = iaga2002.read(args.filename)

    # Add network code to all traces
    for trace in stream:
        trace.stats.network = args.network

    # Can not write masked array
    stream = stream.split()
    logging.info(f'Writing converted IAGA2002 to {output}')
    stream.write(
        output,
        format='MSEED',
        reclen=512,
        encoding='FLOAT32')
