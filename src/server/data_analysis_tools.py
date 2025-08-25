import pandas as pd
import numpy as np
from typing import List, Dict, Any
from fastmcp import FastMCP
import json
from utils import read_excel

def register_tools(mcp: FastMCP):

    @mcp.tool()
    def get_column_distribution(
        file_path: str,
        column_name: str,
        filter_column: str | None = None,
        filter_value: str | int | None = None,
        normalize: bool = True,
        exclude: float | int | None = None
    ) -> Dict[str, Any]:   
        """
        Get the distribution of a specified column.
        
        Args:
            column_name: Name of the column to analyze
            filter_column: Column to filter by (optional)
            filter_value: Value to filter for (optional)
            normalize: Whether to normalize the distribution
            exclude: Value to exclude from analysis
            
        Returns:
            JSON string containing the distribution
        """
        try:
            data = read_excel(file_path)
            
            # Apply filtering
            if filter_column is not None and filter_value is not None:
                if isinstance(filter_column, str):
                    data = data[data[filter_column] == filter_value]
            
            if len(data) == 0:
                return {"error": f"No rows found after filtering for column {filter_column} == {filter_value}"}
            
            # Apply exclusion
            if exclude is not None:
                data = data[data[column_name] != exclude]
            
            if column_name not in data.columns:
                return {"error": f"Column {column_name} does not exist in the data."}
            
            # Calculate distribution
            data = data.dropna(subset=[column_name])
            distribution = data[column_name].value_counts(normalize=normalize).to_dict()
            distribution = {str(float(k)) if isinstance(k, int) else str(k): v for k, v in distribution.items()}

            return {"distribution": json.dumps(distribution, ensure_ascii=False, indent=2)}

        except Exception as e:
            return {"error": f"Error calculating column distribution: {str(e)}"}



    @mcp.tool()
    def get_binary_distribution(
        columns: str,
        value: int = 1,
        unique: bool = False,
        filter_column: str | None = None,
        filter_value: str | int | None = None
    ) -> Dict[str, Any]:
        """
        Get the binary distribution for specified columns.
        
        Args:
            columns: JSON string list of column names
            value: Target value to count (default: 1)
            unique: Whether to ensure only one target value per row
            filter_column: Column to filter by (optional)
            filter_value: Value to filter for (optional)
            
        Returns:
            JSON string containing the binary distribution
        """
        data = read_excel(file_path)

        try:
            columns_list = json.loads(columns)
            
            # Apply filtering
            if filter_column is not None and filter_value is not None:
                data = data[data[filter_column] == filter_value]
            
            data = data.dropna(subset=columns_list)
            
            if len(data) == 0:
                return {"error": f"No rows found after filtering for column {filter_column} == {filter_value}"}

            result = {}
            
            # Drop rows where more than one target value exists in the specified columns
            if unique:
                target_mask = data[columns_list].apply(
                    lambda row: (pd.to_numeric(row, errors='coerce') == value).sum(), axis=1
                )
                data = data[target_mask <= 1]
            
            for col in columns_list:
                if col not in data.columns:
                    result[col] = 0.0
                else:
                    # Count the number of target values in each column
                    numeric_col = pd.to_numeric(data[col], errors='coerce').fillna(0)
                    count = int((numeric_col == value).sum())
                    result[col] = count / len(data) if len(data) > 0 else 0.0
            
            if unique and sum(result.values()) > 0:
                # Normalize so the sum of result is 1.0
                total = sum(result.values())
                result = {k: v / total for k, v in result.items()}

            return {"result": json.dumps(result, ensure_ascii=False, indent=2)}

        except Exception as e:
            return {"error": f"Error calculating binary distribution: {str(e)}"}


    @mcp.tool()
    def get_combined_distribution(
        file_path: str,
        columns: str,
        filtered_column: str | None = None,
        filter_value: str | int | None = None
    ) -> Dict[str, Any]:
        """
        Get the normalized combined distribution of multiple specified columns, suitable for columns
        from the same question and with the same data type.

        Args:
            columns: JSON string list of column names
            filtered_column: Column to filter by (optional)
            filter_value: Value to filter for (optional)
            
        Returns:
            JSON string containing the combined distribution
        """
        data = read_excel(file_path)

        try:
            columns_list = json.loads(columns)
            
            # Apply filtering
            if filtered_column is not None and filter_value is not None:
                data = data[data[filtered_column] == filter_value]
            
            if len(data) == 0:
                return {"error": f"No rows found after filtering for column {filtered_column} == {filter_value}"}

            result = {}
            total_count = len(data)
            
            for col in columns_list:
                if col in data.columns:
                    distribution = data[col].value_counts().to_dict()
                    for key, value in distribution.items():
                        result[key] = result.get(key, 0) + value
                else:
                    print({"error": f"Column {col} does not exist in the data."})

            if total_count > 0:
                # Normalize the result
                result = {k: v / total_count for k, v in result.items()}
                result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))

            return {"result": json.dumps(result, ensure_ascii=False, indent=2)}

        except Exception as e:
            return {"error": f"Error calculating combined distribution: {str(e)}"}


