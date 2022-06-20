#!/usr/bin/env python

import sys
import re
import os
from optparse import OptionParser

class OOM_item:
    name_prefix_trim_size = 10
    def __init__(self, oom_list, trim_size=name_prefix_trim_size):
        self.uid = int(oom_list[0])
        self.tgid = int(oom_list[1])
        self.total_vm = int(oom_list[2])
        self.rss = int(oom_list[3])
        self.pgtables_bytes = int(oom_list[4])
        self.swapents = int(oom_list[5])
        self.oom_score_adj = int(oom_list[6])
        self.name = oom_list[7][0:trim_size]

    def get_rss(self):
        return self.rss
    def get_name(self):
        return self.name
    def __add__(self, other):
        self.total_vm = self.total_vm + other.total_vm
        self.pgtables_bytes = self.pgtables_bytes + other.pgtables_bytes
        self.swapents = self.swapents + other.swapents
    def __str__(self):
        return ("%10d %10d %10d %10d %10d %10d %10d %10s" % (self.uid, self.tgid,
                    self.total_vm, self.rss, self.pgtables_bytes, self.swapents,
                    self.oom_score_adj, self.name))

class OOM:
    rss_top_cut = 8
    def __init__(self, time, hostname, oom_list):
        self.time = time
        self.hostname = hostname
        self.OL = oom_list

    def lump_and_sort_for_rss(self, cut_size=rss_top_cut):
        ul = {}
        for item in self.OL:
            if item.get_name() in ul.keys():
                ul[item.get_name()] += item.get_rss()
            else:
                ul[item.get_name()] = item.get_rss()
        return sorted(ul.items(), key = lambda item: item[1], 
                reverse = True)[:cut_size]
    def get_info(self):
        return ("%5s %10s \t[%22s ]" % ('Date:', self.time, 
                    self.hostname))
    def get_total_rss(self):
        rss_sum = 0
        for item in self.OL:
            rss_sum += item.get_rss()
        return rss_sum

    def top_rss_procs(self, top_cut=rss_top_cut):
        print(self.get_info())
        print("-------------------------------------------------")
        print("%10s \t %10s \t %11s" % ('Pages', 'RSS', 'Proc'))
        print("-------------------------------------------------")
        for rss_item in self.lump_and_sort_for_rss(top_cut):
            print("%10d \t%3.6f GB \t [%14s]" % (rss_item[1], 
                        (float(rss_item[1]*4))/1024/1024 , rss_item[0]))
        print("-------------------------------------------------")
        print("%24d Pages\t : Pages Total" % self.get_total_rss())
        print("%24f GB \t : RSS Total\n" % 
                (float(self.get_total_rss()*4)/1024/1024))

    def et_OL(self):
        return self.OL

def is_start_delimiter(line):
    rex = re.compile('oom_score_adj name')
    return rex.search(line)
def is_data_delimiter(line):
    rex = re.compile('[0-9]+\]\ +[0-9]+\ +[0-9]+\ +[0-9]+\ +[0-9]+\ +[0-9]+\ +[0-9]+\ +[-0-9]+\ [0-9a-zA-Z().-]')
    return rex.search(line)

def get_chunk_list(fd):
    chunk_list = []
    chunks = []
    values = []
    deli_item = None
    while True:
        line = fd.readline()
        if not line:
            break
        else:
            line = line[0:-1]
        if is_data_delimiter(line):
            chunks.append(line)
        else:
            if chunks:
                chunk_list.append(chunks)
                chunks = []
                values = []

    if chunks:
        chunks.append(values)
        chunk_list.append(chunks)
    return chunk_list

#                                                    [ pid ]   uid  tgid total_vm      rss pgtables_bytes swapents oom_score_adj name
# input:    Dec 23 11:54:26 k1715_ptrustla01 kernel: [ 5301]    13  5301  1981935     4972  2584576   188253             0 java
# output:   ['13', '5301', '1981935', '4972', '2584576', '188253', '0', 'java']
def trim_and_split_oom_proc(item):
    if not item:
        return None
    rex = re.compile('[0-9]+\]')
    return item[rex.search(item).end():].split()

def get_rss_usage(cl_item):
    ul = {}
    for item in cl_item:
        il = (trim_and_split_oom_proc(item))
        if il:
            OC = OOM_item(il)
            if OC.get_name() in ul.keys():
                ul[OC.get_name()] = ul[OC.get_name()] + OC.get_rss()
            else:
                ul[OC.get_name()] = OC.get_rss()
    return sorted(ul.items(), key = lambda item: item[1], reverse = True)

def get_OOM_from_chunklist(cl, pts):
    OCL = []
    # get date and hostname in the first line
    cl_t = cl[0].split()
    oom_time = cl_t[0]+" "+cl_t[1]+" "+cl_t[2]
    oom_hostname = cl_t[3]

    for item in cl:
        if len(item) > 3:
            OCL.append(OOM_item(trim_and_split_oom_proc(item), pts))
    return OOM(oom_time, oom_hostname, OCL)

def usage():
    print("usage: OMU.py filepath\n or")
    print("usage: OMU.py -f filepath [options] arg\n")
    print("Options:")
    print("\t-f, --file\t\t file path")
    print("\t-p, --prefix-trim\t The process name trim size. Processes are going lump")
    print("\t-c, --top-cut\t\t The RSS top cut size")
    print("\t-h, --help\t\t This page")

def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", type="string", dest="filename")
    parser.add_option("-p", "--prefix-trim", type="int", dest="ptsize")
    parser.add_option("-c", "--top-cut", type="int", dest="cutsize")
    parser.add_option("-h", "--help", type="string", dest="helps")
    options = None
    filename = None
    pts = 10
    cuts = 7

    if len(sys.argv) < 3:
        filename = sys.argv[1]
    else:
        options, args = parser.parse_args(sys.argv)
        if options.filename:
            filename = options.filename
        if options.ptsize:
            pts = options.ptsize
        if options.cutsize:
            cuts = options.cutsize
        if options.helps:
    if not filename or not os.path.isfile(filename):
        usage()
        return

    with open(options.filename) as fd:
        c_l = get_chunk_list(fd)
    if c_l:
        for cl_i in c_l:
            OC = get_OOM_from_chunklist(cl_i, pts)
            OC.top_rss_procs(cuts)

if __name__ in ("__main__"):
    main()
