### option
你能想到的别人也能想到，那到底如何能创造出自己的算法呢？
现在目标任务，实现人脸的对齐，6-10m的数据库来填充图片
task任务：
1、分类，1,是不是人，2,是不是部分人脸
2、边框回归;
3、坐标回归


一个网络要完成上述三个任务：
首先想想数据是怎样的
网络层如何进行设计
多层网络以基础网络来做，在每层网络上添加loss
分类loss：交叉熵损失代价函数;
边框box：边框回归损失函数
landmarks：点回归损失函数

有无人脸，有无半张人脸，

主体cnn：如何设计？还是需要预先了解输入的图片会使什么样的，才可以具体设计到底多少层？

先不用思考如何设计主体思路，还是应该需要拓宽数据库，这是因为我们这边需要从最开始，aflw and wilder face 这两部分，不和整理数据集，进行训练

deep-face的AI 网络框架：
1、数据层：主要包括什么：image/data/  label：person and whether partial face (iou <0.4):
数据集：widerface，and aflw landmarks
还得要剔除到wideface上很多人脸过小的数据，因为过小的人脸会影响到数据（为什么不能剔除人脸呢？过小的人脸像素不够充足，不能影响，那么需要该如何去测试，像素的图片大小，那么在对比像素的面积呢）
需要做的工作：生成部分人脸，生成的标准：准备生成多少张
aflw：  做网络人脸的精修，包括landmarks的标定，
那么网络的架构，敬请期待明日：
