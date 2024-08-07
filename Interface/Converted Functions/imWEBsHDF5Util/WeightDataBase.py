class IMWEBsException(Exception):
    def __init__(self, class_name, method_name, message):
        super().__init__(f"{class_name}.{method_name}: {message}")

OBJ_TYPE_IUH = 2
OBJ_TYPE_WEIGHT = 3
OBJ_TYPE_REACH = 4

class WeightDataBase:
    def __init__(self):
        self.m_data = None
        self.m_rows = -1
        self.m_cols = -1
        self.m_type = -1
        self.m_weightName = ""

    def reset(self, weightName):
        if self.m_data is not None:
            self.m_data = None
            self.m_rows = -1
            self.m_cols = -1

        # save
        self.m_weightName = weightName

        # get type
        self.m_type = self.getWeightTypeFromName(weightName)

        if self.m_type == -1:
            raise IMWEBsException("WeightDataBase", "reset",
                                  "Wrong weight type! Just can be 2, 3 or 4!")

    def getWeightTypeFromName(self, weightName):
        lowerFileName = weightName.lower()
        if lowerFileName.startswith("iuh"):
            return OBJ_TYPE_IUH
        elif lowerFileName.startswith("weight"):
            return OBJ_TYPE_WEIGHT
        elif lowerFileName == "reachparameter":
            return OBJ_TYPE_REACH
        else:
            return -1

    def getWeightFileName(self):
        return self.m_weightName

    def getType(self):
        return self.m_type

    def getData(self):
        return self.m_data

    def getRows(self):
        return self.m_rows

    def getCols(self):
        return self.m_cols


