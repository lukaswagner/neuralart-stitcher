import subprocess
import os
from PIL import Image
import math
import time

neuralart_dir = '/home/lukas/Dokumente/neuralart-master/'
temp_dir = os.path.abspath('temp')
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
frame_dir = temp_dir + '/frames/'
output_file = os.path.abspath('output.jpg')
style = '/home/lukas/Dokumente/neuralart-master/input/vg_field.jpg'
content = '/home/lukas/Dokumente/neuralart-master/input/IMG_3152.JPG'
style_factor = 2E10
smoothness = 1E-1
num_iters = 10
width = 1000
height = -1
blockCountH = -1
blockCountV = -1
blockHeight = 333
blockWidth = 500
mask_h = Image.open('mask_h.png')
mask_v = Image.open('mask_v.png')
mask_full = Image.open('mask_full.png')

# def parseArgs():
#     try:
#       opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
#    except getopt.GetoptError:
#       print 'test.py -i <inputfile> -o <outputfile>'
#       sys.exit(2)
#    for opt, arg in opts:
#       if opt == '-h':
#          print 'test.py -i <inputfile> -o <outputfile>'
#          sys.exit()
#       elif opt in ("-i", "--ifile"):
#          inputfile = arg
#       elif opt in ("-o", "--ofile"):
#          outputfile = arg
#    print 'Input file is "', inputfile
#    print 'Output file is "', outputfile

def runNeuralart(temp_file):
    neuralartArgs = [
        'qlua', 'main.lua',
        '--style', style,
        '--content', temp_file,
        '--style_factor', str(style_factor),
        '--smoothness', str(smoothness),
        '--display_interval', str(0),
        '--num_iters', str(10),
        '--output_dir', frame_dir,
        '--size', str(500) #same size as temp_file
    ]
    subproc = subprocess.Popen(neuralartArgs, cwd=neuralart_dir)
    subproc.wait()
    copyArgs = [
        'cp',
        frame_dir + '0010.jpg',
        temp_file
    ]
    copyproc = subprocess.Popen(copyArgs)
    copyproc.wait()

def calcDimensionsAndResize(image):
    global width, height, blockCountH, blockCountV, blockWidth, blockHeight
    aspectRatio = image.width / image.height
    if width != -1:
        height = int(width / aspectRatio)
    elif height != -1:
        width = int(height * aspectRatio)
    else:
        width = image.width
        height = image.height
    blockCountH = math.ceil(width / blockWidth)
    blockCountV = math.ceil(height / blockHeight)
    blockWidth = width / blockCountH
    blockHeight = height / blockCountV
    return image.resize((width, height))

def splitHorizontally(row):
    ceilBlockWidth = math.ceil(blockWidth)
    outRow = Image.new("RGB", (width, row.size[1]))
    for i in range(0, blockCountH * 2 - 1):
        cropbox = (
            int(i * 0.5 * ceilBlockWidth),
            0,
            int(min([(i + 2) * 0.5 * ceilBlockWidth, width])),
            row.size[1]
        )
        block = row.crop(cropbox)
        print('>> running neuralart on block ' + str(i * 0.5 + 1) + ' ...')
        temp_file = temp_dir + '/temp.jpg'
        block.save(temp_file)
        runNeuralart(temp_file)
        block = Image.open(temp_file)
        print('>> running neuralart on block ' + str(i * 0.5 + 1) + ' done')
        pastepos = (
            int(i * 0.5 * ceilBlockWidth),
            0
        )
        if(i == 0):
            blockMask = mask_full.resize(block.size)
        else:
            blockMask = mask_h.resize(block.size)
        outRow.paste(block, pastepos, blockMask)
        # print('CROPBOX: ' + str(cropbox) + ' PASTEPOS: ' + str(pastepos))
    return outRow

def splitVertically(image):
    ceilBlockHeight = math.ceil(blockHeight)
    outImage = Image.new("RGB", (width, height))
    for i in range(0, blockCountV * 2 - 1):
        cropbox = (
            0,
            int(i * 0.5 * ceilBlockHeight),
            width,
            int(min([(i + 2) * 0.5 * ceilBlockHeight, height]))
        )
        row = image.crop(cropbox)
        print('> splitting row ' + str(i * 0.5 + 1) + ' horizontally...')
        row = splitHorizontally(row)
        print('> splitting row ' + str(i * 0.5 + 1) + ' horizontally done')
        pastepos = (
            0,
            int(i * 0.5 * ceilBlockHeight)
        )
        if(i == 0):
            rowMask = mask_full.resize(row.size)
        else:
            rowMask = mask_v.resize(row.size)
        #outImage.paste(row, pastepos, rowMask)
        outImage.paste(row, pastepos, rowMask)
        # print('CROPBOX: ' + str(cropbox) + ' PASTEPOS: ' + str(pastepos))
    return outImage

def main():
    start = time.time()
    print('starting neuaralart-stitcher')
    print('loading input...', end=' ')
    image = Image.open(content)
    print('done')
    print('calculating dimensions...', end=' ')
    image = calcDimensionsAndResize(image)
    print('done')
    print('output width: ' + str(width) + ' output height: ' + str(height) + ' blockCountH: ' + str(blockCountH) + ' blockCountV: ' + str(blockCountV) + ' blockWidth: ' + str(blockWidth) + ' blockHeight: ' + str(blockHeight))
    print('splitting vertically...')
    image = splitVertically(image)
    print('splitting vertically done ')
    print('showing and saving output...', end=' ')
    image.show()
    image.save(output_file)
    print('done')
    stop = time.time()
    print('total calculation time: ' + "%.3f" % round(stop - start, 3) + ' seconds')
    print('exiting neuralart-stitcher')

if __name__ == "__main__":
    main()
