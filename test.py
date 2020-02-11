# -8- coding: utf-8 -*-
from unittest import TestCase
from uuid import uuid4

from eventsourcing.application.sqlalchemy import SQLAlchemyApplication

from esexampletodolists.application import TodoListApplication


class TestApplication(TestCase):
    def test(self):
        # Construct application.
        with TodoListApplication.mixin(SQLAlchemyApplication)() as app:


            # assert isinstance(app, TodoListApplication)
            # Check the user initially has no lists.
            user_id = uuid4()

            todo_list = app.get_list(user_id)
            self.assertIsNone(todo_list)

            todo_list_ids = app.get_todo_list_ids(user_id)
            self.assertEqual(todo_list_ids, [])

            # Start a new list.
            todo_list_id = app.start_todo_list(user_id)

            # Check the user has one list.
            todo_list_ids = app.get_todo_list_ids(user_id)
            self.assertEqual(todo_list_ids, {todo_list_id})

            # Check the list has no items.
            self.assertEqual(app.get_todo_items(todo_list_id), ())

            # Add an item to the list.
            app.add_todo_item(todo_list_id=todo_list_id, item='item1')

            # Check the list has one item.
            self.assertEqual(app.get_todo_items(todo_list_id), ('item1',))

            # Update the item.
            app.update_todo_item(todo_list_id=todo_list_id, index=0, item='item1.1')

            # Get the list and see it has the updated item.
            self.assertEqual(app.get_todo_items(todo_list_id), ('item1.1',))

            # Discard the item, and check by getting the list and checking it has no items.
            app.discard_todo_item(todo_list_id=todo_list_id, index=0)
            self.assertEqual(app.get_todo_items(todo_list_id), ())

            # Discard the list, and check there are no list IDs for the user.
            app.discard_todo_list(todo_list_id=todo_list_id)
            todo_list_ids = app.get_todo_list_ids(user_id)
            self.assertEqual(len(todo_list_ids), 0)
