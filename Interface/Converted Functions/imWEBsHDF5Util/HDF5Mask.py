import h5py
import numpy as np
import os
from whitebox import WhiteboxRaster

class HDF5Mask:
    def __init__(self, mask):
        self.m_position1d = None
        self.m_position2d = None
        self.m_nRows = None
        self.m_headers = None
        self.initFromWhiteboxRaster(mask)

    def initFromHDF5Mask(self, h5path, grpName):
        util = HDF5Util()
        h5file = util.writeH5File(h5path)
        group = util.openGroup(h5file, grpName)
        attrList = group.attrs.items()
        size = len(attrList)
        self.m_headers = {}
        for attr in attrList:
            self.m_headers[attr[0]] = float(attr[1])
        self.m_nRows = int(self.m_headers[ATTRIBUTE_CELL_SIZE_NAME])
        dataset1 = util.getDataset(h5file, MASK_NAME_1, OBJ_TYPE_RASTER)
        self.m_position1d = np.array(dataset1)
        dataset2 = util.getDataset(h5file, MASK_NAME_2, OBJ_TYPE_RASTER)
        self.m_position2d = np.array(dataset2)
        if self.m_position1d.size / 2 != self.m_nRows:
            raise IMWEBsException("Mask metadata cell size not equal to position data size!")
        h5file.close()

    def initFromWhiteboxRaster(self, mask):
        noData = mask.no_data_value
        rows = mask.number_of_rows
        cols = mask.number_of_columns
        size = rows * cols
        self.m_position2d = np.zeros(size, dtype=int)
        ii = 0
        for row in range(rows):
            for col in range(cols):
                if mask.get_value(row, col) == noData:
                    self.m_position2d[ii] = -1
                else:
                    self.m_position2d[ii] = self.m_nRows
                    self.m_nRows += 1
                ii += 1
        mask.close()
        self.m_position1d = np.zeros(self.m_nRows * 2, dtype=int)
        index = 0
        for i in range(size):
            if self.m_position2d[i] == -1:
                continue
            self.m_position1d[index * 2] = i // cols
            self.m_position1d[index * 2 + 1] = i % cols
            index += 1
        self.m_headers = {}
        self.m_headers[HEADER_NAME_COL] = float(mask.number_of_columns)
        self.m_headers[HEADER_NAME_ROW] = float(mask.number_of_rows)
        self.m_headers[HEADER_NAME_X] = float(mask.west + 0.5 * mask.cell_size_x)
        self.m_headers[HEADER_NAME_Y] = float(mask.north - 0.5 * mask.cell_size_y)
        self.m_headers[HEADER_NAME_DX] = float(mask.cell_size_x)
        self.m_headers[HEADER_NAME_DY] = float(mask.cell_size_y)
        self.m_headers[HEADER_NAME_NODATA] = float(mask.no_data_value)
        self.m_headers[ATTRIBUTE_CELL_SIZE_NAME] = float(self.m_nRows)

    def getPosition1D(self):
        return self.m_position1d

    def getPosition2D(self):
        return self.m_position2d

    def getHeaders(self):
        return self.m_headers

    def getRasterValuesInMask(self, rasterPath):
        raster = WhiteboxRaster(rasterPath, "r")
        self.verifyRaster(raster)
        values = np.zeros(self.m_nRows, dtype=float)
        for i in range(self.m_nRows):
            if raster.get_value(self.getPosition1D()[i * 2], self.getPosition1D()[i * 2 + 1]) != raster.no_data_value:
                values[i] = float(raster.get_value(self.getPosition1D()[i * 2], self.getPosition1D()[i * 2 + 1]))
            else:
                values[i] = self.getHeaders()[HEADER_NAME_NODATA]
        return values

    def verifyRaster(self, raster):
        for key, value in self.m_headers.items():
            if key == HEADER_NAME_COL and value != float(raster.number_of_columns):
                raise IMWEBsException(f"Mask metadata column number {value} not equal to raster {os.path.basename(raster.data_file)} {raster.number_of_columns}!")
            elif key == HEADER_NAME_ROW and value != float(raster.number_of_rows):
                raise IMWEBsException(f"Mask metadata row number {value} not equal to raster {os.path.basename(raster.data_file)} {raster.number_of_rows}!")
            elif key == HEADER_NAME_DX and abs(value - float(raster.cell_size_x)) > 0.1:
                raise IMWEBsException(f"Mask metadata DX {value} not equal to raster {os.path.basename(raster.data_file)} {raster.cell_size_x}!")
            elif key == HEADER_NAME_DY and abs(value - float(raster.cell_size_y)) > 0.1:
                raise IMWEBsException(f"Mask metadata DY {value} not equal to raster {os.path.basename(raster.data_file)} {raster.cell_size_y}!")
            elif key == HEADER_NAME_NODATA and value != float(raster.no_data_value):
                raise IMWEBsException(f"Mask metadata no data value {value} not equal to raster {os.path.basename(raster.data_file)} {raster.no_data_value}!")

    def getCellNumber(self):
        return self.m_nRows


