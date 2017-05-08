#!/usr/bin/env python3

import DLX

l = open('Hardest.txt', 'r').readlines()
T_sum = 0
for i, mat in enumerate(l):
    S, M, C, T = DLX.solve(list(map(int, mat[:81].replace('.', '0'))))
    print('testcase =', i)
    print('solvable =', 'YES' if M == 1 else 'NO')
    for x in range(9):
        for y in range(9):
            print(S[x * 9 + y], end=' ')
        print()
    print('nodes =', C)
    print('time =', T, 'ns')
    T_sum += T
    assert M == 1
    print()
print('test finished!')
print('average time =', T_sum // len(l), 'ns')
