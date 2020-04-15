#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 17:43:06 2020

@author: yunyun
"""

import os
import requests
from subprocess import call
import argparse
import pickle


_url_root = 'https://github.com/thorn-lab/coronavirus_structural_task_force/raw/master/'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--accept', help="comma-separated list of accepted key words", required='True')
    parser.add_argument('-P', '--dir_prefix', help="save file to prefix")
    args = parser.parse_args()
    return args

def git_fetch(relpath, args):
    accept = args.accept.split(',')
    prefix = args.dir_prefix
    if prefix is None:
        prefix = os.getcwd()
    for file in relpath:
        if all(_ in file for _ in accept):
            call(['wget', '-x', '-nH','--no-check-certificate', 
                  '--content-disposition', '-q',
                  '-P', prefix,
                  _url_root + file])
            print(_url_root + file)
    

def get_path():
    remote_relpath = requests.get(_url_root + 'utils/relpath.pkl')
    with open("relpath.tmp", "wb") as f:
        f.write(remote_relpath.content)
    with open('relpath.tmp', 'rb') as fp:
        relpath_list = pickle.load(fp)
    os.remove('relpath.tmp')
    return relpath_list
        
        
if __name__ == '__main__':
    args = parse_args()  
    relpath = get_path()
    git_fetch(relpath, args)
    
        
