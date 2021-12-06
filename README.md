## Description

This tool is designed to intake a Workflow Execution File (WEX) from Smartsheet Connectors and return a more user friendly output. Note that testing was primarily completed using Jira and Salesforce Connectors. I haven't tested every possible combination of configuration so there is a change you may encoutner errors depending on how things are configured. 

## Requirements

1. Access to a Smartsheet Connector. Smartsheet Connectors are a paid premium add-on for Smartsheet. Please reach out to [Smartsheet Sales](https://www.smartsheet.com/contact/sales) to inquire about purchasing Smartsheet / Connectors.
2. A WEX file downloaded from the Connector.

## Steps to Obtain a WEX File

1. In the Connector dashboard, select the timestamp under the Run Date column of the workflow. This will bring you to the workflow run history where you can see any error messages for each run.
2. Select the timestamp under Last Run for the latest run of the workflow.
3. On following page, go to the hamburger menu (three horizontal lines in the upper left) and choose Download Workflow Execution Support Info.

## Steps to Run

1. Install [Python](https://www.python.org/downloads/)
2. Clone this repo or download as zip and extract into your desired project directory.
3. Run the script from terminal or IDE of your choosing. 

## Output Example

```
Workflow Name: 
Nathan Sandbox Project 1 - Jira Connector WEX Parsing Example

Mapped Project Key(s): 
NSP1

Mapped Smartsheet Name: 
Jira Connector WEX Parsing Example

Field Mappings (Column to Jira Field): 
{'Affected Versions': 'Affected Versions',
'Assignee': 'Assignee',
'Assignee Display Name': 'Assignee Display Name',
'Creation Date': 'Creation Date',
'Description': 'Description',
'Issue Key': 'Issue Key',
'Issue Links': 'Issue Links',
'Issue Type': 'Issue Type',
'Priority': 'Priority',
'Reporter Email Address': 'Reporter Email Address',
'Status': 'Status',
'Summary': 'Summary'}

Jira Filters: 
["JQL = issuetype in ('Epic', 'Story', 'Bug') AND status in ('To Do', 'In "
"Progress')"]

Sheet Filters: 
[('Sync to Jira', 'EQUALS', 'true')]

Groups: 
['IssueType', 'AssigneeEmail', 'Priority']
```

