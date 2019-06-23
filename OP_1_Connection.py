import json
import os
import time
import usb.util
import usb.core
from PIL import ImageDraw, Image
from psutil import disk_partitions
from GPIO_Init import displayImage, getFont
from config import config, savePaths

__author__ = "Hsuan Han Lai (Edward Lai)"
__date__ = "2019-04-02"

workDir = os.path.dirname(os.path.realpath(__file__))

currentStorageStatus = {
    "sampler": 0,
    "synth": 0,
    "drum": 0
}


# OP-1 connection
# def ensure_connection():
#     if not is_connected():
#         wait_for_connection()


def is_connected():
    if usb.core.find(idVendor=config["USB_VENDOR"], idProduct=config["USB_PRODUCT"]) is not None:
        return True
    else:
        return False


# TODO ADD WHILE
def wait_for_connection():
    if is_connected():
        print("Connected!")
    else:
        print("not connected")
    time.sleep(2)


# mountdevice(config["OP_1_Mounted_Dir"],
# Mounting FAT32 with user 
def mountdevice(source, target):
    print("mount device with !" + source + "! !" + target + "! !" + username() + "!")

    ret = os.system('sudo -E mount {} {}'.format(source, target))
    if ret not in (0, 8192):
        raise RuntimeError("Error mounting {} on {}: {}".format(source, target, ret))
    config["OP_1_Mounted_Dir"] = target


def unmountdevice(target):
    ret = os.system('umount {}'.format(target))
    if ret != 0:
        raise RuntimeError("Error unmounting {}: {}".format(target, ret))
    os.system("sudo rm -R " + config["OP_1_Mounted_Dir"])
    config["OP_1_Mounted_Dir"] = ""
    print("unmount op1 finised")


# get the system mount path - /dev/sda
def getmountpath():
    o = os.popen('readlink -f /dev/disk/by-id/' + config["OP_1_USB_ID"]).read()
    return o.rstrip()


# chekcs if the partiion is mounted if not it return ""
def getMountPath():
    mountpath = getmountpath()
    # mountPoint = ""
    for i, disk in enumerate(disk_partitions()):
        print(disk)
        if disk.device == mountpath:
            mountPoint = disk.mountpoint
            config["OP_1_Mounted_Dir"] = mountPoint
            print(config["OP_1_Mounted_Dir"])
            return mountPoint
    return ""


def is_mounted():
    if getMountPath() == "":
        return False
    else:
        return True


def do_mount():
    wait_for_connection()
    if not is_mounted():
        try:
            print("-- device not mounted")
            mountpath = getmountpath()
            config["USB_Mount_Path"] = mountpath
            create_mount_point()
            mountdevice(config["USB_Mount_Path"], config["TargetOp1MountDir"])
        except:
            return False
        return True
    else:
        print("-- device mounted --")
        return True


def check_OP_1_Connection():
    # if config["USB_Mount_Path"] == "":
    #     image = Image.new('1', (128, 64))
    #     image.paste(Image.open(workDir + "/Assets/Img/ConnectOP_1.png").convert("1"))
    #     displayImage(image)

    connected = Image.new('1', (128, 64))
    draw = ImageDraw.Draw(connected)
    draw.text((0, 25), "Connecting.....", font=getFont(), fill='white')
    displayImage(connected)

    if is_connected():
        do_mount()
        connected = Image.new('1', (128, 64))
        draw = ImageDraw.Draw(connected)
        draw.text((0, 25), "Connected", font=getFont(), fill='white')
        displayImage(connected)

        return True
    else:
        connected = Image.new('1', (128, 64))
        draw = ImageDraw.Draw(connected)
        draw.text((0, 25), "No Connection!", font=getFont(), fill='white')
        displayImage(connected)
        config["USB_Mount_Path"] = ""
        config["OP_1_Mounted_Dir"] = ""
        time.sleep(1)
        return False


