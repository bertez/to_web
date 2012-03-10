#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import shlex
import subprocess as sub

class BatchProcess(object):
    """This class processes a list of videos to video formats usable by modern browsers (mp4 and ogv)"""

    __author__ = 'Berto Yáñez'
    __version__ = '0.1'

    encodings = {
            'mp4' : ['ffmpeg -y -i {0} -pass 1 -vcodec libx264 -vpre fast_firstpass -b {3}k -bt {4}k -threads 4 {2}-f rawvideo -an -y /dev/null','ffmpeg -y -i {0} -pass 2 -acodec libfaac -ab {4}k -ac 2 -vcodec libx264 -vpre slow -b {3}k -bt {3}k -threads 4 {2}{1}'],
            'ogv' : ['ffmpeg2theora -V {3} -A {4} {2}--two-pass {0} -o {1}']
            }

    wh_patterns = {
            'mp4' : '-s {0}x{1} ',
            'ogv' : '-x {0} -y {1} '
            }

    localDir = os.getcwd()
    errors = {}
    logs = {}

    def __init__(self, arguments, output_dir, width, height, disable_mp4, disable_ogv, videobr, audiobr):

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
            if os.path.isfile(arg):
                _all_files.append(arg)
            else:
                print '%s is not a valid file to process' % arg

        if len(_all_files) > 0:
            return _all_files
        else:
            sys.exit("No files to process")

    def process(self):
        for video in self.filelist:
            self.errors[video] =  []
            self.logs[video] = []

            video_output = os.path.splitext(os.path.basename(video))[0]
            print 'Processing', video
            print '---'*10

            self.logs[video].append('Starting process of %s' % video)

            for finalformat, command in self.encodings.items():
                print 'Creating %s file' % finalformat

                final_file = self.outputdir + os.sep + video_output + '.' + finalformat
                for cmd in command:

                    wh_string = "" if self.width is None or self.height is None else self.wh_patterns[finalformat].format(self.width, self.height)
                    subp = cmd.format(video, final_file, wh_string , self.videobr, self.audiobr)

                    self.logs[video].append(subp)

                    try:
                        pipe = sub.Popen(shlex.split(subp), stderr=sub.PIPE, stdin=None)
                    except OSError:
                        self.errors[video].append('System error. Check dependencies.')
                    except ValueError:
                        self.errors[video].append('FFmpeg error. Sorry')

                    while True:
                        line = pipe.stderr.readline()
                        if line != '':
                            self.logs[video].append(pipe.stderr.readline())
                        else:
                            break
                    print self.logs[video]

        if len(self.errors[video]) == 0:
            print "\n\nEverything went fine :)"
        else:
            print "There were errors:\n"
            for error in self.errors[video]:
                print error+'\n'

    def __repr__(self):
        resize_info = 'The videos will not be resized' if self.width is None or self.height is None else 'The output video(s) will be this size: {0}x{1}'.format(self.width, self.height)

        batch_info = """

    This video(s) will be processed: {0}
    {1}
    Video bitrate will be: {2}kbps
    Audio bitrate will be: {3}kbps
    You'll find the compressed videos here: {4}

        """.format(str(self.filelist), resize_info, self.videobr, self.audiobr, self.outputdir)

        return batch_info


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description="Example usage: to_web.py --videos video1.avi video2.avi --width 960 --height 540 --output-dir upload")

    group = parser.add_argument_group('resize')

    parser.add_argument('--videos', action='store', dest='videos', default=[], required = True,
                        help='Video to process. You can add multiple.', nargs='+'
                        )

    parser.add_argument('--output-dir', action='store', dest='output_dir', default='videos_to_web',
                        help='Output directory. Path. Default: videos_to_web')

    group.add_argument('--width', action='store', dest='width', default=None,
            help='Output video width. Number.', type=int)

    group.add_argument('--height', action='store', dest='height', default=None,
            help='Output video height. Number.', type=int)

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
