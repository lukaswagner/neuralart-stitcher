import subprocess
import os.path
from PIL import Image
import math

neuralart_dir = '/home/lukas/Dokumente/neuralart-master/'
temp_dir = os.path.abspath('temp/')
frame_dir = temp_dir + 'frames/'
output_file = os.path.abspath('output.jpg')
style = '/home/lukas/Dokumente/neuralart-master/input/vg_field.jpg'
content = '/home/lukas/Dokumente/neuralart-master/input/part_test_2.jpg'
style_factor = 2E10
smoothness = 1E-1
num_iters = 10
width = 1000
height = -1
blockCountH = -1
blockCountV = -1
blockHeight = 333
blockWidth = 500

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
    for i in range(0, blockCountH * 2 - 1):
        block = row.copy().crop(
            (
                int(i * 0.5 * ceilBlockWidth),
                0,
                int(max([(i + 1) * 0.5 * ceilBlockWidth, width])),
                height
            )
        )
        print('running neuralart... ', end=' ')
        temp_file = temp_dir + 'temp.jpg'
        block.save(temp_file)
        runNeuralart(temp_file)
        block = Image.open(temp_file)
        print('done')
        # TODO: blended pasting
        row.paste(
            block,
            (
                int(i * 0.5 * ceilBlockWidth),
                0
            )
        )
    return row

def splitVertically(image):
    ceilBlockHeight = math.ceil(blockHeight)
    for i in range(0, blockCountV * 2 - 1):
        row = image.copy().crop(
            (
                0,
                int(i * 0.5 * ceilBlockHeight),
                width,
                int(max([(i + 1) * 0.5 * ceilBlockHeight, height]))
            )
        )
        print('splitting horizontally...')
        row = splitHorizontally(row)
        print('splitting horizontally done')
        # TODO: blended pasting
        image.paste(
            row,
            (
                0,
                int(i * 0.5 * ceilBlockHeight)
            )
        )
    return image

def main():
    print('starting neuaralart-stitcher')
    print('loading input... ', end=' ')
    image = Image.open(content)
    print('done')
    print('calculating dimensions... ', end=' ')
    image = calcDimensionsAndResize(image)
    print('done')
    print('splitting vertically...')
    image = splitVertically(image)
    print('plitting vertically done')
    print('showing and saving output... ', end=' ')
    image.show()
    image.save(output_file)
    print('done')
    print('exiting neuralart-stitcher')

if __name__ == "__main__":
    main()
