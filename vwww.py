#!/usr/bin/env python2.7
#
# The ISC License:
#
# Copyright (c) 2013, Edd Barrett <vext01@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES 
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os, sys, shutil, time, re
from markdown import markdown

def print_err(s):
    sys.stderr.write("error: {0}\n".format(s))
    sys.exit(1)

def get_file_list(dirn):
    if not os.path.exists(dirn):
        print_err("non-existent directory: {0}".format(dirn))

    return [ x for x in os.listdir(dirn) if x.endswith(".md") ]

# Macros
def macro_date():
    return time.asctime()

def macro_include(filename):
    with open(filename, "r") as f:
        return f.read()

# macro-name -> (function, n_args)
MACRO_TABLE = {
        "date" : (macro_date, 0),
        "include" : (macro_include, 1)
        }

def subs_macros(in_str):
    out_lines = []
    for line in in_str.splitlines():
        match = re.match("(.*)%%(.*)%%(.*)", line)
        if match:
            print(match.groups()[1])
            elems = match.groups()[1].strip().split(":")
            try:
                (func, nargs) = MACRO_TABLE[elems[0]]
            except KeyError:
                print_err("unknown macro '%s'" % elems[0])

            if len(elems) - 1 != nargs:
                print_err("wrong number of args for '%s' macro. "
                "expect %d got %d" % (elems[0], nargs, len(elems) - 1))

            replaced = "%s%s%s" % (match.groups()[0], func(*elems[1:]), match.groups()[2])
            out_lines.extend(replaced.splitlines())
        else:
            out_lines.append(line)

    return "\n".join(out_lines)

def read_template(dirn):
    hpath = os.path.join(dirn, "header.html")
    fpath = os.path.join(dirn, "footer.html")

    with open(hpath, "r") as h_hndl: h_str = subs_macros(h_hndl.read())
    with open(fpath, "r") as f_hndl: f_str = subs_macros(f_hndl.read())

    return (h_str, f_str)

def process_md(md, h_str, f_str, indir, outdir):
    outfilename = os.path.join(outdir, md[0:-3] + ".html")
    infilename = os.path.join(indir, md)

    with open(outfilename, "w") as out_hndl:
        out_hndl.write(h_str)
        with open(infilename, "r") as in_hndl: md_src = subs_macros(in_hndl.read())
        out_hndl.write(markdown(md_src, output_format="xhtml1"))
        out_hndl.write(f_str)

def process_mds(mds, h_str, f_str, indir, outdir):
    if not os.path.exists(outdir): os.mkdir(outdir)

    for i in mds:
        print("processing {0}".format(i))
        process_md(i, h_str, f_str, indir, outdir)

def copy_resources(indir, outdir):
    print("copying resources...")
    resin = os.path.join(indir, "res")
    resout = os.path.join(outdir, "res")
    if os.path.exists(resin): shutil.copytree(resin, resout)

if __name__ == "__main__":

    if len(sys.argv) != 3: print_err("usage: vwww indir outdir")

    indir = sys.argv[1]
    outdir = sys.argv[2]

    mds = get_file_list(indir)

    if not mds: print_err("no markdown to process")
    if os.path.exists(outdir): print_err("output dir already exists")

    (h_str, f_str) = read_template(indir)
    process_mds(mds, h_str, f_str, indir, outdir)

    copy_resources(indir, outdir)
