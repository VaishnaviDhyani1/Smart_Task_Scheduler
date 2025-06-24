# Smart task Scheduler

A comprehensive full-stack Python Flask web application for simulating and visualizing various CPU scheduling algorithms with modern UI and advanced features.


### Process Management
- Add processes with detailed parameters (PID, arrival time, burst time, priority, etc.)
- Calendar view for organizing processes by date
- Delete individual processes
- Clear all processes
- Real-time validation and error handling

##  Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd smart-os-scheduler
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

##  Usage Guide

### 1. Adding Processes
1. Navigate to the home page
2. Fill in the process details:
   - **Process ID**: Unique identifier (positive integer)
   - **Arrival Time**: When the process arrives (HH:MM format)
   - **Burst Time**: CPU time required in minutes
   - **Priority**: Process priority (lower number = higher priority)
   - **Scheduled Date**: Date for process scheduling
   - **Time Quantum**: For Round Robin algorithm (default: 2 minutes)
   - 
3. Click "Add Process"

### 2. Viewing Processes
- Go to "View Processes" to see all processes organized by date
- Each date shows a summary of processes with quick actions
- Delete individual processes or clear all processes

### 3. Running Simulations
- **Single Date**: Click "Simulate" on any date to run all algorithms
- **All Dates**: Click "Simulate All" to run simulations for all dates
- View detailed results with Gantt charts and performance metrics

### 4. Exporting Results
- **CSV Export**: Download results in CSV format for analysis
- **PDF Export**: Generate professional PDF reports with charts and tables

##  Project Structure
```
smart-os-scheduler/
├── app.py                 # Main Flask application
├── scheduler.py           # Core scheduling algorithms
├── gantt_chart.py         # Gantt chart visualization
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with common layout
│   ├── index.html        # Main page with process form
│   ├── view_processes.html # Process calendar view
│   ├── results.html      # Single date simulation results
│   ├── all_results.html  # All dates simulation results
│   ├── 404.html          # 404 error page
│   └── 500.html          # 500 error page
└── static/               # Static files (CSS, JS, images)
    └── charts/           # Generated chart images
```

##  Technical Details

### Backend Architecture
- **Flask**: Web framework for routing and request handling
- **Matplotlib**: Chart generation and visualization
- **Pandas**: Data manipulation for CSV export
- **ReportLab**: PDF generation
- **Dataclasses**: Clean data structures for processes

### Frontend Technologies
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icons and visual elements
- **Custom CSS**: Modern styling with gradients and animations
- **JavaScript**: Interactive features and form validation

### Algorithm Implementation
- **Modular Design**: Each algorithm is implemented as a separate method
- **Error Handling**: Comprehensive error handling for edge cases
- **Performance Optimization**: Efficient data structures and algorithms
- **Extensible**: Easy to add new scheduling algorithms

##  Algorithm Details

### FCFS (First Come First Serve)
- **Type**: Non-preemptive
- **Selection**: Processes are executed in order of arrival
- **Advantages**: Simple, fair, no starvation
- **Disadvantages**: May not be optimal for average waiting time

### SJF (Shortest Job First)
- **Non-preemptive**: Selects shortest job among arrived processes
- **Preemptive (SRTF)**: Selects process with shortest remaining time
- **Advantages**: Minimizes average waiting time
- **Disadvantages**: May cause starvation for long processes

### Priority Scheduling
- **Non-preemptive**: Selects highest priority process among arrived processes
- **Preemptive**: Preempts running process if higher priority process arrives
- **Advantages**: Supports process priorities
- **Disadvantages**: May cause starvation for low priority processes

### Round Robin
- **Type**: Preemptive
- **Selection**: Processes are executed in FIFO order with time quantum
- **Advantages**: Fair, no starvation, good for time-sharing systems
- **Disadvantages**: Performance depends on time quantum size

##  Performance Metrics

The application calculates and compares:
- **Completion Time**: When each process finishes execution
- **Waiting Time**: Time spent waiting in ready queue
- **Turnaround Time**: Total time from arrival to completion
- **Average Waiting Time**: Mean waiting time across all processes
- **Average Turnaround Time**: Mean turnaround time across all processes

##  API Endpoints

### REST API
- `GET /api/processes/<date>` - Get processes for a specific date
- `GET /api/simulate/<date>` - Simulate algorithms for a date

### Web Routes
- `GET /` - Main page with process form
- `POST /add_process` - Add new process
- `GET /view_processes` - View all processes
- `GET /simulate/<date>` - Simulate for specific date
- `GET /simulate_all` - Simulate for all dates
- `GET /export_csv/<date>` - Export CSV results
- `GET /export_pdf/<date>` - Export PDF results





---
