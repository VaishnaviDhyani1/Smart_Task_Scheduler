
from typing import List, Dict
import os
from datetime import datetime


class GanttChartGenerator:
    """Generates HTML-based Gantt charts for scheduling algorithms"""
    
    def __init__(self):
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
            '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA'
        ]
    
    def _get_color(self, pid: int) -> str:
        """Get a color for a process ID"""
        return self.colors[pid % len(self.colors)]
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert HH:MM format to minutes since midnight"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    
    def _minutes_to_time(self, minutes: int) -> str:
        """Convert minutes since midnight to HH:MM format"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def generate_gantt_chart_html(self, gantt_data: List[Dict], algorithm_name: str, 
                                 processes: List = None) -> str:

        if not gantt_data:
            return self._generate_empty_chart_html(algorithm_name)
        
        # Get unique process IDs and create positions
        unique_pids = list(set(item['pid'] for item in gantt_data))
        unique_pids.sort()
        pid_positions = {pid: i for i, pid in enumerate(unique_pids)}
        
        # Calculate time range
        all_times = []
        for item in gantt_data:
            all_times.extend([self._time_to_minutes(item['start']), 
                            self._time_to_minutes(item['end'])])
        
        min_time = min(all_times)
        max_time = max(all_times)
        time_range = max_time - min_time
        
        # Generate time axis labels
        time_ticks = []
        num_ticks = min(10, time_range + 1)
        for i in range(num_ticks):
            time_value = min_time + (i * time_range / (num_ticks - 1))
            time_ticks.append(self._minutes_to_time(int(time_value)))
        
        # Start building HTML
        html = f"""
        <div class="gantt-chart-container">
            <h5 class="text-center mb-3">{algorithm_name}</h5>
            <div class="gantt-chart" style="position: relative; margin: 20px 0;">
                <div class="gantt-timeline" style="display: flex; margin-bottom: 10px;">
                    <div style="width: 100px; text-align: center; font-weight: bold;">Process</div>
                    <div style="flex: 1; display: flex; justify-content: space-between; padding: 0 10px;">
        """
        
        # Add time labels
        for time_label in time_ticks:
            html += f'<span style="font-size: 12px; color: #666;">{time_label}</span>'
        
        html += """
                    </div>
                </div>
        """
        
        # Add process rows
        for pid in unique_pids:
            color = self._get_color(pid)
            y_pos = pid_positions[pid]
            
            html += f"""
                <div class="gantt-row" style="display: flex; align-items: center; margin-bottom: 5px; height: 40px;">
                    <div style="width: 100px; text-align: center; font-weight: bold; color: {color};">
                        P{pid}
                    </div>
                    <div style="flex: 1; position: relative; height: 30px; background: #f8f9fa; border-radius: 5px; margin: 0 10px;">
            """
            
            # Add process execution blocks
            for item in gantt_data:
                if item['pid'] == pid:
                    start_time = self._time_to_minutes(item['start'])
                    end_time = self._time_to_minutes(item['end'])
                    duration = item['duration']
                    
                    # Calculate position and width
                    start_pos = ((start_time - min_time) / time_range) * 100
                    width = (duration / time_range) * 100
                    
                    html += f"""
                        <div class="gantt-block" 
                             style="position: absolute; 
                                    left: {start_pos}%; 
                                    width: {width}%; 
                                    height: 100%; 
                                    background: {color}; 
                                    border-radius: 3px; 
                                    display: flex; 
                                    align-items: center; 
                                    justify-content: center; 
                                    color: white; 
                                    font-weight: bold; 
                                    font-size: 11px; 
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                            P{pid}
                        </div>
                    """
            
            html += """
                    </div>
                </div>
            """
        
        # Add legend if processes are provided
        if processes:
            html += """
                <div class="gantt-legend" style="margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                    <h6 style="margin-bottom: 10px;">Process Details:</h6>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
            """
            
            for pid in unique_pids:
                color = self._get_color(pid)
                process_info = next((p for p in processes if p.pid == pid), None)
                if process_info:
                    html += f"""
                        <div style="display: flex; align-items: center; margin-right: 15px;">
                            <div style="width: 15px; height: 15px; background: {color}; border-radius: 3px; margin-right: 5px;"></div>
                            <span style="font-size: 12px;">P{pid} (AT: {process_info.arrival_time}, BT: {process_info.burst_time})</span>
                        </div>
                    """
            
            html += """
                    </div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def _generate_empty_chart_html(self, algorithm_name: str) -> str:
        """Generate an empty chart when no data is available"""
        return f"""
        <div class="gantt-chart-container">
            <h5 class="text-center mb-3">{algorithm_name}</h5>
            <div class="alert alert-warning text-center">
                <i class="fas fa-exclamation-triangle me-2"></i>
                No data available for Gantt chart
            </div>
        </div>
        """
    
    def generate_comparison_chart_html(self, results: Dict, date: str = None) -> str:
        # Filter valid results
        valid_results = {k: v for k, v in results.items() 
                        if isinstance(v, dict) and 'avg_waiting_time' in v}
        
        if not valid_results:
            return self._generate_empty_chart_html("Algorithm Comparison")
        
        # Prepare data for plotting
        algorithms = []
        avg_waiting_times = []
        avg_turnaround_times = []
        
        for name, result in valid_results.items():
            # Clean algorithm name for display
            clean_name = result['algorithm'].split('(')[0].strip()
            algorithms.append(clean_name)
            avg_waiting_times.append(result['avg_waiting_time'])
            avg_turnaround_times.append(result['avg_turnaround_time'])
        
        # Find maximum values for scaling
        max_waiting = max(avg_waiting_times) if avg_waiting_times else 1
        max_turnaround = max(avg_turnaround_times) if avg_turnaround_times else 1
        
        # Start building HTML
        title = f'Algorithm Performance Comparison'
        if date:
            title += f' - {date}'
        
        html = f"""
        <div class="comparison-chart-container">
            <h4 class="text-center mb-4">{title}</h4>
            <div class="row">
                <div class="col-md-6">
                    <h5 class="text-center mb-3">Average Waiting Time</h5>
                    <div class="chart-container" style="height: 300px; padding: 20px;">
        """
        
        # Generate waiting time bars
        for i, (algo, value) in enumerate(zip(algorithms, avg_waiting_times)):
            height_percent = (value / max_waiting) * 100 if max_waiting > 0 else 0
            html += f"""
                <div class="chart-bar-container" style="margin-bottom: 15px;">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <span style="width: 120px; font-size: 12px; font-weight: bold;">{algo}</span>
                        <span style="font-size: 12px; color: #666;">{value:.1f} min</span>
                    </div>
                    <div class="progress" style="height: 25px; background: #e9ecef;">
                        <div class="progress-bar bg-danger" 
                             style="width: {height_percent}%; 
                                    background: linear-gradient(135deg, #FF6B6B 0%, #ff4b2b 100%) !important;">
                        </div>
                    </div>
                </div>
            """
        
        html += """
                    </div>
                </div>
                <div class="col-md-6">
                    <h5 class="text-center mb-3">Average Turnaround Time</h5>
                    <div class="chart-container" style="height: 300px; padding: 20px;">
        """
        
        # Generate turnaround time bars
        for i, (algo, value) in enumerate(zip(algorithms, avg_turnaround_times)):
            height_percent = (value / max_turnaround) * 100 if max_turnaround > 0 else 0
            html += f"""
                <div class="chart-bar-container" style="margin-bottom: 15px;">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <span style="width: 120px; font-size: 12px; font-weight: bold;">{algo}</span>
                        <span style="font-size: 12px; color: #666;">{value:.1f} min</span>
                    </div>
                    <div class="progress" style="height: 25px; background: #e9ecef;">
                        <div class="progress-bar bg-info" 
                             style="width: {height_percent}%; 
                                    background: linear-gradient(135deg, #4ECDC4 0%, #45B7D1 100%) !important;">
                        </div>
                    </div>
                </div>
            """
        
        html += """
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def generate_gantt_chart(self, gantt_data: List[Dict], algorithm_name: str, 
                           processes: List = None) -> str:
        """Legacy method for compatibility - returns HTML instead of base64 image"""
        return self.generate_gantt_chart_html(gantt_data, algorithm_name, processes)
    
    def generate_comparison_chart(self, results: Dict, date: str = None) -> str:
        """Legacy method for compatibility - returns HTML instead of base64 image"""
        return self.generate_comparison_chart_html(results, date) 