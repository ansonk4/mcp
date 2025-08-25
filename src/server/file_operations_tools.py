import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
from utils import read_excel

def register_tools(mcp: FastMCP):


    @mcp.tool()
    def list_available_files() -> Dict[str, Any]:
        """
        Lists all available files in the 'data/' directory.

        Returns:
            Dict[str, Any]: Dictionary containing a list of file names.
        """
        try:
            data_dir = Path("data")
            if not data_dir.exists() or not data_dir.is_dir():
                return {"error": "'data/' directory does not exist."}
            files = [f"{f.name}" for f in data_dir.iterdir() if f.is_file()]
            return {"files": files}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_excel_columns(file_path: str) -> Dict[str, Any]:
        """
        Returns a list of all column names in the given Excel file.

        Args:
            file_path (str): Path to the Excel file.

        Returns:
            List[str]: List of column names.
        """
        try:
            df = read_excel(file_path)
            return {"columns": df.columns.tolist()}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_columns_stats(
        file_path: str,
        column_name: str | None = None,
    ) -> Dict[str, Any]:
        """
        Get statistics of columns in an Excel file.

        Args:
            file_path (str): Path to the Excel file.

        Returns:
            Dict[str, Any]: Dictionary containing column statistics.
        """
        try:
            df = read_excel(file_path)
            df = df if column_name is None else df[[column_name]]   
            stats = {
                "length": len(df),
                "mean": df.mean().to_dict(),
                "std": df.std().to_dict(),
                "min": df.min().to_dict(),
                "max": df.max().to_dict(),
            }
            return {"stats": stats}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_column_unique_values(file_path: str, column_name: str) -> Dict[str, Any]:
        """
        Get unique values of a specific column in an Excel file.

        Args:
            file_path (str): Path to the Excel file.
            column_name (str): Name of the column to get unique values from.

        Returns:
            Dict[str, Any]: Dictionary containing unique values of the column.
        """
        try:
            df = read_excel(file_path)
            if column_name not in df.columns:
                return {"error": f"Column '{column_name}' does not exist."}
            unique_values = df[column_name].unique().tolist()
            return {"unique_values": unique_values}
        except Exception as e:
            return {"error": str(e)}

