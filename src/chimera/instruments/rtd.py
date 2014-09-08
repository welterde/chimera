import pyrtd

import numpy

import atexit



class RTDException(Exception):
    def __init__(self, msg='unknown'):
        pass

class RTD(object):

    def __init__(self, cam_name, width, height, datasize=16, num_bufs=1):
        self.evt_hndl = pyrtd.rtdIMAGE_EVT_HNDL()
        self.img_info = pyrtd.rtdIMAGE_INFO()
        self.shm = pyrtd.rtdShm()
        self._exited = False

        self.img_info.dataType = -16
        self.img_info.xPixels = width
        self.img_info.yPixels = height
        self.img_info.frameX = 0
        self.img_info.frameY = 0
        self.shmSize = width*height*2

        #self.buffer = pyrtd.new_imgdat((width+1)*(height+1)*2)
        self.buffer = pyrtd.imgArr((width+1)*(height+1)*2)

        if pyrtd.rtdInitImageEvt(cam_name, self.evt_hndl, None) == pyrtd.RTD_ERROR:
            raise RTDException('Got error')

        if pyrtd.rtdShmCreate(num_bufs, self.shm, width, height, datasize) == -1:
            raise RTDException('Got error')

        #atexit.register(self.__del__)

    def __del__(self):
        if self._exited:
            return
        self._exited = True
        pyrtd.rtdShmDelete(self.shm)
        pyrtd.delete_imgdat(self.buffer)

    #def get_buffer(self, offset):
    #    return pyrtd.ptr_add_int(self.buffer, 0)
    #    #return self.buffer

    def get_data(self, width, height):
        return numpy.fromstring(pyrtd.cdata(pyrtd.voidWrap(self.buffer), width*height*2), dtype=numpy.uint16).reshape((height, width))
    
    def fill_next(self):
        pyrtd.rtdShmFill2(0, self.buffer, self.shm, self.shmSize)
        pyrtd.rtdShmStruct(0, self.img_info, self.shm)
        pyrtd.rtdSendImageInfo(self.evt_hndl, self.img_info, None)
