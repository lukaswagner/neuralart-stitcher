import subprocess
import os.path
from PIL import Image
import math

neuralart_dir = '/home/lukas/Dokumente/neuralart-master/'
temp_dir = os.path.abspath('temp')
frame_dir = temp_dir + '/frames'
style = '/home/lukas/Dokumente/neuralart-master/input/vg_field.jpg'
content = '/home/lukas/Dokumente/neuralart-master/input/part_test_2.jpg'
style_factor = 2E6
smoothness = 5E-3
num_iters = 500
width = -1
height = 1000
blockCountH = -1
blockCountV = -1
blockHeight = 500
blockWidth = 333

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

def runNeuralart():
    neuralartArgs = [
        'qlua', 'main.lua',
        '--style', style,
        '--content', content,
        '--style_factor', str(style_factor),
        '--smoothness', str(smoothness),
        '--display_interval', str(0),
        '--num_iters', str(10),
        '--output_dir', frame_dir
    ]
    subproc = subprocess.Popen(neuralartArgs, cwd=neuralart_dir)
    subproc.wait()

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

def splitVertically(image):
    rows = []
    ceilBlockHeight = math.ceil(blockHeight)
    for i in range(0, blockCountV * 2 - 1):
        rows.append(image.copy().crop((
            0,
            int(i * 0.5 * ceilBlockHeight),
            width,
            int((i + 1) * 0.5 * ceilBlockHeight)
        )))
    for i, row in enumerate(rows):
        # TODO: split horizontally
        # TODO: blended pasting
        image.paste(
            row,
            (0,
            int(i * 0.5 * ceilBlockHeight),
            width,
            int(max([(i + 1) * 0.5 * ceilBlockHeight, height])))
        )
    return image

def main():
    print('test')
    #runNeuralart()
    image = Image.open(content)
    image = calcDimensionsAndResize(image)
    image = splitVertically(image)
    image.show()
    print('test2')

if __name__ == "__main__":
    main()
