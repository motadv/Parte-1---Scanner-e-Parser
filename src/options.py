class Options:
    sets: bool = False
    m_table: bool = False
    graph: bool = False
    verbose: bool = False
    files_dir: str

    def __init__(
        self,
        argv: list[str],
        files_dir: str = "",
    ) -> None:
        if "-s" in argv:
            self.sets = True
            argv.remove("-s")
        if "-m" in argv:
            self.m_table = True
            argv.remove("-m")
        if "-g" in argv:
            self.graph = True
            argv.remove("-g")
        if "-v" in argv:
            self.verbose = True
            argv.remove("-v")
        self.files_dir = files_dir
