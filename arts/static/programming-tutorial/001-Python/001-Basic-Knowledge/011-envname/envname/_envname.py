try:
    import platform
    envname = platform.processor() or 'null'
except:
    envname = 'null'