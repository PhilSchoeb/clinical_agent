"""
A singleton class that generates sequential patient codes in the format '0000001', '0000002', etc.
Ensures that each generated code is unique within the runtime session.
"""


class PatientCodeGenerator:
    _instance = None
    _counter = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PatientCodeGenerator, cls).__new__(cls)
        return cls._instance

    def generate_patient_code(self):
        self._counter += 1
        # format "0000001", "0000002",
        return f"{self._counter:07d}"
