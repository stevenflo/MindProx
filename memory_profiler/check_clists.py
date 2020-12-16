#!/usr/bin/python3.6

"""
check_traces.py

Makes sure traces match length constraints
"""

import os
import sys
import re
import tempfile
import shutil
import subprocess
from textwrap import dedent

target_re = re.compile(r".*len=(\d+)")
actual_re = re.compile(r".*length (\d+)")

Template = dedent("""\
    #include <stdio.h>
    #include <stdint.h>
    #error "HEADER NOT INJECTED"
    
    int main(void) {
        uint32_t num_lists = sizeof(EntryPoints) / sizeof(uint32_t);
        uint32_t memory_fp_kib = sizeof(Memory) >> 10;
        printf("Header contains %u lists with total footprint of %u kiB\\n", num_lists, memory_fp_kib);
        
        for (uint32_t i = 0; i < num_lists; i++) {
            uint32_t entry_point = EntryPoints[i]*2;
            uint32_t list_length = 0;
            uint32_t current_loc = entry_point;
            do {
                list_length++;
                uint32_t next_loc = Memory[current_loc]*2;
                if ((next_loc == current_loc) && (current_loc != entry_point)) {
                    fprintf(stderr, "Circular reference detected in list %u\\n", i);
                    return 1;
                }
                if (list_length >= (1 << 24)) {
                    fprintf(stderr, "List %u appears to be infinite\\n", i);
                    return 1;
                }
                current_loc = next_loc;
            } while (current_loc != entry_point);
            printf("List %u is of length %u\\n", i, list_length);
        }
        return 0;
    }\n""")

if len(sys.argv) != 2:
    sys.exit(f"Usage: ./check_clists.py <trace header>")
header_fname = sys.argv[1]
header_basename = os.path.basename(header_fname)

tempdir = tempfile.TemporaryDirectory()
shutil.copy(header_fname, tempdir.name)
os.chdir(tempdir.name)

program_lines = Template.split("\n")
program_lines[2] = f"#include \"{header_basename}\""
program = "\n".join(program_lines)
with open("check_clists.c", "w") as program_f:
    program_f.write(program)

subprocess.run("gcc -Wall -Wextra -Wpedantic -Werror -std=c99 check_clists.c -o check_clists".split(), check=True)
check_results = subprocess.run("./check_clists", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
list_results = str(check_results.stdout, encoding="utf-8")
print(list_results.split("\n")[0])

target_lengths = []
with open(header_basename, "r") as header_f:
    for line in header_f:
        match = target_re.match(line)
        if match is not None:
            target_lengths.append(int(match.group(1)))

actual_lengths = []
for line in list_results.split("\n"):
    match = actual_re.match(line)
    if match is not None:
        actual_lengths.append(int(match.group(1)))

assert(len(target_lengths) == len(actual_lengths))
good = True
for idx in range(len(target_lengths)):
    if target_lengths[idx] == actual_lengths[idx]:
        print(f"List {idx} PASS")
    else:
        print(f"List {idx} FAIL: Target length: {target_lengths[idx]}; Actual length: {actual_lengths[idx]}")
        good = False

if not good:
    sys.exit(1)

