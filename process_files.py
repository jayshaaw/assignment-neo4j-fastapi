import os
import pandas as pd


def process_files(file_name, landing_folder, processed_folder):
    print("Processing file: {}".format(file_name))
    df = pd.read_table(str(landing_folder) + str(file_name))
    cols = df.columns.values[0]
    df.rename(columns={df.columns.values[0]: 'columns'}, inplace=True)
    df = (df['columns']).str.split(pat=',', expand=True)
    df = df.dropna(axis=1)
    col_dict = {i: j for i, j in zip(list(range(18)), pd.Series(cols).str.split(',')[0])}
    df.rename(columns=col_dict, inplace=True)
    df.head(2)
    df.to_csv(str(processed_folder) + str('processed-') + str(file_name))


if __name__ == '__main__':
    file_list = os.listdir('landing-folder/')

    for file in file_list:
        process_files(file, 'landing-folder/', 'processed-folder/')
    print("Processing complete")
