# OMU
Sorted Process of Top in the OOM
## Usage
1. Download OMU.py script 
```
$ git clone https://github.com/colso/OMU.git
```
2. Give a execution permission.
```
$ chmod 755 ./OMU.py
```
3. Run with a messages file 
```
$ ./OMU.py ../<any path>/messages
```
4. Sometime, If you need to update cut-count and prefix-size. Use according to your preference.
```
$ vi OMU.py
...
  6 name_prefix_trim_size = 10     <<<--- process naming length 
  7 rss_top_cut = 8                <<<--- process cut count
```

## sample test result
```
Date: Dec 23 11:54:26 [     k1_a01 ]
----------------------------------------------
     Pages 	        RSS 	        Proc
----------------------------------------------
   3681310 	14.043083 GB 	 [       java]
      1622 	0.006187 GB 	 [ EfamsBatch]
      1281 	0.004887 GB 	 [ EaiCall.sh]
       260 	0.000992 GB 	 [       sshd]
       138 	0.000526 GB 	 [ collector_]
       121 	0.000462 GB 	 [         sh]
        79 	0.000301 GB 	 [        hth]
        66 	0.000252 GB 	 [    ontuned]
----------------------------------------------
                 3685123 Pages	 : Pages Total
               14.057629 GB 	 : RSS Total
```

