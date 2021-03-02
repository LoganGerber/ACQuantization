""" Quantize an image to use a color palette available in Animal Crossing: New Horizons."""
import argparse
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import ACColorGenerator


def QuantizeImage(image_file, nondeterministic=False, alpha=False):
    """ Quantize an image down to 15 colors, all available in Animal Crossing: New Horizons Custom Designer.

    Arguments:
    image_file -- An array-like containing the RGB values of an image.
        Must be of dimensions (x, y, >=3), where x, y are the width and height of the image, respectively.
    nondeterministic -- should the k-means algorithm initialize with a random seed? (default False)
    alpha -- Is there an alpha channel in the supplied image? (default False)

    Returns:
    A numpy array with dimentions (x, y, [3|4]) containing the HSV(A) values of the quantized image.
    """
    color_map = ACColorGenerator.GenerateRgbToHsvColorMap()
    rgb_ac_colors = np.asarray(list(color_map.keys()), dtype=np.float64)

    image = np.array(image_file, dtype=np.float64)
    width, height, depth = tuple(image.shape)

    flattened_image = np.reshape(image, (width * height, depth))
    kmeans = KMeans(n_clusters=15, random_state=None if nondeterministic else 0).fit(
        flattened_image)
    predicted_image = kmeans.cluster_centers_[kmeans.predict(flattened_image)]

    # pylint: disable=consider-using-enumerate
    # pylint: disable=redefined-outer-name
    for i in range(len(predicted_image)):
        predicted_color = predicted_image[i][:3]
        distances = np.sum((rgb_ac_colors - predicted_color) ** 2, axis=1)
        closest_rgb = rgb_ac_colors[np.argmin(distances)]
        closest_hsv = color_map[tuple(closest_rgb)]
        if alpha:
            flattened_image[i] = np.append(closest_hsv, predicted_image[i][3])
        else:
            flattened_image[i] = closest_hsv

    image = np.reshape(flattened_image, (width, height, depth))

    return image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Quantize an image to use a color palette available in Animal Crossing: New Horizons.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('image_file', type=Image.open,
                        help='Location of image to quantize.')

    parser.add_argument('-o', '--output', default='./output.png',
                        help='Location to save the quantized image.', dest='output')

    parser.add_argument('--random-seed', action='store_true',
                        help='''If set, a random seed will be used for initial k-means values.
                                This results in a non-deterministic images being generated.
                                Omitting this will result in a deterministic image being generated.''')

    parser.add_argument('-p', '--palette', choices=['rgb', 'hsv', 'ac'], dest='palette',
                        help='''Print the color palette used in the final image to the standard output stream.
                                "rgb" prints the colors in RGB format (0-255 for each channel).
                                "hsv" prints the colors in HSV format (0-255 for each channel).
                                "ac" prints the HSV indices given in Animal Crossing: New Horizons.''')

    parser.add_argument('--prequantize', action='store_true',
                        help='''If set, quantization will happen once before the image is resized to 32x32.
                                Quantization will still occur after resizing as well.''')

    parser.add_argument('--resize_algorithm', choices=['nearest', 'box', 'bilinear', 'hamming', 'bicubic', 'lanczos'],
                        dest='alg',
                        help='''Resizing algorithm to use when scaling the original image.''', default='bicubic')

    args = parser.parse_args()

    has_alpha = False
    if args.image_file.mode == 'RGBA':
        has_alpha = True

    converted_image = args.image_file.convert('RGBA' if has_alpha else 'RGB')

    if args.prequantize:
        converted_image = QuantizeImage(
            converted_image, args.random_seed, has_alpha)

    resize_alg = None

    if args.alg == 'nearest':
        resize_alg = Image.NEAREST
    elif args.alg == 'box':
        resize_alg = Image.BOX
    elif args.alg == 'bilinear':
        resize_alg = Image.BILINEAR
    elif args.alg == 'hamming':
        resize_alg = Image.HAMMING
    elif args.alg == 'bicubic':
        resize_alg = Image.BICUBIC
    elif args.alg == 'lanczos':
        resize_alg = Image.LANCZOS

    quantized_image = QuantizeImage(
        converted_image.resize((32, 32), resize_alg), args.random_seed, has_alpha)

    # Change the quantized image into RGB values with channels of size 8 bits
    im_width, im_height, im_depth = quantized_image.shape
    flattened_qimage = np.reshape(
        quantized_image, (im_width*im_height, im_depth))

    flattened_rgb_image = np.ndarray(flattened_qimage.shape)

    # pylint: disable=consider-using-enumerate
    for i in range(len(flattened_qimage)):
        pixel = flattened_qimage[i]
        pixel = ACColorGenerator.HsvToRgb(pixel, has_alpha)
        pixel = [round(channel) for channel in pixel]
        flattened_rgb_image[i] = pixel

    fixed_image = flattened_rgb_image.astype(np.int8)
    fixed_image = np.reshape(fixed_image, (im_width, im_height, im_depth))

    Image.fromarray(
        fixed_image, mode='RGBA' if has_alpha else 'RGB').save(args.output)

    if args.palette:
        unique_colors = np.unique(flattened_qimage, axis=0)

        index = 1
        for color in unique_colors:
            if args.palette == 'hsv':
                print(tuple(color))
            elif args.palette == 'rgb':
                print(ACColorGenerator.HsvToRgb(color))
            elif args.palette == 'ac':
                print('{} {}'.format(index, ACColorGenerator.HsvToACIndexes(color)))
                index += 1
        print('{} total colors.'.format(len(unique_colors)))
