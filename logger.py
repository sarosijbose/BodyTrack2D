import sys
import os

class Logging:
 
    def __init__(self, args, filename):

        file_dir = './log/' + args.log_file + '/'
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        self.console = sys.stdout
        self.file = open(filename, 'w+')
 
    def write(self, message):
        self.console.write(message)
        self.file.write(message)
 
    def flush(self):
        self.console.flush()
        self.file.flush()