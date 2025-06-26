# Fruit Detection System - Excel Export Documentation

## Overview

The Fruit Detection System now includes professional Excel export functionality with the title "Fruit Detection System" prominently displayed. This feature allows users to export their mangosteen detection data and summary statistics in a well-formatted Excel file.

## Features

### 1. Professional Excel Templates
- **Title**: "Fruit Detection System" prominently displayed at the top
- **Branding**: Consistent green color scheme (#34c759) matching the application theme
- **Formatting**: Professional headers, borders, and cell formatting
- **Metadata**: Generation timestamp, user information, and filter details

### 2. Detection History Export
- **Location**: Available from the History page and Dashboard
- **Data Included**:
  - Ripeness (Ripe/Unripe)
  - Confidence Percentage
  - Detection Date and Time
  - Image File Name
  - User Information
- **Filtering**: Respects applied filters (ripeness, date range)
- **Summary Statistics**: Automatically included at the bottom

### 3. Dashboard Summary Export
- **Location**: Available from the Dashboard page
- **Data Included**:
  - Total Detections
  - Today/Week/Month Statistics
  - Ripeness Distribution (Ripe/Unripe Mangosteen)
  - Average Confidence
  - Account Information

## File Structure

```
DetectionSystem/
├── excel_template.py          # Main Excel template generator
├── test_excel_export.py       # Test script for export functionality
├── EXCEL_EXPORT_README.md     # This documentation
└── app.py                     # Updated with export routes
```

## Usage

### For Users

1. **Export Detection History**:
   - Navigate to the History page
   - Apply any desired filters (ripeness, date range)
   - Click the "Download" button
   - File will be downloaded as: `Fruit_Detection_System_Detection_Report_YYYYMMDD_HHMMSS.xlsx`

2. **Export Dashboard Summary**:
   - Navigate to the Dashboard page
   - Click the "Export Summary" button
   - File will be downloaded as: `Fruit_Detection_System_Summary_Report_YYYYMMDD_HHMMSS.xlsx`

### For Developers

#### Using the Excel Template Class

```python
from excel_template import FruitDetectionExcelTemplate

# Create template instance
template = FruitDetectionExcelTemplate()

# Export detection data
output = template.create_detection_report(detections, user, filters)
filename = template.generate_filename("Detection_Report")

# Export summary data
output = template.create_summary_report(summary_data, user)
filename = template.generate_filename("Summary_Report")
```

#### Using Convenience Functions

```python
from excel_template import create_detection_export, create_summary_export

# Export detection data
output, filename = create_detection_export(detections, user, filters)

# Export summary data
output, filename = create_summary_export(summary_data, user)
```

## Excel File Format

### Detection Report Structure

```
Row 1:    Fruit Detection System (Title)
Row 2:    Detection Results Report (Subtitle)
Row 3:    Generated on: [timestamp]
Row 4:    User: [username]
Row 5:    Total Detections: [count]
Row 6:    Filters: [applied filters] (if any)
Row 7:    [empty]
Row 8:    [Column Headers]
Row 9+:   [Data Rows]
[Summary Section]
```

### Summary Report Structure

```
Row 1:    Fruit Detection System (Title)
Row 2:    Summary Statistics Report (Subtitle)
Row 3:    Generated on: [timestamp]
Row 4:    User: [username]
Row 5:    [empty]
Row 6+:   [Summary Data]
```

## Styling Features

### Colors
- **Primary**: #34c759 (Green)
- **Secondary**: #2a9d47 (Darker Green)
- **Accent**: #f8f9fa (Light Gray)

### Formatting
- **Title**: 18pt, bold, centered, green color
- **Headers**: 11pt, bold, white text on green background
- **Data**: 10pt, bordered cells
- **Confidence**: Percentage format with 2 decimal places
- **Ripeness**: Centered with light background

### Column Widths
- Ripeness: 12 characters
- Confidence: 15 characters
- Detection Date: 15 characters
- Detection Time: 12 characters
- Image File: 30 characters
- User: 12 characters

## Technical Implementation

### Dependencies
- `pandas`: Data manipulation and Excel writing
- `xlsxwriter`: Advanced Excel formatting
- `BytesIO`: In-memory file handling

### Key Classes

#### FruitDetectionExcelTemplate
Main class for generating Excel exports with professional formatting.

**Methods**:
- `create_detection_report()`: Generate detection history export
- `create_summary_report()`: Generate summary statistics export
- `generate_filename()`: Create timestamped filenames

### Routes Added

1. **`/export_history`**: Export filtered detection history
2. **`/export_dashboard_summary`**: Export dashboard summary statistics

## Testing

Run the test script to verify functionality:

```bash
python test_excel_export.py
```

This will test:
- Detection export creation
- Summary export creation
- Template class functionality
- File generation and formatting

## Error Handling

The export functionality includes comprehensive error handling:
- Empty data sets
- Invalid user data
- File generation errors
- Database query errors

All errors are logged and user-friendly messages are displayed.

## Future Enhancements

Potential improvements for the Excel export functionality:
1. **Charts and Graphs**: Add visual representations of data
2. **Multiple Sheets**: Separate sheets for different data types
3. **Custom Templates**: User-configurable export formats
4. **Batch Export**: Export multiple reports at once
5. **Email Integration**: Automatically email reports
6. **Scheduled Exports**: Automated report generation

## Support

For issues or questions regarding the Excel export functionality:
1. Check the test script output
2. Verify all dependencies are installed
3. Check the application logs for error messages
4. Ensure the user has proper permissions

---

**Note**: The Excel export functionality requires the `xlsxwriter` package. Make sure it's included in your `requirements.txt` file. 