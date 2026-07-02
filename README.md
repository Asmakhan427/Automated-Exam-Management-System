# ExamGenius AI
### AI-Powered Intelligent Examination Management Platform

> Built for The Mastery Mentors Hackathon 

---

## Overview

Examination season is one of the most operationally painful periods for any school or university. Administrators manually build seating charts, juggle spreadsheets to avoid double-booking rooms, and hand-assign invigilators — a process that is slow, error-prone, and frequently perceived as unfair by students.

ExamGenius AI is a desktop platform that automates the entire examination-management workflow using Artificial Intelligence. At its core is a K-Means clustering engine that intelligently groups students into balanced clusters, which are then mapped to rooms, shifts, and invigilators — all in a single click.

**What used to take days of manual spreadsheet work now takes seconds.**

---

## Problem Statement

Universities with thousands of students across multiple departments and batches must, for every exam cycle:

- Split students fairly across dozens of rooms with different capacities
- Avoid overcrowding or under-using any single room
- Ensure every domain present in a room has a qualified invigilator
- Produce transparent, auditable seating plans and reports
- Do all of this quickly, often under time pressure, with zero errors

Doing this by hand in Excel does not scale, is highly bias-prone, and routinely produces mistakes (double-seated students, over-capacity rooms, uneven faculty workload).

---

## Our Solution

ExamGenius AI automates the full pipeline:

| Step | What Happens |
|------|--------------|
| 1. Student Data | Generates/loads student records across departments & batches |
| 2. Room Data | Generates room inventory with realistic capacity distribution |
| 3. Faculty Data | Builds a faculty pool per department |
| 4. K-Means Clustering (AI) | Encodes domain + batch, scales features, clusters students into balanced groups |
| 5. Seating Allocation | Maps clusters to rooms respecting capacity, auto-creates additional exam shifts if needed |
| 6. Faculty Allocation | Round-robin assigns invigilators to every room, covering every domain present |

The result is a fair, optimized, and fully transparent exam plan — generated in seconds, not days — along with AI-generated insights, analytics, and exportable reports.

---

## Features

**Dashboard**
- Live statistics (students, rooms, clusters, utilization)
- Animated pipeline progress with step indicators
- Real-time activity log showing every operation
- Quick-action Run AI Pipeline button

**Configuration Panel**
- Two-way synced student/domain counts
- Domain distribution across 5 departments
- Room count parameter
- Live student data preview table
- Auto-sum validation

**Visual Classroom**
- Clickable seat grid view for every room
- Color-coded seats by department
- Student details on seat click (name, roll number, department, batch, cluster, seat)
- Per-shift room viewing
- Table view for accessibility

**Faculty Allocation**
- Full invigilation assignment table
- Room-wise faculty deployment
- Domain coverage per room
- Student count per room

**Analytics Suite**
- Department distribution pie chart
- Batch breakdown bar chart (19-23)
- Cluster size distribution chart
- Room utilization percentage chart
- Faculty workload bar chart
- Occupancy heatmap (rooms x shifts)

**AI Insights Panel**
- Auto-generated findings from clustering results
- AI Confidence Score (60-99%)
- Actionable recommendations
- Key metrics: most crowded room, average utilization, largest/smallest clusters, busiest faculty, shifts required

**Educational Impact Page**
- 9 impact cards showing real-world benefits
- Time saved, fairness, transparency, scalability
- Faculty management, error reduction, AI-assisted decisions

**How AI Works**
- Visual walkthrough of the complete pipeline
- Student-friendly explanations
- Feature encoding and scaling visualization
- K-Means clustering explanation

**Global Search**
- Search across all data sources
- Fields: Roll number, Student ID, Department, Faculty, Room, Seat number
- Cross-result display with type indicators

**Report & Export**
- TXT report generation
- PDF report export (with matplotlib)
- Excel multi-sheet export (Students, Seating, Faculty, Rooms)
- CSV exports for all dataframes

---

## AI Pipeline

```
Student Data (Domain + Batch)
        ↓
Label Encoding (categorical → numerical)
        ↓
Feature Scaling (StandardScaler)
        ↓
K-Means Clustering
        ↓
Optimized, Balanced Student Groups
        ↓
Room Allocation (capacity-aware, multi-shift)
        ↓
Faculty Assignment (round-robin, domain-matched)
        ↓
Reports, Charts & AI Insights
```

**Feature Engineering:**
- Label Encoding converts domain names and batch years to numerical values
- StandardScaler normalizes feature ranges for optimal clustering

**K-Means Algorithm:**
- Optimal k determined by room count and student population
- n_init=20 for reliable convergence
- max_iter=500 for stable clusters

**Seating Logic:**
- Students sorted by cluster, domain, and batch
- Room capacity constraints enforced
- Automatic shift creation when all rooms full

**Faculty Allocation:**
- Round-robin selection from domain-specific faculty pools
- Every domain present in a room gets at least one qualified invigilator

**Insights Generation:**
- Confidence score based on cluster balance
- Proactive recommendations for optimization
- Key metric extraction from all data sources

---

## Installation

**Prerequisites**
- Python 3.8 or higher
- Tkinter (comes with standard Python installation)

