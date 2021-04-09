# Convert IAGA2002 to MiniSeed

Library for converting IAGA2002 to MiniSeed.

## Installation

```bash
pip3 install --user git+[git repo]
# or
git clone [git repo]
pip3 install --user .
```

## Command-line tools

### iaga2mseed

Convert IAGA2002 to miniseed file

```bash
bash-4.2$ iaga2mseed -h
usage: iaga2mseed [-h] [--output OUTPUT] [--network NETWORK] [-v] filename

Read IAGA2002 file as miniSeed

positional arguments:
  filename           IAGA2002 file to convert

optional arguments:
  -h, --help         show this help message and exit
  --output OUTPUT    Output file (default: [filename].mseed)
  --network NETWORK  Network code (default: XX)
  -v, --verbose      Verbosity
```

### iaga2mscan

Convert IAGA2002 to miniseed for ringserver MSCAN.  It will read current files in the directory and only add the difference to be sent from the input IAGA2002 file.

```bash
bash-4.2$ iaga2mscan -h
usage: iaga2mscan [-h] [--directory DIRECTORY] [--network NETWORK] [-v]
                  filename

Read IAGA2002 file as miniSeed

positional arguments:
  filename              IAGA2002 file to convert

optional arguments:
  -h, --help            show this help message and exit
  --directory DIRECTORY
                        Output file (default: .)
  --network NETWORK     Network code (default: XX)
  -v, --verbose         Verbosity
```
