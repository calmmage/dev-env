from dev_env.core.ffs import create_dirs, clone_projects


def setup():
    create_dirs()
    clone_projects()


if __name__ == "__main__":
    setup()
