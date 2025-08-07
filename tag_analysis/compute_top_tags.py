import argparse

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def proc_opts():
    parser = argparse.ArgumentParser(description="Analyze and graph artwork tags.")
    parser.add_argument("filename", help="Input file containing tag data")
    parser.add_argument("outdir", help="Output directory (default: ./)")
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
    print(f"Got {len(df)} entries:" )
    print(df.head())
    return df

def count_tags(df, group):
    exp_df = df.explode(group)
    cnt_df = exp_df.groupby(group).size().sort_values(ascending=False)
    return cnt_df

if __name__=="__main__":
    opts = proc_opts()
    df = preprocess(opts.filename, opts.time_start, opts.time_stop)
    for grp  in ['characters', 'meta', 'species', 'tags']:
        cnt = count_tags(df, grp)
        cnt.to_csv(opts.outdir + grp + ".csv")
        




