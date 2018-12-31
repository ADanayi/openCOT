# openCOT

openCoT is a Cloud Infrastrcuture manager for FaaS clouds and is initially designed for IoT applications; Although it can be used in other cases too.


# Installation
## Controller

### 1) Installing Docker engine
Install ```docker-cl``` package on the linux based node.

### 2) Install ```Python 3``` on the Node computer
``` bash
sudo apt-get install python3
sudo apt-get install python3-pip
```

### 4) Install the ```PyZMQ``` and ```Docker client``` for Python
```bash
pip install docker
pip install pyzmq
```

### 5) Copy the ```Controller``` folder to the Controller computer



## Node

### 1) Installing Docker engine
Install ```docker-cl``` package on the linux based node.

### 2) Enable Docker to limit containers

#### Open the grub configuration file in a text editor
``` bash
gedit /etc/default/grub
```
#### Add the following line
``` bash
GRUB_CMDLINE_LINUX="cgroup_enable=memory swapaccount=1"
```
#### Save changes
#### Update the grub configuration
``` bash
sudo update-grub
```
#### Restart the docker engine

### 3) Install ```Python 3``` on the Node computer
```bash
sudo apt-get install python3
sudo apt-get install python3-pip
```

### 4) Install the ```PyZMQ``` and ```Docker client``` for Python
```bash
pip install docker
pip install pyzmq
```

### 5) Copy the ``Node`` folder to the Node computer

## Test

On the Controller computer run ```Exec-SimpleController.py``` (in the Controller folder).

```bash
sudo -s
python3 SimpleController.py
```
You should see the output of the Controller's intialization followed by:
```Press enter to start...```

In this moment, on the Node computer, run ```Exec-SimpleNode.py```.
```bash
sudo -s
python3 SimpleController.py
```

Enter 'cluster1' and the IP of the Controller computer. And wait for the Node script to load everything.

Now, go back again to the Controller and press Enter. A successful installation results in the execution of the ```hellocot``` function each 1 second on the Node.
