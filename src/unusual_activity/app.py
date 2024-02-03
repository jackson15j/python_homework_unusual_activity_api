from src.unusual_activity.main import (
    create_app,
    EventStore,
)

app = create_app(EventStore())
