# CS-350-relfection
Final project for CS 350: Implementation of a thermostat prototype using a Raspberry Pi, AHT20 temperature sensor, buttons, LEDs, UART output, and a state machine design. Includes code artifacts and reflection.

CS 350 Thermostat Project

This repository contains my final project for CS 350 where I developed a thermostat prototype using a Raspberry Pi and several hardware components. The project demonstrates how embedded software interacts with sensors, displays, buttons, LEDs, and communication interfaces using a state machine design.

Project Artifacts

This repository includes the files used to build and test the thermostat system. These files include FinalProject.py, DisplayTest.py, TemperatureSensorTest.py, MultiButtonTest.py, and the state machine diagram in PDF format.

Reflection

Summary of the Project
This project involved creating a functioning thermostat prototype that simulates how a real thermostat monitors temperature, responds to user input, and communicates information through a display and UART output. The prototype solves the problem of demonstrating how embedded systems support real world device behavior and how these systems connect to larger architectures.

What I Did Well
I integrated multiple hardware components and software modules into a working system. I managed the temperature sensor, LCD, LEDs, and button input in a way that allowed the thermostat to operate consistently. I also handled debugging effectively, especially identifying that my LCD used a parallel interface instead of I2C and adjusting my code accordingly.

Where I Could Improve
I want to improve my skills with breadboard wiring and understanding hardware layouts. I sometimes struggled with pin arrangements and wiring details, and becoming more comfortable reading diagrams will help future projects.

Tools and Resources I Added to My Support Network
I used Adafruit documentation, Raspberry Pi libraries, and Python modules for GPIO, sensors, and display control. I also became more comfortable using GitHub for managing and presenting project files.

Transferable Skills
This project strengthened my ability to design state driven systems, work with interrupts, read sensors over I2C, manage PWM LED behavior, and organize embedded code. These skills will transfer directly into other IoT projects, embedded coursework, and automation tasks.

How I Made This Project Maintainable and Adaptable
I organized the code into clear functions that separate each part of the system. The structure makes the project easy to read and modify. Because the system follows a well defined state machine, it can be expanded to include new features, such as Wi-Fi communication, without rewriting major parts of the program.

How to Run the Project
Place the required files on the Raspberry Pi. Install the necessary Python packages. Run the program using sudo python3 FinalProject.py. Use the buttons to change modes and adjust the temperature set point.
