
# Update Project Items <sub>New GitHub Projects</sub>

Update a specific field for several items at once. You can filter what items to update (e.g. any item with a "Date" before 2022-01-01) and then specify the field to update (e.g. set "Status" as 'Stale'). Note that this works specifically with the new [GitHub Projects](https://github.com/features/issues)

Use this Action if you're trying to update items in bulk. If you're planning on updating just one item or a few, use my colleague's faster Action: [austenstone/project-update](https://github.com/austenstone/project-update) :)

### Why?
There's already a few Actions that update a single item on a project, but I wanted one that bulk updates several items easily without having to rely on huge workflow matrices. This Action is also a bit more flexible in that you can filter what items you want to update.


## Inputs

````yaml
- uses: eldrick19/bulk-project-update@main
  with:
    token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
    project-number: 123
    org: my-org
    update-field: Status
    update-value: "Updated"
````

The above would would update every item's "Status" field to "Updated"

Possible inputs:

|Input|Description|
|---|---|
|token| **Required**. The PAT used to interact with the Project. For the new GitHub Projects, as of right now, you will have to use [classic PATs](https://docs.github.com/en/enterprise-cloud@latest/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-personal-access-token-classic). Make sure your token has at least the `project` scope.|
|project-number|**Required**. The Project Number. You can find this by looking at the URL of your Project.|
|update-field| **Required**. The field you want to update. This can be the Title, a Custom field, etc. Case-sensitive.|
|update-value|**Required**. The new value you want to set. For example you can update a date fields to this new value.|
|filter-field|**Optional**. This is the field we'll look at for each item in the project, and check if it meets the condition. If this field is left empty, we'll assume you're not filtering for specific items, and we'll update all items in the project.|
|conditional|**Optional**. Compares the value of an item's field to the `filter-value` (e.g. <). See [supported field types](#suported-field-types) for more information on what's available|
|filter-value|**Optional**. The value you want to filter items on|
|org|**Optional**. The organization/user that holds your project. By default we'll take the org/user that your Action is in (i.e. based on the repository from which it's called)|

## Supported Field Types

To filter items, you can use the following field types:

|Field Type|Supported Conditionals|Input Format|
|---|---|---|
|Text (including the Title)| ==, !=|`"Here is text"`|
|Date|==, !=, <, <=, >, >=|`YYYY-MM-DD`|
|Number|==, !=, <, <=, >, >=|`123`|

To update items, you can use the following field types and their corresponding format from above:

- Text (including the Title)
- Date
- Number

<!-- NOTE: Labels and PRs. For these specific field types, you'll have to check the OAuth permissions for the organization you're connecting to. If restrictions are in place, data access to third parties will be limited, including this Action.

This happens because the Labels and PRs are object that exist outside of the Project.   -->

## Contributing

Contributions welcome. Feel free to also submit an issue with suggestions/questions as well!

There's a few issues I've opened myself for improvements to possible field types and conditional options. Can tackle those if there's interest.

To get started, check out the resources folder for sample files