#!/usr/bin/env python3
from pprint import pprint
import copy
import json
import os
import sys
import tempfile
import traceback
import yaml

from ..dev.nargs import Nargs
from ..dev.cached import get_args_dump
from ..dev.exceptions import DeveloperError, EndUserError
from .helpers import CatchEx, err, Elapsed

from ..dev.get_json import has_yaml_module
from ..gpkgs import message as msg


class Node():
    def __init__(self,
        nesting_num,
        child_num,
        max_nodes,
        parent=None,
    ):
        self.dy_nodes=dict()
        self.is_root=None
        self.level=None
        self.nodes=[]
        self.parent=parent
        self.root=None
        self.max_nodes=max_nodes
        self.nesting_num=nesting_num
        self.child_num=child_num
        self.dy=dict()

        if self.parent is None:
            self.nodes_num=1
            self.root=self
            self.level_nodes=dict()
            self.is_root=True
            self.level=1
            self.is_last=True
            self.name="args"
        else:
            self.root=self.parent.root
            self.root.nodes_num+=1
            self.is_root=False
            self.level=self.parent.level+1
            self.parent.nodes.append(self)
            index=self.parent.nodes.index(self)+1
            self.name="arg{}".format(index)
            self.parent.dy[self.name]=self.dy
            self.parent.dy_nodes[self.name]=self

            if self.parent.is_last is True:
                if index == child_num:
                    self.is_last=True
                else:
                    self.is_last=False 
            else:
                self.is_last=False 
        
        if self.level not in self.root.level_nodes:
            self.root.level_nodes[self.level]=[]
        self.root.level_nodes[self.level].append(self)

    def limit_reached(self):
        if self.root.nodes_num >= self.max_nodes:
            return True
        else:
            return False

    def get_level_nodes(self):
        return self.root.level_nodes[self.level]


def get_dict(nesting_num, child_num, max_nodes=None, pnode=None):
    node=Node(nesting_num, child_num, max_nodes, parent=pnode)
    if node.is_last is True:
        for tmp_node in node.get_level_nodes():
            for i in range(child_num):
                if node.limit_reached() is False:
                    get_dict(nesting_num, child_num, max_nodes, pnode=tmp_node)
    if node.is_root is True:
        return node.root.dy

def get_dict_recursion_limit(limit, dy=None, index=1):
    to_return=False
    if dy is None:
        dy=dict(arg=dict())
        to_return=True
    else:
        dy["arg"]=dict()
    
    if index < limit:
        index+=1
        get_dict_recursion_limit(limit, dy["arg"], index)

    if to_return is True:
        return dy


def process(dy_metadata, data, nodes, elapsed, cached, args, cache_file, only_cache=False, add_data=True):

    method=None

    options_file=None
    if isinstance(args, dict):
        method="dict"
        args=copy.deepcopy(args)
    elif isinstance(args, str):
        options_file=args
        if cache_file is None:
            method=args[-4:]
        else:
            method="json/yaml"
        args=None

    elapsed.start()
    nargs=Nargs(metadata=dy_metadata, args=args, raise_exc=True, cache=cached, options_file=options_file, cache_file=cache_file, only_cache=only_cache)
    duration=elapsed.show()

    if add_data is True:
        if nodes not in data:
            data[nodes]=[]
        data[nodes].append(" ")
        data[nodes].append(method)
        data[nodes].append(str(nargs._from_cache))
        if cache_file is None:
            data[nodes].append(str(None))
        else:
            data[nodes].append(os.path.splitext(cache_file)[1][1:])
        data[nodes].append(str(only_cache))
        data[nodes].append("{:.3f}".format(duration))


def delete_files(filenpas):
    for filenpa in filenpas:
        try:
            os.remove(filenpa)
        except:
            pass
        
def test_performance(
    dy_metadata,
    direpa_tmp,
    filenpa_cache,
):
    elapsed=Elapsed()

    max_nodes=[]
    for max_node in range(50, 1050, 50):
        max_nodes.append(max_node)

    for max_node in range(2000, 11000, 1000):
        max_nodes.append(max_node)
    
    for max_node in range(20000, 110000, 10000):
        max_nodes.append(max_node)

    filenpa_options_json=os.path.join(direpa_tmp, "nargs-option.json")
    filenpa_pickle=os.path.join(direpa_tmp, "nargs-cache.pickle")
    filenpa_options_yaml=os.path.join(direpa_tmp, "nargs-option.yaml")
    filenpa_csv=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "performance.csv")

    all_files=[
        filenpa_options_json,
        filenpa_options_yaml,
        filenpa_cache,
        filenpa_pickle,
    ]

    delete_files(all_files)

    labels=[
        "From",
        "Cache",
        "CFile",
        "COnly",
        "Time",
    ]

    hasHeader=False
    data=dict()

    with open(filenpa_csv, "w") as fcsv:

        for max_node in max_nodes:
            print(max_node)
            args=get_dict(5, 10, max_node)

            process(dy_metadata, data, max_node, elapsed, False, args, None)

            with open(filenpa_options_json, "w") as f:
                f.write(json.dumps(dict(args=args)))

            delete_files([filenpa_cache, filenpa_pickle])
            process(dy_metadata, data, max_node, elapsed, False, filenpa_options_json, None)
            process(dy_metadata, data, max_node, elapsed, True, filenpa_options_json, filenpa_cache, add_data=False)
            process(dy_metadata, data, max_node, elapsed, True, filenpa_options_json, filenpa_cache)
            process(dy_metadata, data, max_node, elapsed, True, filenpa_options_json, filenpa_cache, only_cache=True)

            with open(filenpa_options_yaml, "w") as f:
                f.write(yaml.dump(dict(args=args)))

            process(dy_metadata, data, max_node, elapsed, False, filenpa_options_yaml, None)

            if max_node <= 800:
                process(dy_metadata, data, max_node, elapsed, True, filenpa_options_json, filenpa_pickle, add_data=False)
                process(dy_metadata, data, max_node, elapsed, True, filenpa_options_json, filenpa_pickle)
                process(dy_metadata, data, max_node, elapsed, True, filenpa_options_json, filenpa_pickle, only_cache=True)

            if hasHeader is False:
                hasHeader=True
                num_records=int(len(data[max_node])/len(labels)-1) 
                
                fcsv.write(get_headers(labels, num_records)+"\n")

            record=[max_node]
            record.extend(data[max_node])

            fcsv.write(",".join(map(str, record))+"\n")
   
    delete_files(all_files)

def get_headers(labels, num_records):
    headers=[
        "Nodes",
    ]

    for i in range(num_records):
        headers.append(" ")
        headers.extend(labels)

    return ",".join(headers)