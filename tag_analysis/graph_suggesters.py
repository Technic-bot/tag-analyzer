import argparse

import re

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
    parser.add_argument("--outdirectory", "-o", help="Output directory (default: ./graphs/)")
    parser.add_argument('--title', help = 'Prefix name for graphs on disks', default=None)  
    parser.add_argument('--frequency', help = 'Group by frequency in months', default="6ME", type=str)  
    parser.add_argument('--time-start', help = 'Only consider entries after this date')  
    parser.add_argument('--time-stop', help = 'Only consider entries after this date')  
    return parser.parse_args()

class PatreonAnalyzer():
    def __init__(self, infile, outdir):
        self.filename = infile
        self.outdir = outdir

    def preprocess(self, filename, time_start=None, time_stop=None):
        print(f'Reading {self.filename}')
        df = pd.read_csv(self.filename)
        df['date'] = pd.to_datetime(df['date'], format='ISO8601')
        if time_start: 
            df = df[df['date'] > time_start ]
        if time_stop: 
            df = df[df['date'] < time_stop ]

        print(f"Got {len(df)} entries:" )
        print(df.head())
        self.df = df
        return

    def get_suggester(self):
        self.df['suggester'] = \
          self.df['description'].str.extract(
                  r"suggested(?: by )?(.+?)!", flags=re.IGNORECASE)
        none_idx = self.df['suggester'].isna()
        print(f"Got {none_idx.sum()} entries withouth suggesters")

        self.df.loc[none_idx, 'suggester'] = \
           self.df.loc[none_idx, 'description'].str.extract(
                   r"suggested by (\w+)", flags=re.IGNORECASE)[0]
        none_idx = self.df['suggester'].isna()
        print(f"Got {none_idx.sum()} entries withouth suggesters after patching")
        print(self.df.tail(27))
        self.df.loc[none_idx].to_csv("debug.csv")
        return

if __name__=="__main__":
    args = proc_opts()
    analyzer = PatreonAnalyzer(args.filename, args.outdirectory)
    analyzer.preprocess(args.time_start, args.time_stop)
    analyzer.get_suggester()
