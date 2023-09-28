#graphical dependencies
import tkinter as tk
import ttkbootstrap as tb
from tkinter import END

#graphs
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
plt.style.use('ggplot')

#data storage and retrieval dependences
from datetime import datetime, timedelta
import pandas as pd
import xml.etree.ElementTree as ET
import os
from requests_ntlm import HttpNtlmAuth
from urllib.parse import quote
from xml.dom import minidom
import copy

#threading
import requests
import concurrent.futures
import threading




matplotlib.use("Tkagg") #needed to avoid TclError


class UltimateIRTool:
    def __init__(self, root):
        self.frame = tb.Frame(root)  
        ##create text box report will go in
        self.txt = tb.Text(self.frame, state='disabled', width=40, height=20)
        self.txt.grid(row=0, column=0, sticky='nw')
        #self.username = username
        #self.password = password
        # Ask for the username and password
        

        #loading_var gives status updates as the application runs
        self.loading_var = tk.StringVar()
        self.loading_label = tb.Label(self.frame, textvariable=self.loading_var)
        self.loading_label.grid(row=2, column=0, sticky='ew')
        self.refresh_button = tb.Button(self.frame, text="⟲", 
                                        bootstyle= 'info.outline', command=lambda: threading.Thread(target=self.initialize_report).start())
        self.refresh_button.grid(row=0, column=2, sticky='n')
        #creates a progress bar- goes up as progress is made
        self.progressbar = tb.Progressbar(self.frame, bootstyle='info-striped',
                                          maximum=100,
                                          mode='determinate',
                                          value=0)
        self.progressbar.grid(row=3, column=0, sticky='ew')
        self.product_tree = tb.Treeview(self.frame, columns=[0,2], show="headings", bootstyle = "dark", selectmode='extended')
        self.product_tree.grid(row=0, column=3, padx=5, pady=5, sticky="ns")
        self.product_tree.heading(0, text= 'Product')
        self.product_tree.heading(1, text= 'Counts')
        self.product_tree.column(
            column=0,
            width= 200
        )
        self.product_tree.column(
            column=1,
            width= 60
        )
        self.taskstate_tree = tb.Treeview(self.frame, columns=[0,1,2], show="headings", bootstyle = "dark", selectmode='extended')
        self.taskstate_tree.grid(row=0, column=4, padx=5, pady=5, sticky="ns")
        self.taskstate_tree.heading(0, text= 'TaskState')
        self.taskstate_tree.heading(1, text= 'Counts')
        self.taskstate_tree.heading(2, text= 'Inactive')
        self.taskstate_tree.column(
            column=0,
            width= 150
        )
        self.taskstate_tree.column(
            column=1,
            width= 100
        )
        self.taskstate_tree.column(
            column=2,
            width= 100
        )
        
         # Create the Figure and Subplot early so you can update them later
        self.fig = Figure(figsize=(3, 2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor('none')
        self.ax.set_facecolor('none')
        # Create a canvas for your Figure and grid it onto your frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        #self.canvas.get_tk_widget().grid(row=1, column=3, sticky='ne')

        threading.Thread(target=self.initialize_report).start()
#activates report generation every hour on the hour        
    #def schedule_at_hour(self):
    #    # Get the current time
    #    now = datetime.now()
    #    # Get the minutes, seconds and microseconds till the next hour
    #    minutes_till_next_hour = 59 - now.minute
    #    seconds_till_next_hour = 59 - now.second
    #    microseconds_till_next_hour = 999999 - now.microsecond
    #    # Calculate total milliseconds till the next hour
    #    total_milliseconds_till_next_hour = (minutes_till_next_hour * 60 * 1000) + (seconds_till_next_hour * 1000) + (microseconds_till_next_hour // 1000)
    #    # Schedule the report
    #    self.frame.after(total_milliseconds_till_next_hour, lambda: threading.Thread(target=self.initialize_report).start())              
#activates data gathering on multiple threads using concurrent futures
#waits for all of them to finish and then activates report generation
    def initialize_report(self):
        self.progressbar['value'] = 0 #reset progress bar
        self.loading_var.set("Fetching...") #update progress indicator
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(fn) for fn in [self.read_oc_pages,  self.count_folders]}  #self.read_sla_page,

            for future in concurrent.futures.as_completed(futures):
                try:
                    data = future.result()
                    # do something with the data if needed
                except Exception as exc:
                    print(f"An exception occurred: {exc}")

        self.generate_report()
        now = datetime.now()
        time_string = now.strftime("%H:%M:%S")

        # Set the loading_var to include the time when the report has finished fetching
        self.loading_var.set(f"Last Updated at {time_string}.") 

        #self.schedule_at_hour() #schedule next report at hour mark
# not in use anymoer just keeping this as an example i ncase I want to make another graph    
    def create_graph(self):
        # Counts of 'primaryProductName'
        counts = self.data_frames[0]['deliveryProductName'].value_counts()

        # Clear the subplot
        self.ax.clear()

        # Generate the bar graph
        self.ax.bar(counts.index, counts.values)
        self.ax.set_xlabel('Delivery Product ')
        self.ax.set_ylabel('Count')
        self.ax.set_title('Counts')

        # Redraw the canvas (this is what makes it dynamic)
        self.canvas.draw()
#pulls data from OPS SLA power BI page      
    def read_sla_page(self):
        try:
            username = self.username
            password = self.password

            # base url without any parameters
            base_url = "http://ssrs.ad.cmh.prod.evinternal.net/ReportServer?%2FOperationsBI%2FReports%2FPublic%2FOps%20-%20Response%20Time%20SLAs%202022"

            # parameters
            params = {
                "Hour": "1",
                "CreatedFlag": "False",
                "IncludeCAS": "False",
                "rs:ParameterLanguage": "",
                "rs:Command": "Render",
                "rs:Format": "XML",
                "rc:ItemPath": "table1",
            }

            # look at all these parameters
            encoded_params = ""

            # inserts the parameters
            for key, value in params.items():
                # If this isn't the first parameter, add an ampersand to separate it from the previous one
                if encoded_params:
                    encoded_params += "&"

                # URL encode the key and value and add them to the encoded parameters string
                encoded_key = quote(key)
                encoded_value = quote(value)
                encoded_params += f"{encoded_key}={encoded_value}"

            # Combine the base URL and the encoded parameters to get the full URL
            url = f"{base_url}&{encoded_params}"

            auth = HttpNtlmAuth(username, password)

            self.sla_response = requests.get(url, auth=auth)

            if self.sla_response.status_code != 200:
                print("Error: Unable to fetch the page. Status code:", self.sla_response.status_code)
                return None

            self.progressbar['value'] += 30 #increment the progress bar
            self.loading_var.set("Grabbed SLA Content") #this is the slowest function so no one should ever see this

            # Pretty print the xml content for debug
            xml = minidom.parseString(self.sla_response.content)
            pretty_xml = xml.toprettyxml()

            print(pretty_xml) #we print the SLA page response to the console to make sure we didn't completely screw the pooch on it

            return self.sla_response.content  

        except requests.exceptions.RequestException as err:
            print ("RequestException Error:",err)
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except Exception as e:
            print("An error occurred: ", e)
#makes request to the new OC due today and usr pages     
    def read_oc_pages(self):
        headers = {
            "User-Agent": "MadelynHourlyReportScript/1.0 (Contact: madelyn.bailey@eagleview.com; Purpose: grabbing specific counts for generating an hourly report.)",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5"
        }
        urls = [
            "https://api.cmh.platform-prod2.evinternal.net/operations-center/api/TaskTrafficView/?type=21&value=ChangeDetection&type=11&value=True&type=17&value=ReadyForReportFilesArchiving&type=17&value=ReportFilesArchived&type=45&value=Pending-CustomerResponse&type=17&value=Closed&type=32&value=test&type=21&value=EagleView%20OnSite&type=45&value=InProcess-ReadyToCapturePayment&type=45&value=InProcess-UnderReview&type=21&value=Claims%20Assignment&type=21&value=D2M%20-%20Assess%20Detect&type=17&value=ReportFilesBeingArchived&type=32&value=training&type=21&value=Assess%20Detect&type=17&value=PendingNotification&type=45&value=Closed-CanceledByClient&type=45&value=Pending-CreditCardFailure&type=45&value=Completed-Sent&type=17&value=Completed&type=45&value=Pending-SiteMap&type=21&value=EagleView%20Assess&type=21&value=Assess%20View&type=45&value=Completed-SentPM&",
            "https://api.cmh.platform-prod2.evinternal.net/operations-center/api/TaskTrafficView/?type=16&value=ReadyForNoImagesVerification&type=26&value=true&type=30&value=Test&type=30&value=Pilot&type=30&value=training&type=18&value=HQ&"
        ]

        self.data_frames = []

        for i, url in enumerate(urls):
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                self.data_frames.append(copy.deepcopy(df))
                print(f"DataFrame {i+1}:")
                print(df)
                print("\n")
            else:
                print(f"Failed to retrieve data from {url}")
        self.loading_var.set("Grabbed OC Data")
        self.progressbar['value'] += 40
#interprets the responses as pandas dataframes and extracts relevant data                 
    def parse_oc_pages(self):
        #data frame[0] = due today
        #data frame[1] = usr queue
        
        #remove items from due today with substatus of under review or readytocapturepayment 
        self.data_frames[0] = self.data_frames[0][~self.data_frames[0]['subStatus'].isin(['UnderReview', 'ReadyToCapturePayment'])]
        
        #standardize date time stamps 
        self.data_frames[0]['dueDate'] = pd.to_datetime(self.data_frames[0]['dueDate'], format='mixed')
        now = pd.to_datetime('now')

        #get the total count of due today 
        total_count = len(self.data_frames[0])

        # past due
        past_due_df = self.data_frames[0][self.data_frames[0]['dueDate'] < now]
        past_count = len(past_due_df)

        # due in two hours
        two_hours_later = now + pd.Timedelta(hours=2)
        future_due_df = self.data_frames[0][(self.data_frames[0]['dueDate'] >= now) & (self.data_frames[0]['dueDate'] <= two_hours_later)]
        future_count = len(future_due_df)

        #count late items with "INC" in the notes column
        ticketed_count = len(self.data_frames[0].loc[(self.data_frames[0]['dueDate'] < now) & 
                                                    self.data_frames[0]['notes'].str.contains('INC', na=False)])


        usr_count  = len(self.data_frames[1]) 
        print(usr_count)
        
        self.progressbar['value'] +=30
        self.loading_var.set("Parsed OC Content")
        
        self.product_counter()
        self.append_taskstate_counts_to_tree()
        self.create_graph()
        return total_count, past_count, ticketed_count, future_count, usr_count
#count # of each product type on due today 
    def product_counter(self):
        for col in self.data_frames[0].columns:
            print(col)
        # First, count the number of each unique entry in the 'primaryProductName' column
        counts = self.data_frames[0]['primaryProductName'].value_counts()

        # Clear the existing tree entries
        self.product_tree.delete(*self.product_tree.get_children())

        # Now append these counts to your treeview
        for product_name, count in counts.items():
            self.product_tree.insert("", "end", values=(product_name, count))
#identify each task state on due today and     
    def append_taskstate_counts_to_tree(self):
        # First, get a count of each unique entry in the 'taskState' column
        task_state_counts = self.data_frames[0]['taskState'].value_counts()

        # Also count the number of 'False' entries in the 'active' column for each 'taskState'
        inactive_counts = self.data_frames[0][self.data_frames[0]['active'] == False]['taskState'].value_counts()

        # Clear the existing tree entries
        self.taskstate_tree.delete(*self.taskstate_tree.get_children())

        # Now append these counts to your treeview
        for task_state in task_state_counts.index:
            count = task_state_counts[task_state]
            inactive_count = inactive_counts.get(task_state, 0)  # Default to 0 if task_state is not found in inactive_counts
            self.taskstate_tree.insert("", "end", values=(task_state, count, inactive_count))
#interprets XML response of OPS sla page  
    def parse_sla_page(self):
        # Parse the XML content
        content = self.sla_response.content
        root = ET.fromstring(content)
        counter_inprocess_underreview = 0
        counter_created = 0
        # Get the namespace from the root element
        namespace = {'ns': root.tag.split('}')[0].strip('{')}
    
        # Iterate over each "Detail" element in the XML
        for detail in root.findall('.//ns:Detail', namespace):
            # Extract the "MinutesLate" and "Status" attributes
            minutes_late = int(detail.attrib['MinutesLate'])
            status = detail.attrib['Status']

            # If "MinutesLate" is negative...
            if minutes_late < 0:
                # If "Status" is "InProcess-UnderReview", increment the counter
                if status == "InProcess-UnderReview":
                    counter_inprocess_underreview += 1
                # If "Status" begins with "Created-", increment the counter
                elif status.startswith("Created-"):
                    counter_created += 1
        self.progressbar['value'] +=10
        return counter_inprocess_underreview, counter_created
#counts the number of files with a particular extension that the count_folders hands to it
    def count_delivery_folders(self, directory, extension):
        return len([f for f in os.listdir(directory) if f.endswith(extension)])
#creates a rounded to the hour datetime stamp as a report header   
    def get_rounded_datetime(self):
        now = datetime.now()

        # Round to the nearest hour
        if now.minute >= 30:
            now = now + timedelta(hours=1)

        # Replace minutes with "00" 
        now = now.replace(minute=0, second=0)

        # Format the date and time
        timestamp = now.strftime('%m/%d/%y %I:%M %p')

        return timestamp
#handles data needed for folder counts   
    def count_folders(self):
        folders = {
            "QCP": 'S:/3_QCPassed_New/',
            "QCP1": 'S:/3_QCPassed_1/',
            "QCP2": 'S:/3_QCPassed_2/',
            "QCP3": 'S:/3_QCPassed_3/',
            "QCP4": 'S:/3_QCPassed_4/',
            "AutoDelivery": 'S:/3.1_AutoDelivery/',
            "Status Failure": 'S:/3.8_StatusFailures/',
            "ADF": 'S:/3.1_ManualDelivery/ADF/',
            "011NeedsPens": 'S:/2_Measured/QC/011NeedsPenetrations/InProgress/',
        }

        self.folder_counts = {}
        for name, path in folders.items():
            self.folder_counts[name] = self.count_delivery_folders(path, 'evm')
            self.progressbar['value'] +=5
        self.loading_var.set("Counted Delivery Folders")
#collects data generated into an easily readable report              
    def generate_report(self):
        # Clear the text widget
        self.txt.configure(state='normal')
        self.txt.delete('1.0', END)
        report_text = ""
        total_count, past_count, ticketed_count, future_count, usr_count = self.parse_oc_pages()
        timestamp = self.get_rounded_datetime()
        #counter_inprocess_underreview, counter_created = self.parse_sla_page()
        report_text = f"{timestamp}\n"
        report_text += f"Due Today: {total_count}\n"
        report_text += f"Passed Delivery SLA: {past_count} ({ticketed_count} ticketed)\n"
        report_text += f"Due Within 2 Hours: {future_count}\n"
        report_text += f"USR: {usr_count}\n"
        for folder, count in self.folder_counts.items():
            report_text += f"{folder}: {count}\n"
        
        report_text +=f"Passed Dropping SLA: \n"
        report_text +=f"Negative UR: \n"

        self.txt.insert(END, report_text)
        self.txt.configure(state='disabled')

