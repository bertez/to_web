#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

class BatchProcess(object):
    """This class processes a list of videos to video formats usable by modern browsers (mp4 and ogv)"""

    __author__ = 'Berto Yáñez'
    __version__ = '0.1'

    encodings = {
            'mp4' : ['ffmpeg -i {0} -pass 1 -vcodec libx264 -vpre fast_firstpass -b {4}k -bt {4}k -threads 4 -s {2}x{3} -f rawvideo -an -y /dev/null','ffmpeg -i {0} -pass 2 -acodec libfaac -ab {5}k -ac 2 -vcodec libx264 -vpre slow -b {4}k -bt {4}k -threads 4 -s {2}x{3} {1}'],
            'ogv' : ['ffmpeg2theora -V {4} -A {5} -x {2} -y {3} --two-pass {0} -o {1}']
            }

    localDir = os.getcwd()
    errors = []

    def __init__(self, arguments, output_dir, width, height, disable_mp4, disable_ogv, videobr, audiobr):

        assert len(arguments) > 0, 'no files to process'

        self.filelist = self.create_file_list(arguments)
        self.target_dir = output_dir
        self.width = width
        self.height = height
        self.disable_mp4 = disable_mp4
        self.disable_ogv = disable_ogv
        self.videobr = videobr
        self.audiobr = audiobr

        self.outputdir = os.path.join(self.localDir, self.target_dir)

        if not os.path.exists(self.outputdir):
            os.mkdir(self.outputdir)

        if self.disable_ogv:
            del self.encodings['ogv']

        if self.disable_mp4:
            del self.encodings['mp4']

        if len(self.encodings) == 0:
            sys.exit("Exiting. Nothing to do.")

    def create_file_list(self, arguments):
        _all_files = []

        for arg in arguments:
            # if '*' in arg or '?' in arg:
            # 	#o argumento ten unha wildcard
            # 	_all_files.extend(glob(arg))
            # elif os.path.isdir(arg):
            # 	#o argumento é un directorio
            # 	_all_files.extend(glob(os.path.join(arg,'*')))
            if os.path.isfile(arg):
                #parece que é un ficheiro
                _all_files.append(arg)
            else:
                print '%s is not a valid file to process' % arg

        if len(_all_files) > 0:
            return _all_files
        else:
            sys.exit("No files to process")

    def process(self):
        for video in self.filelist:
            video_output = os.path.splitext(os.path.basename(video))[0]

            for finalformat, command in self.encodings.items():
                final_file = self.outputdir + os.sep + video_output + '.' + finalformat
                for cmd in command:
                    subp = cmd.format(video, final_file, self.width, self.height, self.videobr, self.audiobr)

                    print subp

                    import shlex
                    import subprocess as sub

                    pcommand = shlex.split(subp)

                    proc = sub.Popen(pcommand, stdout=sub.PIPE, stderr=sub.PIPE)
                    out, err = proc.communicate()

                    print err

        if len(self.errors) == 0:
            print "\n\nEverything went fine :)"
        else:
            print "You should check this:\n"
            for error in self.errors:
                print error+'\n'

    def __repr__(self):
        return """

    This video(s) will be processed: {0}
    The output video(s) will be this size: {1}x{2}
    Video bitrate will be: {3}kbps
    Audio bitrate will be: {4}kbps
    You'll find the compressed videos here: {5}

        """.format(str(self.filelist), self.width, self.height, self.videobr, self.audiobr, self.outputdir)

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description="Example usage: to_web.py --videos video1.avi video2.avi --width 960 --height 540 --output-dir upload")

    parser.add_argument('--videos', action='store', dest='videos', default=[], required = True,
                        help='Video to process. You can add multiple.', nargs='+'
                        )

    parser.add_argument('--output-dir', action='store', dest='output_dir', default='videos_to_web',
                        help='Output directory. Path. Default: videos_to_web')

    parser.add_argument('--width', action='store', dest='width', default=1280,
            help='Output video width. Number. Default: 1280', type=int)

    parser.add_argument('--height', action='store', dest='height', default=720,
            help='Output video height. Number. Default: 720', type=int)

    parser.add_argument('--video-bitrate', action='store', dest='videobr', default=1500,
            help='Output video bitrate. Number. Default: 1500', type=int)

    parser.add_argument('--audio-bitrate', action='store', dest='audiobr', default=128,
            help='Output audio bitrate. Number. Default: 128', type=int)

    parser.add_argument('--disable-mp4', action='store_true', default=False,
            dest='disable_mp4',
            help='Do not generate the mp4 file.')

    parser.add_argument('--disable-ogv', action='store_true', default=False,
            dest='disable_ogv',
            help='Do not generate the ogv file')

    parser.add_argument('--version', action='version', version='%(prog)s 0.1 by @bertez')

    results = parser.parse_args()

    #sys.exit(results)

    my_batch = BatchProcess(results.videos, results.output_dir, results.width, results.height, results.disable_mp4, results.disable_ogv, results.videobr, results.audiobr)

    print 'Batch process info: ', my_batch

    if raw_input("Does this looks ok to you? [Y/N]: ") == "Y":
        my_batch.process()
    else:
        sys.exit('Exiting...')
