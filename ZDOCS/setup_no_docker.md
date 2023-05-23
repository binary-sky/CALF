# setup on ubuntu without docker

Warning! Always use docker if possible! 


This file is written for those who are very confident to solve all kinds of problems and errors on their own!


## python version

``` sh
python 3.8
```
## pip requirements 
Please read [pip_requirement](pip_requirement.md)


## Download and extract starcraft
``` sh
cd /home/hmp
git clone https://github.com/binary-husky/uhmap-visual-tool.git
python linux_deploy_starcraft_all_versions.py
mv /home/hmp/uhmap-visual-tool/UnrealEngine/home/hmp/*  /home/hmp
```

## Download Unreal-HMAP binary client
Please read [get UHMP](use_unreal_hmap.md)
<!-- ## download and extract starcraft and unreal engine
``` sh
cd /home/hmp
git clone https://github.com/binary-husky/uhmap-visual-tool.git
cd /home/hmp/uhmap-visual-tool/
python linux_deploy.py
python linux_deploy_starcraft_all_versions.py
mv /home/hmp/uhmap-visual-tool/UnrealEngine/home/hmp/*  /home/hmp
```  -->

## Download and extract HMAP main framework
``` sh
cd /home/hmp
git clone https://github.com/binary-husky/hmp2g.git
cd /home/hmp/hmp2g
```
