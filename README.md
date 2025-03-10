# PerformX - Employee Performance Tracker

PerformX is a powerful, interactive dashboard for analyzing employee performance data. Built with Streamlit and enhanced with AI-powered insights, it provides a comprehensive view of individual and team performance metrics.

![PerformX Dashboard](https://img.icons8.com/fluency/96/000000/data-backup.png)

## Features

- **Interactive Dashboard**: Visualize performance metrics with dynamic charts and tables
- **Multi-view Interface**: Navigate between Overview, Individual Performance, Department Analysis, and AI Insights
- **AI-Powered Analysis**: Get intelligent insights on performance data using the Groq LLM API
- **Flexible Data Import**: Upload SQLite databases with employee performance data 
- **Database Compatibility**: Works with both standard format and CONTACTS/TASKS format databases
- **Demo Data Generator**: Try the app with automatically generated sample data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/performx.git
cd performx
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Set up your Groq API key:
   - Create a `.streamlit/secrets.toml` file
   - Add your API key: `GROQ_API_KEY = "your-api-key-here"`

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Upload a database file or use the "Load Demo Data" button
3. Navigate through different views using the sidebar options
4. Filter data by department if needed
5. Enable or disable AI insights based on your preference

## Database Structure

The application expects a SQLite database with at least two tables:

1. **employees**: containing employee information
   - employee_id
   - name
   - department
   - position
   - join_date (optional)

2. **performance_metrics**: containing performance data
   - employee_id
   - tasks_assigned
   - tasks_completed
   - working_hours
   - quality_score
   - review_score
   - month (optional)
   - year (optional)

Alternatively, it can work with CONTACTS/TASKS format:
- CONTACTS (ID, NAME, DEPARTMENT, etc.)
- TASKS (ID, ASSIGNED_TO, STATUS, etc.)

## Views

### Overview
Shows key performance metrics, department comparisons, and top performers across the organization.

### Individual Performance
Provides detailed analysis of specific employees, including performance metrics, visualizations, and AI-powered assessments.

### Department Analysis
Compares performance across departments with metrics like completion rates, productivity, and staffing distribution.

### AI Insights
Dedicated view for AI-powered analysis including:
- Overall company performance
- Department-specific insights
- Custom performance queries

## Requirements

- Python 3.8+
- Streamlit 1.31.0+
- Pandas 2.0.0+
- Plotly 5.13.0+
- NumPy 1.22.0+
- Requests library for API integration
- Groq API key

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
