import os, sys, subprocess

class start(object):
    def __init__(self, ascii_file, h5_file):
        self.ascii_file = ascii_file
        self.dep = self.ascii_file.replace(".TXT", ".dep")
        self.h5_file = h5_file

        self.cwd = os.getcwd()
        self.SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

        os.chdir(self.SCRIPT_DIR)
        self.run()
        os.chdir(self.cwd)
    
    def run(self):
        cmd = ['java',
               '-jar',
               'IMWEBsHDF5Util.jar',
               'save-raster-to-h5',
               '"'+self.dep+'"',
               '"'+self.h5_file+'"']
        os.system(" ".join(cmd))