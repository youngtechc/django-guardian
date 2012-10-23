
def show_db_config(settings, action):
    from django.utils.termcolors import colorize
    db_conf = settings.DATABASES['default']
    output = []
    msg = "Starting %s for db backend: %s" % (action, db_conf['ENGINE'])
    embracer = '=' * len(msg)
    output.append(msg)
    for key in sorted(db_conf.keys()):
        if key == 'PASSWORD':
            value = '****************'
        else:
            value = db_conf[key]
        line = '    %s: "%s"' % (key, value)
        output.append(line)
    embracer = colorize('=' * len(max(output, key=lambda s: len(s))),
        fg='green', opts=['bold'])
    output = [colorize(line, fg='blue') for line in output]
    output.insert(0, embracer)
    output.append(embracer)
    print '\n'.join(output)

