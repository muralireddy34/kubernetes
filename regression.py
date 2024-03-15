#!/bin/python3
import os
import subprocess
import sys
import time
import random
import csv
import time
import shutil
from datetime import datetime
# Function to remove log files from the current working directory

def remove_logs():
    
    # Specify the name of the output CSV file
    output_csv_file = 'output.csv'
    try:
        # Check if the file exists
        if os.path.exists(output_csv_file):
            # Remove the file
            os.remove(output_csv_file)
            print(f"File '{output_csv_file}' deleted successfully.")
        else:
            print(f"File '{output_csv_file}' not found.")
    except Exception as e:
        print(f"Error deleting the file: {e}")

# Function to generate logs based on test cases
def generate_logs():
    output_filename = 'output.csv'
    pass_value = 1
    uvm_Error= []
    UVM_ERR_M = []
    pass_value =[]
    error_values = {}
    seed = 0
    error_counts = {}
    current_timestamp = datetime.now().strftime("%Y-%m-%d")
    with open("errors_file.txt") as f:
        lines = f.read().splitlines()
        for line in lines:
            # Remove ' :'
            cleaned_line = line.replace(' :', '')
            # Initialize the dictionary with zero
            error_counts[cleaned_line] = 0
    # Print the resulting dictionary
    print("error_counts",error_counts)

    with open("errors_file.txt") as f:
        names = f.read().replace(' :','').splitlines()
        print('test',names)
    with open("output.csv", 'a', newline='') as csvfile:
        #with open("errors_file.txt")
        fieldnames = ['File_name', 'seed', 'Run_Time','Pass'] + names + ['Error_messages']

        csvwriter = csv.writer(csvfile)
        # writing the fields
        csvwriter.writerow(fieldnames)
        # Open output_file.txt in write mode
        # Open TestCases_list.txt in read mode
        with open("TestCases_list.txt", "r") as test:
            # Read lines from the test cases file
            lines = test.readlines()
            # Initialize a list to store cleaned test case names
            test_case_names = []
            runs = []
            result = []
            pass_value =[]
            errors_list =[]
            error_values = {}
            try:
                with open("errors_file.txt", 'r') as fil:
                    for lin in fil:
                        errors_list.append(lin.strip())
                #print(errors_list)
            except FileNotFoundError:
                print(f"Error: File '{errors_file.txt}' not found.")
            # except Exception as e:
            #     print(f"Error: {e}")
            for line in lines:
                #print(line)
                # Split the line by ","
                parts = line.strip().split(' ')
                #print(parts)
                # Ensure that the line contains the expected format with two parts
                if len(parts) == 2:
                    # Extract the test case name from the first part
                    test_case_name = parts[0].strip()
                    test_case_names.append(test_case_name)
                    # Extract the run value from the second part
                    run1 = parts[1].strip().split('=')[1].strip()
                    runs.append(int(run1))
            for test_case_name, runs in zip(test_case_names, runs):
                print("\n")
                #print(test_case_name)
                current_timestamp1 = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                if runs != 0:
                    for run in range(1, runs + 1):
                        #print("run", run)
                        l2 = []  # Initialize an empty list to store results for CSV writing
                        l1 = []  # Initialize an empty list to store individual run details
                        # run make command
                        print("Working directory: ",os.getcwd())
                        os.system("make -f makefile {} TEST={}".format('run_test',test_case_name))
                        #log_file = 'ct_axi2ahb_rd_incr_addr_random_data_burst_len_tx_test_2.log'
                        try:
                            log_file = test_case_name + ".log"
                            vdb_file = test_case_name + ".vdb"
                            #vdb_file= "test.vdb"
                            with open(log_file, 'r') as file:
                                for line in file:
                                    #print(line)
                                    for i in error_counts:
                                        # Check for UVM_ERROR in the log
                                        if line.startswith(i):
                                            try:
                                                # Split the line and attempt to extract the numeric value after ':'
                                                values = int(line.split(':')[1].strip())
                                                # Update the corresponding value in the dictionary
                                                error_counts[i] += values
                                            except ValueError:
                                                # Handle the case where the value is not an integer
                                                print(f"Could not convert value to integer in line: {line}")
                                print("error_values",error_counts)
                                # for i in error_values.values():
                                    # Check if any element is equal to 0
                                if all(i == 0 for i in error_counts.values()):
                                    pass_value = 'Pass'
                                else:
                                    pass_value = 'Fail'
                            UVM_ERR_M =[]
                            with open(log_file, 'r') as f1:
                                for line in f1:
                                    for i in error_counts.keys():
                                        # Extract UVM_FATAL messages
                                        if error_counts[i] >= 1 and (line.startswith(i + " " + '@') or line.startswith(i + " " + '..')):
                                            UVM_ERR_M.append(line.strip())
                                                # print("UVM_ERR_M",UVM_ERR_M)
                            # Extract the seed value from the log
                            with open(log_file, 'r') as f2:
                                for line in f2:
                                    if line.startswith('NOTE: automatic random seed used:'):
                                        seed = (line.split(':')[2].strip())
                                    if line.startswith('Time: '):
                                        time = (line.split(':')[1].strip())

                            # Append individual run details to l1 list
                            l1.append(test_case_name)
                            l1.append(seed)
                            l1.append(time)
                            l1.append(pass_value)
                            for i in error_counts.values():
                                l1.append(i)
                            l1.append(UVM_ERR_M)
                            # Append individual run details to l2 list for CSV writing
                            l2.append(l1)
                            for i in l2:
                                # writing the data
                                csvwriter.writerow(i)
                            # row_data = l2 + list(error_values.values())
                            # csvwriter.writerow(row_data)
                            with open("errors_file.txt") as f:
                                # line = f.read().replace(' :','').splitlines()
                                lines = f.read().splitlines()
                                for line in lines:
                                    # Remove ' :'
                                    cleaned_line = line.replace(' :', '')
                                    # Initialize the dictionary with zero
                                    error_counts[cleaned_line] = 0

                            # Specify the path for the first directory
                            #first_directory = "logs_"+current_timestamp
                            base_name, extension = os.path.splitext(log_file)
                            # Construct the new file name
                            new_file = f"{base_name}_"f"{seed}{extension}"
                            # name.append(new_file1)
                            # Rename the file
                            os.rename(log_file, new_file)
                            first_directory = f"logs_{current_timestamp}"
                            print(first_directory)
                            # Check if the first directory exists, if not, create it
                            if not os.path.exists(first_directory):
                                os.makedirs(first_directory)
                                print(f"Directory '{first_directory}' created successfully.")
                            # Append the current timestamp to the test_case_name
                            test_case_name_with_timestamp = f"{test_case_name}_{current_timestamp1}"
                            # Specify the path for the second directory inside the first directory
                            second_directory = os.path.join(first_directory, test_case_name_with_timestamp)
                            # Check if the second directory exists, if not, create it
                            if not os.path.exists(second_directory):
                                os.makedirs(second_directory)
                                print(f"Directory '{second_directory}' created successfully.")
                            # Append date and time information to the destination path for hi.txt
                            destination_path = os.path.join(second_directory, new_file)
                            # Move the hi.txt file to the destination path
                            shutil.move(new_file, destination_path)

                            #Extract file extension
                            base_name, extension = os.path.splitext(vdb_file)
                            # Construct the new file name
                            new_file1 = f"{base_name}_"f"{seed}{extension}"
                            # name.append(new_file)
                            # Rename the file
                            os.rename(vdb_file, new_file1)
                            # print(f"File renamed from '{filename}' to '{new_file}'.")
                            #first_directory1 = "vdb"
                            first_directory1 = f"vdbs_{current_timestamp}"
                            print(first_directory)

                            # Check if the first directory exists, if not, create it
                            if not os.path.exists(first_directory1):
                                os.makedirs(first_directory1)
                                print(f"Directory '{first_directory1}' created successfully.")
                            # Append the current timestamp to the test_case_name
                            test_case_name_with_timestamp = f"{test_case_name}_{current_timestamp1}"
                            # Specify the path for the second directory inside the first directory
                            second_directory1 = os.path.join(first_directory1, test_case_name_with_timestamp)
                            # Check if the second directory exists, if not, create it
                            if not os.path.exists(second_directory1):
                                os.makedirs(second_directory1)
                                print(f"Directory '{second_directory1}' created successfully.")
                            # Append date and time information to the destination path for hi.txt
                            destination_path1 = os.path.join(second_directory1, new_file)
                            shutil.move(new_file1, destination_path1)

                        except FileNotFoundError:
                            print(f"Error: File '{log_file}' not found.")
                        # except Exception as e:
                        #     print(f"Error: {e}")
                else:
                    pass
if __name__ == '__main__':
    remove_logs()
    generate_logs()