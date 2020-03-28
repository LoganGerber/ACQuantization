import colorsys
import sys
import argparse

SAT_VAL_STEP = 100 / 14


def GenerateValidACColors():
    rgb_values = set()
    for h in range(0, 360, 12):
        s = 0
        while s <= 100:
            v = 0
            while v <= 100:
                rgb = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
                rgb = tuple(map(lambda x: int(x * 255), rgb))

                rgb_values.add(rgb)

                v += SAT_VAL_STEP
            s += SAT_VAL_STEP

    return rgb_values


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Print all valid RGB colors in Animal Crossing: New Horizon.', prefix_chars='-/')
    argparser.add_argument('-t', '--total', action='store_true', dest='print_total',
                           help='Print the total number of entries at the end.')

    args = argparser.parse_args()

    vals = GenerateValidACColors()

    for val in vals:
        print(val)

    if args.print_total:
        print('{} total values'.format(len(vals)))
