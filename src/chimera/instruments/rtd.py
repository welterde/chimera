import pyrtd

import numpy

import atexit



class RTDException(Exception):
    def __init__(self, msg='unknown'):
        pass

class RTD(object):

    def __init__(self, cam_name, width, height, datasize=16, num_bufs=3):
        self.evt_hndl = pyrtd.rtdIMAGE_EVT_HNDL()
        self.img_info = pyrtd.rtdIMAGE_INFO()
        self.shm = pyrtd.rtdShm()

        self.img_info.dataType = datasize
        self.img_info.xPixels = width
        self.img_info.yPixels = height
        self.img_info.frameX = 0
        self.img_info.frameY = 0

        self.buffer = pyrtd.new_imgdat(width*height)

        if pyrtd.rtdInitImageEvt(cam_name, self.evt_hndl, None) == RTD_ERROR:
            raise RTDException('Got error')

        if rtdShmCreate(num_bufs, self.shm, width, height, datasize) == -1:
            raise RTDException('Got error')

        atexit.register(self.__del__)

    def __del__(self):
        pyrtd.rtdShmDelete(self.shm)
        pyrtd.delete_imgdat(self.buffer)

    def get_buffer(self, offset):
        return pyrtd.ptr_add_int(self.buffer, offset*2)

    def get_data(self, width, height):
        return numpy.fromstring(pyrtd.cdata(self.buffer, width*height*2), dtype=numpy.uint16).reshape((height, width))
    
    def fill_next(self):
        i = pyrtd.rtdShmFillFirst(self.buffer, self.shm)
        pyrtd.rtdShmStruct(i, self.img_info, self.shm)
        pyrtd.rtdSendImageInfo(self.evt_hndl, self.img_info, None)
