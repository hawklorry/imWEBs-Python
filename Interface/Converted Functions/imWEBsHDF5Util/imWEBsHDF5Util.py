import os
import sys
from whitebox import WhiteboxRaster

class IMWEBsHDF5Util:
    def __init__(self):
        self.h5wutil = None
        self.versionNumber = "1.0.0"
        self.programName = "IMWEBsHDF5Util.jar"
        self.commands = {
            "save-mask-to-h5": {
                "name": "save-mask-to-h5",
                "options": "Arg1: mask raster path (.dep); Arg2: Output HDF5 file path",
                "description": "Save mask raster file to the 'asc' group in HDF file."
            },
            "generate-h5": {
                "name": "generate-h5",
                "options": "Arg1: Input directory of both raster and weight files; Arg2: Output HDF5 file path",
                "description": "Generate HDF5 file using all raster and weight files in the designate input directory."
            },
            "save-raster-to-h5": {
                "name": "save-raster-to-h5",
                "options": "Arg1: input raster path (.dep); Arg2: HDF5 file path",
                "description": "Save raster file to the 'asc' group in HDF file."
            },
            "save-raster-to-h5-and-rename": {
                "name": "save-raster-to-h5-and-rename",
                "options": "Arg1: input raster path (.dep); Arg2: destination table name saved in HDF file; Arg3: HDF5 file path",
                "description": "Save raster file to the 'asc' group in HDF file and rename the destination table."
            },
            "save-weight-to-h5": {
                "name": "save-weight-to-h5",
                "options": "Arg1: weight file path; Arg2: HDF5 file path",
                "description": "Save mask raster file to the 'asc' group in HDF file"
            }
        }

    def getH5WritingUtil(self):
        if self.h5wutil is None:
            self.h5wutil = HDF5WritingUtil()
        return self.h5wutil

    def GenerateH5(self, inputDir, h5path):
        dir = os.path.join(inputDir)

        # get all rasters files (*.dep) in input directory
        rasterFileArray = [f for f in os.listdir(dir) if f.lower().endswith('.dep')]

        # get all weight files (*.txt) in the input directory
        weightFileArray = [f for f in os.listdir(dir) if f.lower().endswith('.txt')]

        # check if mask file exists
        maskFile = os.path.join(inputDir, MASK_FILE_NAME + RASTER_EXTENSION)
        if rasterFileArray and not os.path.exists(maskFile):
            raise IMWEBsException(f"Mask file (mask.dep) not found in directory: {inputDir}")

        # write all raster and weight files to H5
        self.getH5WritingUtil().addAllParameters(maskFile, rasterFileArray, weightFileArray, h5path)

    def saveMaskToH5(self, maskPath, h5path):
        self.getH5WritingUtil().addRaster(h5path, GROUP_NAME_RASTER, maskPath, True)

    def saveMaskToH5(self, mask, h5path):
        self.getH5WritingUtil().addRaster(h5path, GROUP_NAME_RASTER, mask, True)

    def saveRasterToH5(self, rasterPath, h5path):
        self.getH5WritingUtil().addRaster(h5path, GROUP_NAME_RASTER, rasterPath, False)

    def saveRasterToH5(self, raster, h5path):
        self.getH5WritingUtil().addRaster(h5path, GROUP_NAME_RASTER, raster, False)

    def saveRasterToH5AndRename(self, rasterPath, rasterName, h5path):
        self.getH5WritingUtil().addRaster(h5path, GROUP_NAME_RASTER, rasterPath, rasterName, False)

    def saveRasterToH5AndRename(self, raster, rasterName, h5path):
        self.getH5WritingUtil().addRaster(h5path, GROUP_NAME_RASTER, raster, rasterName, False)

    def saveWeightToH5(self, weightPath, h5path):
        self.getH5WritingUtil().addWeight(h5path, GROUP_NAME_WEIGHT, weightPath, OBJ_TYPE_WEIGHT)

    def verifyRasterUsingMask(self, maskPath, rasterPath):
        mask = WhiteboxRaster(maskPath, "r")
        ras = WhiteboxRaster(rasterPath, "r")

        try:
            HDF5Mask(mask).verifyRaster(ras)
            return True
        except IMWEBsException as e:
            print(e)
            return False

    def main(self, args):
        if len(args) == 0 or args[0].lower().contains("help"):
            sb = []
            sb.append(f"{self.versionNumber}\n\n")
            sb.append(f"Usage: {self.programName} [command] [arguments]\n\n")
            sb.append("Commands:\n")
            for c in self.commands.values():
                sb.append(f" {c['name']} [{c['options']}]\t{c['description']}\n")
            print(''.join(sb))
        elif args[0] in self.commands:
            try:
                if args[0].lower() == "save-mask-to-h5":
                    self.saveMaskToH5(args[1], args[2])
                elif args[0].lower() == "generate-h5":
                    self.GenerateH5(args[1], args[2])
                elif args[0].lower() == "save-raster-to-h5":
                    self.saveRasterToH5(args[1], args[2])
                elif args[0].lower() == "save-raster-to-h5-and-rename":
                    self.saveRasterToH5AndRename(args[1], args[2], args[3])
                elif args[0].lower() == "save-weight-to-h5":
                    self.saveWeightToH5(args[1], args[2])
                elif args[0].lower() == "verify-raster-using-mask":
                    self.verifyRasterUsingMask(args[1], args[2])

                sb = []
                sb.append(f"{self.programName} {self.versionNumber}\n\n")
                sb.append(f"Finish running command \"{args[0]}\" SUCCESSFULLY!\n\n")
                print(''.join(sb))
            except Exception as e:
                raise IMWEBsException(
                    f"Running command \"{args[0]}\" FAILED!\n"
                    f"{e}\nPlease check input arguments as the following command description\n"
                    f"{self.commands[args[0]]['name']} [{self.commands[args[0]]['options']}]\t{self.commands[args[0]]['description']}"
                )
        else:
            sb = []
            sb.append(f"{self.programName} {self.versionNumber}\n\n")
            sb.append(f"Error: command not found for \"{args[0]}\"\n\n")
            sb.append("Supporting commands:\n")
            for c in self.commands.values():
                sb.append(f" {c['name']} [{c['options']}]\t{c['description']}\n")
            print(''.join(sb))

if __name__ == "__main__":
    util = IMWEBsHDF5Util()
    util.main(sys.argv[1:])


