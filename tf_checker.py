"""Checks if a set of TFRecords appear to be valid.
Specifically, this checks whether the provided record sizes are consistent and
that the file does not end in the middle of a record. It does not verify the
CRCs.
"""
import struct
from multiprocessing import Pool
import tensorflow.compat.v1 as tf

from tensorflow.compat.v1 import app
from tensorflow.compat.v1 import flags
from tensorflow.compat.v1 import gfile
from tensorflow.compat.v1 import logging

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string("input_data_pattern", "",
                    "File glob defining for the TFRecords files.")

def check(path):
    with gfile.Open(path, "rb") as f:
      first_read = True
      while True:
        length_raw = f.read(8)
        if not length_raw and first_read:
          logging.fatal("File %s has no data.", path)
          break
        elif not length_raw:
          logging.info("File %s looks good.", path)
          break
        else:
          first_read = False
        if len(length_raw) != 8:
          logging.fatal("File ends when reading record length: " + path)
          break
        length, = struct.unpack("L", length_raw)
        # +8 to include the crc values.
        record = f.read(length + 8)
        if len(record) != length + 8:
          logging.fatal("File ends in the middle of a record: " + path)
          break
    
def main(unused_argv):
  logging.set_verbosity(tf.logging.INFO)
  paths = gfile.Glob(FLAGS.input_data_pattern)
  logging.info("Found %s files.", len(paths))
  
  p = Pool(5)
  print(p.map(check, paths))
    


if __name__ == "__main__":
  app.run()