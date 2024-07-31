# LIFE ACTUARIAL CASHFLOW MODEL APP

<<<<<<< HEAD
[image of desktop monitor with green theme](public\assets\main-img-wide-jpg.jpg)

## About

This application is powered by Python, and is designed to assist life actuaries in projecting their insurance liability cashflows.
It seamlessly integrates with your existing pricing Excel models.
Users simply need to 'link' this application to their pricing model by specifying the directory path of the Excel file and the names of the tables and input parameters defined in the Excel file—then you're all set.

With this 'link' design, users no longer need to prepare separate input files to run the Python-based model.

The main idea for this app is to have a user-friendly interface that could connect excel model with Python - so actuaries can continue working with their excel model comfortably, while utilising the flexibility and power of Python language.

## Release 1.0.0-beta - Initial Pre-release Preview

This release (https://github.com/ibrahimcode85/life_cashflow_app/releases/tag/v1.0.0-beta) contains all the basic features to connect excel model and Python scripts.

- Path to the excel model can be defined for the app to get the necessary data (i.e. model parameters and tables)
- The input and tables name used in the excel model can be defined in the app. So users do not need to recreate additional files for the python model to run.

### Getting Started

1. Get the application zip file `life_cashflow_app-win32-x64-1.0.0` in the release section. The main files provided:

   - The executable file : `.\life_cashflow_app.exe`.
   - The sample excel model where the Python script is based on : `.\resources\app\resources\pricing_model.xlsx`.

2. Navigate to _Input Settings_ and specify the directory path to the Excel file, along with the names of the tables and input parameters defined in the Excel file. These inputs has been populated based on the sample excel model (just need to update the path directory for the excel model.)

3. Navigate to _Output Settings_ to specify the format and type of output to be generated. Again this has been pre-populated - please choose your option before proceeding.

4. Click the _Run Button_ from the navigation bar. This will execute Prophet script. The run log can be displayed directly within this application or a separate log file can be generated as one of the output files for audit purposes (please select this option in the _Output Settings_).

## Future Enhancement Roadmap

- [ ] Enhanced graphical user interface - by allowing user to select tables and cells directly in excel (instead of specifying the names). We plan to utilize SheetJS to display the Excel interface.
- [ ] Allowing greater flexibility for user to define their own Python script. Instead of connecting with pre-built script, user can defined the path of their script and execute them.

## Feedback

I created this application as a hobby. But you are welcome to provide any feedback to make it better or report any bugs or issues you encounter.
