'''
MSCAN directory for IAGA2002
============================

We will use simplified file structure for this (some BUD structure)

<dir>/<NET>/<STA>/NET.STA.LOC.CHAN.YEAR.DAY.TIMESTAMP

Example:

<dir>/C2/OTT/C2.OTT.R0.UFX.2021.065.1617968213

.. codeauthor:: Charles Blais
'''
import logging
from obspy import Stream, Trace, UTCDateTime, read
import numpy as np
from typing import List, Union
from pathlib import Path


class RingException(Exception):
    '''Custom exception'''


def __get_matching_stores(
    directory: Union[str, Path],
    trace: Trace
) -> List[Path]:
    '''
    Scan the directory for all matching traces

    ..  note:: We are assuming the trace for a single day only
        (like IAGA2002 data)

    :param str directory: MSCAN directory
    :type trace: :class:`obspy.Trace`
    :param trace: trace data
    :rtype: [str]
    '''
    return list(Path(directory).joinpath(
        trace.stats.network,
        trace.stats.station,
    ).glob(
        '{network}.{station}.{location}.{channel}.{year}.{doy}.*'.format(
            **trace.stats,
            year=trace.stats.starttime.year,
            doy=trace.stats.starttime.strftime('%j')
        )
    ))


def __get_stored_trace(
    directory: Union[str, Path],
    trace: Trace,
) -> Trace:
    '''
    Load the matching trace information found in MSCAN directory

    ..  note: filenames are in ascending order meaning newer traces
        will overwrite older traces data in the merge

    :param str directory: MSCAN directory
    :type trace: :class:`obspy.Trace`
    :param trace: trace data
    :rtype: :class:`obspy.Trace`
    '''
    filenames = __get_matching_stores(directory, trace)
    stream = Stream()
    for filename in filenames:
        logging.info(f'Reading content of {filename}')
        stream += read(str(filename))
        stream = stream.merge(method=1)

    if len(stream) == 0:
        return Trace()
    if len(stream) != 1:
        raise RingException(f'The merged stream contained more then 1 trace \
which should not happen:\n {stream}')
    return stream[0]


def get_difference(
    directory: Union[str, Path],
    trace: Trace,
) -> Stream:
    '''
    Get the data from the trace sent that does not match
    the data found in the MSCAN directory.  This will result in the data
    that should be written to the MSCAN directory.

    :param str directory: MSCAN directory
    :type trace: :class:`obspy.Trace`
    :param trace: trace data
    :rtype: :class:`obspy.Trace`
    '''
    stored_trace = __get_stored_trace(directory, trace)
    # No trace found in store, all are new
    if stored_trace.stats.npts == 0:
        logging.debug('No trace found in store')
        return trace.split()

    logging.debug(
        f'Trim content of read stream:\n{stored_trace}\nto match:\n{trace}')
    stored_trace = stored_trace.trim(
        trace.stats.starttime,
        trace.stats.endtime,
        pad=True,
    )
    if stored_trace.stats.npts != trace.stats.npts:
        raise RingException("Oops, I don't think I got the trim right!")
    mask = (stored_trace.data - trace.data) == 0
    trace.data = np.ma.array(trace.data, mask=mask)
    return trace.split()


def update(
    directory: Union[str, Path],
    trace: Trace,
) -> bool:
    '''
    Update the MSCAN directory with only the difference

    :param str directory: MSCAN directory
    :type trace: :class:`obspy.Trace`
    :param trace: trace data
    :rtype: bool
    '''
    logging.debug(f'Update content for trace:\n{trace}')
    write_stream = get_difference(directory, trace)
    logging.debug(f'Difference found:\n{write_stream}')
    if len(write_stream) == 0:
        logging.info('No data to update')
        return False

    # Get the filename
    filename = Path(directory).joinpath(
        trace.stats.network,
        trace.stats.station,
        '{network}.{station}.{location}.{channel}.\
{year}.{doy}.{timestamp}'.format(
            **trace.stats,
            year=trace.stats.starttime.year,
            doy=trace.stats.starttime.strftime('%j'),
            timestamp=UTCDateTime().timestamp,
        )
    )

    # Write to directory
    logging.info(f'Writting new stream to {filename}:\n{write_stream}')
    filename.parent.mkdir(parents=True, exist_ok=True)
    write_stream.write(
        str(filename),
        format='MSEED',
        reclen=512,
        encoding='FLOAT32')

    return True
