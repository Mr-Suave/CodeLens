The documentation generated for senior is as follows:123

# IIT Tirupati Student Database - Senior Developer Documentation

This project implements a student database management system using Java and object-oriented principles. It provides functionalities for adding, updating, deleting, and viewing student records.  The system distinguishes between undergraduate and graduate students, leveraging inheritance for code reusability.

## Dependencies

This project utilizes standard Java libraries and does not have any external dependencies.  It relies heavily on the `java.util` package for data structures like `ArrayList` and `HashMap`.

## Architecture and Structure

The code is structured around three core classes:

* **`Student`**:  This class represents a generic student and holds attributes like name, roll number, semester, courses, and faculty advisor. It provides a `toString()` method for formatted output of student information.

* **`GraduateStudent`**: This class extends the `Student` class using inheritance. It represents a graduate student and inherits all the attributes from the `Student` class. The `toString()` method is overridden to prepend "Graduate Student Details:" to the output.

* **`StudentDatabase`**:  This class manages the student database using a `HashMap` where the roll number serves as the key and the `Student` object as the value.  It provides methods for adding, updating, deleting, and viewing student records, as well as a helper method to check if a student exists.

* **`Viva`**: Contains the `main` method which drives the application's user interface. It presents a menu-driven system for user interaction, allowing for both admin and user modes.

## Key Functionalities and Logic

### Data Storage

The `StudentDatabase` class employs a `HashMap` to store student records.  This choice offers efficient retrieval of student information based on their roll number (key).  The `addStudent()` method checks for existing roll numbers before adding a new record.


### User Modes

The application distinguishes between admin and user modes:

* **Admin Mode**:  Allows for adding (both undergraduate and graduate students), updating, and deleting student records.  Input validation is performed, specifically to ensure unique roll numbers.


* **User Mode**: Allows viewing student details based on the roll number.

### Input Handling

The `Viva` class utilizes the `Scanner` class to handle user input, providing a simple command-line interface.  Input is parsed and validated as required. The `nextLine()` method is strategically used after `nextInt()` calls to consume newline characters, preventing issues with subsequent string input.


### Inheritance

The `GraduateStudent` class inherits from the `Student` class, demonstrating the use of inheritance to avoid code duplication. This promotes maintainability and extensibility.


## Critical Code Snippets

### Adding a Student:
```java
Student newStudent = new Student(name, rollNumber, semester, courses, facultyAdvisor);
studentDatabase.addStudent(newStudent);
```
This snippet demonstrates the creation of a `Student` object and its addition to the database.

### Updating a Student:
```java
Student updatedStudent = new Student(name, rollNumber, semester, courses, facultyAdvisor);
studentDatabase.updateStudent(rollNumber, updatedStudent);
```

This shows how an existing student record is updated with new information.

### Polymorphism:

```java
studentDatabase.addStudent(newGraduateStudent); //where newGraduateStudent is an instance of GraduateStudent
```
This line highlights polymorphism. Although `addStudent()` expects a `Student` object, it can accept a `GraduateStudent` object because `GraduateStudent` is a subclass of `Student`.


This structure ensures clear separation of concerns, with each class having a well-defined responsibility. The use of a `HashMap` for the database ensures efficient data retrieval, while the separation of admin and user modes provides a secure way to manage the student data. The inheritance implemented between the `Student` and `GraduateStudent` classes demonstrates good object-oriented design principles, enhancing code reusability and maintainability.  The code also provides basic input validation to enhance robustness.
