#Process WEX files and output user friendly results
import json
import logging
import os
import pprint
import time

#Setup INFO Logging
log_formatter = logging.Formatter('%(message)s')
file_logger = logging.getLogger(__name__)
file_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('WEX_file_parsed.txt')
file_logger.addHandler(file_handler)
file_handler.setFormatter(log_formatter)

#Log to console
#console_logger = logging.getLogger().addHandler(logging.StreamHandler())

#Get Mapped Jira Projects
def mapped_projects(wex_json):

    try:
        mapped_projects = wex_json['workflow']['body']['data']['leftEndpoint']['externalEndpointID']
        for r in (('{"externalEndpointIDs":', ''), ('}', '')):
            mapped_projects = mapped_projects.replace(*r)

    except KeyError:
        mapped_projects = wex_json['workflow']['body']['data']['leftEndpoint']['externalEndpointID']

    return mapped_projects

#Generate LeftColumnID List. This is a list of the fields mapped in the workflow.
def field_mapping_list(wex_json):
    leftColumnID_list = []
    for fieldMapping in wex_json['workflow']['body']['data']['columnMapping']['columnMappingEntries']:
        try:
            leftColumnID_list.append(fieldMapping['leftColumnID'])
        except KeyError as e:
            print(f'Could not find "leftColumnID" in {fieldMapping}!')

    #print(f'List of leftColumnIDs: {leftColumnID_list}')
    return leftColumnID_list

#Jira Fields Canonical List
def left_field_canon(canonical_names):
    fields_list_canonical = []
    for data in canonical_names:
        if data['canonicalName'] is not None:        
            fields_list_canonical.append(data['canonicalName'])
        
    return(fields_list_canonical)

#Jira fields Display Names
def left_field_display(display_names):
    fields_list_display = []
    for data in display_names:
        if data['displayName'] is not None:        
            fields_list_display.append(data['displayName'])
        
    return(fields_list_display)

#Get the Jira Canonical info
def jira_leftColumnInfo(wex_json):
    return wex_json['leftColumnInfos']['body']['data']

#Get Smartsheet Canonical Info
def smar_rightColumnInfo(wex_json):
    try:
        return wex_json['rightColumnInfos']['body']['data']
    except KeyError:
        print('Something went wrong when trying to unpack Smartsheet column information. The user who downloaded the WEX likely does not have access to the sheet. Please have the workflow owner download the WEX then try again.')
        input('Press enter to exit...')
        exit()

#Smar Canonical List
def right_field_canon(canonical_names):
    fields_list_canonical = []
    for data in canonical_names:
        if data['canonicalName'] is not None:        
            fields_list_canonical.append(data['canonicalName'])
        
    return(fields_list_canonical)

#Smar Display Names
def right_field_display(display_names):
    fields_list_display = []
    for data in display_names:
        if data['displayName'] is not None:        
            fields_list_display.append(data['displayName'])
        
    return(fields_list_display)

#Find the matching Display Name for a given LeftColumnID/Canonical Name for mapped fields
def find_field_matches(column_mapping, canonical_names):
    
    matching_displayNames = []

    # Iterate over all leftColumnIDs first
    for leftColumnID in column_mapping:
        # Then iterate over data list.
        for data in canonical_names:
            if data['canonicalName'] == leftColumnID:
                matching_displayNames.append(data['displayName'])
                break
    
    return matching_displayNames

#Get list of columns that are mapped
def column_mapping_list(wex_json):
    rightColumnID_list = []
    for columnMapping in wex_json['workflow']['body']['data']['columnMapping']['columnMappingEntries']:
        try:
            rightColumnID_list.append(columnMapping['rightColumnID'])
        except KeyError as e:
            print(f'Could not find "leftColumnID" in {columnMapping}!')
    
    return rightColumnID_list

#Get the column display names
def column_displayName(wex_json):
    return wex_json['rightColumnInfos']['body']['data']

#Find matching column display name for mapped columns
def find_column_matches(column_mapping, column_canonical_names):
    matching_displayNames = []
    # Iterate over all rightColumnIDs first
    for rightColumnID in column_mapping:
        # Then iterate over data list.
        for data in column_canonical_names:
            if data['canonicalName'] == rightColumnID:
                matching_displayNames.append(data['displayName'])
                break
             
    return matching_displayNames

#Build column ID / Name dict
def column_dict(column_mapping, column_canonical_names):
    mapped_columns = {}
    # Iterate over all rightColumnIDs first
    for rightColumnID in column_mapping:
        # Then iterate over data list.
        for data in column_canonical_names:
            if data['canonicalName'] == rightColumnID:
                mapped_columns[rightColumnID] = data['displayName'] #build column dict for later use
                break
             
    return mapped_columns

