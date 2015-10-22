#!/usr/bin/env python

import argparse
import numpy as np
import scipy.io as sio
import os
import sys
sys.path.insert(1, '.')
from vdetlib.vdet.dataset import imagenet_vdet_classes
from vdetlib.utils.common import quick_args
from vdetlib.utils.protocol import proto_load, proto_dump, bbox_hash
import gzip
import json

if __name__ == '__main__':
    args = quick_args(['vid_file', 'score_root', 'save_det'])

    vid_proto = proto_load(args.vid_file)
    vid_name = vid_proto['video']
    assert  vid_name == os.path.basename(os.path.normpath(args.score_root))
    print "Processing {}.".format(vid_name)

    det_proto = {}
    det_proto['video'] = vid_name
    det_proto['detections'] = []
    for frame in vid_proto['frames']:
        frame_id = frame['frame']
        basename = os.path.splitext(frame['path'])[0]
        score_file = os.path.join(args.score_root, basename + '.mat')
        if os.path.isfile(score_file):
            d = sio.loadmat(score_file)
            boxes = d['boxes']
            zs = d['zs']
            for box, scores in zip(boxes, zs):
                det = {}
                bbox = box.tolist()
                det['frame'] = frame_id
                det['bbox'] = bbox
                det['hash'] = bbox_hash(vid_name, frame_id, bbox)
                scores_proto = []
                for class_id, (cls_name, score) in \
                    enumerate(zip(imagenet_vdet_classes[1:], scores), start=1):
                    scores_proto.append({
                        "class": cls_name,
                        "class_id": class_id,
                        "score": float(score)
                    })
                det['scores'] = scores_proto
                det_proto['detections'].append(det)
    proto_dump(det_proto, args.save_det)
