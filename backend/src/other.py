from src.data_store import data_store
# Resets the data store
def clear_v1():
    store = data_store.get()
    store['session_num'] = 0
    store['message_num'] = 0
    store['users'].clear()
    store['channels'].clear()
    store['dms'].clear()
    store['workspace_stats'].clear()
    data_store.set(store)

    return {}
