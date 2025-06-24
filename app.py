from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from scheduler import Scheduler, Task
from gantt_chart import GanttChartGenerator
import os
from datetime import datetime
import json


app = Flask(__name__)
app.secret_key = 'smart_os_scheduler_secret_key_2024'

scheduler = Scheduler()
gantt_generator = GanttChartGenerator()


@app.route('/')
def index():
    """Main page with task input form"""
    return render_template('index.html')


@app.route('/add_task', methods=['POST'])
def add_task():
    """Add a new task to the scheduler"""
    try:
        # Get form data
        pid = int(request.form['pid'])
        arrival_time = request.form['arrival_time']
        burst_time = int(request.form['burst_time'])
        priority = int(request.form['priority'])
        scheduled_date = request.form['scheduled_date']
        time_quantum = int(request.form.get('time_quantum', 2))
        
        # Validate inputs
        if pid <= 0 or burst_time <= 0 or priority < 0:
            flash('Invalid input values. PID and Burst Time must be positive, Priority must be non-negative.', 'error')
            return redirect(url_for('index'))
        
        # Check if PID already exists for the same date
        existing_tasks = scheduler.get_tasks_by_date(scheduled_date)
        if any(p.pid == pid for p in existing_tasks):
            flash(f'Task ID {pid} already exists for date {scheduled_date}.', 'error')
            return redirect(url_for('index'))
        
        # Create and add task
        task = Task(
            pid=pid,
            arrival_time=arrival_time,
            burst_time=burst_time,
            priority=priority,
            scheduled_date=scheduled_date,
            time_quantum=time_quantum
        )
        
        scheduler.add_task(task)
        flash(f'Task P{pid} added successfully for {scheduled_date}!', 'success')
        
    except ValueError as e:
        flash('Invalid input format. Please check your inputs.', 'error')
    except Exception as e:
        flash(f'Error adding task: {str(e)}', 'error')
    
    return redirect(url_for('index'))


@app.route('/view_tasks')
def view_tasks():
    """View all tasks grouped by date"""
    # Group tasks by date
    tasks_by_date = {}
    for task in scheduler.tasks:
        date = task.scheduled_date
        if date not in tasks_by_date:
            tasks_by_date[date] = []
        tasks_by_date[date].append(task)
    
    # Sort dates
    sorted_dates = sorted(tasks_by_date.keys())
    
    total_tasks = len(scheduler.tasks)
    
    return render_template('view_tasks.html', 
                         tasks_by_date=tasks_by_date,
                         sorted_dates=sorted_dates,
                         total_tasks=total_tasks)


@app.route('/simulate/<date>')
def simulate_date(date):
    """Simulate all algorithms for a specific date"""
    try:
        # Get tasks for the date
        tasks = scheduler.get_tasks_by_date(date)
        
        if not tasks:
            flash(f'No tasks found for date {date}.', 'error')
            return redirect(url_for('view_tasks'))
        
        # Run all algorithms
        results = scheduler.run_all_algorithms(date)
        
        # Generate Gantt charts (HTML-based)
        gantt_charts = {}
        for algorithm_name, result in results.items():
            if isinstance(result, dict) and 'gantt_data' in result:
                gantt_charts[algorithm_name] = gantt_generator.generate_gantt_chart_html(
                    result['gantt_data'], 
                    result['algorithm'], 
                    tasks
                )
        
        # Generate comparison chart
        comparison_chart = gantt_generator.generate_comparison_chart_html(results, date)
        
        return render_template('results.html',
                             date=date,
                             tasks=tasks,
                             results=results,
                             gantt_charts=gantt_charts,
                             comparison_chart=comparison_chart)
    
    except Exception as e:
        flash(f'Error simulating algorithms: {str(e)}', 'error')
        return redirect(url_for('view_tasks'))


@app.route('/simulate_all')
def simulate_all():
    """Simulate all algorithms for all dates"""
    try:
        if not scheduler.tasks:
            flash('No tasks to simulate.', 'error')
            return redirect(url_for('view_tasks'))
        
        # Get all unique dates
        dates = list(set(p.scheduled_date for p in scheduler.tasks))
        dates.sort()
        
        all_results = {}
        for date in dates:
            all_results[date] = scheduler.run_all_algorithms(date)
        
        # Calculate algorithm performance stats to avoid logic in template
        algorithm_stats = {}
        for date, date_results in all_results.items():
            best_algo = date_results.get('best_algorithm')
            if best_algo and best_algo != "No valid results" and best_algo in date_results:
                result = date_results[best_algo]
                if 'algorithm' in result:
                    if best_algo not in algorithm_stats:
                        algorithm_stats[best_algo] = {
                            'wins': 0, 
                            'best_score': float('inf'),
                            'name': result['algorithm']
                        }
                    
                    algorithm_stats[best_algo]['wins'] += 1
                    
                    score = result.get('avg_waiting_time', 0) + result.get('avg_turnaround_time', 0)
                    if score < algorithm_stats[best_algo]['best_score']:
                        algorithm_stats[best_algo]['best_score'] = score

        return render_template('all_results.html',
                             dates=dates,
                             all_results=all_results,
                             algorithm_stats=algorithm_stats)
    
    except Exception as e:
        flash(f'Error simulating all algorithms: {str(e)}', 'error')
        return redirect(url_for('view_tasks'))


