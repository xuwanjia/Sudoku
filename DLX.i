%module DLX
%include "carrays.i"
%array_class(int,intArray);
%{
#include "DLX.h"
%}
void DLXsolve(int* sdk);
void DLXgenerate(int* f,int* sdk);
%pythoncode%{
def solve(l):
        a=intArray(100)
        for i in range(81): a[i]=l[i]
        _DLX.DLXsolve(a)
        S=[]
        for i in range(81): S.append(a[i])
        M=a[81]
        C=a[82]
        T=a[83]*(10**9)+a[84]
        del(a)
        return S,M,C,T
def generate():
        import random
        a=intArray(100)
        b=intArray(100)
        f=list(range(81))
        random.shuffle(f)
        for i in range(81): b[i]=f[i]
        b[81]=random.randint(0,10**9)
        _DLX.DLXgenerate(b,a)
        S=[]
        for i in range(81): S.append(a[i])
        del(a)
        return S
%}
