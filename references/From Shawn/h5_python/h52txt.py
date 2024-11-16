import numpy
import os, sys
import h5py

def export2txt(h5_name, outdir):
    with h5py.File(h5_name, 'r') as h5_file:
        for group in h5_file.keys():
            for ds_name in h5_file[group].keys():
                if ds_name in ["subarea", "weight_p", "weight_w", "weight_t", "weight_pet",
                               "rb_fen_gww_drainage", "rb_fen_gww_parts", "tile_drain",
                               "wascob_parts", "wascob_drainage"]:
                    try:
                        ds_data = h5_file[group][ds_name]
                        np_array = numpy.array(ds_data, dtype='f')
                        numpy.savetxt(os.path.join(outdir, ds_name+".txt"), np_array, fmt='%f')
                    except:
                        continue

export2txt(sys.argv[1], sys.argv[2])
