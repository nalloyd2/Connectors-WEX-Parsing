**Description**
Tool to intake a Workflow Execution File (WEX) from Smartsheet Connectors and return a more user friendly output. Note that testing was primarily completed using Jira and Salesforce Connectors. 

**Requirements**
1. Access to a Smartsheet Connector. Smartsheet Connectors are a paid premium add-on for Smartsheet. Please reach out to [Smartsheet Sales](https://www.smartsheet.com/contact/sales) to inquire about purchasing Smartsheet / Connectors.
2. A WEX file downloaded from the Connector.

**Output Example**

>Workflow Name: 
>Nathan Sandbox Project 1 - Jira Connector WEX Parsing Example
>
>Mapped Project Key(s): 
>NSP1
>
>Mapped Smartsheet Name: 
Jira Connector WEX Parsing Example
>
>Field Mappings (Column to Jira Field): 
>{'Affected Versions': 'Affected Versions',
 >'Assignee': 'Assignee',
 >'Assignee Display Name': 'Assignee Display Name',
 >'Creation Date': 'Creation Date',
 >'Description': 'Description',
 >'Issue Key': 'Issue Key',
 >'Issue Links': 'Issue Links',
 >'Issue Type': 'Issue Type',
 >'Priority': 'Priority',
 >'Reporter Email Address': 'Reporter Email Address',
 >'Status': 'Status',
 >'Summary': 'Summary'}
>
>Jira Filters: 
>["JQL = issuetype in ('Epic', 'Story', 'Bug') AND status in ('To Do', 'In "
 >"Progress')"]
>
>Sheet Filters: 
>[('Sync to Jira', 'EQUALS', 'true')]
>
>Groups: 
>['IssueType', 'AssigneeEmail', 'Priority']


