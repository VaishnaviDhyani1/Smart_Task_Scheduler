from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import heapq


@dataclass
class Task:
    """Task data structure"""
    pid: int
    arrival_time: str  # HH:MM format
    burst_time: int    # minutes
    priority: int
    scheduled_date: str  # dd-mm-yyyy format
    time_quantum: int = 2  # for Round Robin
    
    def __post_init__(self):
        # Convert arrival time to minutes for easier calculations
        self.arrival_minutes = self._time_to_minutes(self.arrival_time)
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert HH:MM format to minutes since midnight"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    
    def _minutes_to_time(self, minutes: int) -> str:
        """Convert minutes since midnight to HH:MM format"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"


class Scheduler:
    """Main scheduler class containing all algorithm implementations"""
    
    def __init__(self):
        self.tasks = []
        self.results = {}
    
    def add_task(self, task: Task):
        """Add a task to the scheduler"""
        self.tasks.append(task)
    
    def clear_tasks(self):
        """Clear all tasks"""
        self.tasks.clear()
        self.results.clear()
    
    def get_tasks_by_date(self, date: str) -> List[Task]:
        """Get all tasks for a specific date"""
        return [t for t in self.tasks if t.scheduled_date == date]
    
    def fcfs(self, tasks: List[Task]) -> Dict:
        """First Come First Serve (Non-preemptive)"""
        if not tasks:
            return {"error": "No tasks to schedule"}
        
        # Sort by arrival time
        sorted_tasks = sorted(tasks, key=lambda x: x.arrival_minutes)
        
        current_time = sorted_tasks[0].arrival_minutes
        completion_times = {}
        waiting_times = {}
        turnaround_times = {}
        gantt_data = []
        
        for task in sorted_tasks:
            # If current time is before arrival, wait
            if current_time < task.arrival_minutes:
                current_time = task.arrival_minutes
            
            # Task execution
            start_time = current_time
            completion_time = current_time + task.burst_time
            completion_times[task.pid] = completion_time
            
            # Calculate times
            waiting_time = start_time - task.arrival_minutes
            turnaround_time = completion_time - task.arrival_minutes
            
            waiting_times[task.pid] = waiting_time
            turnaround_times[task.pid] = turnaround_time
            
            # Gantt chart data
            gantt_data.append({
                'pid': task.pid,
                'start': task._minutes_to_time(start_time),
                'end': task._minutes_to_time(completion_time),
                'duration': task.burst_time
            })
            
            current_time = completion_time
        
        avg_waiting_time = sum(waiting_times.values()) / len(waiting_times)
        avg_turnaround_time = sum(turnaround_times.values()) / len(turnaround_times)
        
        return {
            'algorithm': 'FCFS (First Come First Serve)',
            'completion_times': completion_times,
            'waiting_times': waiting_times,
            'turnaround_times': turnaround_times,
            'avg_waiting_time': round(avg_waiting_time, 2),
            'avg_turnaround_time': round(avg_turnaround_time, 2),
            'gantt_data': gantt_data
        }
    
    def sjf_non_preemptive(self, tasks: List[Task]) -> Dict:
        """Shortest Job First (Non-preemptive)"""
        if not tasks:
            return {"error": "No tasks to schedule"}
        
        # Sort by arrival time first
        sorted_tasks = sorted(tasks, key=lambda x: x.arrival_minutes)
        
        current_time = sorted_tasks[0].arrival_minutes
        completion_times = {}
        waiting_times = {}
        turnaround_times = {}
        gantt_data = []
        remaining_tasks = sorted_tasks.copy()
        
        while remaining_tasks:
            # Find tasks that have arrived
            available_tasks = [t for t in remaining_tasks 
                                 if t.arrival_minutes <= current_time]
            
            if not available_tasks:
                # No task available, move time forward
                current_time = min(t.arrival_minutes for t in remaining_tasks)
                continue
            
            # Select shortest job among available tasks
            selected_task = min(available_tasks, key=lambda x: x.burst_time)
            
            # Task execution
            start_time = current_time
            completion_time = current_time + selected_task.burst_time
            completion_times[selected_task.pid] = completion_time
            
            # Calculate times
            waiting_time = start_time - selected_task.arrival_minutes
            turnaround_time = completion_time - selected_task.arrival_minutes
            
            waiting_times[selected_task.pid] = waiting_time
            turnaround_times[selected_task.pid] = turnaround_time
            
            # Gantt chart data
            gantt_data.append({
                'pid': selected_task.pid,
                'start': selected_task._minutes_to_time(start_time),
                'end': selected_task._minutes_to_time(completion_time),
                'duration': selected_task.burst_time
            })
            
            current_time = completion_time
            remaining_tasks.remove(selected_task)
        
        avg_waiting_time = sum(waiting_times.values()) / len(waiting_times)
        avg_turnaround_time = sum(turnaround_times.values()) / len(turnaround_times)
        
        return {
            'algorithm': 'SJF Non-Preemptive (Shortest Job First)',
            'completion_times': completion_times,
            'waiting_times': waiting_times,
            'turnaround_times': turnaround_times,
            'avg_waiting_time': round(avg_waiting_time, 2),
            'avg_turnaround_time': round(avg_turnaround_time, 2),
            'gantt_data': gantt_data
        }
    
    def sjf_preemptive(self, tasks: List[Task]) -> Dict:
        """Shortest Job First (Preemptive) - SRTF"""
        if not tasks:
            return {"error": "No tasks to schedule"}
        
        # Create task copies with remaining burst time
        task_copies = []
        for t in tasks:
            task_copies.append({
                'pid': t.pid,
                'arrival_minutes': t.arrival_minutes,
                'burst_time': t.burst_time,
                'remaining_burst': t.burst_time,
                'original_task': t
            })
        
        current_time = min(t['arrival_minutes'] for t in task_copies)
        completion_times = {}
        waiting_times = {}
        turnaround_times = {}
        gantt_data = []
        
        while any(t['remaining_burst'] > 0 for t in task_copies):
            # Find tasks that have arrived and have remaining burst time
            available_tasks = [t for t in task_copies 
                                 if t['arrival_minutes'] <= current_time and t['remaining_burst'] > 0]
            
            if not available_tasks:
                # No task available, move time forward
                next_arrival = min(t['arrival_minutes'] for t in task_copies 
                                 if t['remaining_burst'] > 0)
                current_time = next_arrival
                continue
            
            # Select task with shortest remaining burst time
            selected_task = min(available_tasks, key=lambda x: x['remaining_burst'])
            
            # Execute for 1 time unit
            start_time = current_time
            current_time += 1
            selected_task['remaining_burst'] -= 1
            
            # Gantt chart data
            gantt_data.append({
                'pid': selected_task['pid'],
                'start': selected_task['original_task']._minutes_to_time(start_time),
                'end': selected_task['original_task']._minutes_to_time(current_time),
                'duration': 1
            })
            
            # Check if task completed
            if selected_task['remaining_burst'] == 0:
                completion_time = current_time
                completion_times[selected_task['pid']] = completion_time
                
                # Calculate times
                original_task = selected_task['original_task']
                waiting_time = completion_time - original_task.arrival_minutes - original_task.burst_time
                turnaround_time = completion_time - original_task.arrival_minutes
                
                waiting_times[selected_task['pid']] = waiting_time
                turnaround_times[selected_task['pid']] = turnaround_time
        
        avg_waiting_time = sum(waiting_times.values()) / len(waiting_times)
        avg_turnaround_time = sum(turnaround_times.values()) / len(turnaround_times)
        
        return {
            'algorithm': 'SJF Preemptive (Shortest Remaining Time First)',
            'completion_times': completion_times,
            'waiting_times': waiting_times,
            'turnaround_times': turnaround_times,
            'avg_waiting_time': round(avg_waiting_time, 2),
            'avg_turnaround_time': round(avg_turnaround_time, 2),
            'gantt_data': gantt_data
        }
    
    def priority_non_preemptive(self, tasks: List[Task]) -> Dict:
        """Priority Scheduling (Non-preemptive)"""
        if not tasks:
            return {"error": "No tasks to schedule"}
        
        # Sort by arrival time first
        sorted_tasks = sorted(tasks, key=lambda x: x.arrival_minutes)
        
        current_time = sorted_tasks[0].arrival_minutes
        completion_times = {}
        waiting_times = {}
        turnaround_times = {}
        gantt_data = []
        remaining_tasks = sorted_tasks.copy()
        
        while remaining_tasks:
            # Find tasks that have arrived
            available_tasks = [t for t in remaining_tasks 
                                 if t.arrival_minutes <= current_time]
            
            if not available_tasks:
                # No task available, move time forward
                current_time = min(t.arrival_minutes for t in remaining_tasks)
                continue
            
            # Select highest priority task (lowest priority number)
            selected_task = min(available_tasks, key=lambda x: x.priority)
            
            # Task execution
            start_time = current_time
            completion_time = current_time + selected_task.burst_time
            completion_times[selected_task.pid] = completion_time
            
            # Calculate times
            waiting_time = start_time - selected_task.arrival_minutes
            turnaround_time = completion_time - selected_task.arrival_minutes
            
            waiting_times[selected_task.pid] = waiting_time
            turnaround_times[selected_task.pid] = turnaround_time
            
            # Gantt chart data
            gantt_data.append({
                'pid': selected_task.pid,
                'start': selected_task._minutes_to_time(start_time),
                'end': selected_task._minutes_to_time(completion_time),
                'duration': selected_task.burst_time
            })
            
            current_time = completion_time
            remaining_tasks.remove(selected_task)
        
        avg_waiting_time = sum(waiting_times.values()) / len(waiting_times)
        avg_turnaround_time = sum(turnaround_times.values()) / len(turnaround_times)
        
        return {
            'algorithm': 'Priority Non-Preemptive',
            'completion_times': completion_times,
            'waiting_times': waiting_times,
            'turnaround_times': turnaround_times,
            'avg_waiting_time': round(avg_waiting_time, 2),
            'avg_turnaround_time': round(avg_turnaround_time, 2),
            'gantt_data': gantt_data
        }
    
    def priority_preemptive(self, tasks: List[Task]) -> Dict:
        """Priority Scheduling (Preemptive)"""
        if not tasks:
            return {"error": "No tasks to schedule"}
        
        # Create task copies with remaining burst time
        task_copies = []
        for t in tasks:
            task_copies.append({
                'pid': t.pid,
                'arrival_minutes': t.arrival_minutes,
                'burst_time': t.burst_time,
                'remaining_burst': t.burst_time,
                'priority': t.priority,
                'original_task': t
            })
        
        current_time = min(t['arrival_minutes'] for t in task_copies)
        completion_times = {}
        waiting_times = {}
        turnaround_times = {}
        gantt_data = []
        
        while any(t['remaining_burst'] > 0 for t in task_copies):
            # Find tasks that have arrived and have remaining burst time
            available_tasks = [t for t in task_copies 
                                 if t['arrival_minutes'] <= current_time and t['remaining_burst'] > 0]
            
            if not available_tasks:
                # No task available, move time forward
                next_arrival = min(t['arrival_minutes'] for t in task_copies 
                                 if t['remaining_burst'] > 0)
                current_time = next_arrival
                continue
            
            # Select task with highest priority (lowest priority number)
            selected_task = min(available_tasks, key=lambda x: x['priority'])
            
            # Execute for 1 time unit
            start_time = current_time
            current_time += 1
            selected_task['remaining_burst'] -= 1
            
            # Gantt chart data
            gantt_data.append({
                'pid': selected_task['pid'],
                'start': selected_task['original_task']._minutes_to_time(start_time),
                'end': selected_task['original_task']._minutes_to_time(current_time),
                'duration': 1
            })
            
            # Check if task completed
            if selected_task['remaining_burst'] == 0:
                completion_time = current_time
                completion_times[selected_task['pid']] = completion_time
                
                # Calculate times
                original_task = selected_task['original_task']
                waiting_time = completion_time - original_task.arrival_minutes - original_task.burst_time
                turnaround_time = completion_time - original_task.arrival_minutes
                
                waiting_times[selected_task['pid']] = waiting_time
                turnaround_times[selected_task['pid']] = turnaround_time
        
        avg_waiting_time = sum(waiting_times.values()) / len(waiting_times)
        avg_turnaround_time = sum(turnaround_times.values()) / len(turnaround_times)
        
        return {
            'algorithm': 'Priority Preemptive',
            'completion_times': completion_times,
            'waiting_times': waiting_times,
            'turnaround_times': turnaround_times,
            'avg_waiting_time': round(avg_waiting_time, 2),
            'avg_turnaround_time': round(avg_turnaround_time, 2),
            'gantt_data': gantt_data
        }
    
    def round_robin(self, tasks: List[Task]) -> Dict:
        """Round Robin Scheduling"""
        if not tasks:
            return {"error": "No tasks to schedule"}
        
        # Use the first task's time quantum, or default to 2
        time_quantum = tasks[0].time_quantum if tasks else 2
        
        # Create task copies with remaining burst time
        task_copies = []
        for t in tasks:
            task_copies.append({
                'pid': t.pid,
                'arrival_minutes': t.arrival_minutes,
                'burst_time': t.burst_time,
                'remaining_burst': t.burst_time,
                'original_task': t
            })
        
        current_time = min(t['arrival_minutes'] for t in task_copies)
        completion_times = {}
        waiting_times = {}
        turnaround_times = {}
        gantt_data = []
        ready_queue = []
        
        # Sort by arrival time
        task_copies.sort(key=lambda x: x['arrival_minutes'])
        
        while task_copies or ready_queue:
            # Add arrived tasks to ready queue
            while task_copies and task_copies[0]['arrival_minutes'] <= current_time:
                ready_queue.append(task_copies.pop(0))
            
            if not ready_queue:
                # No task in ready queue, move time forward
                current_time = task_copies[0]['arrival_minutes']
                continue
            
            # Get next task from ready queue
            current_task = ready_queue.pop(0)
            
            # Execute task
            start_time = current_time
            execution_time = min(time_quantum, current_task['remaining_burst'])
            current_time += execution_time
            current_task['remaining_burst'] -= execution_time
            
            # Gantt chart data
            gantt_data.append({
                'pid': current_task['pid'],
                'start': current_task['original_task']._minutes_to_time(start_time),
                'end': current_task['original_task']._minutes_to_time(current_time),
                'duration': execution_time
            })
            
            # Check if task completed
            if current_task['remaining_burst'] == 0:
                completion_time = current_time
                completion_times[current_task['pid']] = completion_time
                
                # Calculate times
                original_task = current_task['original_task']
                waiting_time = completion_time - original_task.arrival_minutes - original_task.burst_time
                turnaround_time = completion_time - original_task.arrival_minutes
                
                waiting_times[current_task['pid']] = waiting_time
                turnaround_times[current_task['pid']] = turnaround_time
            else:
                # Task not completed, add back to ready queue
                ready_queue.append(current_task)
        
        avg_waiting_time = sum(waiting_times.values()) / len(waiting_times)
        avg_turnaround_time = sum(turnaround_times.values()) / len(turnaround_times)
        
        return {
            'algorithm': f'Round Robin (Time Quantum: {time_quantum})',
            'completion_times': completion_times,
            'waiting_times': waiting_times,
            'turnaround_times': turnaround_times,
            'avg_waiting_time': round(avg_waiting_time, 2),
            'avg_turnaround_time': round(avg_turnaround_time, 2),
            'gantt_data': gantt_data
        }
    
    def run_all_algorithms(self, date: str = None) -> Dict:
        """Run all scheduling algorithms for tasks on a specific date"""
        if date:
            target_tasks = self.get_tasks_by_date(date)
        else:
            target_tasks = self.tasks
        
        if not target_tasks:
            return {"error": f"No tasks found for date: {date}"}
        
        results = {}
        
        # Run all algorithms
        algorithms = [
            ('fcfs', self.fcfs),
            ('sjf_non_preemptive', self.sjf_non_preemptive),
            ('sjf_preemptive', self.sjf_preemptive),
            ('priority_non_preemptive', self.priority_non_preemptive),
            ('priority_preemptive', self.priority_preemptive),
            ('round_robin', self.round_robin)
        ]
        
        for name, algorithm_func in algorithms:
            try:
                results[name] = algorithm_func(target_tasks)
            except Exception as e:
                results[name] = {"error": f"Error in {name}: {str(e)}"}
        
        # Find best algorithm
        best_algorithm = self._find_best_algorithm(results)
        results['best_algorithm'] = best_algorithm
        
        return results
    
    def _find_best_algorithm(self, results: Dict) -> str:
        """Find the best algorithm based on average waiting time and turnaround time"""
        valid_results = {k: v for k, v in results.items() 
                        if isinstance(v, dict) and 'avg_waiting_time' in v}
        
        if not valid_results:
            return "No valid results"
        
        # Calculate combined score (lower is better)
        algorithm_scores = {}
        for name, result in valid_results.items():
            # Weight waiting time and turnaround time equally
            score = result['avg_waiting_time'] + result['avg_turnaround_time']
            algorithm_scores[name] = score
        
        # Find algorithm with lowest score
        best_algorithm = min(algorithm_scores.items(), key=lambda x: x[1])[0]
        
        return best_algorithm 