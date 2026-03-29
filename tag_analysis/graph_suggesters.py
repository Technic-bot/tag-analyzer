import argparse

import re

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import PowerNorm

years = mdates.YearLocator()
six_months = mdates.MonthLocator(interval=6)
auto_locator = mdates.AutoDateLocator()

def proc_opts():
    parser = argparse.ArgumentParser(description="Analyze and graph artwork tags.")
    parser.add_argument("filename", help="Input file containing tag data")
    parser.add_argument("--preprocessed", action='store_true', help="Preprocessed file with suggesters")
    parser.add_argument("--outdirectory", "-o", help="Output directory (default: ./graphs/)")
    parser.add_argument('--title', help = 'Prefix name for graphs on disks', default=None)  
    parser.add_argument('--frequency', help = 'Group by frequency in months', default="QE", type=str)  
    parser.add_argument('--time-start', help = 'Only consider entries after this date')  
    parser.add_argument('--time-stop', help = 'Only consider entries after this date')  
    return parser.parse_args()

class PatreonAnalyzer():
    def __init__(self, infile, outdir):
        self.filename = infile
        self.outdir = outdir
        self.no_suggs_file = "/no_suggs.csv"

    def preprocess(self, filename, time_start=None, time_stop=None):
        print(f'Reading {self.filename}')
        df = pd.read_csv(self.filename)
        df['date'] = pd.to_datetime(df['date'], format='ISO8601')
        if time_start: 
            df = df[df['date'] > time_start ]
        if time_stop: 
            df = df[df['date'] < time_stop ]

        print(f"Got {len(df)} entries:" )
        # print(df.head())
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
        # print(self.df.tail())
        # normalizing
        self.df['suggester'] = self.df['suggester'].str.lower()
        self.df['suggester'] = self.df['suggester'].str.strip()
        self.no_sugg_df = self.df.loc[none_idx]
        return
    
    def special_cases(self):
        # Things
        idx = self.df['suggester'].str.contains('thingsare', na=False) 
        print(f"Found {len(idx)} instances for ThingAre<Something>")
        self.df.loc[idx,'suggester'] = 'thingsare'
        return

    def persist_data(self):
        """ Persists processed csv """
        if self.outdir:
            self.df.to_csv(self.outdir + "suggesters.csv", index=False)
            self.no_sugg_df.to_csv(self.outdir + "no_suggester.csv", index=False)
        else:
            print("No output directory selected")
        return

    def get_top_suggesters(self, n_top=25):
        self.top_sug_df = self.df.groupby('suggester').size().sort_values(ascending=False)
        head_df = self.top_sug_df.head(n_top)
        self.top_suggesters = head_df.index.to_list()
        print(head_df)
        total = self.top_sug_df.sum()
        print("Total grouped sketches", total)
        if self.outdir:
            self.top_sug_df.to_csv(self.outdir + "top_suggesters.csv")

    def suggester_heatmap(self, freq='QE', suggester_slice=[]):
        heat_df = self.df
        if suggester_slice:
            print(heat_df)
            mask = self.df['suggester'].isin(suggester_slice)
            heat_df = self.df[mask]
            
        grouper = pd.Grouper(key='date', freq=freq)
        grp = heat_df.groupby([grouper, 'suggester'])
        # print(grp.size().reset_index(name='count'))
        wide_df = grp.size().reset_index(name='count').pivot(
                index="suggester", columns="date", values='count'
                ).fillna(0)
        wide_df = wide_df.reindex(suggester_slice)
        # print(wide_df)

        data = wide_df.values
        rows, cols = wide_df.shape
        dates = mdates.date2num(wide_df.columns)
        dt = dates[1] - dates[0]
        
        fig, ax = plt.subplots(figsize=(12,6))
        im = ax.imshow(data, aspect='auto',
                       extent=[dates.min(), dates.max(), -0.5, data.shape[0] - 0.5],
                       cmap='cividis',
                       norm=PowerNorm(gamma=0.5),
                       interpolation='nearest',
                       origin='lower')
        
        ax.xaxis_date()
        locator = mdates.AutoDateLocator()
        fmtr = mdates.DateFormatter('%Y-%m')

        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(fmtr)
    
        ax.set_yticks(np.arange(rows))
        ax.set_yticklabels(wide_df.index)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        ax.set_title("Suggester heatmap over time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Suggester")
        
        cb = plt.colorbar(im, ax=ax)
        cb.set_label("Number of suggestions")
    
        ax.annotate("By TecBot with ♥ ", xy= (1.05,-0.1),
                xycoords='axes fraction', fontsize=10)
        if not self.outdir:
            plt.show()
        else:
            fig.savefig(self.outdir + "suggesters.png")


if __name__=="__main__":
    args = proc_opts()
    analyzer = PatreonAnalyzer(args.filename, args.outdirectory)
    analyzer.preprocess(args.time_start, args.time_stop)
    if not args.preprocessed:
        analyzer.get_suggester()
        analyzer.special_cases()
        analyzer.persist_data()
    analyzer.get_top_suggesters()
    n_uniq = analyzer.df['suggester'].nunique()
    print(f"Number of unique suggesters: {n_uniq}")
    suggs= analyzer.top_suggesters.extend(['dan vaelling','technic_bot','noxamillion'])
    analyzer.suggester_heatmap(suggester_slice=analyzer.top_suggesters, freq=args.frequency)


