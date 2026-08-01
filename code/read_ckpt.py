"""Reader for prover checkpoint files (ckpt format SPCK0001).

Format (little-endian):
  8 bytes   magic "SPCK0001"
  8 x int64: NSYM, NV, NCYC, budget, gen_depth, ntasks, tasks_done, nodes_total
  int32     solutions found so far
  ntasks x Task: Mask (ceil(NV/64) x uint64), int32 e, int32 R, int32 E, int32 more
  ntasks x uint8: done flags

Usage:
  python read_ckpt.py FILE [--stats]
"""

import struct
import sys
from collections import Counter

MAGIC = b"SPCK0001"


def load(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        assert magic == MAGIC, f"bad magic {magic}"
        hdr = struct.unpack("<8q", f.read(64))
        nsym, nv, ncyc, budget, depth, ntasks, tasks_done, nodes = hdr
        (solutions,) = struct.unpack("<i", f.read(4))
        words = (nv + 63) // 64
        task_fmt = f"<{words}Q4i"
        task_size = struct.calcsize(task_fmt)
        tasks = []
        for _ in range(ntasks):
            row = struct.unpack(task_fmt, f.read(task_size))
            tasks.append({"mask": row[:words], "e": row[words],
                          "R": row[words + 1], "E": row[words + 2],
                          "more": row[words + 3]})
        done = f.read(ntasks)
    return {"nsym": nsym, "nv": nv, "ncyc": ncyc, "budget": budget,
            "depth": depth, "ntasks": ntasks, "tasks_done": tasks_done,
            "nodes": nodes, "solutions": solutions, "tasks": tasks,
            "done": done}


def main():
    d = load(sys.argv[1])
    print(f"n={d['nsym']} budget={d['budget']} depth={d['depth']} "
          f"tasks={d['ntasks']} done={d['tasks_done']} "
          f"({100.0 * d['tasks_done'] / max(d['ntasks'], 1):.2f}%) "
          f"nodes={d['nodes']} solutions={d['solutions']}")
    if "--stats" in sys.argv:
        rc = Counter(t["R"] for t in d["tasks"])
        ec = Counter(t["E"] for t in d["tasks"])
        print(f"R distribution: {dict(sorted(rc.items()))}")
        print(f"E distribution: {dict(sorted(ec.items()))}")


if __name__ == "__main__":
    main()
