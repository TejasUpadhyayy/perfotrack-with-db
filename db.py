import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# File path for the SQLite database
db_file = "performx_test_data.db"

# Create a connection to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print(f"Creating test database: {db_file}")

# Define departments and positions
departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Customer Support", "Product", "Operations"]
positions = {
    "Engineering": ["Software Engineer", "Senior Engineer", "Tech Lead", "QA Engineer", "DevOps Engineer"],
    "Sales": ["Sales Representative", "Account Executive", "Sales Manager", "Business Development", "Sales Analyst"],
    "Marketing": ["Marketing Specialist", "Content Writer", "SEO Specialist", "Social Media Manager", "Brand Manager"],
    "HR": ["HR Coordinator", "Recruiter", "HR Manager", "Benefits Specialist", "Training Coordinator"],
    "Finance": ["Accountant", "Financial Analyst", "Finance Manager", "Bookkeeper", "Payroll Specialist"],
    "Customer Support": ["Support Agent", "Support Manager", "Customer Success", "Technical Support", "Support Lead"],
    "Product": ["Product Manager", "Product Owner", "UX Designer", "Product Analyst", "Technical Writer"],
    "Operations": ["Operations Analyst", "Operations Manager", "Project Coordinator", "Business Analyst", "Admin Assistant"]
}

# Create employees dataframe
num_employees = 50
employee_ids = list(range(1001, 1001 + num_employees))
names_first = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", 
              "David", "Susan", "Richard", "Jessica", "Joseph", "Sarah", "Thomas", "Karen", "Charles", "Nancy",
              "Daniel", "Lisa", "Matthew", "Margaret", "Anthony", "Betty", "Mark", "Sandra", "Donald", "Ashley",
              "Steven", "Dorothy", "Paul", "Kimberly", "Andrew", "Emily", "Joshua", "Donna", "Kenneth", "Michelle",
              "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa", "Edward", "Deborah", "Ronald", "Stephanie"]
names_last = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
             "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
             "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King",
             "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter",
             "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins"]

# Generate random employee data
employee_data = []
for i in range(num_employees):
    emp_id = employee_ids[i]
    first_name = names_first[i % len(names_first)]
    last_name = names_last[i % len(names_last)]
    full_name = f"{first_name} {last_name}"
    
    department = random.choice(departments)
    position = random.choice(positions[department])
    
    # Generate join date between 1-5 years ago
    days_ago = random.randint(365, 365 * 5)
    join_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    
    # Generate random salary based on position and seniority
    base_salary = {
        "Engineering": 85000,
        "Sales": 65000,
        "Marketing": 60000,
        "HR": 55000,
        "Finance": 70000,
        "Customer Support": 50000,
        "Product": 80000,
        "Operations": 60000
    }
    
    # Add seniority bonus (more senior = higher salary)
    seniority_factor = 1 + ((5 * 365 - days_ago) / (5 * 365)) * 0.5
    
    # Add position bonus
    position_bonus = 1
    if "Senior" in position or "Lead" in position or "Manager" in position:
        position_bonus = 1.4
    elif "Specialist" in position or "Analyst" in position:
        position_bonus = 1.2
        
    salary = int(base_salary[department] * seniority_factor * position_bonus)
    
    # Add some random variation
    salary = int(salary * random.uniform(0.9, 1.1))
    
    # Round to nearest thousand
    salary = round(salary / 1000) * 1000
    
    employee_data.append({
        "employee_id": emp_id,
        "name": full_name,
        "department": department,
        "position": position,
        "join_date": join_date,
        "salary": salary,
        "email": f"{first_name.lower()}.{last_name.lower()}@company.com",
        "manager_id": random.choice([e for e in employee_ids if e != emp_id]) if random.random() > 0.2 else None
    })

# Create employees dataframe
employees_df = pd.DataFrame(employee_data)

# Now create performance metrics for the past 6 months
performance_data = []

# Assign some personality traits to make performance data more realistic
employee_traits = {}
for emp_id in employee_ids:
    # Each trait is on a scale of 0-1
    employee_traits[emp_id] = {
        "efficiency": random.uniform(0.6, 1.0),          # How efficiently they work
        "dedication": random.uniform(0.7, 1.0),          # How many tasks they take on
        "quality": random.uniform(0.7, 1.0),             # Quality of their work
        "consistency": random.uniform(0.7, 0.95),        # How consistent their work is
        "improvement": random.uniform(-0.1, 0.1),        # How much they improve month-to-month
    }

months = ["October", "November", "December", "January", "February", "March"]
years = [2024, 2024, 2024, 2025, 2025, 2025]

