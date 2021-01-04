#!/usr/bin/python3

import sys

# read each line coming from stdin and reverse it

def reverse(line):

    return ' '.join(reversed(line.split()))

if __name__ == '__main__':
    for line in sys.stdin:
        print(reverse(line))


