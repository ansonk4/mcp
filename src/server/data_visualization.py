import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
import base64


def register_tools(mcp: FastMCP):
    
    @mcp.tool()
    def visualize_column_distribution(
        distribution_data: str,
        chart_type: str = "bar",
        title: str = "Column Distribution",
        x_label: str = "Categories",
        y_label: str = "Values",
        color: str = "#1f77b4"
    ) -> Dict[str, Any]:
        """
        Create a chart from column distribution data.
        
        Args:
            distribution_data: JSON string containing the distribution data
            chart_type: Type of chart ("bar", "pie", "line")
            title: Chart title
            x_label: Label for x-axis
            y_label: Label for y-axis
            color: Color for the chart elements (hex code or name)
            
        Returns:
            Dict with base64 encoded PNG image
        """
        try:
            # Parse the distribution data
            distribution = json.loads(distribution_data)
            
            # Extract keys and values
            labels = list(distribution.keys())
            values = list(distribution.values())
            
            # Create the chart based on type
            if chart_type == "bar":
                fig = go.Figure(data=[go.Bar(
                    x=labels,
                    y=values,
                    marker_color=color
                )])
                fig.update_layout(
                    title=title,
                    xaxis_title=x_label,
                    yaxis_title=y_label
                )
            elif chart_type == "pie":
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values
                )])
                fig.update_layout(title=title)
            elif chart_type == "line":
                fig = go.Figure(data=go.Scatter(
                    x=labels,
                    y=values,
                    mode='lines+markers',
                    line=dict(color=color)
                ))
                fig.update_layout(
                    title=title,
                    xaxis_title=x_label,
                    yaxis_title=y_label
                )
            else:
                return {"error": f"Unsupported chart type: {chart_type}"}
            
            # Convert to base64 PNG
            img_bytes = fig.to_image(format="png")
            encoded = base64.b64encode(img_bytes).decode('utf-8')
            
            return {"image": encoded}
            
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON format in distribution_data: {str(e)}"}
        except Exception as e:
            return {"error": f"Error creating chart: {str(e)}"}


    @mcp.tool()
    def visualize_binary_distribution(
        binary_data: str,
        chart_type: str = "bar",
        title: str = "Binary Distribution",
        x_label: str = "Columns",
        y_label: str = "Proportion",
        color: str = "#1f77b4"
    ) -> Dict[str, Any]:
        """
        Create a chart from binary distribution data.
        
        Args:
            binary_data: JSON string containing the binary distribution data
            chart_type: Type of chart ("bar", "pie", "line")
            title: Chart title
            x_label: Label for x-axis
            y_label: Label for y-axis
            color: Color for the chart elements (hex code or name)
            
        Returns:
            Dict with base64 encoded PNG image
        """
        try:
            # Parse the binary distribution data
            data = json.loads(binary_data)
            
            # Extract keys and values
            labels = list(data.keys())
            values = list(data.values())
            
            # Create the chart based on type
            if chart_type == "bar":
                fig = go.Figure(data=[go.Bar(
                    x=labels,
                    y=values,
                    marker_color=color
                )])
                fig.update_layout(
                    title=title,
                    xaxis_title=x_label,
                    yaxis_title=y_label
                )
            elif chart_type == "pie":
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values
                )])
                fig.update_layout(title=title)
            elif chart_type == "line":
                fig = go.Figure(data=go.Scatter(
                    x=labels,
                    y=values,
                    mode='lines+markers',
                    line=dict(color=color)
                ))
                fig.update_layout(
                    title=title,
                    xaxis_title=x_label,
                    yaxis_title=y_label
                )
            else:
                return {"error": f"Unsupported chart type: {chart_type}"}
            
            # Convert to base64 PNG
            img_bytes = fig.to_image(format="png")
            encoded = base64.b64encode(img_bytes).decode('utf-8')
            
            return {"image": encoded}
            
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON format in binary_data: {str(e)}"}
        except Exception as e:
            return {"error": f"Error creating chart: {str(e)}"}


    @mcp.tool()
    def visualize_combined_distribution(
        combined_data: str,
        chart_type: str = "bar",
        title: str = "Combined Distribution",
        x_label: str = "Categories",
        y_label: str = "Values",
        color: str = "#1f77b4"
    ) -> Dict[str, Any]:
        """
        Create a chart from combined distribution data.
        
        Args:
            combined_data: JSON string containing the combined distribution data
            chart_type: Type of chart ("bar", "pie", "line")
            title: Chart title
            x_label: Label for x-axis
            y_label: Label for y-axis
            color: Color for the chart elements (hex code or name)
            
        Returns:
            Dict with base64 encoded PNG image
        """
        try:
            # Parse the combined distribution data
            data = json.loads(combined_data)
            
            # Extract keys and values
            labels = list(data.keys())
            values = list(data.values())
            
            # Create the chart based on type
            if chart_type == "bar":
                fig = go.Figure(data=[go.Bar(
                    x=labels,
                    y=values,
                    marker_color=color
                )])
                fig.update_layout(
                    title=title,
                    xaxis_title=x_label,
                    yaxis_title=y_label
                )
            elif chart_type == "pie":
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values
                )])
                fig.update_layout(title=title)
            elif chart_type == "line":
                fig = go.Figure(data=go.Scatter(
                    x=labels,
                    y=values,
                    mode='lines+markers',
                    line=dict(color=color)
                ))
                fig.update_layout(
                    title=title,
                    xaxis_title=x_label,
                    yaxis_title=y_label
                )
            else:
                return {"error": f"Unsupported chart type: {chart_type}"}
            
            # Convert to base64 PNG
            img_bytes = fig.to_image(format="png")
            encoded = base64.b64encode(img_bytes).decode('utf-8')
            
            return {"image": encoded}
            
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON format in combined_data: {str(e)}"}
        except Exception as e:
            return {"error": f"Error creating chart: {str(e)}"}


    @mcp.tool()
    def compare_distributions(
        distribution1: str,
        distribution2: str,
        label1: str = "Distribution 1",
        label2: str = "Distribution 2",
        title: str = "Distribution Comparison",
        x_label: str = "Categories",
        y_label: str = "Values"
    ) -> Dict[str, Any]:
        """
        Create a comparison chart from two distribution datasets.
        
        Args:
            distribution1: JSON string containing the first distribution data
            distribution2: JSON string containing the second distribution data
            label1: Label for the first distribution
            label2: Label for the second distribution
            title: Chart title
            x_label: Label for x-axis
            y_label: Label for y-axis
            
        Returns:
            Dict with base64 encoded PNG image
        """
        try:
            # Parse the distribution data
            data1 = json.loads(distribution1)
            data2 = json.loads(distribution2)
            
            # Get all unique keys from both distributions
            all_keys = set(data1.keys()) | set(data2.keys())
            sorted_keys = sorted(all_keys)
            
            # Extract values for each distribution, using 0 for missing keys
            values1 = [data1.get(key, 0) for key in sorted_keys]
            values2 = [data2.get(key, 0) for key in sorted_keys]
            
            # Create the comparison bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sorted_keys,
                y=values1,
                name=label1
            ))
            fig.add_trace(go.Bar(
                x=sorted_keys,
                y=values2,
                name=label2
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title=x_label,
                yaxis_title=y_label,
                barmode='group'
            )
            
            # Convert to base64 PNG
            img_bytes = fig.to_image(format="png")
            encoded = base64.b64encode(img_bytes).decode('utf-8')
             
            return {"image": encoded}
            
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON format in distribution data: {str(e)}"}
        except Exception as e:
            return {"error": f"Error creating comparison chart: {str(e)}"}