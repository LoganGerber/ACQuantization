"""Get all valid RGB colors in the Animal Crossing: New Horizon Custom Designer."""
import colorsys
import argparse


def GenerateHsvACColors():
    """ Generate a list of all unique HSV colors available for use in the Animal Crossing: New Horizon Custom Designer.
    """
    hue_step = 255 / 29
    sat_val_step = 255 / 14

    hsv_values = list()
    hue = 0
    while hue < 255:
        sat = 0
        while sat <= 255:
            val = 0
            while val <= 255:
                hsv_values.append((hue, sat, val))

                val += sat_val_step
            sat += sat_val_step
        hue += hue_step

    return hsv_values


def HsvToRgb(hsv, alpha=False):
    """ Convert an HSV color to RGB.
    hsv is expected to be of form [0-255, 0-255, 0-255]
    """

    norm_hsv = [channel / 255 for channel in hsv]
    norm_rgb = colorsys.hsv_to_rgb(norm_hsv[0], norm_hsv[1], norm_hsv[2])

    rgb = tuple(map(lambda c: c * 255, norm_rgb))

    if alpha:
        rgb = (rgb[0], rgb[1], rgb[2], hsv[3])

    return rgb


def GenerateRgbACColors():
    """ Generate a list of all unique RGB colors available for use in the Animal Crossing: New Horizon Custom Designer.
    """
    rgb_values = list()
    for hsv_color in GenerateHsvACColors():
        rgb = HsvToRgb(hsv_color)
        if not rgb in rgb_values:
            rgb_values.append(rgb)

    return rgb_values


def GenerateRgbToHsvColorMap():
    """ Generate a map from all Animal Crossing RGB colors to their respective HSV values
    """
    mapping = {}
    for hsv_color in GenerateHsvACColors():
        mapping[HsvToRgb(hsv_color)] = hsv_color

    return mapping


def GenerateHsvToRgbColorMap():
    """ Generate a map from all Animal Crossing HSV colors to their respective RGB values
    """
    mapping = {}
    for hsv_color in GenerateHsvACColors():
        mapping[hsv_color] = HsvToRgb(hsv_color)

    return mapping


def HsvToACIndexes(hsv):
    """ Convert an HSV color to its closest valid color in Animal Crossing: New Horizons.
    HSV colors are expected to be of the form (0-255, 0-255, 0-255)
    """
    hue_step = 255 / 29
    sat_val_step = 255 / 14

    return (
        int(round(hsv[0] / hue_step)) + 1,
        int(round(hsv[1] / sat_val_step)) + 1,
        int(round(hsv[2] / sat_val_step)) + 1)


def __ExecColors(args):
    colors = GenerateHsvACColors() if args.mode == 'hsv' else GenerateRgbACColors()

    for color in colors:
        if args.mode == 'rgb_rounded':
            color = (round(color[0]), round(color[1]), round(color[2]))
        print(color)

    if args.print_total:
        print('{} total colors.'.format(len(colors)))


def __ExecIndex(args):
    hue = (args.hue / args.ranges[0]) * 255
    sat = (args.sat / args.ranges[1]) * 255
    val = (args.val / args.ranges[2]) * 255

    print(HsvToACIndexes((hue, sat, val)))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Color utilities for Animal Crossing: New Horizons.')

    subparsers = argparser.add_subparsers(title='Utilities')

    colors_parser = subparsers.add_parser(
        'colors', help='Generate all valid colors usable in Animal Crossing: New Horizons.')

    colors_parser.add_argument('-m', '--mode', dest='mode', choices=['rgb', 'rgb_rounded', 'hsv'], default='rgb',
                               help='Format for the printed colors. Default is "rgb".')
    colors_parser.add_argument('-t', '--total', action='store_true', dest='print_total',
                               help='Print the total number of entries at the end.')
    colors_parser.set_defaults(func=__ExecColors)

    index_parser = subparsers.add_parser(
        'index',
        help='Convert an HSV value to the closest indexes available in the Animal Crossing Custom Designer.')

    index_parser.add_argument('hue', help='Hue', metavar='Hue', type=float)
    index_parser.add_argument('sat', help='Saturation',
                              metavar='Saturation', type=float)
    index_parser.add_argument('val', help='Value', metavar='Value', type=float)
    index_parser.add_argument('-r', '--input-ranges', nargs=3, default=[255.0, 255.0, 255.0], type=float,
                              help='''
                              The maximum values for hue, saturation, and value. For example, when the values 360 100 100 are supplied, Hue will have a range of 0-360, Saturation will have a range 0-100, and Value will have a range 0-100. Default is 255 255 255.
                              ''', dest='ranges', metavar='RANGE')
    index_parser.set_defaults(func=__ExecIndex)

    parsed_args = argparser.parse_args()

    parsed_args.func(parsed_args)
