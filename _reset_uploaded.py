from pathlib import Path

import pandas as pd

from __table import C_IS_UPLOADED


def __reset_all_uploaded_to_false():
    print('!!! This should not be used in production !!!')
    df_file = 'data/scrap/products.csv'
    try:
        if Path(df_file).exists():
            df = pd.read_csv(df_file)
            df[C_IS_UPLOADED] = False
            df.to_csv(df_file, index=False)
            print(df[C_IS_UPLOADED])

    except FileNotFoundError:
        pass


if __name__ == '__main__':
    __reset_all_uploaded_to_false()
