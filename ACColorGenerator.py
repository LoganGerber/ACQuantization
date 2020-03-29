"""Get all valid RGB colors in the Animal Crossing: New Horizon Custom Designer."""
import colorsys
import argparse


def GenerateHsvACColors():
    """ Generate a list of all unique HSV colors available for use in the Animal Crossing: New Horizon Custom Designer.
    """
    sat_val_step = 100 / 14

    hsv_values = list()
    for hue in range(0, 360, 12):
        sat = 0
        while sat <= 100:
            val = 0
            while val <= 100:
                hsv_values.append((hue, sat, val))

                val += sat_val_step
            sat += sat_val_step

    return hsv_values


def GenerateRgbACColors():
    """ Generate a list of all unique RGB colors available for use in the Animal Crossing: New Horizon Custom Designer.
    """
    rgb_values = list()
    for hsv_color in GenerateHsvACColors():
        norm_rgb = colorsys.hsv_to_rgb(
            hsv_color[0] / 360, hsv_color[1] / 100, hsv_color[2] / 100)
        rgb_values.append(tuple(map(lambda c: c * 255, norm_rgb)))

    return rgb_values


def GenerateRgbToHsvColorMap():
    """ Generate a map from all Animal Crossing RGB colors to their respective HSV values
    """
    mapping = {}
    for hsv_color in GenerateHsvACColors():
        norm_rgb = colorsys.hsv_to_rgb(
            hsv_color[0] / 360, hsv_color[1] / 100, hsv_color[2] / 100)
        rgb = tuple(map(lambda c: c * 255, norm_rgb))

        mapping[rgb] = hsv_color

    return mapping


def GenerateHsvToRgbColorMap():
    """ Generate a map from all Animal Crossing HSV colors to their respective RGB values
    """
    mapping = {}
    for hsv_color in GenerateHsvACColors():
        norm_rgb = colorsys.hsv_to_rgb(
            hsv_color[0] / 360, hsv_color[1] / 100, hsv_color[2] / 100)
        rgb = tuple(map(lambda c: c * 255, norm_rgb))

        mapping[hsv_color] = rgb

    return mapping


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Print all valid colors in Animal Crossing: New Horizon Custom Designer.', prefix_chars='-/')
    argparser.add_argument('-m', '--mode', dest='mode', choices=['rgb', 'rgb_rounded', 'hsv'], default='rgb',
                           help='Format for the printed colors. Default is "rgb".')
    argparser.add_argument('-t', '--total', action='store_true', dest='print_total',
                           help='Print the total number of entries at the end.')

    args = argparser.parse_args()

    colors = GenerateHsvACColors() if args.mode == 'hsv' else GenerateRgbACColors()

    for color in colors:
        if args.mode == 'rgb_rounded':
            color = [round(color[0]), round(color[1]), round(color[2])]
        else:
            color = list(color)
        print(color)

    if args.print_total:
        print('{} total colors.'.format(len(colors)))
