import h5py

class HDF5Util:
    OBJ_TYPE_RASTER = 1
    OBJ_TYPE_WEIGHT = 2
    OBJ_TYPE_IUH = 3
    OBJ_TYPE_REACH = 4

    GROUP_NAME_RASTER = "asc"
    GROUP_NAME_WEIGHT = "weight"
    GROUP_NAME_IUH = "iuh"
    GROUP_NAME_REACH = "reach"
    MASK_NAME_1 = "mask1"
    MASK_NAME_2 = "mask2"
    RASTER_EXTENSION = ".dep"
    TIFF_EXTENSION = ".tif"

    @staticmethod
    def getRASTER_EXTENTION(isTif):
        return HDF5Util.TIFF_EXTENSION if isTif else HDF5Util.RASTER_EXTENSION

    MASK_FILE_NAME = "mask"
    HDF_NAME = "parameter.h5"
    FLOW_ACC_NAME = "flow_acc"
    FLOW_DIRECTION_NAME = "flow_dir"
    FLOW_PATH_NAME = "flow_path"
    FLOW_ORDER_NAME = "flow_order"
    ATTRIBUTE_MIN_NAME = "MIN"
    ATTRIBUTE_MAX_NAME = "MAX"
    ATTRIBUTE_CELL_SIZE_NAME = "CELL_SIZE"

    HEADER_NAME_COL = "NCOLS"
    HEADER_NAME_ROW = "NROWS"
    HEADER_NAME_X = "XLLCENTER"
    HEADER_NAME_Y = "YLLCENTER"
    HEADER_NAME_DX = "DX"
    HEADER_NAME_DY = "DY"
    HEADER_NAME_NODATA = "NODATA_VALUE"

    @staticmethod
    def createH5File(h5path):
        h5file = h5py.File(h5path, 'w')
        return h5file

    @staticmethod
    def openH5File(h5path):
        h5file = h5py.File(h5path, 'r')
        return h5file

    @staticmethod
    def writeH5File(h5path):
        h5file = h5py.File(h5path, 'w')
        return h5file

    @staticmethod
    def readH5File(h5path):
        h5file = h5py.File(h5path, 'r')
        return h5file

    @staticmethod
    def isGroupExist(h5path, groupName):
        h5file = HDF5Util.writeH5File(h5path)
        out = groupName in h5file
        h5file.close()
        return out

    @staticmethod
    def openGroup(h5file, groupName):
        out = None
        try:
            out = h5file[groupName]
        except KeyError:
            pass
        return out

    @staticmethod
    def objType2Name(objType):
        if objType == HDF5Util.OBJ_TYPE_RASTER:
            return HDF5Util.GROUP_NAME_RASTER
        if objType == HDF5Util.OBJ_TYPE_WEIGHT:
            return HDF5Util.GROUP_NAME_WEIGHT
        raise ValueError("Wrong Type!")

    @staticmethod
    def createGroup(h5path, groupName):
        h5file = HDF5Util.openH5File(h5path)
        if not HDF5Util.isGroupExist(h5path, groupName):
            h5file.create_group(groupName)
        h5file.close()

    @staticmethod
    def getDataset(h5file, objName, objType):
        groupName = HDF5Util.objType2Name(objType)
        if groupName in h5file:
            group = h5file[groupName]
            if objName in group:
                return group[objName]
        return None

    @staticmethod
    def getAttribute(hobject, attrName):
        if isinstance(hobject, h5py.Dataset) or isinstance(hobject, h5py.Group):
            if attrName in hobject.attrs:
                return hobject.attrs[attrName]
        else:
            raise ValueError("HObject type error! Must be Group or Dataset to get attribute!")

    @staticmethod
    def isAttributeExist(hobject, attrName):
        return HDF5Util.getAttribute(hobject, attrName) is not None

    @staticmethod
    def isRasterExist(h5path, rasterName):
        h5file = HDF5Util.readH5File(h5path)
        out = HDF5Util.getDataset(h5file, rasterName, HDF5Util.OBJ_TYPE_RASTER) is not None
        h5file.close()
        return out

    @staticmethod
    def isWeightExist(h5path, weightName, objType):
        h5file = HDF5Util.readH5File(h5path)
        out = HDF5Util.getDataset(h5file, weightName, objType) is not None
        h5file.close()
        return out


