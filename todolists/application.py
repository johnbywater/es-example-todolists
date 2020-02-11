from typing import Optional

from eventsourcing.application.simple import SimpleApplication
from eventsourcing.domain.model.collection import Collection

from todolists.domainmodel import (
    TodoList,
    TodoListCollection,
    make_user_list_collection_id,
)


class TodoListApplication(SimpleApplication):
    persist_event_type = (TodoList.Event, Collection.Event)

    def get_todo_list_ids(self, user_id):
        """Returns list of IDs of to-do lists for a user."""
        collection_id = make_user_list_collection_id(user_id)
        collection = self.get_collection(collection_id)
        if collection is not None:
            return collection.items
        else:
            return []

    def start_todo_list(self, user_id):
        """Starts new to-do list for a user."""
        todo_list = TodoList.start(user_id=user_id)
        collection = self.add_list_to_collection(todo_list.id, user_id)
        self.save([todo_list, collection])
        return todo_list.id

    def add_list_to_collection(self, todo_list_id, user_id):
        collection_id = make_user_list_collection_id(user_id)
        collection = self.get_or_create_collection(collection_id)
        collection.add_item(todo_list_id)
        return collection

    def get_or_create_collection(self, collection_id):
        collection = self.get_collection(collection_id)
        if collection is None:
            collection = TodoListCollection.__create__(originator_id=collection_id)
        return collection

    def remove_list_from_collection(self, todo_list_id, user_id):
        collection_id = make_user_list_collection_id(user_id)
        collection = self.get_collection(collection_id)
        if collection is not None:
            collection.remove_item(todo_list_id)
        return collection

    def add_todo_item(self, todo_list_id, item):
        """Added to-do item to a to-do list."""
        todo_list = self.get_list(todo_list_id)
        todo_list.add_item(item=item)
        self.save([todo_list])

    def get_todo_items(self, todo_list_id):
        """Returns a tuple of to-do items."""
        todo_list = self.get_list(todo_list_id)
        return tuple(todo_list.items)

    def update_todo_item(self, todo_list_id, index, item):
        """Updates a to-do item in a list."""
        todo_list = self.get_list(todo_list_id)
        todo_list.update_item(index, item)
        self.save([todo_list])

    def discard_todo_item(self, todo_list_id, index):
        """Discards a to-do item in a list."""
        todo_list = self.get_list(todo_list_id)
        todo_list.discard_item(index)
        self.save([todo_list])

    def discard_todo_list(self, todo_list_id):
        """Discards a to-do list."""
        todo_list = self.get_list(todo_list_id)
        todo_list.__discard__()
        collection = self.remove_list_from_collection(todo_list.id, todo_list.user_id)
        self.save([todo_list, collection])

    def get_collection(self, collection_id) -> Optional[TodoListCollection]:
        try:
            collection = self.repository[collection_id]
        except KeyError:
            pass
        else:
            assert isinstance(collection, TodoListCollection), collection
            return collection

    def get_list(self, todo_list_id) -> TodoList:
        try:
            todo_list = self.repository[todo_list_id]
        except KeyError:
            pass
        else:
            assert isinstance(todo_list, TodoList)
            return todo_list
