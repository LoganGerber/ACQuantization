"""Get all valid RGB colors in the Animal Crossing: New Horizon Custom Designer."""
import colorsys
import argparse


def GenerateValidACColors():
    """ Generate a set of all unique RGB colors available for use in the Animal Crossing: New Horizon Custom Designer.
    """
    sat_val_step = 100 / 14

    rgb_values = set()
    for hue in range(0, 360, 12):
        sat = 0
        while sat <= 100:
            val = 0
            while val <= 100:
                rgb = colorsys.hsv_to_rgb(hue / 360, sat / 100, val / 100)
                rgb = tuple(map(lambda x: int(x * 255), rgb))

                rgb_values.add(rgb)

                val += sat_val_step
            sat += sat_val_step

    return rgb_values


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Print all valid RGB colors in Animal Crossing: New Horizon Custom Designer.', prefix_chars='-/')
    argparser.add_argument('-t', '--total', action='store_true', dest='print_total',
                           help='Print the total number of entries at the end.')

    args = argparser.parse_args()

    colors = GenerateValidACColors()

    for color in colors:
        print(color)

    if args.print_total:
        print('{} total colors.'.format(len(colors)))
