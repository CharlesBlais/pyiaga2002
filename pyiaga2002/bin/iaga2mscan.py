"""
..  codeauthor:: Charles Blais
"""
import os
import argparse
import logging

import pyiaga2002.iaga2002 as iaga2002
import pyiaga2002.mscan as mscan


def main():
    """
    Convert IAGA2002 file to miniSeed for MSCAN ringserver.

    .. see:: iaga2mseed.py

    This extends the conversation by updating only difference of files
    found in a MSEEDSCAN directory for the ringserver.  The content
    of the directory per observatory is read, merged, and only the differences
    are added.

    We will use simplified file structure for this (some BUD structure)

    <dir>/<NET>/<STA>/NET.STA.LOC.CHAN.YEAR.DAY.TIMESTAMP

    Example:

    <dir>/C2/OTT/C2.OTT.R0.UFX.2021.065.1617968213

    where timestamp is the submit time

    :author: Charles Blais
    """
    parser = argparse.ArgumentParser(
        description='Read IAGA2002 file as miniSeed')
    parser.add_argument(
        'filename',
        help='IAGA2002 file to convert')
    parser.add_argument(
        '--directory',
        default=os.getcwd(),
        help=f'Output file (default: {os.getcwd()})')
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

    stream = iaga2002.read(args.filename)
    # Add network code to all traces and update
    for trace in stream:
        trace.stats.network = args.network
        mscan.update(args.directory, trace)
