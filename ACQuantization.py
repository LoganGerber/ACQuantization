""" Quantize an image to use a color palette available in Animal Crossing: New Horizons."""
import argparse
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import ACColorGenerator


def QuantizeImage(image_file, nondeterministic=False):
    """ Quantize an image down to 15 colors, all available in Animal Crossing: New Horizons Custom Designer.

    Arguments:
    image_file -- An array-like containing the RGB values of an image.
        Must be of dimensions (x, y, 3), where x, y are the width and height of the image, respectively.
    nondeterministic -- should the k-means algorithm initialize with a random seed? (default False)

    Returns:
    A numpy array with dimentions (x, y, 3) containing the HSV values of the quantized image.
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
        predicted_color = predicted_image[i]
        distances = np.sum((rgb_ac_colors - predicted_color) ** 2, axis=1)
        closest_rgb = rgb_ac_colors[np.argmin(distances)]
        closest_hsv = color_map[tuple(closest_rgb)]
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

    args = parser.parse_args()

    quantized_image = QuantizeImage(
        args.image_file.convert('RGB'), args.random_seed)

    # Change the quantized image into RGB values with channels of size 8 bits
    im_width, im_height, im_depth = quantized_image.shape
    flattened_qimage = np.reshape(
        quantized_image, (im_width*im_height, im_depth))

    flattened_rgb_image = np.ndarray(flattened_qimage.shape)

    # pylint: disable=consider-using-enumerate
    for i in range(len(flattened_qimage)):
        pixel = flattened_qimage[i]
        pixel = ACColorGenerator.HsvToRgb(pixel)
        pixel = [round(channel) for channel in pixel]
        flattened_rgb_image[i] = pixel

    fixed_image = flattened_rgb_image.astype(np.int8)
    fixed_image = np.reshape(fixed_image, (im_width, im_height, im_depth))

    Image.fromarray(fixed_image, mode='RGB').save(args.output)

    if args.palette:
        unique_colors = np.unique(flattened_qimage, axis=0)

        for color in unique_colors:
            if args.palette == 'hsv':
                print(tuple(color))
            elif args.palette == 'rgb':
                print(ACColorGenerator.HsvToRgb(color))
            elif args.palette == 'ac':
                print(ACColorGenerator.HsvToACIndexes(color))
