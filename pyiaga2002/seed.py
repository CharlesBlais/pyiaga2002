'''
author: Charles Blais
'''


class SeedError(Exception):
    '''Seed Exception Class'''
    pass


def get_bandcode(sampling_rate, corner_period=None):
    '''
    Convert the sampling rate (hz) to its respective band code
    See Appendix A of the Seed documentation

    :param sampling_rate: sampling rate in Hz
    :param corner_period: corner period used to determine bandcode

    :return: bandcode, string

    :throws: MseedException
    '''
    if sampling_rate >= 1000 and sampling_rate < 5000:
        return 'G' if corner_period < 10 else 'F'
    if sampling_rate >= 250 and sampling_rate < 1000:
        return 'D' if corner_period < 10 else 'C'
    if sampling_rate >= 80 and sampling_rate < 250:
        return 'E' if corner_period < 10 else 'H'
    if sampling_rate >= 10 and sampling_rate < 80:
        return 'S' if corner_period < 10 else 'B'
    if sampling_rate > 1 and sampling_rate < 10:
        return 'M'
    if sampling_rate == 1:
        return 'L'
    if sampling_rate >= 0.05 and sampling_rate < 1:
        return 'V'
    if sampling_rate >= 0.001 and sampling_rate < 0.05:
        return 'U'
    if sampling_rate >= 0.0001 and sampling_rate < 0.001:
        return 'R'
    if sampling_rate >= 0.00001 and sampling_rate < 0.0001:
        return 'P'
    if sampling_rate >= 0.000001:
        return 'T'
    raise SeedError("Unable to convert sampling rate {0} to SEED band code".format("sampling_rate"))