#Get the Jira filters that are mapped
def map_jira_filters(wex_json, fields_dictionary):
    
    jira_filters = []
    #loop = 0
    for filterMapping in wex_json['workflow']['body']['data']['filterLeftToRight']['filters']:
        #loop += 1
        try: #Try for JQL first
        
            jira_filters.append('JQL = ' + filterMapping['query'])

        except KeyError:
            try: #Try for normal AND filters
                for k in fields_dictionary:

                    if k == filterMapping['columnName']:
                        jira_filters.append((fields_dictionary.get(k), filterMapping['operator'], filterMapping['value'])) 
     
            except KeyError:
                
                if filterMapping['type'] == 'OR' or 'AND':    
                
                    try: #Try for OR / AND with multiple value options
                        for k in fields_dictionary:
                            if k == filterMapping['columnName']:
                                jira_filters.append((fields_dictionary.get(k), filterMapping['operator'], list(i['value'] for i in filterMapping['filters'])))
                    
                    except KeyError:
                        file_logger.info('Someting went wrong : /') #If we get this deep and get a KeyError it's likely I'm not accounting for some filter scenario

    return jira_filters
        
#Get Sheet filters that are mapped
def map_sheet_filters(wex_json, column_dictionary):

    sheet_filters = []
    sheet_filters_raw = wex_json['workflow']['body']['data']['filterRightToLeft']['filters']

    for filterMapping in sheet_filters_raw:
        
        try: #Try for normal AND filters
            for k in column_dictionary:
                if k == filterMapping['columnName']:
                    sheet_filters.append((column_dictionary.get(k), filterMapping['operator'], filterMapping['value'])) 
            
        except KeyError:
            
            if filterMapping['type'] == 'OR' or 'AND':    
            
                try: #Try for OR / AND with multiple value options
                    for k in column_dictionary:
                        if k == filterMapping['columnName']:
                            sheet_filters.append((column_dictionary.get(k), filterMapping['operator'], list(i['value'] for i in filterMapping['filters'])))
                
                except KeyError:
                    file_logger.info('someting went wrong.') #If we get this deep and get a KeyError it's likely I'm not accounting for some filter scenario
          
    return sheet_filters

#Get Grouping Definitions
def get_groups(wex_json):

    groups = []
    for ID in wex_json['workflow']['body']['data']['columnMapping']['hierarchyLevels']:
        groups.append(ID['columnID'])
    
    return groups

