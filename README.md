# Automated-Exam-Management-System
This project is a GUI-based Automated Exam Management System developed using Unsupervised Learning (K-Means Clustering). It efficiently manages student seating arrangements and faculty allocation for large-scale university exams.
Overview
The system handles approximately 2400–2500 students across multiple domains and batches, ensuring optimal room utilization and organized exam environments.
 Objectives
Automate exam seating plan generation
Group students using K-Means clustering (based on domain & batch)
Allocate faculty based on domain expertise
Optimize room capacity usage
Provide a user-friendly interface for administration
 Key Features
- Student Data Generation & Preprocessing
- K-Means Clustering for grouping students
- Optimized Seating Plan (with multi-shift support)
- Faculty Allocation per room
- Data Visualization (charts & graphs)
- Report Generation (TXT & Excel export)
- Interactive GUI (Tkinter-based)
- System Workflow
Data Collection
Students from batches 19–23 across 5 domains
Room capacities (25–35 seats)
Faculty data
Data Preprocessing
Encoding categorical features (domain, batch)
Feature scaling
K-Means Clustering
Students grouped based on domain & batch
Optimal clusters ≈ number of rooms
Seating Plan Generation
Assign students to rooms based on clusters
Ensure capacity constraints
Handle multiple exam shifts
Faculty Allocation
Assign faculty based on domain presence in rooms
Balanced distribution using round-robin
Reporting
Generate summary reports
Export data to Excel
🛠️ Technologies Used
Python
NumPy & Pandas (data handling)
Scikit-learn (K-Means clustering)
Tkinter (GUI)
Matplotlib (visualization)
📊 Output Includes
Seating plan (room-wise & shift-wise)
Faculty allocation per room
Cluster distribution
Domain & batch statistics
Exportable reports
  - How to Run
# Install dependencies
pip install numpy pandas matplotlib scikit-learn openpyxl

# Run the application
python main.py
 Project Highlights
Handles large datasets (~2500 students)
Implements real-world constraints (room capacity, shifts)
Uses Machine Learning for optimization
Provides user-friendly GUI interface
 Limitations
Uses generated data (no real-time database)
K-Means assumes uniform cluster sizes
No advanced cheating-prevention logic
 Future Improvements
Integration with real student database
Web-based version (Flask/React)
Advanced AI optimization techniques
PDF report generation
 Author
Asma Khan
