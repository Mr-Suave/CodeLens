class Person:
    """Base class for all people in the school system."""
    
    def __init__(self, name, age, address):
        self.name = name
        self.age = age
        self.address = address
        self._id = None
    
    def get_info(self):
        """Return basic information about the person."""
        return f"{self.name}, {self.age} years old"
    
    @property
    def id(self):
        return self._id


class School:
    """Main school class that manages students and teachers."""
    
    def __init__(self, name, address, principal=None):
        self.name = name
        self.address = address
        self.principal = principal
        self.students = []
        self.teachers = []
        
        # Nested class for school resources
        class Resources:
            def __init__(self, budget, equipment):
                self.annual_budget = budget
                self.equipment = equipment
                self.allocated = {}
            
            def allocate(self, department, amount):
                if amount <= self.annual_budget:
                    self.allocated[department] = amount
                    self.annual_budget -= amount
                    return True
                return False
        
        # Create resources instance
        self.resources = Resources(1000000, ['computers', 'books', 'sports equipment'])
    
    def add_student(self, student):
        """Add a student to the school."""
        self.students.append(student)
        student.school = self
    
    def add_teacher(self, teacher):
        """Add a teacher to the school."""
        self.teachers.append(teacher)
        teacher.school = self
    
    def get_statistics(self):
        """Get statistics about the school."""
        return {
            "total_students": len(self.students),
            "total_teachers": len(self.teachers),
            "student_teacher_ratio": len(self.students) / max(1, len(self.teachers))
        }


class Student(Person):
    """Class representing a student in the school."""
    
    def __init__(self, name, age, address, grade_level):
        super().__init__(name, age, address)
        self.grade_level = grade_level
        self.courses = []
        self.grades = {}
        self.school = None
    
    def enroll(self, course):
        """Enroll student in a course."""
        self.courses.append(course)
    
    def assign_grade(self, course, grade):
        """Assign a grade to the student for a specific course."""
        if course in self.courses:
            self.grades[course] = grade
    
    def get_gpa(self):
        """Calculate student's GPA."""
        if not self.grades:
            return 0.0
        
        grade_points = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}
        total_points = sum(grade_points.get(grade, 0) for grade in self.grades.values())
        return total_points / len(self.grades)


class MiddleSchoolStudent(Student):
    """Class representing a middle school student (grades 6-8)."""
    
    def __init__(self, name, age, address, grade_level, homeroom_teacher):
        if not (6 <= grade_level <= 8):
            raise ValueError("Middle school students must be in grades 6-8")
        super().__init__(name, age, address, grade_level)
        self.homeroom_teacher = homeroom_teacher
        self.extracurricular_activities = []
    
    def add_activity(self, activity):
        """Add an extracurricular activity."""
        self.extracurricular_activities.append(activity)
    
    def is_eligible_for_student_council(self):
        """Check if student is eligible for student council."""
        return self.get_gpa() >= 3.0 and len(self.extracurricular_activities) >= 2


class HighSchoolStudent(Student):
    """Class representing a high school student (grades 9-12)."""
    
    def __init__(self, name, age, address, grade_level, counselor):
        if not (9 <= grade_level <= 12):
            raise ValueError("High school students must be in grades 9-12")
        super().__init__(name, age, address, grade_level)
        self.counselor = counselor
        self.service_hours = 0
        self.college_applications = []
        
        # Nested class for college application
        class CollegeApplication:
            def __init__(self, college_name, status="Pending"):
                self.college_name = college_name
                self.status = status  # "Pending", "Accepted", "Rejected"
                self.submitted_date = None
            
            def submit(self, date):
                self.submitted_date = date
            
            def update_status(self, new_status):
                self.status = new_status
        
        # Make the nested class accessible
        self.CollegeApplication = CollegeApplication
    
    def apply_to_college(self, college_name):
        """Apply to a college."""
        application = self.CollegeApplication(college_name)
        self.college_applications.append(application)
        return application
    
    def add_service_hours(self, hours):
        """Add community service hours."""
        self.service_hours += hours
    
    def is_eligible_for_graduation(self):
        """Check if student is eligible for graduation."""
        required_service_hours = 100
        return self.service_hours >= required_service_hours and self.get_gpa() >= 2.0


