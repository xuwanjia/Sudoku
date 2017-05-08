swig -python DLX.i
gcc -O3 -fPIC -shared DLX_wrap.c -o _DLX.so -I`whereis python3 | egrep -o '[[:graph:]]*/include/python3[[:graph:]]*'` -lpython3
