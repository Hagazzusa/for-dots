extends Resource
## Immutable authored Korean text. StoryPanel copies pages before choosing a branch.
@export var title: String = ""
@export var pages: Array[String] = []
## Optional first-page choices. Each choice replaces the remaining pages with one response.
@export var choice_labels: Array[String] = []
@export var choice_responses: Array[String] = []
