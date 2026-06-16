from app.services.export_service import ExportService

report_data = {
    'date': '2026-05-20',
    'total_employees': 3,
    'checked_in': 3,
    'present': 3,
    'late': 1,
    'absent': 0,
    'attendance_rate': 100,
    'total_working_hours': 24,
    'total_overtime_actual_hours': 3,
    'total_overtime_hours': 4.5,
    'attendances': [
        {
            'employee_name': 'Nguyen Van A',
            'employee_code': 'E001',
            'check_in_time': '2026-05-20T08:00:00',
            'check_out_time': '2026-05-20T17:00:00',
            'working_hours': 8,
            'overtime_check_in_time': None,
            'overtime_check_out_time': None,
            'overtime_actual_hours': None,
            'overtime_hours': 0,
            'status': 'present',
            'status_label': 'Đi làm đúng giờ'
        },
        {
            'employee_name': 'Tran Thi B',
            'employee_code': 'E002',
            'check_in_time': '2026-05-20T08:15:00',
            'check_out_time': '2026-05-20T17:00:00',
            'working_hours': 7.75,
            'overtime_check_in_time': None,
            'overtime_check_out_time': None,
            'overtime_actual_hours': None,
            'overtime_hours': 0,
            'status': 'late',
            'status_label': 'Đi làm muộn'
        }
    ]
}

out = ExportService.export_to_excel(report_data, 'daily')
with open('test_daily.xlsx', 'wb') as f:
    f.write(out.read())
print('Wrote test_daily.xlsx')