@app.route('/delete_task/<int:pid>/<date>')
def delete_task(pid, date):
    """Delete a specific task"""
    try:
        tasks = scheduler.get_tasks_by_date(date)
        task_to_delete = next((p for p in tasks if p.pid == pid), None)
        
        if task_to_delete:
            scheduler.tasks.remove(task_to_delete)
            flash(f'Task P{pid} deleted successfully.', 'success')
        else:
            flash(f'Task P{pid} not found for date {date}.', 'error')
    
    except Exception as e:
        flash(f'Error deleting task: {str(e)}', 'error')
    
    return redirect(url_for('view_tasks'))


@app.route('/clear_all')
def clear_all():
    """Clear all tasks"""
    try:
        scheduler.clear_tasks()
        flash('All tasks cleared successfully.', 'success')
    except Exception as e:
        flash(f'Error clearing tasks: {str(e)}', 'error')
    
    return redirect(url_for('view_tasks'))


@app.route('/export_csv/<date>')
def export_csv(date):
    """Export results to CSV format (simplified version)"""
    try:
        results = scheduler.run_all_algorithms(date)
        tasks = scheduler.get_tasks_by_date(date)
        
        if not tasks:
            flash(f'No tasks found for date {date}.', 'error')
            return redirect(url_for('view_tasks'))
        
        # Create simple CSV content
        csv_content = []
        csv_content.append("Task Information")
        csv_content.append("PID,Arrival Time,Burst Time,Priority,Scheduled Date")
        
        for task in tasks:
            csv_content.append(f"{task.pid},{task.arrival_time},{task.burst_time},{task.priority},{task.scheduled_date}")
        
        csv_content.append("")
        
        # Add algorithm results
        for algorithm_name, result in results.items():
            if isinstance(result, dict) and 'algorithm' in result:
                csv_content.append(f"Algorithm: {result['algorithm']}")
                csv_content.append("PID,Completion Time,Waiting Time,Turnaround Time")
                
                for task in tasks:
                    if task.pid in result.get('completion_times', {}):
                        csv_content.append(f"{task.pid},{result['completion_times'][task.pid]},{result['waiting_times'][task.pid]},{result['turnaround_times'][task.pid]}")
                
                csv_content.append(f"Average Waiting Time,{result.get('avg_waiting_time', 'N/A')}")
                csv_content.append(f"Average Turnaround Time,{result.get('avg_turnaround_time', 'N/A')}")
                csv_content.append("")
        
        # Create response
        from flask import Response
        return Response(
            '\n'.join(csv_content),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=scheduler_results_{date}.csv'}
        )
    
    except Exception as e:
        flash(f'Error exporting CSV: {str(e)}', 'error')
        return redirect(url_for('view_tasks'))


@app.route('/export_pdf/<date>')
def export_pdf(date):
    """Export results to PDF format (placeholder)"""
    flash('PDF export requires additional dependencies (reportlab). Please use CSV export instead.', 'warning')
    return redirect(url_for('view_tasks'))


@app.route('/api/tasks/<date>')
def api_tasks_by_date(date):
    """API endpoint to get tasks by date"""
    try:
        tasks = scheduler.get_tasks_by_date(date)
        task_list = []
        
        for task in tasks:
            task_list.append({
                'pid': task.pid,
                'arrival_time': task.arrival_time,
                'burst_time': task.burst_time,
                'priority': task.priority,
                'scheduled_date': task.scheduled_date,
                'time_quantum': task.time_quantum
            })
        
        return jsonify({'tasks': task_list, 'date': date})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/simulate/<date>')
def api_simulate_date(date):
    """API endpoint to simulate algorithms for a date"""
    try:
        results = scheduler.run_all_algorithms(date)
        
        # Remove gantt_data from API response to reduce size
        api_results = {}
        for key, value in results.items():
            if isinstance(value, dict) and 'gantt_data' in value:
                api_value = value.copy()
                del api_value['gantt_data']  # Remove gantt data for API
                api_results[key] = api_value
            else:
                api_results[key] = value
        
        return jsonify(api_results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Create static directories
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/charts', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 