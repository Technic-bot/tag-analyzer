python tag_analysis/graph_tags.py data/2026/october/tom-2026-10-20.json chars_full.txt --out results/graphs/tom_fischbach/2026/october/ooct22_ --freq QE --time-start 2016-01-01
python tag_analysis/graph_suggesters.py data/2026/october/twokinds_patreon.csv --freq QE --time-start 2016-01-01 --outdir results/graphs/tom_fischbach/2026/october/oct22_

python tag_analysis/graph_tags.py data/2026/october/tom-2026-10-20.json chars_full.txt --out results/graphs/tom_fischbach/2026/october/ooct22_recent_ --freq ME --time-start 2024-12-01
python tag_analysis/graph_suggesters.py data/2026/october/twokinds_patreon.csv --freq ME --time-start 2024-12-01 --outdir results/graphs/tom_fischbach/2026/october/oct22_recent_

