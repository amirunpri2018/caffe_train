#!/usr/bin/python
# -*- coding:UTF-8 -*-
from __future__ import division
import os, cv2, sys, shutil
import numpy as np
from xml.dom.minidom import Document

rootdir = "../../../dataset/facedata"
convet2yoloformat = False
convert2vocformat = True

# 最小取20大小的脸，并且补齐
minsize2select = 10
cropsize2select = 60
usepadding = True

datasetprefix = "../../../dataset/facedata/wider_face"  #
use_blur_occlu_attri = False #True #

classflyFile = "./wider_face_classfly_distance_data.txt"


def convertimgset(img_set="train"):
    imgdir = rootdir + '/wider_face/' + "JPEGImages/wider_" + img_set + "/images"
    gtfilepath = rootdir + "/wider_face_split/wider_face_" + img_set + "_bbx_gt.txt"
    imagesdir = rootdir + '/wider_face/' + "annoImg"
    vocannotationdir = rootdir + '/wider_face/' + "Annotations"
    labelsdir = rootdir + '/wider_face/' + "label"
    cropImgsDir = rootdir + '/wider_face/' + "CropImg"
    croplabelsdir = rootdir + '/wider_face/' + "Croplabel"
    if not os.path.exists(imagesdir):
        os.mkdir(imagesdir)
    if not os.path.exists(labelsdir):
        os.mkdir(labelsdir)
    if not os.path.exists(rootdir + '/wider_face/' + "/ImageSets"):
        os.mkdir(rootdir + '/wider_face/' + "/ImageSets")
    if not os.path.exists(rootdir + '/wider_face/' + "/ImageSets/Main"):
        os.mkdir(rootdir + '/wider_face/' + "/ImageSets/Main")
    if use_blur_occlu_attri:
        if not os.path.exists(croplabelsdir):
            os.mkdir(croplabelsdir)
        if not os.path.exists(cropImgsDir):
            os.mkdir(cropImgsDir)

    if convert2vocformat:
        if not os.path.exists(vocannotationdir):
            os.mkdir(vocannotationdir)
    index = 0

    f_set = open(rootdir + '/wider_face/' + "/ImageSets/Main/" + img_set + ".txt", 'w')
    if use_blur_occlu_attri:
        f_set_crop = open(rootdir + '/wider_face/' + "/ImageSets/Main/crop_" + img_set + ".txt", 'w')
    classfly_file = open(classflyFile, 'a+')
    
    with open(gtfilepath, 'r') as gtfile:
        while (True):  # and len(faces)<10
            filename = gtfile.readline()[:-1]
            if (filename == ""):
                break;
            sys.stdout.write("\r" + str(index) + ":" + filename + "\n")
            sys.stdout.flush()
            imgpath = imgdir + "/" + filename
            img = cv2.imread(imgpath)
            img_width = img.shape[1]
            img_height = img.shape[0]
            if not img.data:
                break;

            saveimg = img.copy()
            showimg = saveimg.copy()
            numbbox = int(gtfile.readline())
            bboxes = []
            blurs = []
            occlus = []
            for i in range(numbbox):
                line = gtfile.readline()
                line = line.split(' ')
                if (int(line[3]) <= 0 or int(line[2]) <= 0 or int(line[7]) == 1):
                    continue
                x = int(line[0])
                y = int(line[1])
                width = int(line[2])
                height = int(line[3])
                blur = int(line[4])
                occlu = int(line[8])
                bbox = (x, y, width, height)
                x2 = x + width
                y2 = y + height
                # face=img[x:x2,y:y2]
                if width >= minsize2select and height >= minsize2select:
                    bboxes.append(bbox)
                    occlus.append(occlu)
                    blurs.append(blur)
                    LableFileName = labelsdir + '/' + filename.replace("/", "_").split('.jpg')[0]
                    content = str(x) + ' ' + str(y) + ' ' + str(width) + ' ' + str(height) + ' ' + str(blur) + ' ' + str(occlu) +'\n'
                    label_file = open(LableFileName, 'a+')
                    label_file.writelines(content)
                    label_file.close()
                    if use_blur_occlu_attri and width >= cropsize2select and height >= cropsize2select:
                        cropImgFileName = cropImgsDir + '/' + filename.replace("/", "_").split('.jpg')[0] + '_crop_' + str(i) + '.jpg'
                        cropLableFileName = croplabelsdir + '/' + filename.replace("/", "_").split('.jpg')[0] + '_crop_' + str(i)
                        x11 = np.maximum(x - 0/2, 0)
                        y11 = np.maximum(y - 0/2, 0)
                        x22 = np.minimum(x2 + 0/2, img.shape[1])
                        y22 = np.minimum(y2 + 0/2, img.shape[0])
                        cropImg = img[int(y11):int(y22),int(x11):int(x22),:]
                        cv2.imwrite(cropImgFileName, cropImg)
                        croplabel_file = open(cropLableFileName, 'w')
                        txtline = str(blur) + ' ' + str(occlu) + '\n'
                        croplabel_file.write(txtline)
                        croplabel_file.close()
                        f_set_crop.write(os.path.abspath(cropImgFileName).split('.jpg')[0] + '\n')
                    cv2.rectangle(showimg, (x, y), (x2, y2), (0, 255, 0))
                else:
                    saveimg[y:y2, x:x2, :] = (104,117,123)
                    cv2.rectangle(showimg, (x, y), (x2, y2), (0, 0, 255))
            filename = filename.replace("/", "_")
            if len(bboxes) == 0:
                print
                "warrning: no face"
                continue
            cv2.imwrite(imagesdir + "/" + filename, saveimg)
            # generate filelist
            imgfilepath = filename[:-4]
            f_set.write(os.path.abspath(imagesdir + "/" + filename).split('.jpg')[0] + '\n')
            if convet2yoloformat:
                height = saveimg.shape[0]
                width = saveimg.shape[1]
                txtpath = labelsdir + "/" + filename
                txtpath = txtpath[:-3] + "txt"
                ftxt = open(txtpath, 'w')
                for i in range(len(bboxes)):
                    bbox = bboxes[i]
                    xcenter = (bbox[0] + bbox[2] * 0.5) / width
                    ycenter = (bbox[1] + bbox[3] * 0.5) / height
                    wr = bbox[2] * 1.0 / width
                    hr = bbox[3] * 1.0 / height
                    txtline = "0 " + str(xcenter) + " " + str(ycenter) + " " + str(wr) + " " + str(hr) + "\n"
                    ftxt.write(txtline)
                ftxt.close()
            if convert2vocformat:
                xmlpath = vocannotationdir + "/" + filename
                xmlpath = xmlpath[:-3] + "xml"
                doc = Document()
                annotation = doc.createElement('annotation')
                doc.appendChild(annotation)
                folder = doc.createElement('folder')
                folder_name = doc.createTextNode('widerface')
                folder.appendChild(folder_name)
                annotation.appendChild(folder)
                filenamenode = doc.createElement('filename')
                filename_name = doc.createTextNode(filename)
                filenamenode.appendChild(filename_name)
                annotation.appendChild(filenamenode)
                source = doc.createElement('source')
                annotation.appendChild(source)
                database = doc.createElement('database')
                database.appendChild(doc.createTextNode('wider face Database'))
                source.appendChild(database)
                annotation_s = doc.createElement('annotation')
                annotation_s.appendChild(doc.createTextNode('PASCAL VOC2007'))
                source.appendChild(annotation_s)
                image = doc.createElement('image')
                image.appendChild(doc.createTextNode('flickr'))
                source.appendChild(image)
                flickrid = doc.createElement('flickrid')
                flickrid.appendChild(doc.createTextNode('-1'))
                source.appendChild(flickrid)
                owner = doc.createElement('owner')
                annotation.appendChild(owner)
                flickrid_o = doc.createElement('flickrid')
                flickrid_o.appendChild(doc.createTextNode('yanyu'))
                owner.appendChild(flickrid_o)
                name_o = doc.createElement('name')
                name_o.appendChild(doc.createTextNode('yanyu'))
                owner.appendChild(name_o)
                size = doc.createElement('size')
                annotation.appendChild(size)
                width = doc.createElement('width')
                width.appendChild(doc.createTextNode(str(saveimg.shape[1])))
                height = doc.createElement('height')
                height.appendChild(doc.createTextNode(str(saveimg.shape[0])))
                depth = doc.createElement('depth')
                depth.appendChild(doc.createTextNode(str(saveimg.shape[2])))
                size.appendChild(width)
                size.appendChild(height)
                size.appendChild(depth)
                segmented = doc.createElement('segmented')
                segmented.appendChild(doc.createTextNode('0'))
                annotation.appendChild(segmented)
                for i in range(len(bboxes)):
                    bbox = bboxes[i]
                    blur = blurs[i]
                    occlu = occlus[i]
                    objects = doc.createElement('object')
                    annotation.appendChild(objects)
                    object_name = doc.createElement('name')
                    object_name.appendChild(doc.createTextNode('face'))
                    objects.appendChild(object_name)
                    pose = doc.createElement('pose')
                    pose.appendChild(doc.createTextNode('Unspecified'))
                    objects.appendChild(pose)
                    truncated = doc.createElement('truncated')
                    truncated.appendChild(doc.createTextNode('1'))
                    objects.appendChild(truncated)
                    if use_blur_occlu_attri:
                        blur_node = doc.createElement('blur')
                        blur_node.appendChild(doc.createTextNode(str(blur)))
                        objects.appendChild(blur_node)
                        occlusion_node = doc.createElement('occlusion')
                        occlusion_node.appendChild(doc.createTextNode(str(occlu)))
                        objects.appendChild(occlusion_node)
                    difficult = doc.createElement('difficult')
                    difficult.appendChild(doc.createTextNode('0'))
                    objects.appendChild(difficult)
                    bndbox = doc.createElement('bndbox')
                    objects.appendChild(bndbox)
                    xmin = doc.createElement('xmin')
                    xmin.appendChild(doc.createTextNode(str(bbox[0])))
                    bndbox.appendChild(xmin)
                    ymin = doc.createElement('ymin')
                    ymin.appendChild(doc.createTextNode(str(bbox[1])))
                    bndbox.appendChild(ymin)
                    xmax = doc.createElement('xmax')
                    xmax.appendChild(doc.createTextNode(str(bbox[0] + bbox[2])))
                    bndbox.appendChild(xmax)
                    ymax = doc.createElement('ymax')
                    ymax.appendChild(doc.createTextNode(str(bbox[1] + bbox[3])))
                    bndbox.appendChild(ymax)
                    if img_set == "train":
                        ################### cluster BBox ############################
                        ## get relative x, y , w, h corresponind width, height#######
                        ################### cluster BBox ############################
                        class_bdx_center_x = float((int(bbox[0])+int(bbox[0])+int(bbox[2]))/(2*int(img_width)))
                        class_bdx_center_y = float((int(bbox[1])+int(bbox[1])+int(bbox[3]))/(2*int(img_height)))
                        class_bdx_w = float(int(bbox[2])/int(img_width))
                        class_bdx_h = float(int(bbox[3])/int(img_height))
                        classfly_content = str(class_bdx_center_x) + ' ' + str(class_bdx_center_y) + ' ' + str(class_bdx_w)+ ' '+str(class_bdx_h)+'\n'
                        classfly_file.writelines(classfly_content)
                        ###################### end cluster BBox ####################
                f = open(xmlpath, "w")
                f.write(doc.toprettyxml(indent=''))
                f.close()
                # cv2.imshow("img",showimg)
            # cv2.waitKey()
            index = index + 1
    classfly_file.close()
    f_set.close()

