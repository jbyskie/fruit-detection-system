"""
Excel Template Generator for Fruit Detection System
Provides professional Excel export templates with consistent formatting
"""

import pandas as pd
from io import BytesIO
from datetime import datetime
import xlsxwriter


class FruitDetectionExcelTemplate:
    """Excel template generator for Fruit Detection System exports"""
    
    def __init__(self):
        self.title = "Fruit Detection System"
        self.primary_color = "#34c759"
        self.secondary_color = "#2a9d47"
        self.accent_color = "#f8f9fa"
        
    def create_detection_report(self, detections, user, filters=None):
        """
        Create a comprehensive detection report Excel file
        
        Args:
            detections: List of detection objects
            user: User object
            filters: Dictionary of applied filters
            
        Returns:
            BytesIO object containing the Excel file
        """
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Convert detections to DataFrame
            data = [{
                'Ripeness': d.ripeness,
                'Confidence (%)': round(d.confidence * 100, 2),
                'Detection Date': d.timestamp.strftime('%Y-%m-%d'),
                'Detection Time': d.timestamp.strftime('%H:%M:%S'),
                'Image File': d.image_path,
                'User': user.username
            } for d in detections]
            
            df = pd.DataFrame(data)
            
            # Write to Excel with formatting
            df.to_excel(writer, index=False, sheet_name='Detection Results', startrow=8)
            
            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Detection Results']
            
            # Apply formatting
            self._apply_detection_formatting(workbook, worksheet, df, user, filters)
        
        output.seek(0)
        return output
    
    def create_summary_report(self, summary_data, user):
        """
        Create a summary statistics report
        
        Args:
            summary_data: Dictionary containing summary statistics
            user: User object
            
        Returns:
            BytesIO object containing the Excel file
        """
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('Summary Report')
            
            # Apply summary formatting
            self._apply_summary_formatting(workbook, worksheet, summary_data, user)
        
        output.seek(0)
        return output
    
    def _apply_detection_formatting(self, workbook, worksheet, df, user, filters):
        """Apply professional formatting to detection report"""
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 18,
            'font_color': self.primary_color,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        subtitle_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_color': '#666666',
            'align': 'center',
            'valign': 'vcenter'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'font_color': 'white',
            'bg_color': self.primary_color,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': self.secondary_color
        })
        
        data_format = workbook.add_format({
            'font_size': 10,
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#e0e0e0'
        })
        
        confidence_format = workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#e0e0e0',
            'num_format': '0.00"%"'
        })
        
        ripeness_format = workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#e0e0e0',
            'bg_color': self.accent_color
        })
        
        # Add title and metadata
        worksheet.merge_range('A1:F1', self.title, title_format)
        worksheet.merge_range('A2:F2', 'Detection Results Report', subtitle_format)
        worksheet.merge_range('A3:F3', f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', subtitle_format)
        worksheet.merge_range('A4:F4', f'User: {user.username}', subtitle_format)
        worksheet.merge_range('A5:F5', f'Total Detections: {len(df)}', subtitle_format)
        
        # Add filter information if any
        if filters:
            filter_info = []
            for key, value in filters.items():
                if value and value != 'all':
                    filter_info.append(f'{key.title()}: {value}')
            
            if filter_info:
                worksheet.merge_range('A6:F6', f'Filters: {", ".join(filter_info)}', subtitle_format)
        
        # Set column widths
        worksheet.set_column('A:A', 12)  # Ripeness
        worksheet.set_column('B:B', 15)  # Confidence
        worksheet.set_column('C:C', 15)  # Detection Date
        worksheet.set_column('D:D', 12)  # Detection Time
        worksheet.set_column('E:E', 30)  # Image File
        worksheet.set_column('F:F', 12)  # User
        
        # Apply header formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(8, col_num, value, header_format)
        
        # Apply data formatting
        for row_num in range(len(df)):
            for col_num in range(len(df.columns)):
                cell_value = df.iloc[row_num, col_num]
                
                if col_num == 0:  # Ripeness column
                    worksheet.write(row_num + 9, col_num, cell_value, ripeness_format)
                elif col_num == 1:  # Confidence column
                    worksheet.write(row_num + 9, col_num, cell_value, confidence_format)
                else:
                    worksheet.write(row_num + 9, col_num, cell_value, data_format)
        
        # Add summary statistics
        self._add_summary_section(worksheet, df, len(df) + 12, header_format, data_format, title_format)
    
    def _apply_summary_formatting(self, workbook, worksheet, summary_data, user):
        """Apply formatting to summary report"""
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 18,
            'font_color': self.primary_color,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        subtitle_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_color': '#666666',
            'align': 'center',
            'valign': 'vcenter'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'font_color': 'white',
            'bg_color': self.primary_color,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': self.secondary_color
        })
        
        data_format = workbook.add_format({
            'font_size': 10,
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#e0e0e0'
        })
        
        # Add title
        worksheet.merge_range('A1:D1', self.title, title_format)
        worksheet.merge_range('A2:D2', 'Summary Statistics Report', subtitle_format)
        worksheet.merge_range('A3:D3', f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', subtitle_format)
        worksheet.merge_range('A4:D4', f'User: {user.username}', subtitle_format)
        
        # Add summary data
        row = 6
        for key, value in summary_data.items():
            worksheet.write(row, 0, key.replace('_', ' ').title(), header_format)
            worksheet.write(row, 1, value, data_format)
            row += 1
    
    def _add_summary_section(self, worksheet, df, start_row, header_format, data_format, title_format):
        """Add summary statistics section to detection report"""
        
        worksheet.merge_range(f'A{start_row}:F{start_row}', 'Summary Statistics', title_format)
        
        # Calculate statistics
        total_detections = len(df)
        ripe_count = len(df[df['Ripeness'] == 'ripe'])
        unripe_count = len(df[df['Ripeness'] == 'unripe'])
        avg_confidence = df['Confidence (%)'].mean()
        
        # Add statistics
        worksheet.write(start_row + 1, 0, 'Total Detections:', header_format)
        worksheet.write(start_row + 1, 1, total_detections, data_format)
        worksheet.write(start_row + 2, 0, 'Ripe Mangosteen:', header_format)
        worksheet.write(start_row + 2, 1, ripe_count, data_format)
        worksheet.write(start_row + 3, 0, 'Unripe Mangosteen:', header_format)
        worksheet.write(start_row + 3, 1, unripe_count, data_format)
        worksheet.write(start_row + 4, 0, 'Average Confidence:', header_format)
        worksheet.write(start_row + 4, 1, f'{avg_confidence:.2f}%', data_format)
        
        # Add ripeness percentage
        if total_detections > 0:
            ripe_percentage = (ripe_count / total_detections) * 100
            unripe_percentage = (unripe_count / total_detections) * 100
            
            worksheet.write(start_row + 6, 0, 'Ripeness Distribution:', header_format)
            worksheet.write(start_row + 7, 0, 'Ripe Percentage:', header_format)
            worksheet.write(start_row + 7, 1, f'{ripe_percentage:.1f}%', data_format)
            worksheet.write(start_row + 8, 0, 'Unripe Percentage:', header_format)
            worksheet.write(start_row + 8, 1, f'{unripe_percentage:.1f}%', data_format)
    
    def generate_filename(self, report_type="Report"):
        """Generate filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'Fruit_Detection_System_{report_type}_{timestamp}.xlsx'


def create_detection_export(detections, user, filters=None):
    """
    Convenience function to create detection export
    
    Args:
        detections: List of detection objects
        user: User object
        filters: Dictionary of applied filters
        
    Returns:
        Tuple of (BytesIO object, filename)
    """
    template = FruitDetectionExcelTemplate()
    output = template.create_detection_report(detections, user, filters)
    filename = template.generate_filename("Detection_Report")
    return output, filename


def create_summary_export(summary_data, user):
    """
    Convenience function to create summary export
    
    Args:
        summary_data: Dictionary containing summary statistics
        user: User object
        
    Returns:
        Tuple of (BytesIO object, filename)
    """
    template = FruitDetectionExcelTemplate()
    output = template.create_summary_report(summary_data, user)
    filename = template.generate_filename("Summary_Report")
    return output, filename 