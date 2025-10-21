"""
Export allocation results to Excel
"""
import os
from datetime import datetime

import json

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class ResultsExporter:
    """Export allocation results to Excel"""
    
    def __init__(self, state):
        self.state = state
        
        # Import the helper function
        import sys
        
        def data_path(relative_path):
            """Get path for writable data files"""
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            full_path = os.path.join(base_path, relative_path)
            directory = os.path.dirname(full_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            return full_path
        
        # Use data_path for exports directory
        self.exports_dir = os.path.dirname(data_path("exports/dummy.txt"))
        
        print(f"Exports will be saved to: {self.exports_dir}")

    
    def generate_filename(self, shift_time, extension):
        """Generate filename with date and shift time, using selected_date if available."""
        # Check if a specific date was selected in the application state
        if self.state.selected_date:
            date_str = self.state.selected_date
        # If no date was selected, use the current date as a fallback
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Construct the filename using the determined date, shift time, and file extension
        filename = f"Allocation_{date_str}_{shift_time}.{extension}"
        
        # Join the filename with the predefined 'exports' directory path.
        # self.exports_dir is already configured in the __init__ method.
        return os.path.join(self.exports_dir, filename)
    
    

    def save_allocation_json(self, shift_time):
        """Save allocation data as JSON"""
        
        filename = self.generate_json_filename(shift_time)
        
        # Prepare data structure
        allocation_data = {
            'metadata': {
                'date': self.state.selected_date or datetime.now().strftime("%Y-%m-%d"),
                'shift_time': shift_time,
                'shift_group': self.state.shift_group,
                'exported_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            'processes': [],
            'machines': [],
            'unassigned_workers': []
        }
        
        # Add processes
        for process_data in self.state.PROCESSES:
            process_name = process_data[0]
            if process_name in self.state.allocations:
                workers = self.state.allocations[process_name]
                product = self.state.get_product_for_allocation(process_name) or "N/A"
                lot_number = self.state.get_lot_number_for_allocation(process_name) or "N/A"
                
                print(f"DEBUG: Adding process {process_name} with {len(workers)} workers")
                
                process_data_dict = {
                    'name': process_name,
                    'product': product,
                    'lot_number': lot_number,
                    'workers': [
                        {
                            'name': w,
                            'display_name': self.state.get_worker_display_name(w),
                            'is_overtime': w in self.state.overtime_workers,
                            'is_temp': w in self.state.temp_workers
                        }
                        for w in workers
                    ],
                    'worker_count': len(workers)
                }
                allocation_data['processes'].append(process_data_dict)
        
        # Add machines
        for machine_data in self.state.compression_machines:
            machine_name = machine_data[0]
            if machine_name in self.state.allocations:
                workers = self.state.allocations[machine_name]
                product = self.state.get_product_for_allocation(machine_name) or "N/A"
                lot_number = self.state.get_lot_number_for_allocation(machine_name) or "N/A"
                
                print(f"DEBUG: Adding machine {machine_name} with {len(workers)} workers")
                
                machine_data_dict = {
                    'name': machine_name,
                    'product': product,
                    'lot_number': lot_number,
                    'workers': [
                        {
                            'name': w,
                            'display_name': self.state.get_worker_display_name(w),
                            'is_overtime': w in self.state.overtime_workers,
                            'is_temp': w in self.state.temp_workers
                        }
                        for w in workers
                    ],
                    'worker_count': len(workers)
                }
                allocation_data['machines'].append(machine_data_dict)
        
        # Add unassigned workers
        for worker in sorted(self.state.available_workers):
            allocation_data['unassigned_workers'].append({
                'name': worker,
                'display_name': self.state.get_worker_display_name(worker),
                'is_overtime': worker in self.state.overtime_workers,
                'is_temp': worker in self.state.temp_workers
            })
        
        print(f"DEBUG: Saving {len(allocation_data['processes'])} processes and {len(allocation_data['machines'])} machines")
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(allocation_data, f, indent=4, ensure_ascii=False)

        # Log to audit trail
        from audit_trail import audit_trail
        audit_trail.log_edit(
            change_type='ALLOCATION_CREATED',
            allocation_date=self.state.selected_date or datetime.now().strftime("%Y-%m-%d"),
            shift_time=shift_time,
            details={
                'processes_allocated': len(allocation_data['processes']),
                'machines_allocated': len(allocation_data['machines']),
                'total_workers_assigned': allocation_data['metadata'].get('total_workers', 0),
                'unassigned_workers': len(allocation_data['unassigned_workers']),
                'group': self.state.shift_group
            }
        )
        
        print(f"Allocation saved to: {filename}")
        print("="*60 + "\n")
        return filename

    def generate_json_filename(self, shift_time):
        """Generate JSON filename with date and shift time"""
        import sys
        
        def data_path(relative_path):
            """Get path for writable data files"""
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            full_path = os.path.join(base_path, relative_path)
            directory = os.path.dirname(full_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            return full_path
        
        if self.state.selected_date:
            date_str = self.state.selected_date
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        filename = f"Allocation_{date_str}_{shift_time}.json"
        
        # Use data_path to get the correct path
        return data_path(os.path.join("allocations_json", filename))
    
    def export_to_pdf(self, shift_time):
        """Export results to PDF"""
        filename = self.generate_filename(shift_time, "pdf")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Container for PDF elements
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        # Add title
        story.append(Paragraph("Worker Allocation Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        

        # Add report info - use selected date
        if self.state.selected_date:
            date_str = datetime.strptime(self.state.selected_date, "%Y-%m-%d").strftime("%B %d, %Y")
        else:
            date_str = datetime.now().strftime("%B %d, %Y")

        info_text = f"<b>Date:</b> {date_str}<br/><b>Shift:</b> {self.state.shift_time}<br/><b>Group:</b> {self.state.shift_group}"

        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add Production Processes section
        self._add_processes_to_pdf(story, heading_style, styles)
        
        # Add Compression Machines section
        self._add_machines_to_pdf(story, heading_style, styles)
        
        # Add Unassigned Workers section
        self._add_unassigned_to_pdf(story, heading_style, styles)
        
        # Build PDF
        doc.build(story)
        return filename
    
    def _add_processes_to_pdf(self, story, heading_style, styles):
        """Add production processes section to PDF"""
        # Check if any processes are allocated
        if not any(process_data[0] in self.state.allocations for process_data in self.state.PROCESSES):
            return
        
        # Section heading
        story.append(Paragraph("Production Processes", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Table data
        data = [['Process', 'Product', 'Lot Number', 'Workers', 'Count']]
        
        # Add rows
        for process_data in self.state.PROCESSES:
            process_name = process_data[0]
            if process_name in self.state.allocations:
                workers = self.state.allocations[process_name]
                product = self.state.get_product_for_allocation(process_name) or "N/A"
                lot_number = self.state.get_lot_number_for_allocation(process_name) or "N/A"
                worker_names = ", ".join([self.state.get_worker_display_name(w) for w in workers])
                
                data.append([
                    process_name,
                    product,
                    lot_number,
                    worker_names,
                    str(len(workers))
                ])
        
        # Create table
        table = Table(data, colWidths=[1.5*inch, 2.3*inch, 1*inch, 2*inch, 0.6*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Count column centered
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))

    def _add_machines_to_pdf(self, story, heading_style, styles):
        """Add compression machines section to PDF"""
        # Check if any machines are allocated
        if not any(machine_data[0] in self.state.allocations for machine_data in self.state.compression_machines):
            return
        
        # Section heading
        story.append(Paragraph("Compression Machines", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Table data
        data = [['Machine', 'Product', 'Lot Number', 'Workers', 'Count']]  # Changed 'Process' to 'Machine'
        
        # Add rows
        for machine_data in self.state.compression_machines:
            machine_name = machine_data[0]
            if machine_name in self.state.allocations:
                workers = self.state.allocations[machine_name]
                product = self.state.get_product_for_allocation(machine_name) or "N/A"
                lot_number = self.state.get_lot_number_for_allocation(machine_name) or "N/A"
                worker_names = ", ".join([self.state.get_worker_display_name(w) for w in workers])
                
                data.append([
                    machine_name,  # ← Changed from process_name
                    product,
                    lot_number,
                    worker_names,
                    str(len(workers))
                ])
        
        # Create table
        table = Table(data, colWidths=[1.5*inch, 2.3*inch, 1*inch, 2*inch, 0.6*inch])
        
        # Style the table (purple header for machines)
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Count column centered (changed from 3 to 4)
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))

    def _add_unassigned_to_pdf(self, story, heading_style, styles):
            """Add unassigned workers section to PDF"""
            if not self.state.available_workers:
                return
            
            # Section heading
            story.append(Paragraph("Unassigned Workers", heading_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Get unassigned workers
            unassigned = ", ".join([
                self.state.get_worker_display_name(w) 
                for w in sorted(self.state.available_workers)
            ])
            
            # Create a styled paragraph
            unassigned_style = ParagraphStyle(
                'Unassigned',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#e74c3c'),
                leftIndent=20,
                rightIndent=20
            )
            
            story.append(Paragraph(unassigned, unassigned_style))