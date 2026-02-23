import argparse

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap

years = mdates.YearLocator()
six_months = mdates.MonthLocator(interval=6)
auto_locator = mdates.AutoDateLocator()

def proc_opts():
    parser = argparse.ArgumentParser(description="Analyze and graph artwork tags.")
    parser.add_argument("filename", help="Input file containing tag data")
    parser.add_argument("tags", nargs="+", help="Tags to graph in list form")
    parser.add_argument("--outdirectory", "-o", help="Output directory (default: ./graphs/)")
    parser.add_argument('--title', help = 'Prefix name for graphs on disks', default=None)  
    parser.add_argument('--frequency', help = 'Group by frequency in months', default="6ME", type=str)  
    parser.add_argument('--time-start', help = 'Only consider entries after this date')  
    parser.add_argument('--time-stop', help = 'Only consider entries after this date')  
    return parser.parse_args()

def preprocess(filename, time_start=None, time_stop=None):
    print(f'Reading {filename}')
    df = pd.read_json(filename)
    if time_start: 
        df = df[df['creation'] > time_start ]
    if time_stop: 
        df = df[df['creation'] < time_stop ]
    df['creation'] = pd.to_datetime(df['creation'], format='ISO8601')
    valid_cols = ['characters', 'tags', 'species'] #meta
    df['all_tags'] = df[valid_cols[0]]
    for col in valid_cols:
        df['all_tags'] += df[col]

    tag_columns = ['meta', 'characters', 'tags', 'species']
    unused_cols = ['meta', 'characters', 'tags', 'pools', 'species']
    print("Removing redundant columns")
    df = df.drop(columns=unused_cols)
    print(f"Got {len(df)} entries:" )
    print(df.head())
    return df

def group_tags(df, tags, freq):
    print(f"Counting for: {tags}")
    exp_df = df.explode('all_tags')
    print(f"Exploding all tags got {len(df)}" )
    print(exp_df.head())
    grouper = pd.Grouper(key='creation', freq=freq)
    # grp = exp_df.groupby([grouper, 'all_tags']).size().unstack(fill_value=0)
    grp = exp_df.groupby([grouper, 'all_tags'])['id'].nunique().unstack(fill_value=0)
    # exp_df.groupby([grouper, 'all_tags']).size().to_csv("debug.csv")
    print("Tag group output")
    print(grp[tags].tail())
    # Slice before returning
    return grp[tags]

def parse_tags(tags):
    # Passed a list through cli
    if len(tags) > 1:
        tag_list = tags
        color_list = [None] * len(tags)
    else:
        tag_filename = tags[0]
        tag_list = []
        color_list = []
        with open(tag_filename,'r') as tag_file:
            for line in tag_file:
                tag, color = parse_line(line)
                tag_list.append(tag)
                color_list.append(color)
                
    print(tag_list)
    return tag_list, color_list

def parse_line(line):
    proc_line = line.split()
    tag = proc_line[0]
    color = None
    if len(proc_line) > 1:
        color = proc_line[1]
    return tag, color

def group_artworks(df, freq):
    grouper = pd.Grouper(key='creation', freq=freq)
    time_grp = df.groupby(grouper).size()
    print(time_grp.tail())
    return time_grp

def merge_df(tag_df, times_df):
    print("Merging dataframes")
    merged_df = tag_df 
    merged_df['others'] = merged_df.sum(axis=1) - time_df
    merged_df['total'] = time_df
    print(merged_df.head())
    return merged_df

def graph_tags(merged_df, tags, colors):
    # plt.style.use('seaborn-v0_8-darkgrid')
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(19.2,10.8))
    bottom = np.zeros_like(merged_df.index)
    for tag, color in zip(tags, colors):
        ax.bar(
            merged_df.index, merged_df[tag].values, label=tag, bottom=bottom,
            width=-50, color=color, align='edge')
        bottom+=merged_df[tag].values
  
    ax.xaxis_date()
    fmtr = mdates.DateFormatter('%Y-%m')

    ax.xaxis.set_major_locator(auto_locator)
    ax.xaxis.set_major_formatter(fmtr)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    ax.legend()
    ax.set_title("Tags over time")
    ax.annotate("By TecBot with ♥ ", xy= (0.8,-0.1),
                xycoords='axes fraction', fontsize=10)
    return fig

def graph_heatmap(df):
    plt.style.use('seaborn-v0_8-darkgrid')

    df = df[df.sum().sort_values(ascending=False).index]
    data = df.T.values
    chars = df.columns
    times = df.index
    dates = mdates.date2num(times)

    custom_cmap = LinearSegmentedColormap.from_list(
        "my_cmap",
        #["#72CDFF", '#F7941D'],
        [ "#6dcff6", "#f7941d"],
        N=256  # smoothness
    )

    # Things:
    cyan, orange = [ "#6dcff6", "#f7941d"]
    # Me
    cyan, orange = ["#72CDFF", '#F7941D']

    fig, ax = plt.subplots(figsize=(19.2,10.8))
    im = ax.imshow(data,
            aspect='auto',
            # cmap=custom_cmap,
            cmap="cividis",
            interpolation='nearest',
            extent=[dates.min(), dates.max(), 0, data.shape[0]],
            origin='lower'
            )

    cb = plt.colorbar(im, ax=ax)
    cb.set_label("Incidence of characters in artworks")

    ax.xaxis_date()
    locator = mdates.AutoDateLocator()
    fmtr = mdates.DateFormatter('%Y-%m')

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(fmtr)

    ax.set_yticks(np.arange(len(chars)))
    ax.set_yticklabels(chars)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')


    ax.set_title("Heatmap of characters over time")
    ax.annotate("By TecBot with ♥ ", xy= (0.8,-0.1),
                xycoords='axes fraction', fontsize=10)
    return fig
        
if __name__=="__main__":
    opts = proc_opts()
    tags, colors = parse_tags(opts.tags)
    df = preprocess(opts.filename, opts.time_start, opts.time_stop)
    tag_df = group_tags(df, tags, opts.frequency)
    time_df = group_artworks(df, opts.frequency)
    # fig = graph_tags(tag_df, tags, colors)
    htm = graph_heatmap(tag_df)
    if not opts.outdirectory:
        plt.show()
    else:
        # fig.savefig(opts.outdirectory + "tags_over_time.png")
        htm.savefig(opts.outdirectory + "heatmap.png")



    
