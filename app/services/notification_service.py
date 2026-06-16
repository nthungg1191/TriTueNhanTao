"""Notification Service - Hệ thống cảnh báo và thông báo"""
from app import db
from app.models import Employee, Attendance, SystemLog
from datetime import date, datetime, time, timedelta
from typing import List, Dict, Optional


class NotificationService:
    """Service for managing notifications and alerts"""
    
    @staticmethod
    def get_dashboard_alerts() -> List[Dict]:
        """Lấy danh sách cảnh báo cho dashboard"""
        alerts = []
        today = date.today()
        
        # Kiểm tra nhân viên đi muộn
        late_attendances = Attendance.query.filter(
            Attendance.date == today,
            Attendance.status == 'late'
        ).count()
        
        if late_attendances > 0:
            alerts.append({
                'type': 'warning',
                'title': f'⚠️ {late_attendances} nhân viên đi muộn',
                'message': f'Có {late_attendances} nhân viên đã chấm công muộn hôm nay',
                'priority': 'medium',
                'action_url': '/admin/attendance?filter=late'
            })
        
        # Kiểm tra nhân viên vắng mặt
        total_employees = Employee.query.filter_by(is_active=True).count()
        checked_in = Attendance.query.filter_by(date=today).count()
        absent_count = total_employees - checked_in
        
        if absent_count > 0:
            alerts.append({
                'type': 'danger',
                'title': f'❌ {absent_count} nhân viên vắng mặt',
                'message': f'Có {absent_count} nhân viên chưa chấm công hôm nay',
                'priority': 'high',
                'action_url': '/admin/attendance?filter=absent'
            })
        
        # Kiểm tra tỷ lệ chấm công thấp
        if total_employees > 0:
            attendance_rate = (checked_in / total_employees * 100)
            if attendance_rate < 70:
                alerts.append({
                    'type': 'warning',
                    'title': f'📉 Tỷ lệ chấm công thấp: {attendance_rate:.1f}%',
                    'message': f'Chỉ có {attendance_rate:.1f}% nhân viên đã chấm công',
                    'priority': 'medium',
                    'action_url': '/admin/reports?type=daily'
                })
        
        # Kiểm tra nhân viên chưa check-out
        incomplete_attendances = Attendance.query.filter(
            Attendance.date == today,
            Attendance.check_in_time.isnot(None),
            Attendance.check_out_time.is_(None)
        ).count()
        
        if incomplete_attendances > 0:
            alerts.append({
                'type': 'info',
                'title': f'⏰ {incomplete_attendances} nhân viên chưa check-out',
                'message': f'Có {incomplete_attendances} nhân viên đã check-in nhưng chưa check-out',
                'priority': 'low',
                'action_url': '/admin/attendance?filter=incomplete'
            })
        
        return alerts
    
    @staticmethod
    def check_late_employees(threshold_minutes: int = 15) -> List[Dict]:
        """Kiểm tra nhân viên đi muộn (quá threshold phút)"""
        today = date.today()
        alerts = []
        
        # Lấy tất cả attendance có status late
        late_attendances = Attendance.query.filter(
            Attendance.date == today,
            Attendance.status == 'late'
        ).all()
        
        for att in late_attendances:
            if att.check_in_time and att.employee:
                # Tính số phút muộn
                schedule = att.employee.get_current_schedule()
                if schedule:
                    scheduled_start = datetime.combine(today, schedule.shift_start)
                    late_minutes = (att.check_in_time - scheduled_start).total_seconds() / 60
                    
                    if late_minutes > threshold_minutes:
                        alerts.append({
                            'employee_id': att.employee_id,
                            'employee_name': att.employee.name,
                            'employee_code': att.employee.employee_code,
                            'late_minutes': int(late_minutes),
                            'check_in_time': att.check_in_time,
                            'severity': 'high' if late_minutes > 60 else 'medium'
                        })
        
        return alerts
    
    @staticmethod
    def check_absent_employees() -> List[Dict]:
        """Kiểm tra nhân viên vắng mặt"""
        today = date.today()
        alerts = []
        
        # Lấy tất cả nhân viên active
        all_employees = Employee.query.filter_by(is_active=True).all()
        
        # Lấy những người đã chấm công
        checked_in_ids = db.session.query(Attendance.employee_id).filter_by(date=today).all()
        checked_in_ids = [id[0] for id in checked_in_ids]
        
        # Những người chưa chấm công
        for emp in all_employees:
            if emp.id not in checked_in_ids:
                alerts.append({
                    'employee_id': emp.id,
                    'employee_name': emp.name,
                    'employee_code': emp.employee_code,
                    'department': emp.get_department_name(),
                    'date': today.isoformat()
                })
        
        return alerts
    
    @staticmethod
    def check_incomplete_attendances() -> List[Dict]:
        """Kiểm tra attendance chưa hoàn thành (chưa check-out)"""
        today = date.today()
        alerts = []
        
        # Lấy tất cả attendance đã check-in nhưng chưa check-out
        incomplete = Attendance.query.filter(
            Attendance.date == today,
            Attendance.check_in_time.isnot(None),
            Attendance.check_out_time.is_(None)
        ).all()
        
        for att in incomplete:
            if att.employee:
                # Tính số giờ đã làm
                hours_worked = 0
                if att.check_in_time:
                    now = datetime.now()
                    delta = now - att.check_in_time
                    hours_worked = delta.total_seconds() / 3600
                
                alerts.append({
                    'attendance_id': att.id,
                    'employee_id': att.employee_id,
                    'employee_name': att.employee.name,
                    'employee_code': att.employee.employee_code,
                    'check_in_time': att.check_in_time,
                    'hours_worked': round(hours_worked, 2),
                    'date': today.isoformat()
                })
        
        return alerts
    
    @staticmethod
    def send_notification(employee_id: int, notification_type: str, message: str, 
                         priority: str = 'medium', metadata: Optional[Dict] = None):
        """Gửi thông báo cho nhân viên (lưu vào log)"""
        from flask import current_app
        import smtplib
        from email.message import EmailMessage

        # Log the notification in system logs
        log = SystemLog.log_action(
            user_id=None,  # System notification
            action=f'notification_{notification_type}',
            entity_type='employee',
            entity_id=employee_id,
            details=message,
            status='success'
        )

        # Try sending email if SMTP configured and employee has email
        try:
            smtp_host = current_app.config.get('SMTP_HOST')
            smtp_port = int(current_app.config.get('SMTP_PORT', 0) or 0)
            smtp_user = current_app.config.get('SMTP_USER')
            smtp_pass = current_app.config.get('SMTP_PASS')
            mail_from = current_app.config.get('MAIL_FROM') or smtp_user

            if smtp_host and smtp_port and smtp_user and smtp_pass:
                emp = Employee.query.get(employee_id)
                if emp and emp.email:
                    msg = EmailMessage()
                    msg['Subject'] = f"Thông báo: {notification_type}"
                    msg['From'] = mail_from
                    msg['To'] = emp.email
                    msg.set_content(message)

                    # Use SSL for common secure ports
                    if smtp_port in (465,):
                        server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
                    else:
                        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
                        server.starttls()

                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
                    server.quit()
        except Exception:
            # Don't fail the main flow if email sending fails; we already logged the notification
            pass

        return log
    
    @staticmethod
    def get_employee_notifications(employee_id: int, days: int = 7) -> List[Dict]:
        """Lấy thông báo của một nhân viên"""
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        
        logs = SystemLog.query.filter(
            SystemLog.entity_type == 'employee',
            SystemLog.entity_id == employee_id,
            SystemLog.action.like('notification_%'),
            SystemLog.created_at >= start_date
        ).order_by(SystemLog.created_at.desc()).all()
        
        notifications = []
        for log in logs:
            notifications.append({
                'id': log.id,
                'type': log.action.replace('notification_', ''),
                'message': log.details,
                'created_at': log.created_at.isoformat(),
                'status': log.status
            })
        
        return notifications
    
    @staticmethod
    def get_user_notifications(user_id: int, since_id: int = 0, limit: int = 10) -> List[Dict]:
        """
        Get notifications for a user (for SSE stream)
        
        Args:
            user_id: User ID
            since_id: Get notifications after this ID
            limit: Maximum number of notifications
            
        Returns:
            List of notification dictionaries
        """
        # Get dashboard alerts as notifications
        alerts = NotificationService.get_dashboard_alerts()
        
        notifications = []
        for i, alert in enumerate(alerts):
            notifications.append({
                'id': since_id + i + 1,
                'type': alert.get('type', 'info'),
                'title': alert.get('title', ''),
                'message': alert.get('message', ''),
                'timestamp': datetime.now().isoformat(),
                'action_url': alert.get('action_url')
            })
        
        return notifications[:limit]
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Get count of unread notifications for user"""
        # Simplified - in production, query Notification model
        alerts = NotificationService.get_dashboard_alerts()
        return len([a for a in alerts if a.get('type') in ['danger', 'warning']])

