# Tag Analyzer

This small repo allows you visualize the top tags of certain queries for e621 and similar web galleries for arts. This was done mainly as a way to visualize how the arts by Tom Fischbach has evolved over time. What trends emerge and dissaper how character popularity evolved etc. But should work with any list of post from e621 from any query you do. 

Input format is a json parsed from e621 json endpoint will eventually add a link here once i clean up the system i use to query the site but if you are interested you should probably get a good idea for the format for the examples i have here under the [data](data/) folder it should be a json with title and tags.

## Usage

Mostly for me but if anyone wants to use this for their own: This repo contains 2 scripts [compute_top_tags.py](tag_analysis/compute_top_tags.py) which allows you to quickly visualize all the unique tags from your query and their absolute frequency. You can invoke it as follows:

```bash
python tag_analysis/compute_top_tags.py data/2025/tom-26-jul-25.json  results/top_tags/
```

This will create 4 different files under the selected folder. Characters.csv meta.csv, species.csv and tags.csv which simply lists the top tags in that category and frequency in decreasing order

The other script [graph_tags.py](tag_analysis/graph_tags.py) is much more interesting it takes a list of tags either provided through cli or thorugh a file and graphs how the number of times that suite of tags appears over time. You can use it as follows:

```bash
python tag_analysis/graph_tags.py data/2025/tom-26-jul-25.json chars.txt --freq 3ME --time-start 2015-02-01
```

Like so you pass a json containing the e621 results from your query and a list of tags, in this case character names, in the chars.txt file. You can specify time grouping, in this case each 3 months or quarter and also can specify when to start counting.

An alternative invocation, that allows you to save the graph to disk instead of just visualizing it is as follows:

```bash
python tag_analysis/graph_tags.py data/2025/tom-26-jul-25.json chars.txt --freq 3ME --time-start 2015-02-01 --outdir results/graphs/tom_fischbach/ago-2025/
```

Finally you can specify tags per command line argument as follows:

```bash
python tag_analysis/graph_tags.py data/2025/tom-26-jul-25.json "flora_(twokinds)" trace_legacy keith_keiser natani
```

As you can see is clunky so not really recommended but good for a fast and easy visualization if you have the exact names of the tags at hand.

The workflow i use is i get my tags from the comput_top_tags script and then ensemble a suitable tags.txt file to run with graph_tags.py