for month_idx, (month, year) in enumerate(zip(months, years)):
    for emp in employee_data:
        emp_id = emp["employee_id"]
        traits = employee_traits[emp_id]
        
        # Base number of tasks depends on department
        if emp["department"] in ["Engineering", "Product"]:
            base_tasks = random.randint(15, 25)
        elif emp["department"] in ["Sales", "Marketing"]:
            base_tasks = random.randint(20, 35)
        else:
            base_tasks = random.randint(20, 30)
        
        # Modify based on dedication trait and slight monthly variance
        tasks_assigned = int(base_tasks * (0.8 + traits["dedication"] * 0.4) * random.uniform(0.9, 1.1))
        
        # Completion percentage based on efficiency, adjusted by month (improvement)
        completion_pct = min(0.98, traits["efficiency"] + (traits["improvement"] * month_idx))
        tasks_completed = int(tasks_assigned * completion_pct * random.uniform(0.95, 1.0))
        
        # Add some more realistic variation - sometimes people have a bad month
        if random.random() < 0.05:  # 5% chance of a "bad month"
            tasks_completed = int(tasks_completed * random.uniform(0.7, 0.85))
        
        # Working hours - base around 160-180 per month with some variation
        working_hours = round(random.uniform(160, 180) * (0.9 + traits["dedication"] * 0.2))
        
        # Quality score (1-5 scale) based on quality trait
        quality_base = 3.0 + (traits["quality"] * 2.0)
        # Adjust slightly based on month (improvement)
        quality_score = round(min(5.0, quality_base + (traits["improvement"] * month_idx * 1.5)), 1)
        
        # Review score from manager (1-5 scale)
        # More variable than quality since it includes subjective manager assessment
        review_base = 3.0 + (traits["quality"] * 1.8)
        review_score = round(min(5.0, review_base * random.uniform(0.9, 1.1)), 1)
        
        # Revenue generated (only for Sales and Marketing)
        revenue_generated = None
        if emp["department"] in ["Sales", "Marketing"]:
            base_revenue = 15000 if emp["department"] == "Sales" else 8000
            revenue_factor = (0.7 + traits["efficiency"] * 0.6) * (0.8 + traits["dedication"] * 0.4)
            revenue_generated = int(base_revenue * revenue_factor * random.uniform(0.8, 1.3))
            
            # Add some month-to-month growth or seasonal effects
            if month in ["December", "January"]:  # End of year/beginning of year boost
                revenue_generated = int(revenue_generated * random.uniform(1.1, 1.3))
            elif month == "February":  # February dip
                revenue_generated = int(revenue_generated * random.uniform(0.8, 0.9))
        
        # Customer feedback score (only for Customer Support)
        customer_feedback = None
        if emp["department"] == "Customer Support":
            customer_feedback = round(min(5.0, (3.5 + traits["quality"] * 1.5) * random.uniform(0.9, 1.05)), 1)
        
        # Bugs reported/fixed (only for Engineering)
        bugs_fixed = None
        if emp["department"] == "Engineering":
            bugs_fixed = int(tasks_completed * random.uniform(0.2, 0.5) * traits["efficiency"])
        
        performance_data.append({
            "employee_id": emp_id,
            "month": month,
            "year": year,
            "tasks_assigned": tasks_assigned,
            "tasks_completed": tasks_completed,
            "working_hours": working_hours,
            "quality_score": quality_score,
            "review_score": review_score,
            "revenue_generated": revenue_generated,
            "customer_feedback": customer_feedback,
            "bugs_fixed": bugs_fixed
        })

# Create performance dataframe
performance_df = pd.DataFrame(performance_data)

# Create a skills table
skills = ["Python", "JavaScript", "React", "SQL", "Project Management", "Data Analysis", 
          "Public Speaking", "Customer Service", "Sales", "Marketing", "Content Writing",
          "Leadership", "Budgeting", "UX Design", "DevOps", "Cloud Services",
          "Machine Learning", "Communication", "Problem Solving", "Team Collaboration"]

employee_skills = []
for emp in employee_data:
    # Decide how many skills (2-6)
    num_skills = random.randint(2, 6)
    
    # For managers and senior positions, add more skills
    if "Manager" in emp["position"] or "Senior" in emp["position"] or "Lead" in emp["position"]:
        num_skills += random.randint(1, 3)
    
    # Assign relevant skills based on department, plus some random ones
    relevant_skills = []
    if emp["department"] == "Engineering":
        relevant_skills = ["Python", "JavaScript", "SQL", "Problem Solving", "DevOps", "Cloud Services"]
    elif emp["department"] == "Sales":
        relevant_skills = ["Sales", "Communication", "Public Speaking", "Customer Service"]
    elif emp["department"] == "Marketing":
        relevant_skills = ["Marketing", "Content Writing", "Communication", "Data Analysis"]
    elif emp["department"] == "HR":
        relevant_skills = ["Communication", "Leadership", "Team Collaboration"]
    elif emp["department"] == "Finance":
        relevant_skills = ["Budgeting", "Data Analysis", "SQL"]
    elif emp["department"] == "Customer Support":
        relevant_skills = ["Customer Service", "Communication", "Problem Solving"]
    elif emp["department"] == "Product":
        relevant_skills = ["UX Design", "Project Management", "Team Collaboration"]
    elif emp["department"] == "Operations":
        relevant_skills = ["Project Management", "Data Analysis", "Leadership"]
    
    # Select from relevant skills first, then add random ones if needed
    selected_relevant = min(len(relevant_skills), num_skills - 1)
    emp_skills = random.sample(relevant_skills, selected_relevant)
    
    # Add some random skills to reach the desired number
    remaining_skills = [s for s in skills if s not in emp_skills]
    random_skills = random.sample(remaining_skills, num_skills - len(emp_skills))
    emp_skills.extend(random_skills)
    
    # Add to the list with skill ratings
    for skill in emp_skills:
        rating = random.randint(3, 5)
        employee_skills.append({
            "employee_id": emp["employee_id"],
            "skill": skill,
            "rating": rating
        })

