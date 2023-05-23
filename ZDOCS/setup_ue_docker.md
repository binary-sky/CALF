# Start up UE Docker Container | 
Warning! Unreal engine is included in this docker, 500GB disk space is needed.


```sh
sudo docker ps
```

```sh
sudo docker run -itd   --name  $USER-swarm \
--net host \
--memory 500G \
--gpus all \
--shm-size=32G \
fuqingxu/hmp:unreal-trim


sudo docker exec -it  $USER-swarm sed -i 's/2266/4567/g' /etc/ssh/sshd_config
sudo docker exec -it  $USER-swarm service ssh start
sudo docker exec -it  $USER-swarm bash
```

Now find a computer to ssh into it: ```ssh hmp@your_host_ip -p 2233```
```
# IP Addr: share with the host
# SSH Port 4567
# UserName: hmp
# Password: hmp
```
