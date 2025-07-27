import json
import pandas as pd
import numpy as np
import argparse

def parser_opts():
  parser = argparse.ArgumentParser(
          description='Processes json files into simpler csvs while doin some basic preprocessing')
  parser.add_argument('file', help='in json file')
  parser.add_argument('outfile', help='output csv file')
  parser.add_argument('--format', help='format to output', default='csv')
  return parser.parse_args()

def preprocess_df(df,drop_chars=False, drop_tags=False):
  print("Got {} entries ".format(len(df)))
  df['creation'] = pd.to_datetime(df['creation'])
  df['update'] = pd.to_datetime(df['update'])
  # do not care about characters in this case
  if drop_chars:
    df.drop('characters', axis=1, inplace=True)
  if drop_tags:
    df.drop('tags', axis=1, inplace=True)
  return df

def clean_df(df):
  twk_df = preprocess_df(df)
  twk_df = remove_comic_pages(twk_df)
  return twk_df
  #twk_df = remove_non_color(twk_df)

def remove_comic_pages(df):
  """
  Remove any entry inside a pool, that is a comic.
  """
 # df = df[~df["pools"].astype(bool)]
  removal_list=[7516]
  exploded = df.explode('pools')
  df_slc = exploded['pools'].isin(removal_list)
  pruned = exploded[~df_slc]  
  pruned.drop_duplicates('id',inplace=True)
  
  # We removed every entry with a pool, remove the column
  print("Trimmmed down to  {} entries ".format(len(pruned)))

  return pruned

def main():
  args=parser_opts()
  df = pd.read_json(args.file)

  df_proc=clean_df(df)
  if args.outfile:
    if args.format == 'json':
      df_proc.to_json(args.outfile,orient='records')
    else:
      df_proc.set_index('id',inplace=True)
      df_proc.to_csv(args.outfile)
  

if __name__=="__main__":
  main()
  
