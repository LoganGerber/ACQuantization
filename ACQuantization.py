""" Quantize an image to use a color pallet available in Animal Crossing: New Horizons."""
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
    rgb_ac_colors = np.asarray(list(color_map.keys()))

    image = np.array(image_file)
    width, height, depth = tuple(image.shape)

    flattened_image = np.reshape(image, (width * height, depth))
    kmeans = KMeans(n_clusters=15, random_state=None if nondeterministic else 0).fit(
        flattened_image)
    predicted_image = kmeans.cluster_centers_[kmeans.predict(flattened_image)]

    # pylint: disable=consider-using-enumerate
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
        description='Quantize an image to use a color pallet available in Animal Crossing: New Horizons.')
    parser.add_argument('image_file', type=Image.open,
                        help='Location of image to quantize.')
    parser.add_argument('-o', '--output', default='./output.png',
                        help='Location to save the quantized image. Default is "output.png"', dest='output')
    parser.add_argument('--random-seed', action='store_true',
                        help='''If set, a random seed will be used for initial k-means values.
                                This results in a non-deterministic images being generated.
                                Omitting this will result in a deterministic image being generated.''')

    args = parser.parse_args()

    quantized_image = QuantizeImage(
        args.image_file.convert('RGB'), args.random_seed)

    Image.fromarray(quantized_image, mode='HSV').convert(
        'RGB').save(args.output)
