try:
    import API, prices, products
except(ImportError,):
    from . import products, prices