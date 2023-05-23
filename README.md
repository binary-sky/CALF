# CALF

reproduction method:

- start docker container:
```
docker run -itd   --name  hmp-$USER \
--net host \
--gpus all \
--shm-size=16G \
fuqingxu/hmp:latest
```

- clone this resp:
```
git clone git@github.com:binary-husky/CALF.git
```

- run calf:
```
python autorl_script.py
```