#Main Function
def main(wex_json):
    
    #Connector Type
    print('Confirming connector type...')
    time.sleep(1)
    connector_type = wex_json['supportInfoRequest']['connectorType']
    
    #workflow name
    print('fetching Workflow Name...')
    time.sleep(1)
    workflow_name = wex_json['workflow']['body']['data']['name']
    
    # Mapped Projects / Objects
    
    if connector_type == 'JIRA':
        print('fetching Jira projects...')
        time.sleep(1)
        jira_projects = mapped_projects(wex_json)  

    elif connector_type == 'SALESFORCE':
        print('fetching Salesforce objects...')
        time.sleep(1)
        salesforce_object = wex_json['workflow']['body']['data']['leftEndpoint']['externalEndpointID']

    elif connector_type == 'GENERIC':
        print('fetching Dynamics objects...')
        time.sleep(1)
        dyamics_object = wex_json['workflow']['body']['data']['leftEndpoint']['externalEndpointID']

    #Mapped Sheet
    print('fetching mapped sheet...')
    time.sleep(1)
    mapped_sheet = wex_json['workflow']['body']['data']['rightEndpoint']['name']

    #Functions for finding user readable field mappings
    print('fetching mapped fields...')
    time.sleep(1)
    field_mapping = field_mapping_list(wex_json)
    left_field_info = jira_leftColumnInfo(wex_json)
    right_field_info = smar_rightColumnInfo(wex_json)
    column_mapping = column_mapping_list(wex_json)

    column_canonical_names = column_displayName(wex_json)
    field_matching_displayNames = find_field_matches(field_mapping, left_field_info)
    column_matching_displayNames = find_column_matches(column_mapping, column_canonical_names)

    #Build Dicts
    """Jira Field Dictionaries"""
    all_fields_canonical_names = left_field_canon(left_field_info)
    all_fields_display_names = left_field_display(left_field_info)
    fields_dictionary = dict(zip(all_fields_canonical_names, all_fields_display_names))

    """Smartsheet Column Dictionaries"""
    all_column_canonical_names = right_field_canon(right_field_info)
    all_column_display_names = right_field_display(right_field_info)
    column_dictionary = dict(zip(all_column_canonical_names, all_column_display_names))

    """Field Mappings Dictionary (Columns : Fields)"""
    columns_to_fields_dictionary = dict(zip(column_matching_displayNames, field_matching_displayNames))
    column_to_fields_dict_formatted = json.dumps(columns_to_fields_dictionary, indent=1)

    #Map out Jira and Sheet filters
    print('fetching configured filters...')
    time.sleep(1)
    left_filters = map_jira_filters(wex_json, fields_dictionary)
    sheet_filters = map_sheet_filters(wex_json, column_dictionary)

    #Get Grouping definitions
    print('fetching configured grouping...')
    time.sleep(1)
    workflow_groups = get_groups(wex_json)

    #print(fields_dictionary)
    print('Logging to file...')
    time.sleep(1)
    if connector_type == 'JIRA':

        file_logger.info('Workflow Name: ' + '\r' + str(workflow_name) + '\r')
        file_logger.info('Mapped Project Key(s): ' + '\r' + str(jira_projects) + '\r')
        file_logger.info('Mapped Smartsheet Name: ' + '\r' + str(mapped_sheet) + '\r')
        file_logger.info('Field Mappings (Column to Jira Field): ' + '\r' + str(pprint.pformat(columns_to_fields_dictionary)) + '\r')
        file_logger.info('Jira Filters: ' + '\r' + str(pprint.pformat(left_filters)) + '\r')
        file_logger.info('Sheet Filters: ' + '\r' + str(pprint.pformat(sheet_filters)) + '\r')
        file_logger.info('Groups: ' + '\r' + str(pprint.pformat(workflow_groups)) + '\r')
    
    elif connector_type == 'SALESFORCE':

        file_logger.info('Workflow Name: ' + '\r' + str(workflow_name) + '\r')
        file_logger.info('Mapped Object: ' + str(salesforce_object) + '\r')
        file_logger.info('Field Mappings (Column : Salesforce Field): ' + str(column_to_fields_dict_formatted) + '\r')
        file_logger.info('Salesforce Filters: ' + str(left_filters) + '\r')
        file_logger.info('Sheet Filters: ' + '\r' + str(pprint.pformat(sheet_filters)) + '\r')
        file_logger.info('Groups: ' + '\r' + str(pprint.pformat(workflow_groups)) + '\r')

    elif connector_type == 'GENERIC':
    
        file_logger.info('Workflow Name: ' + '\r' + str(workflow_name) + '\r')
        file_logger.info('Mapped Object: ' + str(dyamics_object) + '\r')
        file_logger.info('Field Mappings (Column : Dynamics Field): ' + str(column_to_fields_dict_formatted) + '\r')
        file_logger.info('Dynamics Filters: ' + str(left_filters) + '\r')
        file_logger.info('Sheet Filters: ' + '\r' + str(pprint.pformat(sheet_filters)) + '\r')
        file_logger.info('Groups: ' + '\r' + str(pprint.pformat(workflow_groups)) + '\r')

    #Update a sheet  
    #sheet_updates = sheet_updater(columns_to_fields_dictionary, jira_filters, sheet_filters)

if __name__ == '__main__':
 
    wex_file_path = input('Drag your WEX file into the terminal...    ').replace('"', '')
    base = os.path.splitext(wex_file_path)[0]
    wex_json_file = os.rename(wex_file_path, base + '.json')
    wex_file = open(base + '.json')
    wex_json = json.load(wex_file)

    if 'orgSupportInfo' in str(wex_file): #or wex_json['workflows'] is not None:
        
        print('\n' + 'It looks like you have added an Account Support Info file rather than a WEX file. Please capture a WEX file and try again.' + '\n'  + '\r' +
        'Instructions for gathering Workflow Support Info File:' + '\n' + '\r' +

        '1. In the Jira Connector dashboard, select the timestamp under the Run Date column of the workflow.' + '\n' +  'This will bring you to the workflow run history where you can see any error messages for each run.' + '\n' + 
        '2. Select the timestamp under Last Run for the latest run of the workflow.' + '\n' + '(If you see Completed with Errors select that entry)' + '\n' + '\r' +
        '3. On following page, go to the hamburger menu (three horizontal lines in the upper left)' + '\n' + 'and choose Download Workflow Execution Support Info.' + '\n' + '\r')
        
        input('Press Enter to exit...')
        quit()
    
    #Start Main function to parse through the WEX and log outputs
    main(wex_json)
    print('WEX file parsed. Please see the result file for details.')
    input('Press Enter to exit...')