def generatetxt(img_set="train"):
    gtfilepath = rootdir + "/wider_face_split/wider_face_" + img_set + "_bbx_gt.txt"
    f = open(rootdir + "/" + img_set + ".txt", "w")
    with open(gtfilepath, 'r') as gtfile:
        while (True):  # and len(faces)<10
            filename = gtfile.readline()[:-1]
            if (filename == ""):
                break;
            filename = filename.replace("/", "_")
            imgfilepath = datasetprefix + "/images/" + filename
            f.write(imgfilepath + '\n')
            numbbox = int(gtfile.readline())
            for i in range(numbbox):
                line = gtfile.readline()
    f.close()


def generatevocsets(img_set="train"):
    if not os.path.exists(rootdir + "/ImageSets"):
        os.mkdir(rootdir + "/ImageSets")
    if not os.path.exists(rootdir + "/ImageSets/Main"):
        os.mkdir(rootdir + "/ImageSets/Main")
    gtfilepath = rootdir + "/wider_face_split/wider_face_" + img_set + "_bbx_gt.txt"
    f = open(rootdir + "/ImageSets/Main/" + img_set + ".txt", 'w')
    with open(gtfilepath, 'r') as gtfile:
        while (True):  # and len(faces)<10
            filename = gtfile.readline()[:-1]
            if (filename == ""):
                break;
            filename = filename.replace("/", "_")
            imgfilepath = filename[:-4]
            f.write(imgfilepath + '\n')
            numbbox = int(gtfile.readline())
            for i in range(numbbox):
                line = gtfile.readline()
    f.close()


def convertdataset():
    classfy_ = open(classflyFile, "w")
    classfy_.truncate()
    classfy_.close()
    img_sets = ["train", "val"]
    for img_set in img_sets:
        convertimgset(img_set)


if __name__ == "__main__":
    convertdataset()
    shutil.move(rootdir + '/wider_face/' + "/ImageSets/Main/" + "train.txt", rootdir + '/wider_face/' + "/ImageSets/Main/" + "wider_train.txt")
    shutil.move(rootdir +  '/wider_face/' + "/ImageSets/Main/" + "val.txt", rootdir + '/wider_face/' + "/ImageSets/Main/" + "wider_val.txt")
