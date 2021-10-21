subscribers = {}

def subscribe(event_type: str, fn):
    if not event_type in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append(fn)

def post(event_type: str, *args, **kwargs):
    if not event_type in subscribers:
        return
    for fn in subscribers[event_type]:
        fn(*args, **kwargs)
