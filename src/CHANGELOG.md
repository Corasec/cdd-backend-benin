# Changelog

List of features add to the project

## unreleased

- updated `sync_tasks()` method to reflet previous change
- added `manager_role` to `task` model. Need to match `role` field of model `facilitator` to be assign to the agent (changed `task` and `facilitaor` related form views and template accordingly )
- changed administrative level allocation to agent
- `facilitator` is now agent with different role. `facilitator` is now an `agent` `role`
- added `role` field to `facilitator` model
- updating `views` relatives to phases, activities and tasks
- updated `FacilitatorListTableView` for search filter
- updated `FacilitatorListView` to match new administrative level structure
- changed `Administrativelevel` model to reflet Benin condition