#!/bin/sh
if ! test -f ../prototxt/google/train.prototxt ;then
	echo "error: train.prototxt does not exit."
	echo "please generate your own model prototxt primarily."
        exit 1
fi
../../../../../build/tools/caffe train --solver=../prototxt/google/solver.prototxt -gpu 1 \
#--snapshot=face_recog/tiny_iter_9740.solverstate
