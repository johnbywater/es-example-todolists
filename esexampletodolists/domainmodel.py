from uuid import UUID, uuid4, uuid5

from eventsourcing.domain.model.aggregate import AggregateRoot
from eventsourcing.domain.model.collection import Collection

USER_LIST_COLLECTION_NS = UUID("af3e9b7b-22e0-4758-9b0b-c90949d4838e")


class TodoListCollection(AggregateRoot, Collection):
    pass


class TodoList(AggregateRoot):
    """Root entity of todo list aggregate."""

    def __init__(self, user_id, **kwargs):
        super(TodoList, self).__init__(**kwargs)
        self.user_id = user_id
        self.items = []

    class Event(AggregateRoot.Event):
        """Layer base class."""

    @classmethod
    def start(cls, user_id):
        todo_list_id = uuid4()
        return cls.__create__(
            originator_id=todo_list_id, user_id=user_id, event_class=cls.Started
        )

    class Started(Event, AggregateRoot.Created):
        """Published when a new list is started."""

    def add_item(self, item):
        """Adds item."""
        self.__trigger_event__(
            TodoList.ItemAdded, item=item,
        )

    class ItemAdded(Event):
        """Published when an item is added to a list."""

        @property
        def item(self):
            return self.__dict__["item"]

        def mutate(self, entity):
            entity.items.append(self.item)

    def update_item(self, index, item):
        """Updates item."""
        self.__trigger_event__(
            TodoList.ItemUpdated, index=index, item=item,
        )

    class ItemUpdated(Event):
        """Published when an item is updated in a list."""

        @property
        def index(self):
            return self.__dict__["index"]

        @property
        def item(self):
            return self.__dict__["item"]

        def mutate(self, entity):
            entity.items[self.index] = self.item

    def discard_item(self, index):
        """Discards item."""
        self.__trigger_event__(
            TodoList.ItemDiscarded, index=index,
        )

    class ItemDiscarded(Event):
        """Published when an item in a list is discarded."""

        @property
        def index(self):
            return self.__dict__["index"]

        def mutate(self, entity):
            entity.items.pop(self.index)


def make_user_list_collection_id(user_id, collection_ns=USER_LIST_COLLECTION_NS):
    return uuid5(collection_ns, str(user_id))
