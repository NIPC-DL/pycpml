# -*- coding: utf-8 -*-
"""
juliet.py - Juliet Test Suite (https://samate.nist.gov/SRD/testsuite.php)

:Author: Verf
:Email: verf@protonmail.com
:License: MIT
"""
import re
import pickle
import zipfile
from concurrent import futures
from torchplp.utils.loader import loader_cc
from torchplp.utils.utils import download_file
from .models import Dataset
from .constants import JULIET_URL

def tag_file(file):
    """extract function from file and tag it by it's name"""
    samples = list()
    ast = loader_cc(str(file))
    decl = [x for x in ast.walk() if x.is_definition and x.kind == 'FUNCTION_DECL']
    for node in decl:
        if 'main' in str(node.data):
            continue
        if str(node.data) == 'good':
            continue
        if str(node.data) == 'bad':
            continue
        if len(list(node.walk())) < 6:
            continue
        label = 1 if 'bad' in str(node.data) else 0
        samples.append([node, label])
    return samples

def tag_all_files(files):
    """tag all files"""
    all_samples = list()
    with futures.ProcessPoolExecutor() as pool:
        for samples in pool.map(tag_file, files):
            all_samples.extend(samples)
    return all_samples

class Juliet(Dataset):
    """Juliet Test Suite <https://samate.nist.gov/SRD/testsuite.php>

    Args:
        root (str): Path to save dataset
        download (bool, optional): Default true, download dataset from internet
        proxy (str): The proxy for download.
            eg. 'http://user:pass@host:port/'
                'socks5://user:pass@host:port'

    """

    def __init__(self, root, download=True, proxy=None, cache=True):
        super(Juliet, self).__init__(root)
        self._case = self._root / 'C' / 'testcases'
        self._cache = self._root / 'cache'
        self._cache.mkdir(parents=True, exist_ok=True)

        if download:
            self.download(proxy)

        self._category = dict()
        for d in self._case.iterdir():
            if d.is_dir() and self.iscwe(d.name):
                file_list = list()
                for f in d.glob('**/*.*'):
                    if f.suffix in ['.c', '.cpp'] and self.iscwe(f.name):
                        file_list.append(f)
                self._category[self.iscwe(d.name)] = file_list

    def download(self, proxy):
        """Download Juliet Test Suiet from NIST website

        Args:
            proxy (str): proxy used for download.
                eg. 'http://user:pass@host:port/'
                    'socks5://user:pass@host:port'

        """
        print(f'Download {JULIET_URL}')
        if not self._case.exists():
            download_file(JULIET_URL, self._root, proxy)
            print('Download success, start extracting')
            zip_file = self._root / JULIET_URL.split('/')[-1]
            with zipfile.ZipFile(str(zip_file)) as z:
                z.extractall(str(self._root))
            print('Extracting success')
        else:
            print(f"Dataset exist, download cancel")

    def load(self, category=None):
        for c in category:
            files = self._category[c]
            samples = tag_all_files(files)
            yield c, samples

    @staticmethod
    def iscwe(name):
        m = re.match(r'CWE\d{2,3}', name)
        return m.group() if m is not None else False
