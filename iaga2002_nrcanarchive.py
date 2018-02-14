#!/usr/bin/env python
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
import os
import sys

import iaga2002
import gzip

def get_nrcan_archive_filename(trace, directory=''):
    '''See description'''
    return os.path.join(
        directory,
        trace.stats.starttime.strftime("%Y"),
        trace.stats.starttime.strftime("%m"),
        trace.stats.starttime.strftime("%m"),
        "{timestamp}.{network}.{station}.{location}.{channel}.mseed".format(
            timestamp = trace.stats.starttime.strftime("%Y%m%d"),
            network = trace.stats.network,
            station = trace.stats.station,
            location = trace.stats.location,
            channel = trace.stats.channel
        )
    )


def main():
    '''Main routine'''
    import argparse
    parser = argparse.ArgumentParser(description='Read IAGA2002 directory structure and convert to miniSeed into NRCan archive')
    parser.add_argument('directory', help='IAGA2002 archive directory')
    parser.add_argument('--output', default=os.getcwd(), help='Output base directory (default: [filename].mseed)')
    parser.add_argument('--network', default='C2', help='Network code (default: C2)')
    args = parser.parse_args()

    for root, subdirs, files in os.walk(args.directory):
        for filename in files:
            if filename.endswith(".min.gz") or filename.endswith(".sec.gz"):
                fptr = gzip.open(os.path.join(root, filename), 'rb')
                stream = iaga2002.read(fptr)
                fptr.close()
            elif filename.endswith(".min") or filename.endswith(".sec"):
                stream = iaga2002.read(os.path.join(root, filename))
            else:
                continue
            for trace in stream:
                trace.stats.network = args.network
                output = get_nrcan_archive_filename(trace, args.output)
                print output
                trace.write(output, format='MSEED', reclen=512, encoding='FLOAT32')


if __name__ == "__main__":
    sys.exit(main())
