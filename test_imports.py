#!/usr/bin/env python3
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.routes import admin
from app.models.attendance import Attendance

print('Imports OK')
print('Has get_shift_breakdown:', hasattr(Attendance, 'get_shift_breakdown'))
print('Has get_shift_breakdown_labels:', hasattr(Attendance, 'get_shift_breakdown_labels'))
