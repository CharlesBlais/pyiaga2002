'''
..  codeauthor:: Charles Blais <charles.blais@canada.ca>
'''
import logging
from pathlib import Path
import shutil

import pytest
import pyiaga2002.iaga2002 as iaga2002
import pyiaga2002.mscan as mscan


TEST_DIR = Path('.').joinpath('tests', '.tmp')
TEST_NETWORK = 'XX'


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute asserts before and after a test is run"""
    logging.debug(f'Making test directory {TEST_DIR}')
    TEST_DIR.mkdir(exist_ok=True)
    yield  # this is where the testing happens
    logging.debug(f'Deleting test directory {TEST_DIR}')
    shutil.rmtree(TEST_DIR)


def test_correction():
    '''
    Test correction scenario
    '''
    stream1 = iaga2002.read('tests/scenario_correction/ykc20210405vmin.min.1')
    stream2 = iaga2002.read('tests/scenario_correction/ykc20210405vmin.min.2')

    for trace in stream1:
        trace.stats.network = TEST_NETWORK
        mscan.update(TEST_DIR, trace)

    changed = False
    for trace in stream2:
        trace.stats.network = TEST_NETWORK
        if not changed:
            changed = mscan.update(TEST_DIR, trace)
    assert changed


def test_gap():
    '''
    Test gap scenario
    '''
    stream1 = iaga2002.read('tests/scenario_gap/ykc20210405vmin.min.1')
    stream2 = iaga2002.read('tests/scenario_gap/ykc20210405vmin.min.2')

    for trace in stream1:
        trace.stats.network = TEST_NETWORK
        mscan.update(TEST_DIR, trace)

    changed = False
    for trace in stream2:
        trace.stats.network = TEST_NETWORK
        if not changed:
            changed = mscan.update(TEST_DIR, trace)
    assert changed


def test_newdata():
    '''
    Test gap scenario
    '''
    stream1 = iaga2002.read('tests/scenario_newdata/ykc20210405vmin.min.1')
    stream2 = iaga2002.read('tests/scenario_newdata/ykc20210405vmin.min.2')

    for trace in stream1:
        trace.stats.network = TEST_NETWORK
        mscan.update(TEST_DIR, trace)

    changed = False
    for trace in stream2:
        trace.stats.network = TEST_NETWORK
        if not changed:
            changed = mscan.update(TEST_DIR, trace)
    assert changed


def test_nochange():
    '''
    Test gap scenario
    '''
    stream1 = iaga2002.read('tests/scenario_nochange/ykc20210405vmin.min.1')
    stream2 = iaga2002.read('tests/scenario_nochange/ykc20210405vmin.min.2')

    for trace in stream1:
        trace.stats.network = TEST_NETWORK
        mscan.update(TEST_DIR, trace)

    changed = False
    for trace in stream2:
        trace.stats.network = TEST_NETWORK
        if not changed:
            changed = mscan.update(TEST_DIR, trace)
    assert not changed
