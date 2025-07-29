import argparse

import pandas as pd
import matplotlib.pyplot as plt


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
    df['all_tags'] = df['meta'] + df['characters'] + df['tags'] + df['species']
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
    grp = exp_df.groupby([grouper, 'all_tags']).size().unstack(fill_value=0)
    print("Tag group output")
    print(grp[tags].head())
    # Slice before returning
    return grp[tags]

def group_artworks(df, freq):
    grouper = pd.Grouper(key='creation', freq=freq)
    time_grp = df.groupby(grouper).size()
    print(time_grp.head())
    return time_grp

def merge_df(tag_df, times_df):
    print("Merging dataframes")
    merged_df = tag_df 
    print(merged_df.sum(axis=1))
    merged_df['others'] = time_df - merged_df.sum(axis=1)
    merged_df['total'] = time_df
    print(merged_df)
    return merged_df

if __name__=="__main__":
    opts = proc_opts()
    df = preprocess(opts.filename, opts.time_start, opts.time_stop)
    tag_df = group_tags(df, opts.tags, opts.frequency)
    time_df = group_artworks(df, opts.frequency)
    merged_df = merge_df(tag_df, time_df)


    
