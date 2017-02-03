from test_multiproc import DoSomething, DoSomethingElse


WORKERS = {
    'DoSomething': {
        'class': DoSomething,
        'filename_for_output': 'output',
        'path': '/home/bogdan/Projects/vkscraper/DoSomething/',
    },
    'DoSomethingElse': {
        'class': DoSomethingElse,
        'filename_for_output': 'output',
        'path': '/home/bogdan/Projects/vkscraper/DoSomethingElse/',
    }
}
