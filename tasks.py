from invoke import task

@task
def test(c):
    """
    Run tests
    """
    c.run("python -m unittest discover")