# Create skills dataframe
skills_df = pd.DataFrame(employee_skills)

# Create training data
training_data = []
trainings = [
    "New Employee Orientation",
    "Leadership Development",
    "Technical Skills Workshop",
    "Communication Skills",
    "Project Management Basics",
    "Advanced SQL",
    "Python for Data Analysis",
    "Cloud Services Training",
    "Sales Techniques",
    "Customer Service Excellence",
    "Marketing Analytics",
    "Financial Planning",
    "HR Compliance",
    "DevOps Practices",
    "Product Management"
]

# Add some training records
for emp in employee_data:
    # Decide how many trainings this employee has completed (0-4)
    num_trainings = random.randint(0, 4)
    
    # New employees more likely to have orientation
    if (datetime.now() - datetime.strptime(emp["join_date"], '%Y-%m-%d')).days < 180:
        if "New Employee Orientation" not in [t["training_name"] for t in training_data if t["employee_id"] == emp["employee_id"]]:
            # Add orientation with recent date
            training_date = (datetime.strptime(emp["join_date"], '%Y-%m-%d') + timedelta(days=random.randint(7, 30))).strftime('%Y-%m-%d')
            training_data.append({
                "employee_id": emp["employee_id"],
                "training_name": "New Employee Orientation",
                "completion_date": training_date,
                "score": random.randint(70, 100)
            })
            num_trainings -= 1

    # Add department-specific trainings
    dept_trainings = {
        "Engineering": ["Technical Skills Workshop", "Python for Data Analysis", "DevOps Practices"],
        "Sales": ["Sales Techniques", "Communication Skills"],
        "Marketing": ["Marketing Analytics", "Communication Skills"],
        "HR": ["HR Compliance", "Communication Skills"],
        "Finance": ["Financial Planning", "Advanced SQL"],
        "Customer Support": ["Customer Service Excellence", "Communication Skills"],
        "Product": ["Product Management", "Project Management Basics"],
        "Operations": ["Project Management Basics", "Leadership Development"]
    }
    
    # Select trainings with preference for department-specific ones
    selected_trainings = []
    if emp["department"] in dept_trainings and num_trainings > 0:
        avail_dept_trainings = [t for t in dept_trainings[emp["department"]] 
                              if t not in [tr["training_name"] for tr in training_data if tr["employee_id"] == emp["employee_id"]]]
        to_select = min(len(avail_dept_trainings), random.randint(1, num_trainings))
        if to_select > 0:
            selected_trainings.extend(random.sample(avail_dept_trainings, to_select))
            num_trainings -= to_select
    
    # Fill remaining with random trainings
    if num_trainings > 0:
        avail_trainings = [t for t in trainings 
                         if t not in selected_trainings 
                         and t not in [tr["training_name"] for tr in training_data if tr["employee_id"] == emp["employee_id"]]]
        to_select = min(len(avail_trainings), num_trainings)
        if to_select > 0:
            selected_trainings.extend(random.sample(avail_trainings, to_select))
    
    # Add selected trainings with random dates and scores
    for training in selected_trainings:
        # Generate completion date within the last year
        days_ago = random.randint(30, 365)
        completion_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # Generate score (65-100)
        score = random.randint(65, 100)
        
        training_data.append({
            "employee_id": emp["employee_id"],
            "training_name": training,
            "completion_date": completion_date,
            "score": score
        })

# Create training dataframe
training_df = pd.DataFrame(training_data)

# Save all dataframes to the SQLite database
employees_df.to_sql('employees', conn, index=False, if_exists='replace')
performance_df.to_sql('performance_metrics', conn, index=False, if_exists='replace')
skills_df.to_sql('employee_skills', conn, index=False, if_exists='replace')
training_df.to_sql('training_records', conn, index=False, if_exists='replace')

# Close the connection
conn.close()

print(f"Test database created successfully with the following data:")
print(f"- {len(employees_df)} employees")
print(f"- {len(performance_df)} performance records")
print(f"- {len(skills_df)} skill records")
print(f"- {len(training_df)} training records")
print(f"\nDatabase saved as: {db_file}")
print(f"You can now upload this file to the PerformX application for testing.")