def unmount_OP_1():
    if is_mounted():
        unmountDisplay = Image.new('1', (128, 64))
        draw = ImageDraw.Draw(unmountDisplay)
        draw.text((30, 25), "Ejecting!", font=getFont(), fill='white')
        displayImage(unmountDisplay)
        unmountdevice(config["OP_1_Mounted_Dir"])
        config["OP_1_Mounted_Dir"] = ""
        config["USB_Mount_Path"] = ""
        unmountDisplay = Image.new('1', (128, 64))
        draw = ImageDraw.Draw(unmountDisplay)
        draw.text((30, 25), "Ejected!", font=getFont(), fill='white')
        displayImage(unmountDisplay)
        time.sleep()
        return True
    else:
        unmountDisplay = Image.new('1', (128, 64))
        draw = ImageDraw.Draw(unmountDisplay)
        draw.text((15, 25), "No Device to Eject", font=getFont(), fill='white')
        displayImage(unmountDisplay)
        time.sleep(1)
        return False


def create_mount_point():
    try:
        os.system("sudo mkdir -p " + config["TargetOp1MountDir"])
        os.system("sudo chmod 0777 " + config["TargetOp1MountDir"])
    except:
        print("error cant create mount point directory")


def get_abbreviation(text):
    """
    Rename texts to abbreviations in order to fit better to the screen
    """
    if text == "Element":
        return "Elem"
    elif text == "Tremolo":
        return "Tremo"
    elif text == "Random":
        return "Rand"
    elif text == "Sampler":
        return "Sample"
    else:
        return text


def getFileCount(startPath):
    """
    Given path to dir, and return the counts of .aif files and all child directory
    :param startPath: path to folder
    :return: int: total count of aif files
    """
    filesCount = 0
    for root, dirs, files in os.walk(startPath):
        for f in files:
            if f.endswith('.aif') and not f.startswith("."):
                filesCount += 1
    return filesCount


def analyzeAIF(pathTOAIF):
    """
    path to the op1 AIF file extracting json format from the meta data and analyze patch type
    :param pathTOAIF: path to OP1 aif file
    :return: tuple of three strings (type, fx,lfo)
    """
    with open(pathTOAIF, 'rb') as reader:
        file = str(reader.read())
    strBuilder = ""
    startflag = False
    for i in file:
        if i == "}":
            strBuilder += "}"
            break
        if startflag:
            strBuilder += str(i)
        if not startflag and i == "{":
            strBuilder += str(i)
            startflag = True
    data = json.loads(strBuilder)
    return data.get("type").capitalize(), data.get("fx_type").capitalize(), data.get("lfo_type").capitalize()


# def checkOccupiedSlots(startPath):
#     patchType = ""
#     sampleEngine = []
#     synthEngine = []
#     drum = []
#     for root, dirs, files in os.walk(startPath):
#         for f in files:
#             currentFilePath = str(root) + "/" + f
#             if f.endswith('.aif') and not f.startswith("."):
#                 try:
#                     patchType, fx, lfo = analyzeAIF(currentFilePath)
#                 except:
#                     pass
#             if patchType == "Drum" or patchType == "Dbox" and "drum" in currentFilePath:
#                 drum.append(currentFilePath)
#             elif patchType == "Sampler":
#                 sampleEngine.append(currentFilePath)
#             else:
#                 synthEngine.append(currentFilePath)
#     return [sampleEngine, synthEngine, drum]


def update_Current_Storage_Status():
    currentStorageStatus["sampler"] = getFileCount(config["OP_1_Mounted_Dir"] + "/synth")
    currentStorageStatus["synth"] = getFileCount(config["OP_1_Mounted_Dir"] + "/drum")
    currentStorageStatus["drum"] = getFileCount(config["OP_1_Mounted_Dir"] + "/drum")
    return currentStorageStatus["sampler"], currentStorageStatus["synth"], currentStorageStatus["drum"]
