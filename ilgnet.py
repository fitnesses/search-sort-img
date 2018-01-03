from caffe2.proto import caffe2_pb2
import numpy as np
import skimage.io
import skimage.transform
import logging
from caffe2.python import workspace

logger = logging.getLogger('ilgnet')
# logging.basicConfig(level=logging.DEBUG)

INPUT_IMAGE_SIZE = 227
MEAN_FILE = '/mnt/tmp-img/ml/ILGnet/mean/AVA2_mean.npy'
INIT_NET = '/mnt/tmp-img/ml/ILGnet/init_net.pb'
PREDICT_NET = '/mnt/tmp-img/ml/ILGnet/predict_net.pb'


def crop_center(img, cropx, cropy):
    y, x, c = img.shape
    startx = x // 2 - (cropx//2)
    starty = y // 2 - (cropy//2)
    return img[starty:starty + cropy, startx:startx + cropx]


def rescale(img, input_height, input_width):
    logger.debug("Original image shape:" + str(img.shape) + " and remember it should be in H, W, C!")
    logger.debug("Model's input shape is %dx%d" % (input_height, input_width))
    aspect = img.shape[1] / float(img.shape[0])
    logger.debug("Orginal aspect ratio: " + str(aspect))
    if(aspect > 1):
        # landscape orientation - wide image
        res = int(aspect * input_height)
        imgScaled = skimage.transform.resize(img, (input_width, res))
    if(aspect < 1):
        # portrait orientation - tall image
        res = int(input_width / aspect)
        imgScaled = skimage.transform.resize(img, (res, input_height))
    if(aspect == 1):
        imgScaled = skimage.transform.resize(img, (input_width, input_height))

    logger.debug("New image shape:" + str(imgScaled.shape) + " in HWC")
    return imgScaled


def process_images(images):

    mean = np.load(MEAN_FILE).mean(1).mean(1)
    mean = mean[:, np.newaxis, np.newaxis]
    processed_img = []
    for img_path in images:

        img = skimage.img_as_float(skimage.io.imread(img_path)).astype(np.float32)
        img = rescale(img, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE)
        img = crop_center(img, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE)

        img = img.swapaxes(1, 2).swapaxes(0, 1)

        img = img[(2, 1, 0), :, :]
        img = img * 255 - mean
        # add batch size
        img = img[np.newaxis, :, :, :].astype(np.float32)
	processed_img.append(img)
    return processed_img


def score(images):
    imgs = process_images(images)
    with open(INIT_NET) as f:
        init_net = f.read()
    with open(PREDICT_NET) as f:
        predict_net = f.read()

    p = workspace.Predictor(init_net, predict_net)
   
    img_to_score = {} 
    for (index, img) in enumerate(imgs):
        results = p.run([img])
        logger.debug('img: %s with score %f \n\t' % (images[index], results[0][0,1]))
        img_to_score[images[index]] = results[0][0, 1]

    return img_to_score


# score(['steak/1.jpg', 'steak/2.jpg'])
