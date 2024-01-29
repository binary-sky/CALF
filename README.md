# Introduction

This is the open source program of the CALF paper.
This source code is a fork of the HMP repository.
The Hybrid Multi-agent Playground (HMP) is an experimental framework designed for Reinforcement Learning (RL) researchers.
Unlike any other framework which only isolates the TASKs from the framework, 
HMP also separates the ALGORITHMs from the framework to achieve excellent compatibility.

```mermaid
flowchart LR
    A["Open source program of CALF paper"]
    A --> B["Fork of HMP repository"]
    --> C["Hybrid Multi-agent Playground (HMP)"]
    C --> D["Experimental framework for RL researchers"]
    C --> E["Separation of TASKs from the framework"]
    C --> F["Separation of ALGORITHMs from the framework"]
    F --> G["Achieve excellent compatibility"]
```

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
git clone https://github.com/binary-husky/CALF.git
```

- run calf:
```
python autorl_script.py
```
