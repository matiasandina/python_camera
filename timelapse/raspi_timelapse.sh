# See details here 
# https://blog.securem.eu/projects/2016/02/21/recording-a-timelapse-with-a-raspberry-pi/

# -t 0 means never stop (in ms)
# -tl take pictures every lapse of ms (10000 is 10 sec)

# -ts (--timestamp) that will use the number of seconds since 1900.

raspistill -t 60000 -tl 10000 -n -w 1920 -h 1080 -ts -o image_%d.jpg