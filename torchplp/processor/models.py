# -*- coding: utf-8 -*-
"""
models.py - The processor model defination

:Author: Verf
:Email: verf@protonmail.com
:License: MIT
"""
import abc


class Processor(metaclass=abc.ABCMeta):
    """The upper class of processor"""

    def __repr__(self):
        return self.__class__.__name__

class Parser(metaclass=abc.ABCMeta):
    """The upper class of parser"""

    def __repr__(self):
        return self.__class__.__name__


class Embedder(metaclass=abc.ABCMeta):
    """The upper class of words model"""

    def __repr__(self):
        return self.__class__.__name__

    @abc.abstractmethod
    def train(self, sents):
        """Training words model"""
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, key):
        """Work as dict"""
        raise NotImplementedError
