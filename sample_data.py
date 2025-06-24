"""
Sample Data Generator for Smart OS Scheduler
Generates sample tasks for testing the application
"""

from scheduler import Task, Scheduler
from datetime import datetime, timedelta
import random


def generate_sample_data():
    """Generate sample tasks for testing"""
    scheduler = Scheduler()
    
    # Sample data for different scenarios
    sample_tasks = [
        # Scenario 1: Simple FCFS test
        {
            'pid': 1, 'arrival_time': '09:00', 'burst_time': 5, 'priority': 1, 
            'scheduled_date': '2024-01-15', 'time_quantum': 2
        },
        {
            'pid': 2, 'arrival_time': '09:02', 'burst_time': 3, 'priority': 2, 
            'scheduled_date': '2024-01-15', 'time_quantum': 2
        },
        {
            'pid': 3, 'arrival_time': '09:05', 'burst_time': 8, 'priority': 3, 
            'scheduled_date': '2024-01-15', 'time_quantum': 2
        },
        
        # Scenario 2: Priority scheduling test
        {
            'pid': 4, 'arrival_time': '10:00', 'burst_time': 4, 'priority': 5, 
            'scheduled_date': '2024-01-16', 'time_quantum': 2
        },
        {
            'pid': 5, 'arrival_time': '10:01', 'burst_time': 6, 'priority': 1, 
            'scheduled_date': '2024-01-16', 'time_quantum': 2
        },
        {
            'pid': 6, 'arrival_time': '10:03', 'burst_time': 2, 'priority': 3, 
            'scheduled_date': '2024-01-16', 'time_quantum': 2
        },
        {
            'pid': 7, 'arrival_time': '10:05', 'burst_time': 7, 'priority': 2, 
            'scheduled_date': '2024-01-16', 'time_quantum': 2
        },
        
        # Scenario 3: Round Robin test
        {
            'pid': 8, 'arrival_time': '14:00', 'burst_time': 10, 'priority': 4, 
            'scheduled_date': '2024-01-17', 'time_quantum': 3
        },
        {
            'pid': 9, 'arrival_time': '14:02', 'burst_time': 6, 'priority': 2, 
            'scheduled_date': '2024-01-17', 'time_quantum': 3
        },
        {
            'pid': 10, 'arrival_time': '14:05', 'burst_time': 8, 'priority': 1, 
            'scheduled_date': '2024-01-17', 'time_quantum': 3
        },
        {
            'pid': 11, 'arrival_time': '14:08', 'burst_time': 4, 'priority': 3, 
            'scheduled_date': '2024-01-17', 'time_quantum': 3
        },
        
        # Scenario 4: Complex mixed scenario
        {
            'pid': 12, 'arrival_time': '16:00', 'burst_time': 12, 'priority': 1, 
            'scheduled_date': '2024-01-18', 'time_quantum': 2
        },
        {
            'pid': 13, 'arrival_time': '16:01', 'burst_time': 3, 'priority': 5, 
            'scheduled_date': '2024-01-18', 'time_quantum': 2
        },
        {
            'pid': 14, 'arrival_time': '16:03', 'burst_time': 7, 'priority': 2, 
            'scheduled_date': '2024-01-18', 'time_quantum': 2
        },
        {
            'pid': 15, 'arrival_time': '16:05', 'burst_time': 5, 'priority': 4, 
            'scheduled_date': '2024-01-18', 'time_quantum': 2
        },
        {
            'pid': 16, 'arrival_time': '16:07', 'burst_time': 9, 'priority': 3, 
            'scheduled_date': '2024-01-18', 'time_quantum': 2
        },
        
        # Scenario 5: Short burst times for SRTF
        {
            'pid': 17, 'arrival_time': '18:00', 'burst_time': 2, 'priority': 2, 
            'scheduled_date': '2024-01-19', 'time_quantum': 1
        },
        {
            'pid': 18, 'arrival_time': '18:01', 'burst_time': 4, 'priority': 1, 
            'scheduled_date': '2024-01-19', 'time_quantum': 1
        },
        {
            'pid': 19, 'arrival_time': '18:02', 'burst_time': 1, 'priority': 3, 
            'scheduled_date': '2024-01-19', 'time_quantum': 1
        },
        {
            'pid': 20, 'arrival_time': '18:03', 'burst_time': 3, 'priority': 2, 
            'scheduled_date': '2024-01-19', 'time_quantum': 1
        }
    ]
    
    # Add tasks to scheduler
    for task_data in sample_tasks:
        task = Task(**task_data)
        scheduler.add_task(task)
    
    return scheduler


def generate_random_data(num_tasks=20, num_dates=5):
    """Generate random task data for testing"""
    scheduler = Scheduler()
    
    # Generate dates
    base_date = datetime.now()
    dates = [(base_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_dates)]
    
    pid_counter = 1
    
    for date in dates:
        # Generate 2-6 tasks per date
        num_tasks_per_date = random.randint(2, 6)
        
        for i in range(num_tasks_per_date):
            # Random arrival time between 9:00 and 17:00
            hour = random.randint(9, 17)
            minute = random.randint(0, 59)
            arrival_time = f"{hour:02d}:{minute:02d}"
            
            # Random burst time between 1 and 15 minutes
            burst_time = random.randint(1, 15)
            
            # Random priority between 1 and 5
            priority = random.randint(1, 5)
            
            # Random time quantum between 1 and 4
            time_quantum = random.randint(1, 4)
            
            task = Task(
                pid=pid_counter,
                arrival_time=arrival_time,
                burst_time=burst_time,
                priority=priority,
                scheduled_date=date,
                time_quantum=time_quantum
            )
            
            scheduler.add_task(task)
            pid_counter += 1
    
    return scheduler


def print_sample_data_info(scheduler):
    """Print information about the generated sample data"""
    print("=== Sample Data Information ===")
    print(f"Total tasks: {len(scheduler.tasks)}")
    
    # Group by date
    tasks_by_date = {}
    for task in scheduler.tasks:
        date = task.scheduled_date
        if date not in tasks_by_date:
            tasks_by_date[date] = []
        tasks_by_date[date].append(task)
    
    print(f"Dates: {len(tasks_by_date)}")
    print("\nTasks by date:")
    for date in sorted(tasks_by_date.keys()):
        tasks = tasks_by_date[date]
        print(f"  {date}: {len(tasks)} tasks")
        
        # Show task details
        for task in tasks:
            print(f"    P{task.pid}: AT={task.arrival_time}, BT={task.burst_time}, "
                  f"Priority={task.priority}, TQ={task.time_quantum}")
    
    print("\n=== Ready for Testing ===")
    print("You can now run the application and test with this sample data.")


if __name__ == "__main__":
    print("Smart OS Scheduler - Sample Data Generator")
    print("=" * 50)
    
    # Generate sample data
    scheduler = generate_sample_data()
    
    # Print information
    print_sample_data_info(scheduler)
    
    # Optionally generate random data
    print("\n" + "=" * 50)
    print("To generate random data instead, uncomment the following lines:")
    print("# random_scheduler = generate_random_data(30, 7)")
    print("# print_sample_data_info(random_scheduler)")
    
    print("\nSample data has been generated and is ready for testing!")
    print("Run 'python app.py' to start the application.") 