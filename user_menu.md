# MCP Data Analysis Assistant - User Guide

Welcome to the MCP Data Analysis Assistant! This guide will help you understand how to interact with the system and make the most of its capabilities.

## Getting Started

When you first connect to the assistant, it will:
1. Greet you and introduce itself
2. List all available Excel files in the `data/` directory
3. Ask you to choose a file for analysis

## Basic Usage

You can interact with the assistant using natural language. You don't need to know specific commands - just describe what you want to do with your data.

Examples of things you can ask:
- "Show me the columns in [file name]"
- "What's the distribution in [column name]?"
- "What's the distribution in [column name1] filterd by [column name2] = [filter value] ?
- "Create a [ bar/pie/line ] chart showing [some data]"
- "Compare the distribution in these columns: [column1, column2, column3]"
- "What values exist in [column name]"
- "Give me statistics for [column name]"

### Important: Working with Multiple Related Columns

For data where information is spread across several related columns (e.g., **希望修讀, 希望修讀_A, 希望修讀_B**), use the keyword `combined distribution` instead of `distribution` to analyze them together.

**Example:**
```
User: What is the combined distribution of 希望修讀, 希望修讀_A, 希望修讀_B?
Model: [Provides combined distribution data]
User: Plot a bar chart with the top 5 majors based on the above distribution
Model: [Provides bar chart visualization]
```
This approach helps you see overall trends and rankings across multiple columns representing similar data.



## Advanced Usage

### Chaining Multiple Commands

You can ask the assistant to perform complex multi-step analyses by chaining commands together:

1. **Combined Distributions Across Files**:
   ```
   User: Give me the [column] distribution from 2025.xlsx and 2024.xlsx to show overall trends
   Model: ...
   User: Plot a graph compare two year distribution
   ```

### Advanced Filtering and Analysis

1. **Multiple Conduction**:
    ```
    User: Show me the distirbution of 中文成績 for all male student with school id = 10.
    ```

2. **Exclusion Analysis**:
   ```
   User: Show the distribution of [column], but exclude any 'N/A' responses.
   ```

3. **Normalized vs Raw Data**:
   ```
   User: Show me both the raw counts and normalized percentages for the [column] distribution.
   ```

### Cross-file Analysis

1. **Comparing Multiple Files**:
   ```
   User: Compare the [columns] in customer_data_jan.xlsx with customer_data_feb.xlsx.
   ```

## Available Tools

The assistant has access to the following tools that it can use automatically to analyze your data, key to include the tools name your prompt to help to model select the correct tools:

### File Operations Tools

1. **list_available_files()**
   - Lists all Excel files in the `data/` directory
   - Used automatically when you first connect

2. **get_excel_columns(file_path)**
   - Returns all column names in a specified Excel file
   - Example: "What columns are in survey_data.xlsx?"

3. **get_columns_stats(file_path, column_name)**
   - Provides statistics (mean, std, min, max) for numerical columns
   - Example: "What are the statistics for the age column?"

4. **get_column_unique_values(file_path, column_name)**
   - Lists all unique values in a specified column
   - Example: "What are all the unique responses in the gender column?"

### Data Analysis Tools

1. **get_column_distribution(file_path, column_name, filter_column, filter_value, normalize, exclude)**
   - Analyzes the distribution of values in a column
   - Can filter data, normalize results, and exclude specific values
   - Example: "Show the distribution of responses in the satisfaction column"

2. **get_binary_distribution(columns, value, unique, filter_column, filter_value)**
   - Analyzes binary (yes/no or 0/1) distributions across multiple columns
   - Example: "Show which features are most commonly used (value=1)"

3. **get_combined_distribution(file_path, columns, filtered_column, filter_value)**
   - Combines distributions from multiple related columns
   - Useful for questions with the same response options across multiple items
   - Example: "Combine the distributions for all the satisfaction questions"

### Data Visualization Tools

1. **visualize_column_distribution(distribution_data, chart_type, title, x_label, y_label, color)**
   - Creates charts from distribution data
   - Chart types: "bar", "pie", "line"
   - Example: "Create a bar chart of the age distribution"

## Best Practices

1. **Be Specific**: When referring to files or columns, try to be as specific as possible
2. **Ask One Question at a Time**: For best results, ask one clear question at a time
3. **Follow Up**: If the assistant asks for clarification, provide the requested information
4. **Explore**: Feel free to ask follow-up questions or request alternative visualizations to gain deeper insights.
5. **Retry**: If you encounter errors from the model provider or tools, simply ask the assistant to repeat the task; this often resolves temporary issues.

## Example Conversations

### Example 1: Basic Data Exploration
```
User: What files do you have?
Assistant: I found these files: survey_data.xlsx, customer_data.xlsx
User: Let's look at survey_data.xlsx
Assistant: Here are the columns: age, gender, satisfaction, usage_frequency
User: Show me the distribution of satisfaction ratings
Assistant: [Provides satisfaction distribution data]
User: Can you make a bar chart of that?
Assistant: [Provides bar chart visualization]
```

### Example 2: Filtered Analysis
```
User: I want to analyze customer_data.xlsx
Assistant: I see columns: customer_id, age, region, purchase_amount
User: Show me purchase amounts for customers in the North region
Assistant: [Provides filtered statistics]
User: Create a pie chart showing purchase distribution by age group
Assistant: [Provides pie chart visualization]
```

## Troubleshooting

If you encounter issues:
1. Make sure your Excel files are in the `data/` directory
2. Ensure your files are in .xlsx format
3. Check that column names match exactly (case-sensitive)
4. If the assistant seems stuck, try rephrasing your question


## Need Help?

If you're unsure what to ask, try these starter questions:
- "What files are available?"
- "Show me all columns in [file name]"
- "What's the distribution of [column name]?"
- "What's the combined distribution of [column, column2, column3]?"
- "Create a visualization of [data]"

For more complex tasks, try:
- "Analyze [file name] comprehensively"
- "Show me trends in [data] with visualizations"
- "Compare [column1] and [column2] with charts"
- "Filter [data] by [condition] and analyze the results"