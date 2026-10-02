#!/usr/bin/env python3
import sqlite3
import sys
sys.path.insert(0, '/mnt/nas/mala/work/archaeology/worker')
from dream_compare import fetch_dream, compare

conn = sqlite3.connect('/mnt/nas/mala/work/archaeology/data/archaeology_phase1_clean.db')
cur = conn.cursor()

cur.execute("""
    SELECT seed_word, GROUP_CONCAT(id)
    FROM dreams
    WHERE seed_word IS NOT NULL
    GROUP BY seed_word
    HAVING COUNT(*) >= 2
""")

results = []
for seed, ids_str in cur.fetchall():
    ids = [int(x) for x in ids_str.split(',')]
    for i in range(len(ids)):
        for j in range(i+1, len(ids)):
            d1 = fetch_dream(conn, ids[i])
            d2 = fetch_dream(conn, ids[j])
            if d1 and d2:
                m = compare(d1, d2)
                results.append({
                    'seed': seed,
                    'id1': ids[i], 'id2': ids[j],
                    'temp1': d1['temperature'], 'temp2': d2['temperature'],
                    'primary1': d1['penalized_primary'], 'primary2': d2['penalized_primary'],
                    'composite': m['composite'],
                    'same_primary': m['archetype']['same_primary'],
                    'text_jaccard': m['text']['jaccard'],
                    'archetype_cosine': m['archetype']['cosine_similarity'],
                })

results.sort(key=lambda x: x['composite'], reverse=True)

print(f"Total same-seed pairs compared: {len(results)}")
print()
print("MOST DIVERGENT same-seed pairs:")
for r in results[:10]:
    same = "SAME" if r['same_primary'] else "DIFF"
    print(f"  {r['seed']:12s} #{r['id1']}({r['temp1']}) vs #{r['id2']}({r['temp2']})  "
          f"composite={r['composite']:.3f}  {same:4s}  "
          f"text={r['text_jaccard']:.3f}  archetype_cos={r['archetype_cosine']:.3f}")

print()
print("MOST SIMILAR same-seed pairs:")
for r in results[-10:]:
    same = "SAME" if r['same_primary'] else "DIFF"
    print(f"  {r['seed']:12s} #{r['id1']}({r['temp1']}) vs #{r['id2']}({r['temp2']})  "
          f"composite={r['composite']:.3f}  {same:4s}  "
          f"text={r['text_jaccard']:.3f}  archetype_cos={r['archetype_cosine']:.3f}")

print()
comps = [r['composite'] for r in results]
mean_c = sum(comps) / len(comps)
median_c = sorted(comps)[len(comps)//2]
print(f"Composite distance stats: mean={mean_c:.3f}, median={median_c:.3f}, "
      f"min={min(comps):.3f}, max={max(comps):.3f}")
same_prim = sum(1 for r in results if r['same_primary'])
print(f"Same primary archetype: {same_prim}/{len(results)} ({100*same_prim/len(results):.1f}%)")
