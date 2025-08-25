import pandas as pd
import numpy as np
import os

def read_excel(file_path: str) -> pd.DataFrame:
    try:
        data_path = os.path.join("data/", file_path)
        df = pd.read_excel(data_path)

        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        df = df.map(lambda x: np.nan if isinstance(x, str) and x.strip() == "" else x)
        df = df.replace([999, "999"], np.nan)
        
        return df
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {str(e)}")