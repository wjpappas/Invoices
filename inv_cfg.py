#! usr/bin/python
import configparser
import argparse
import textwrap

def read_user_cli_args():   # this doesn't act correctly when no args are given
    """Handle the CLI user interactions.
    Returns:
        argparse.Namspace: Populated namespace object
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent('''\
        builds config file "[vendor].ini" from map and data files
        --------------------------------------------------
        map file    "sherwin_map.txt"
        data file   "[vendor].txt"    '''))
    parser.add_argument('-f', '--file', nargs=2, help='enter two files, "map" and "data"')
    return parser.parse_args()

def make_config(key_map, vendor):
    config = configparser.ConfigParser()
    with open(key_map, 'r')as read_k, open(vendor, 'r')as read_v:
        sect_test = [x.rstrip() for x in read_k.readline().split(',')]
        for ss in sect_test:
            config[ss] = {}
        v_sect = config.sections()
        r_val = [int(x.rstrip()) for x in read_v.readline().split(',')]
#        print(sect_test, v_sect, r_val)
        for sect, val in zip(v_sect, r_val):
            for kline in range(val):
                kline = (read_k.readline()).strip()
                vline = (read_v.readline()).strip()
#                print(sect, kline, vline)
                config[sect][kline] = vline
    outputFile = vendor[:vendor.index('.')] + '.ini'
    with open(outputFile, 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    input = read_user_cli_args()
    print(input)
    list_re, list_gp = input.file
    make_config(list_re, list_gp)
#print(list_re)
#print(list_gp)
