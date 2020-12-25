import os
from aenum import NamedConstant
class Finger(NamedConstant):
    """
        Define all env variable
    """
    # Define all port register and variable neccessary
    STARTCODE = 0xEF01
    SETSYSTEMPARAMETER_BAUDRATE = 4
    SETSYSTEMPARAMETER_SECURITY_LEVEL = 5
    SETSYSTEMPARAMETER_PACKAGE_SIZE = 6

    COMMANDPACKET = 0x01

    ACKPACKET = 0x07
    DATAPACKET = 0x02
    ENDDATAPACKET = 0x08

    # Instruction codes

    VERIFYPASSWORD = 0x13
    SETPASSWORD = 0x12
    SETADDRESS = 0x15
    SETSYSTEMPARAMETER = 0x0E
    GETSYSTEMPARAMETERS = 0x0F
    TEMPLATEINDEX = 0x1F
    TEMPLATECOUNT = 0x1D




    # Port register
    READIMAGE = 0x01
    # Note: The documentation mean upload to host computer.
    DOWNLOADIMAGE = 0x0A

    CONVERTIMAGE = 0x02

    CREATETEMPLATE = 0x05
    STORETEMPLATE = 0x06
    SEARCHTEMPLATE = 0x04
    LOADTEMPLATE = 0x07
    DELETETEMPLATE = 0x0C

    CLEARDATABASE = 0x0D
    GENERATERANDOMNUMBER = 0x14
    COMPARECHARACTERISTICS = 0x03

    # Note: The documentation mean download from host computer.
    UPLOADCHARACTERISTICS = 0x09

    # Note: The documentation mean upload to host computer.
    DOWNLOADCHARACTERISTICS = 0x08

    # Parameters of setSystemParameter()
    #
    OK = 0x00



    """
        Define some error
    """
    ERROR_COMMUNICATION = 0x01

    ERROR_WRONGPASSWORD = 0x13

    ERROR_INVALIDREGISTER = 0x1A

    ERROR_NOFINGER = 0x02
    ERROR_READIMAGE = 0x03

    ERROR_MESSYIMAGE = 0x06
    ERROR_FEWFEATUREPOINTS = 0x07
    ERROR_INVALIDIMAGE = 0x15

    ERROR_CHARACTERISTICSMISMATCH = 0x0A

    ERROR_INVALIDPOSITION = 0x0B
    ERROR_FLASH = 0x18

    ERROR_NOTEMPLATEFOUND = 0x09

    ERROR_LOADTEMPLATE = 0x0C

    ERROR_DELETETEMPLATE = 0x10

    ERROR_CLEARDATABASE = 0x11

    ERROR_NOTMATCHING = 0x08

    ERROR_DOWNLOADIMAGE = 0x0F
    ERROR_DOWNLOADCHARACTERISTICS = 0x0D

    # Unknown error codes

    ERROR_ADDRCODE = 0x20
    ERROR_PASSVERIFY = 0x21

    ERROR_PACKETRESPONSEFAIL = 0x0E

    ERROR_TIMEOUT = 0xFF
    ERROR_BADPACKET = 0xFE



    """
        Buffer for two register
    """

    # Char buffers

    CHARBUFFER1 = 0x01

    CHARBUFFER2 = 0x02
