import json
from datetime import datetime
import requests

# ---- HELPER FUNCTIONS ----

# Function that filters the items to update
def filter_items_to_update(data, filter_field, conditional, filter_value):
    item_ids = []
    item_names = []
    # If no filter is set, add all items to the list
    if not filter_field:
        print("No filter field specified. Updating all items.")
        for node in data:
          item_ids.append(node['id'])
    # Otheriwse, filter the items
    else:
      print("Filtering items to update...")
      for node in data:
        item_fields = node['fieldValues']['nodes']
        for item in item_fields:
            if item and item['field'] and item['field']['name']:
                if item['field']['name'] == filter_field:
                    match [item['field']['dataType'], conditional]:
                        case [('DATE'), ('==' | '!=' | '<' | '<=' | '>' | '>=')]:
                            exec("if datetime.strptime(item['date'][:10], '%Y-%m-%d') " + conditional + " datetime.strptime('" + filter_value + "', '%Y-%m-%d'):\n\titem_ids.append(node['id'])")
                        case [('TEXT' | 'TITLE' ), ('==' | '!=')]:
                            exec("if item['text'] " + conditional + " '" + filter_value + "':\n\titem_ids.append(node['id'])")
                        case [('NUMBER'), ('==' | '!=' | '<' | '<=' | '>' | '>=')]:
                            print(conditional, filter_value)
                            exec("if item['number'] " + conditional + " " + filter_value + ":\n\titem_ids.append(node['id'])")
                        case _:
                            print("Conditional not supported. Please check the action inputs.")
                            exit(1)
                # If the item field is the title, store the title (item name) to a variable for now
                elif item['field']['name'] == 'Title':
                    item_names.append(item['text'])
            # If we are at the end of the loop and the item ids list does not have the item id, that means we this item does not match the filter, so we should remove the item name from the list
            # We are keeping the item names in a separate list so that we can print the names of the items that will be updated. For logging purposes.
            if len(item_fields) == item_fields.index(item) + 1 and node['id'] not in item_ids:
                item_names.pop()
                
    return item_ids, item_names

# Function that gets the paramater based on the input field
def get_filter_field_parameter(data, input_field_name, parameter):
    filter_field_paramater = ''
    for node in data:
        item_fields = node['fieldValues']['nodes']
        for item in item_fields:
            if item and item['field'] and item['field']['name']:
                if item['field']['name'] == input_field_name:
                    filter_field_paramater = item['field'][parameter]
                    break

    return filter_field_paramater

# Function that gets the option id for a single select field given the input field name and option name
def get_option_id(data, input_field_name, option_name):
    option_id = ''
    for node in data:
        item_fields = node['fieldValues']['nodes']
        for item in item_fields:
            if item and item['field'] and item['field']['name']:
                if item['field']['name'] == input_field_name:
                    for option in item['field']['options']:
                        if option['name'] == option_name:
                            option_id = option['id']
                            break
    return option_id
    

# ---- QUERY FUNCTIONS ----

# Function that uses GraphQL to get the project data
def get_project_data(org, project_number, token):
    # GraphQL query
    query = '''
    {
      organization(login: "''' + str(org) + '''") {
        projectV2(number: ''' + str(project_number) + ''') {
          items(last: 100) {
                  nodes {
                    fieldValues(last: 100) {
                      nodes {
                        ... on ProjectV2ItemFieldTextValue {
                          text
                          field {
                            ... on ProjectV2Field {
                              name
                              dataType
                              id
                            }
                          }
                        }
                        ... on ProjectV2ItemFieldDateValue {
                          date
                          field {
                            ... on ProjectV2Field {
                              name
                              dataType
                              id
                            }
                          }
                        }
                        ... on ProjectV2ItemFieldSingleSelectValue {
                          name
                          field {
                            ... on ProjectV2SingleSelectField {
                              id
                              name
                              dataType
                              options {
                                id
                                name
                              }
                            }
                          }
                        }
                        ... on ProjectV2ItemFieldNumberValue {
                          number
                          field {
                            ... on ProjectV2Field {
                              name
                              dataType
                              id
                            }
                          }
                        }
                        ... on ProjectV2ItemFieldLabelValue {
                          field {
                            ... on ProjectV2Field {
                              id
                              name
                              dataType
                            }
                          }
                          labels(first: 10) {
                            edges {
                              node {
                                name
                              }
                            }
                          }
                        }
                        ... on ProjectV2ItemFieldPullRequestValue {
                          field {
                            ... on ProjectV2Field {
                              id
                              name
                              dataType
                            }
                          }
                          pullRequests(first: 10) {
                            edges {
                              node {
                                permalink
                                number
                              }
                            }
                          }
                        }
                      }
                    }
                    id
                  }
                }
                id
              }
            }
          }
    '''
    # Headers with authentication token
    headers = {
        'Content-Type': 'application',
        'Authorization': 'token ' + token,
    }
    # Request to GitHub GraphQL API with a timeout of 10 seconds
    response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers, timeout=10)
    # Check if the request was successful
    if response.status_code != 200:
        print("Query to your project failed to run by returning code of {}. Verify your inputs (token/org/project number)".format(response.status_code))
        exit(1)
    # Check if GraphQL query was successful
    if response.json().get('errors'):
        print("Query to your project failed to run by returning the following message: {}".format(response.json().get('errors')))
        exit(1)
    
    # Get Project ID and data
    project_id = response.json()['data']['organization']['projectV2']['id']
    data = response.json()['data']['organization']['projectV2']['items']['nodes']

    return project_id, data

# Function that sends a GraphQL mutation to update an item on a specified field
def update_item(update, token):
    # GraphQL mutation
    mutation = '''
    mutation {
      updateProjectV2ItemFieldValue(
        input: {
          projectId: "''' + str(update['project_id']) + '''"
          itemId: "''' + str(update['item_id']) + '''"
          fieldId: "''' + str(update['field_id']) + '''"
          value: {
            ''' + str(update['field_type']) + ''': ''' + str(update['field_value']) + '''
          }
        }
      ) {
        projectV2Item {
          id
        }
      }
    }
    '''
    # Headers with authentication token
    headers = {
        'Content-Type': 'application',
        'Authorization': 'token ' + token,
    }
    # Post to GitHub GraphQL API with a timeout of 10 seconds')
    response = requests.post('https://api.github.com/graphql', json={'query': mutation}, headers=headers, timeout=10)
    # Check if the request was successful
    if response.status_code != 200:
        print("Mutation to update item failed to run by returning code of {}. Verify your inputs (token/org/project number)".format(response.status_code))
        exit(1)
    # Check if GraphQL mutation was successful
    if response.json().get('errors'):
        print("Mutation to update item failed to run by returning the following message: {}".format(response.json().get('errors')))
        exit(1)


