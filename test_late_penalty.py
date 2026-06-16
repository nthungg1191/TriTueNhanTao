"""Test late arrival penalty logic - Unit Tests"""
from datetime import datetime, date, time, timedelta
import sys
from unittest.mock import Mock, MagicMock


# Mock classes to simulate database models without full Flask/SQLAlchemy
class MockWorkSchedule:
    def __init__(self, shift_start, shift_end):
        self.shift_start = shift_start
        self.shift_end = shift_end


class MockEmployee:
    def __init__(self):
        self.id = 1
        self.name = 'Test Employee'
    
    def get_current_schedule(self):
        return MockWorkSchedule(time(8, 0), time(17, 0))


def create_mock_attendance(check_in_time, check_out_time, check_in_time_2, check_out_time_2, test_date=None):
    """Create a mock attendance object"""
    if test_date is None:
        test_date = date.today()
    
    att = Mock()
    att.date = test_date
    att.check_in_time = datetime.combine(test_date, check_in_time)
    att.check_out_time = datetime.combine(test_date, check_out_time)
    att.check_in_time_2 = datetime.combine(test_date, check_in_time_2)
    att.check_out_time_2 = datetime.combine(test_date, check_out_time_2)
    att.employee = MockEmployee()
    att.working_hours = 0.0
    att.overtime_hours = 0.0
    
    # Import the actual method from Attendance model
    from app.models.attendance import Attendance
    att._calculate_deduction = Attendance._calculate_deduction.__get__(att)
    att._apply_time_deductions = Attendance._apply_time_deductions.__get__(att)
    att.calculate_working_hours = Attendance.calculate_working_hours.__get__(att)
    
    return att


def setup_test_data():
    """Setup test data"""
    return None


def test_all_on_time():
    """Test: All 4 punches on time - should count as 8 hours"""
    today = date.today()
    
    att = create_mock_attendance(
        time(8, 0, 0),      # check_in - on time
        time(12, 0, 0),     # check_out - on time
        time(13, 0, 0),     # check_in_2 - on time
        time(17, 0, 0),     # check_out_2 - on time
        today
    )
    
    att.calculate_working_hours()
    print(f"✓ All on-time test: {att.working_hours}h (expected 8.0)")
    assert att.working_hours == 8.0, f"Expected 8.0, got {att.working_hours}"


def test_check_in_late_5_min():
    """Test: Check-in 5 minutes late (0.1s-30min) - deduct 0.5"""
    today = date.today()
    
    att = create_mock_attendance(
        time(8, 5, 0),      # check_in - 5 min late
        time(12, 0, 0),     # check_out - on time
        time(13, 0, 0),     # check_in_2 - on time
        time(17, 0, 0),     # check_out_2 - on time
        today
    )
    
    att.calculate_working_hours()
    expected = 8.0 - 0.5  # 7.5
    print(f"✓ Check-in 5min late test: {att.working_hours}h (expected {expected})")
    assert att.working_hours == expected, f"Expected {expected}, got {att.working_hours}"


def test_check_out_late_45_min():
    """Test: Check-out 45 minutes early (30min-1hour) - deduct 1.0"""
    today = date.today()
    
    att = create_mock_attendance(
        time(8, 0, 0),      # check_in - on time
        time(11, 15, 0),    # check_out - 45 min early
        time(13, 0, 0),     # check_in_2 - on time
        time(17, 0, 0),     # check_out_2 - on time
        today
    )
    
    att.calculate_working_hours()
    expected = 8.0 - 1.0  # 7.0
    print(f"✓ Check-out 45min early test: {att.working_hours}h (expected {expected})")
    assert att.working_hours == expected, f"Expected {expected}, got {att.working_hours}"


def test_check_in2_late_35_min():
    """Test: Afternoon check-in 35 minutes late (30min-1hour) - deduct 1.0"""
    today = date.today()
    
    att = create_mock_attendance(
        time(8, 0, 0),      # check_in - on time
        time(12, 0, 0),     # check_out - on time
        time(13, 35, 0),    # check_in_2 - 35 min late
        time(17, 0, 0),     # check_out_2 - on time
        today
    )
    
    att.calculate_working_hours()
    expected = 8.0 - 1.0  # 7.0
    print(f"✓ Afternoon check-in 35min late test: {att.working_hours}h (expected {expected})")
    assert att.working_hours == expected, f"Expected {expected}, got {att.working_hours}"


def test_multiple_deductions():
    """Test: Multiple punches with issues - cumulative deduction"""
    today = date.today()
    
    att = create_mock_attendance(
        time(8, 10, 0),     # check_in - 10 min late (deduct 0.5)
        time(12, 0, 0),     # check_out - on time
        time(13, 25, 0),    # check_in_2 - 25 min late (deduct 0.5)
        time(17, 0, 0),     # check_out_2 - on time
        today
    )
    
    att.calculate_working_hours()
    expected = 8.0 - 0.5 - 0.5  # 7.0
    print(f"✓ Multiple deductions test: {att.working_hours}h (expected {expected})")
    assert att.working_hours == expected, f"Expected {expected}, got {att.working_hours}"


def test_check_out2_early_50_min():
    """Test: Afternoon checkout 50 min early (30-60min) - deduct 1.0"""
    today = date.today()
    
    att = create_mock_attendance(
        time(8, 0, 0),      # check_in - on time
        time(12, 0, 0),     # check_out - on time
        time(13, 0, 0),     # check_in_2 - on time
        time(16, 10, 0),    # check_out_2 - 50 min early
        today
    )
    
    att.calculate_working_hours()
    expected = 8.0 - 1.0  # 7.0
    print(f"✓ Afternoon checkout 50min early test: {att.working_hours}h (expected {expected})")
    assert att.working_hours == expected, f"Expected {expected}, got {att.working_hours}"


def run_all_tests():
    """Run all tests"""
    print("Running Time Deduction Tests...\n")
    
    try:
        test_all_on_time()
        test_check_in_late_5_min()
        test_check_out_late_45_min()
        test_check_in2_late_35_min()
        test_multiple_deductions()
        test_check_out2_early_50_min()
        
        print("\n✅ All tests passed!")
        return True
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
