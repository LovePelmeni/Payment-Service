try:
    import API, products, subscriptions
except(ImportError,):
    from . import products, subscriptions