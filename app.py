import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import requests
import json
import re
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="PerformX - Employee Performance Tracker",
    page_icon="📊",
    layout="wide",
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .card {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    .ai-insights {
        background-color: #f8f9fa;
        border-left: 4px solid #1E88E5;
        padding: 15px;
        margin: 10px 0;
        color: #333333 !important; /* Force dark text color regardless of theme */
    }
</style>
""", unsafe_allow_html=True)

# Groq API details
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "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")
MODEL = "llama-3.3-70b-versatile"

# Title
st.markdown("<h1 class='main-header'>PerformX - Employee Performance Tracker</h1>", unsafe_allow_html=True)

# Function to extract data from SQLite database
def load_data(db_file):
    try:
        conn = sqlite3.connect(db_file)
        
        # Get list of all tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Create a dictionary to store dataframes
        data_dict = {}
        
        # Load each table into a dataframe
        for table in tables:
            table_name = table[0]
            data_dict[table_name] = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        conn.close()
        return data_dict, None
    except Exception as e:
        return None, str(e)

# Function to analyze employee performance
def analyze_performance(employee_data, metrics_data):
    """
    Analyze employee performance based on available metrics
    This is a simplified version - in a real app, more complex analysis would be done
    """
    # Merge employee data with metrics
    if 'employee_id' in employee_data.columns and 'employee_id' in metrics_data.columns:
        performance_data = pd.merge(
            employee_data, 
            metrics_data, 
            on='employee_id', 
            how='inner'
        )
        
        # Calculate additional metrics (example)
        if 'tasks_completed' in performance_data.columns and 'tasks_assigned' in performance_data.columns:
            performance_data['completion_rate'] = (
                performance_data['tasks_completed'] / performance_data['tasks_assigned']
            ).fillna(0)
            
        if 'working_hours' in performance_data.columns and 'tasks_completed' in performance_data.columns:
            performance_data['productivity'] = (
                performance_data['tasks_completed'] / performance_data['working_hours']
            ).fillna(0)
            
        return performance_data
    else:
        # Return basic employee data if metrics cannot be merged
        return employee_data

# Function to get department performance
def get_department_performance(performance_data):
    if 'department' not in performance_data.columns:
        return None
    
    # Group by department and calculate averages
    dept_performance = performance_data.groupby('department').agg({
        'tasks_completed': 'sum',
        'tasks_assigned': 'sum',
        'working_hours': 'sum',
        'productivity': 'mean',
        'completion_rate': 'mean'
    }).reset_index()
    
    # Calculate department completion rate
    dept_performance['dept_completion_rate'] = (
        dept_performance['tasks_completed'] / dept_performance['tasks_assigned']
    ).fillna(0)
    
    return dept_performance

# Function to query Groq API for AI insights
def query_groq_api(prompt):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from AI.")
    except Exception as e:
        return f"Error querying AI: {str(e)}"

# Function to generate AI performance insights
def generate_ai_insights(employee_data, performance_data, employee_name=None, department=None):
    if employee_name:
        # Filter data for specific employee
        emp_data = performance_data[performance_data['name'] == employee_name]
        
        if emp_data.empty:
            return "No data available for this employee."
        
        # Create prompt for individual employee
        prompt = f"""
        Analyze the following employee's performance:
        
        Name: {employee_name}
        Department: {emp_data.iloc[0].get('department', 'N/A')}
        Position: {emp_data.iloc[0].get('position', 'N/A')}
        
        Performance metrics:
        - Tasks assigned: {emp_data['tasks_assigned'].sum()}
        - Tasks completed: {emp_data['tasks_completed'].sum()}
        - Completion rate: {(emp_data['tasks_completed'].sum() / emp_data['tasks_assigned'].sum() * 100):.1f}%
        - Average working hours: {emp_data['working_hours'].mean():.1f}
        - Average quality score: {emp_data['quality_score'].mean():.2f}/5.0
        - Average review score: {emp_data['review_score'].mean():.2f}/5.0
        
        Provide a concise professional performance analysis with 3-4 specific insights, strengths, and areas for improvement.
        Format your response with bullet points where appropriate. Keep it under 300 words.
        """
        
        return query_groq_api(prompt)
    
    elif department:
        # For department analysis
        dept_data = performance_data[performance_data['department'] == department]
        
        if dept_data.empty:
            return "No data available for this department."
        
        prompt = f"""
        Analyze the following department performance:
        
        Department: {department}
        Number of employees: {len(dept_data['name'].unique())}
        
        Department metrics:
        - Tasks assigned: {dept_data['tasks_assigned'].sum()}
        - Tasks completed: {dept_data['tasks_completed'].sum()}
        - Completion rate: {(dept_data['tasks_completed'].sum() / dept_data['tasks_assigned'].sum() * 100):.1f}%
        - Average working hours: {dept_data['working_hours'].mean():.1f}
        - Average quality score: {dept_data['quality_score'].mean():.2f}/5.0
        - Average review score: {dept_data['review_score'].mean():.2f}/5.0
        
        Provide a concise professional department performance analysis with 3-4 key insights, strengths, and areas for improvement.
        Format your response with bullet points where appropriate. Keep it under 300 words.
        """
        
        return query_groq_api(prompt)
    
    else:
        # For overall performance
        prompt = f"""
        Analyze the following overall company performance:
        
        Number of employees: {len(performance_data['name'].unique())}
        Number of departments: {len(performance_data['department'].unique())}
        
        Overall metrics:
        - Tasks assigned: {performance_data['tasks_assigned'].sum()}
        - Tasks completed: {performance_data['tasks_completed'].sum()}
        - Completion rate: {(performance_data['tasks_completed'].sum() / performance_data['tasks_assigned'].sum() * 100):.1f}%
        - Average working hours: {performance_data['working_hours'].mean():.1f}
        - Average quality score: {performance_data['quality_score'].mean():.2f}/5.0
        - Average review score: {performance_data['review_score'].mean():.2f}/5.0
        
        Provide a concise professional company performance analysis with 3-4 key insights, strengths, and areas for improvement.
        Format your response with bullet points where appropriate. Keep it under 300 words.
        """
        
        return query_groq_api(prompt)
    
# Sidebar for file upload and options
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/data-backup.png", width=80)
    st.markdown("## Upload Database")
    uploaded_file = st.file_uploader("Choose a SQLite database file", type=['db', 'sqlite', 'sqlite3'])
    
    if uploaded_file is not None:
        # Save the uploaded file to a temporary file
        bytes_data = uploaded_file.getvalue()
        db_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(db_path, "wb") as f:
            f.write(bytes_data)
        
        # Load data from the database
        data_dict, error = load_data(db_path)
        
        if error:
            st.error(f"Error loading database: {error}")
        else:
            st.success("Database loaded successfully!")
            
            # Display table selection if multiple tables exist
            table_names = list(data_dict.keys())
            
            st.markdown("## Select Data Tables")
            
            # Check if standard tables exist
            if 'employees' in table_names and 'performance_metrics' in table_names:
                employee_table = 'employees'
                performance_table = 'performance_metrics'
                st.info("Standard tables detected and selected automatically.")
            # Check for CONTACTS/TASKS format
            elif 'CONTACTS' in table_names and 'TASKS' in table_names:
                st.info("CONTACTS/TASKS format detected.")
                # Rename columns to match our expected format
                contacts_df = data_dict['CONTACTS'].copy()
                tasks_df = data_dict['TASKS'].copy()
                
                # Map CONTACTS to employees format
                if 'ID' in contacts_df and 'NAME' in contacts_df:
                    contacts_df = contacts_df.rename(columns={
                        'ID': 'employee_id',
                        'NAME': 'name'
                    })
                    if 'DEPARTMENT' in contacts_df:
                        contacts_df = contacts_df.rename(columns={'DEPARTMENT': 'department'})
                    else:
                        contacts_df['department'] = 'Default'
                    
                    if 'POSITION' not in contacts_df:
                        contacts_df['position'] = 'Unknown'
                    
                    data_dict['employees'] = contacts_df
                
                # Map TASKS to performance_metrics format
                if 'ID' in tasks_df and 'ASSIGNED_TO' in tasks_df:
                    tasks_df = tasks_df.rename(columns={
                        'ASSIGNED_TO': 'employee_id'
                    })
                    
                    # Create metrics based on tasks
                    if 'STATUS' in tasks_df:
                        employee_metrics = []
                        for emp_id in contacts_df['employee_id'].unique():
                            emp_tasks = tasks_df[tasks_df['employee_id'] == emp_id]
                            
                            # Metrics
                            tasks_assigned = len(emp_tasks)
                            tasks_completed = len(emp_tasks[emp_tasks['STATUS'] == 'Completed'])
                            
                            employee_metrics.append({
                                'employee_id': emp_id,
                                'tasks_assigned': tasks_assigned,
                                'tasks_completed': tasks_completed,
                                'working_hours': np.random.randint(160, 180),
                                'quality_score': np.random.uniform(3.0, 5.0),
                                'review_score': np.random.uniform(3.0, 5.0),
                                'month': 'Current',
                                'year': 2025
                            })
                        
                        data_dict['performance_metrics'] = pd.DataFrame(employee_metrics)
                
                employee_table = 'employees'
                performance_table = 'performance_metrics'
            else:
                employee_table = st.selectbox(
                    "Select employee table:",
                    table_names,
                    index=0 if table_names else None
                )
                
                performance_table = st.selectbox(
                    "Select performance metrics table:",
                    table_names,
                    index=min(1, len(table_names)-1) if len(table_names) > 1 else 0
                )
            
            # View options
            st.markdown("## View Options")
            view_mode = st.radio(
                "Select view mode:",
                ["Overview", "Individual Performance", "Department Analysis", "AI Insights"]
            )
            
            # Filtering options
            if employee_table in data_dict and 'department' in data_dict[employee_table].columns:
                departments = ['All'] + sorted(data_dict[employee_table]['department'].unique().tolist())
                selected_department = st.selectbox("Filter by department:", departments)
            else:
                selected_department = 'All'
            
            # AI Insights toggle
            enable_ai = st.checkbox("Enable AI Insights", value=True)
    else:
        st.info("Please upload a SQLite database file (.db)")
        
        # Add demo data button
        if st.button("Load Demo Data"):
            # Create a demo database
            conn = sqlite3.connect("demo_db.db")
            
            # Create employees table
            employees_df = pd.DataFrame({
                'employee_id': range(1, 11),
                'name': [f"Employee {i}" for i in range(1, 11)],
                'department': ['Sales', 'Marketing', 'IT', 'HR', 'Sales', 'Marketing', 'IT', 'Sales', 'HR', 'IT'],
                'position': ['Manager', 'Specialist', 'Developer', 'Recruiter', 'Sales Rep', 'Designer', 'Analyst', 'Sales Rep', 'HR Assistant', 'Developer'],
                'join_date': pd.date_range(start='2020-01-01', periods=10, freq='M')
            })
            
            # Create performance metrics table
            import numpy as np
            np.random.seed(42)
            
            performance_df = pd.DataFrame({
                'employee_id': range(1, 11),
                'tasks_assigned': np.random.randint(10, 50, 10),
                'tasks_completed': [0] * 10,  # Will calculate below
                'working_hours': np.random.randint(160, 200, 10),
                'quality_score': np.random.uniform(3.0, 5.0, 10).round(2),
                'review_score': np.random.uniform(2.5, 5.0, 10).round(2),
                'month': ['March'] * 10,
                'year': [2025] * 10
            })
            
            # Ensure tasks_completed is always <= tasks_assigned
            for i in range(10):
                performance_df.loc[i, 'tasks_completed'] = np.random.randint(
                    performance_df.loc[i, 'tasks_assigned'] // 2,
                    performance_df.loc[i, 'tasks_assigned'] + 1
                )
            
            # Save tables to the database
            employees_df.to_sql('employees', conn, index=False)
            performance_df.to_sql('performance_metrics', conn, index=False)
            
            conn.close()
            
            # Load the demo data
            data_dict, _ = load_data("demo_db.db")
            
            # Set default selections
            table_names = list(data_dict.keys())
            employee_table = 'employees'
            performance_table = 'performance_metrics'
            view_mode = "Overview"
            selected_department = 'All'
            enable_ai = True
            
            st.success("Demo data loaded successfully!")
            st.rerun()

        # Main content area
if 'data_dict' in locals() and data_dict:
    # Process and analyze the data
    if employee_table in data_dict and performance_table in data_dict:
        employee_data = data_dict[employee_table]
        metrics_data = data_dict[performance_table]
        
        # Analyze performance
        performance_data = analyze_performance(employee_data, metrics_data)
        
        # Get department performance
        dept_performance = get_department_performance(performance_data)
        
        # Filter by department if selected
        if selected_department != 'All' and 'department' in performance_data.columns:
            filtered_data = performance_data[performance_data['department'] == selected_department]
        else:
            filtered_data = performance_data
        
        # Display based on selected view mode
        if view_mode == "Overview":
            # Key metrics
            st.markdown("<h2 class='sub-header'>Key Performance Metrics</h2>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                st.metric(
                    "Total Employees", 
                    len(filtered_data)
                )
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col2:
                st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                if 'tasks_completed' in filtered_data.columns and 'tasks_assigned' in filtered_data.columns:
                    completion_rate = (filtered_data['tasks_completed'].sum() / filtered_data['tasks_assigned'].sum()) * 100
                    st.metric(
                        "Task Completion Rate", 
                        f"{completion_rate:.1f}%"
                    )
                else:
                    st.metric("Task Completion Rate", "N/A")
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col3:
                st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                if 'quality_score' in filtered_data.columns:
                    avg_quality = filtered_data['quality_score'].mean()
                    st.metric(
                        "Avg. Quality Score", 
                        f"{avg_quality:.2f}/5.0"
                    )
                else:
                    st.metric("Avg. Quality Score", "N/A")
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col4:
                st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                if 'review_score' in filtered_data.columns:
                    avg_review = filtered_data['review_score'].mean()
                    st.metric(
                        "Avg. Review Score", 
                        f"{avg_review:.2f}/5.0"
                    )
                else:
                    st.metric("Avg. Review Score", "N/A")
                st.markdown("</div>", unsafe_allow_html=True)
                
            # AI Insights
            if enable_ai:
                st.markdown("<h2 class='sub-header'>AI Performance Insights</h2>", unsafe_allow_html=True)
                with st.spinner("Generating AI insights..."):
                    ai_insights = generate_ai_insights(employee_data, filtered_data)
                    st.markdown(f"<div class='ai-insights'>{ai_insights}</div>", unsafe_allow_html=True)
            
            # Department comparison
            if dept_performance is not None:
                st.markdown("<h2 class='sub-header'>Department Performance</h2>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    fig = px.bar(
                        dept_performance,
                        x='department',
                        y='dept_completion_rate',
                        title='Task Completion Rate by Department',
                        labels={'dept_completion_rate': 'Completion Rate', 'department': 'Department'},
                        color='department',
                        color_discrete_sequence=px.colors.qualitative.Plotly,
                        text_auto='.1%'
                    )
                    fig.update_traces(texttemplate='%{text}', textposition='outside')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    fig = px.pie(
                        dept_performance,
                        names='department',
                        values='tasks_completed',
                        title='Tasks Completed by Department',
                        color='department',
                        color_discrete_sequence=px.colors.qualitative.Plotly,
                        hole=0.4
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Top performers
            st.markdown("<h2 class='sub-header'>Top Performers</h2>", unsafe_allow_html=True)
            
            if 'productivity' in filtered_data.columns:
                top_employees = filtered_data.sort_values('productivity', ascending=False).head(5)
                
                if 'name' in top_employees.columns:
                    fig = px.bar(
                        top_employees,
                        x='name',
                        y='productivity',
                        title='Top 5 Employees by Productivity',
                        labels={'productivity': 'Productivity (Tasks/Hour)', 'name': 'Employee'},
                        color='productivity',
                        color_continuous_scale='Blues',
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Full employee table
            st.markdown("<h2 class='sub-header'>Employee Performance Data</h2>", unsafe_allow_html=True)
            st.dataframe(filtered_data, use_container_width=True)
            
        elif view_mode == "Individual Performance":
            st.markdown("<h2 class='sub-header'>Individual Performance Analysis</h2>", unsafe_allow_html=True)
            
            # Employee selector
            if 'name' in filtered_data.columns:
                employees = filtered_data['name'].tolist()
                selected_employee = st.selectbox("Select Employee:", employees)
                
                # Filter data for selected employee
                if selected_employee:
                    employee_row = filtered_data[filtered_data['name'] == selected_employee].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Employee details
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        st.markdown(f"### {employee_row['name']}")
                        
                        detail_cols = ['employee_id', 'department', 'position', 'join_date']
                        for col in detail_cols:
                            if col in employee_row:
                                st.write(f"**{col.replace('_', ' ').title()}:** {employee_row[col]}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        # Performance metrics
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        st.markdown("### Performance Metrics")
                        
                        metric_cols = ['tasks_completed', 'tasks_assigned', 'working_hours', 'quality_score', 'review_score']
                        for col in metric_cols:
                            if col in employee_row:
                                st.write(f"**{col.replace('_', ' ').title()}:** {employee_row[col]}")
                        
                        if 'completion_rate' in employee_row:
                            st.write(f"**Completion Rate:** {employee_row['completion_rate']*100:.1f}%")
                        
                        if 'productivity' in employee_row:
                            st.write(f"**Productivity:** {employee_row['productivity']:.2f} tasks/hour")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # AI Insights for this employee
                    if enable_ai:
                        st.markdown("<h3 class='sub-header'>AI Performance Assessment</h3>", unsafe_allow_html=True)
                        with st.spinner("Generating AI insights..."):
                            ai_insights = generate_ai_insights(employee_data, filtered_data, employee_name=selected_employee)
                            st.markdown(f"<div class='ai-insights'>{ai_insights}</div>", unsafe_allow_html=True)
                    
                    # Performance visualization
                    st.markdown("<h3 class='sub-header'>Performance Visualization</h3>", unsafe_allow_html=True)
                    
                    if 'completion_rate' in employee_row and 'productivity' in employee_row:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Task completion gauge
                            st.markdown("<div class='card'>", unsafe_allow_html=True)
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=employee_row['completion_rate'] * 100,
                                title={'text': "Task Completion Rate"},
                                gauge={
                                    'axis': {'range': [0, 100]},
                                    'bar': {'color': "royalblue"},
                                    'steps': [
                                        {'range': [0, 50], 'color': "lightgray"},
                                        {'range': [50, 75], 'color': "gray"},
                                        {'range': [75, 100], 'color': "lightblue"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': 90
                                    }
                                }
                            ))
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        with col2:
                            # Productivity comparison
                            st.markdown("<div class='card'>", unsafe_allow_html=True)
                            avg_productivity = filtered_data['productivity'].mean()
                            
                            fig = go.Figure()
                            
                            fig.add_trace(go.Bar(
                                x=['Employee', 'Department Avg'],
                                y=[employee_row['productivity'], avg_productivity],
                                text=[f"{employee_row['productivity']:.2f}", f"{avg_productivity:.2f}"],
                                textposition='auto',
                                marker_color=['royalblue', 'lightgray']
                            ))
                            
                            fig.update_layout(
                                title="Productivity Comparison",
                                xaxis_title="",
                                yaxis_title="Tasks per Hour",
                                height=300
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Additional performance analysis if month/year data available
                    if 'month' in filtered_data.columns and 'year' in filtered_data.columns:
                        employee_history = filtered_data[filtered_data['name'] == selected_employee]
                        
                        if len(employee_history) > 1:
                            st.markdown("<h3 class='sub-header'>Performance Trends</h3>", unsafe_allow_html=True)
                            
                            # Create period labels for consistent ordering
                            employee_history['period'] = employee_history.apply(
                                lambda x: f"{x['month']} {x['year']}", axis=1
                            )
                            
                            # Sort by year and month
                            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                                          'July', 'August', 'September', 'October', 'November', 'December']
                            employee_history['month_idx'] = employee_history['month'].apply(lambda x: month_order.index(x) if x in month_order else -1)
                            employee_history = employee_history.sort_values(by=['year', 'month_idx'])
                            
                            # Create trend chart
                            fig = px.line(
                                employee_history,
                                x='period',
                                y=['tasks_assigned', 'tasks_completed'],
                                title='Task Assignment and Completion Trend',
                                labels={'value': 'Count', 'period': 'Period', 'variable': 'Metric'},
                                markers=True,
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Quality and review score trends
                            if 'quality_score' in employee_history.columns and 'review_score' in employee_history.columns:
                                fig = px.line(
                                    employee_history,
                                    x='period',
                                    y=['quality_score', 'review_score'],
                                    title='Quality and Review Score Trend',
                                    labels={'value': 'Score', 'period': 'Period', 'variable': 'Metric'},
                                    markers=True,
                                )
                                fig.update_layout(yaxis_range=[0, 5])
                                st.plotly_chart(fig, use_container_width=True)

        elif view_mode == "Department Analysis":
            st.markdown("<h2 class='sub-header'>Department Analysis</h2>", unsafe_allow_html=True)
            
            # Department comparison
            if dept_performance is not None:
                # Department metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                    st.metric(
                        "Total Departments", 
                        len(dept_performance)
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                    if 'dept_completion_rate' in dept_performance:
                        best_dept = dept_performance.loc[dept_performance['dept_completion_rate'].idxmax()]
                        st.metric(
                            "Best Performing Dept", 
                            f"{best_dept['department']}"
                        )
                    else:
                        st.metric("Best Performing Dept", "N/A")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col3:
                    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                    if 'tasks_completed' in dept_performance:
                        most_productive = dept_performance.loc[dept_performance['tasks_completed'].idxmax()]
                        st.metric(
                            "Most Productive Dept", 
                            f"{most_productive['department']}"
                        )
                    else:
                        st.metric("Most Productive Dept", "N/A")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Department visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    if 'dept_completion_rate' in dept_performance:
                        fig = px.bar(
                            dept_performance,
                            x='department',
                            y='dept_completion_rate',
                            title='Task Completion Rate by Department',
                            labels={'dept_completion_rate': 'Completion Rate', 'department': 'Department'},
                            color='department',
                            text_auto='.1%'
                        )
                        fig.update_traces(texttemplate='%{text}', textposition='outside')
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    if 'working_hours' in dept_performance and 'tasks_completed' in dept_performance:
                        # Calculate department productivity
                        dept_performance['dept_productivity'] = dept_performance['tasks_completed'] / dept_performance['working_hours']
                        
                        fig = px.bar(
                            dept_performance,
                            x='department',
                            y='dept_productivity',
                            title='Productivity by Department (Tasks per Hour)',
                            labels={'dept_productivity': 'Productivity', 'department': 'Department'},
                            color='department',
                            text_auto='.2f'
                        )
                        fig.update_traces(texttemplate='%{text}', textposition='outside')
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # AI Insights for selected department
                if enable_ai and selected_department != 'All':
                    st.markdown("<h3 class='sub-header'>AI Department Analysis</h3>", unsafe_allow_html=True)
                    with st.spinner("Generating AI insights..."):
                        ai_insights = generate_ai_insights(employee_data, filtered_data, department=selected_department)
                        st.markdown(f"<div class='ai-insights'>{ai_insights}</div>", unsafe_allow_html=True)
                
                # Department staffing
                if 'department' in employee_data.columns:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    dept_counts = employee_data['department'].value_counts().reset_index()
                    dept_counts.columns = ['department', 'count']
                    
                    fig = px.pie(
                        dept_counts,
                        names='department',
                        values='count',
                        title='Employee Distribution by Department',
                        color='department',
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Department data table
                st.markdown("<h3 class='sub-header'>Department Performance Data</h3>", unsafe_allow_html=True)
                st.dataframe(dept_performance, use_container_width=True)
        
        elif view_mode == "AI Insights":
            st.markdown("<h2 class='sub-header'>AI Performance Insights</h2>", unsafe_allow_html=True)
            
            # Create tabs for different AI insights
            tabs = st.tabs(["Overall Insights", "Department Insights", "Custom Query"])
            
            with tabs[0]:
                st.subheader("Company Performance Summary")
                with st.spinner("Generating AI insights..."):
                    ai_insights = generate_ai_insights(employee_data, filtered_data)
                    st.markdown(f"<div class='ai-insights'>{ai_insights}</div>", unsafe_allow_html=True)
                    
                # Show key charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Completion rate by department
                    if dept_performance is not None and 'dept_completion_rate' in dept_performance:
                        fig = px.bar(
                            dept_performance,
                            x='department',
                            y='dept_completion_rate',
                            title='Task Completion Rate by Department',
                            labels={'dept_completion_rate': 'Completion Rate', 'department': 'Department'},
                            color='department',
                            text_auto='.1%'
                        )
                        fig.update_traces(texttemplate='%{text}', textposition='outside')
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Employee distribution
                    if 'department' in employee_data.columns:
                        dept_counts = employee_data['department'].value_counts().reset_index()
                        dept_counts.columns = ['department', 'count']
                        
                        fig = px.pie(
                            dept_counts,
                            names='department',
                            values='count',
                            title='Employee Distribution by Department',
                            color='department',
                            hole=0.4
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            with tabs[1]:
                st.subheader("Department-Specific Insights")
                if 'department' in employee_data.columns:
                    dept_list = sorted(employee_data['department'].unique().tolist())
                    selected_dept = st.selectbox("Select Department for Analysis:", dept_list)
                    
                    if selected_dept:
                        with st.spinner(f"Analyzing {selected_dept} department..."):
                            dept_filtered_data = performance_data[performance_data['department'] == selected_dept]
                            dept_ai_insights = generate_ai_insights(employee_data, dept_filtered_data, department=selected_dept)
                            st.markdown(f"<div class='ai-insights'>{dept_ai_insights}</div>", unsafe_allow_html=True)
                        
                        # Department employee table
                        st.subheader(f"Employees in {selected_dept}")
                        dept_employees = dept_filtered_data[['name', 'position', 'tasks_assigned', 'tasks_completed', 'quality_score', 'review_score']]
                        st.dataframe(dept_employees, use_container_width=True)
                        
                        # Performance charts
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Top performers in department
                            if 'productivity' in dept_filtered_data.columns and 'name' in dept_filtered_data.columns:
                                top_dept_employees = dept_filtered_data.sort_values('productivity', ascending=False).head(5)
                                
                                fig = px.bar(
                                    top_dept_employees,
                                    x='name',
                                    y='productivity',
                                    title=f'Top Performers in {selected_dept}',
                                    color='productivity',
                                    color_continuous_scale='Blues',
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Quality score distribution
                            if 'quality_score' in dept_filtered_data.columns:
                                fig = px.histogram(
                                    dept_filtered_data,
                                    x='quality_score',
                                    title=f'Quality Score Distribution in {selected_dept}',
                                    labels={'quality_score': 'Quality Score'},
                                    color_discrete_sequence=['royalblue'],
                                    nbins=10
                                )
                                st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Department information not available in the data.")
            
            with tabs[2]:
                st.subheader("Custom Performance Query")
                query = st.text_area("Enter your performance analysis question:", 
                                    placeholder="E.g., What are the strengths and weaknesses of the Engineering department?")
                
                if query:
                    # Create a context-rich prompt with available data
                    with st.spinner("Analyzing your query..."):
                        # Create a data summary to provide context
                        data_summary = f"""
                        Number of employees: {len(employee_data)}
                        Departments: {', '.join(employee_data['department'].unique())}
                        
                        Performance metrics available: {', '.join(metrics_data.columns)}
                        
                        Key performance indicators:
                        - Average completion rate: {(performance_data['tasks_completed'].sum() / performance_data['tasks_assigned'].sum() * 100):.1f}%
                        - Average quality score: {performance_data['quality_score'].mean():.2f}/5.0
                        """
                        
                        # Create the prompt
                        custom_prompt = f"""
                        Analyze the following performance query about our company:
                        
                        Query: {query}
                        
                        Context:
                        {data_summary}
                        
                        Provide a well-reasoned response based on the available data. Be specific and factual.
                        Format your response with clear sections and bullet points where appropriate.
                        """
                        
                        custom_response = query_groq_api(custom_prompt)
                        st.markdown(f"<div class='ai-insights'>{custom_response}</div>", unsafe_allow_html=True)
    else:
        st.error("Selected tables not found in the database.")