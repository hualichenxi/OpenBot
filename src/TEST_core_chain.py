#!/usr/bin/python
# coding=utf-8
from core_chain import CoreChainGenerator


def test_full():
    s = u'杨幂在三生三世实力桃花中中饰演的角色是'

    generator = CoreChainGenerator()
    core_chains = generator.generate(s)
    for core_chain in core_chains:
        core_chain.display()

if __name__ == '__main__':
    test_full()