class Teacher(Person):
    """Class representing a teacher."""
    
    def __init__(self, name, age, address, subject, education_level):
        super().__init__(name, age, address)
        self.subject = subject
        self.education_level = education_level  # "Bachelor's", "Master's", "PhD"
        self.courses_taught = []
        self.students = []
        self.school = None
        
        # Nested class for teaching certification
        class Certification:
            def __init__(self, cert_type, issue_date, expiry_date):
                self.cert_type = cert_type
                self.issue_date = issue_date
                self.expiry_date = expiry_date
                self.is_valid = True
            
            def renew(self, new_expiry_date):
                self.expiry_date = new_expiry_date
            
            def invalidate(self):
                self.is_valid = False
        
        self.certifications = []
        self.Certification = Certification
    
    def add_certification(self, cert_type, issue_date, expiry_date):
        """Add a teaching certification."""
        cert = self.Certification(cert_type, issue_date, expiry_date)
        self.certifications.append(cert)
        return cert
    
    def assign_course(self, course):
        """Assign a course to the teacher."""
        self.courses_taught.append(course)
    
    def grade_student(self, student, course, grade):
        """Grade a student for a specific course."""
        if student in self.students and course in self.courses_taught:
            student.assign_grade(course, grade)
    
    def calculate_teaching_load(self):
        """Calculate the teacher's current teaching load."""
        return len(self.courses_taught) * 3  # 3 hours per course


class Course:
    """Class representing a course offered at the school."""
    
    def __init__(self, name, code, credits, teacher=None):
        self.name = name
        self.code = code
        self.credits = credits
        self.teacher = teacher
        self.students = []
        self.max_capacity = 30
        
        # Nested class for course materials
        class Material:
            def __init__(self, title, type_of_material):
                self.title = title
                self.type = type_of_material  # "Textbook", "Handout", "Digital"
                self.assigned_date = None
            
            def assign(self, date):
                self.assigned_date = date
        
        self.materials = []
        self.Material = Material
    
    def add_material(self, title, type_of_material):
        """Add course material."""
        material = self.Material(title, type_of_material)
        self.materials.append(material)
        return material
    
    def enroll_student(self, student):
        """Enroll a student in the course."""
        if len(self.students) < self.max_capacity:
            self.students.append(student)
            student.enroll(self)
            return True
        return False
    
    def is_at_capacity(self):
        """Check if the course is at capacity."""
        return len(self.students) >= self.max_capacity


# Example usage
if __name__ == "__main__":
    # Create a school
    central_high = School("Central High School", "123 Education Lane")
    
    # Create a teacher
    mrs_jones = Teacher("Sarah Jones", 45, "456 Teacher St", "Mathematics", "Master's")
    mrs_jones.add_certification("Advanced Mathematics", "2020-01-15", "2025-01-15")
    central_high.add_teacher(mrs_jones)
    
    # Create courses
    algebra = Course("Algebra I", "MATH101", 3, mrs_jones)
    algebra.add_material("Algebra Fundamentals", "Textbook")
    
    # Create students
    john = HighSchoolStudent("John Smith", 16, "789 Student Ave", 10, "Mr. Davis")
    john.add_service_hours(50)
    central_high.add_student(john)
    
    mary = MiddleSchoolStudent("Mary Johnson", 13, "101 Young St", 7, "Ms. Williams")
    mary.add_activity("Chess Club")
    central_high.add_student(mary)
    
    # Enroll students in courses
    algebra.enroll_student(john)
    algebra.enroll_student(mary)
    
    # Teacher grades students
    mrs_jones.grade_student(john, algebra, "A")
    mrs_jones.grade_student(mary, algebra, "B")
    
    # John applies to a college
    application = john.apply_to_college("State University")
    application.submit("2024-11-01")