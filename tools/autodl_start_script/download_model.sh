#!/bin/bash

cd /root/autodl-tmp && conda run -n base pip install codewithgpu && conda run -n base cg down xxxiu/glm-4-9b-chat