**Step-by-Step Installation**

1. Clone the repository
```bash
git clone https://github.com/yourusername/examgenius-ai.git
cd examgenius-ai
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

If you don't have a requirements.txt file, install manually:
```bash
pip install numpy pandas matplotlib scikit-learn openpyxl
```

3. Run the application
```bash
python examgenius_ai.py
```

**Linux-Specific Setup**
If Tkinter is missing on Linux:
```bash
sudo apt-get install python3-tk
```

**Dependencies File (requirements.txt)**
```
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
openpyxl>=3.1.0
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Tkinter (Python GUI) |
| AI Engine | scikit-learn (KMeans, StandardScaler, LabelEncoder) |
| Data Processing | pandas, numpy |
| Visualization | matplotlib |
| Exports | openpyxl (Excel), matplotlib (PDF) |
| Language | Python 3.8+ |

**Architecture Diagram**
```
┌─────────────────────────────────────────────────────────┐
│                     ExamGenius AI (Tkinter)              │
│                                                           │
│  ┌───────────┐   ┌────────────────────────────────────┐ │
│  │  Sidebar  │   │            Content Area             │ │
│  │ Navigation│   │  Dashboard / Config / Classroom /   │ │
│  │           │   │  Faculty / Analytics / AI Insights / │ │
│  │           │   │  Impact / How AI Works / Search /   │ │
│  │           │   │  Report                              │ │
│  └───────────┘   └────────────────────────────────────┘ │
│                                                           │
│  ┌────────────────────── AI Engine ───────────────────┐ │
│  │ pandas · numpy · scikit-learn (KMeans, Scaler)      │ │
│  │ Student/Room/Faculty Generation → Clustering →       │ │
│  │ Seating → Faculty Allocation → Insights              │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌───────────────── Export Layer ─────────────────────┐ │
│  │  TXT · PDF (matplotlib) · Excel (openpyxl) · CSV     │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Educational Impact

**Time Saved:** What used to take administrators days of manual spreadsheet work now takes seconds. Frees staff to focus on students rather than data entry.

**Fair Seat Allocation:** K-Means clustering balances students across rooms objectively. Removes human bias from the seating process. Every student gets fair treatment regardless of department.

**Reduced Exam Errors:** Automated capacity checks prevent double-bookings. No overcrowded rooms or under-utilized spaces. Eliminates manual spreadsheet errors.

**Better Faculty Management:** Round-robin invigilator allocation keeps workload balanced. Every faculty member gets fair assignment distribution. Domain expertise matched to room requirements.

**Improved Transparency:** Every student can see exactly which room, seat and shift they are assigned to. Faculty can view their invigilation schedule. Administrators can audit the entire process.

**Reduced Manual Work:** One click replaces hours of spreadsheet juggling. Let exam cells scale to thousands of students effortlessly. No more copy-paste errors.

**AI-Assisted Decisions:** Data-driven insights help administrators spot issues. Proactive recommendations before exam day. Confidence scores validate the allocation quality.

**Scalability:** Scales down easily for smaller institutions with fewer students. Scales up to thousands of students across multiple departments. Handles multiple exam shifts seamlessly.

**Built for Education:** Specifically designed for school and university needs. Understanding of academic domains and batches. Faculty expertise matched to student domains.

---

## Screenshots

**Dashboard**

<img width="1919" height="963" alt="image" src="https://github.com/user-attachments/assets/16619fbf-f7da-4949-9eee-89b94c75ac04" />

*Main dashboard showing statistics, pipeline progress, and activity log*

**Configuration**
<img width="1919" height="995" alt="image" src="https://github.com/user-attachments/assets/91e40337-9b66-4ad4-9c64-ae686231cfe4" />


*Configuration panel with domain distribution and student preview*

**Visual Classroom**
<img width="1916" height="1002" alt="image" src="https://github.com/user-attachments/assets/918133e0-888d-4d10-b3b1-9bb2bf5cabad" />

*Interactive seat grid with color-coded departments*

**Analytics**
<img width="1919" height="993" alt="image" src="https://github.com/user-attachments/assets/5c4d389c-520b-4fc2-9a1f-905d09f06f2c" />

*Analytics suite with multiple chart types*

**AI Insights**
<img width="1919" height="968" alt="image" src="https://github.com/user-attachments/assets/15bb6279-9ad2-4363-a206-05513bd0be55" />

*AI-generated insights with confidence score and recommendations*

**How AI Works**
<img width="1919" height="998" alt="image" src="https://github.com/user-attachments/assets/2247efd3-6560-4f20-9be9-46a75718181e" />

*Visual walkthrough of the AI pipeline*

**Global Search**
<img width="1919" height="1009" alt="image" src="https://github.com/user-attachments/assets/a6a00f2e-1b7e-4a71-b7bc-31ce46f1c1c0" />

*Global search across all data sources*

**Report & Export**
<img width="1919" height="996" alt="image" src="https://github.com/user-attachments/assets/b2dea99b-0d92-4246-bdca-68a3cd98482c" />

*Report generation and export options*

---

*"Making examinations fair, fast, and transparent — powered by AI."*
