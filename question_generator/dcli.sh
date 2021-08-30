#nvidia-docker run -it -p 5000:5000 gq_bert
docker run --runtime=nvidia -e DEVICE=cuda:0 -e NVIDIA_VISIBLE_DEVICES=0 -it -p 7500:5000 gq_bert
