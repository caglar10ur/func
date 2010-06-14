import fact_module

class ArchitectureFacts(fact_module.BaseFactModule):

    version = "0.0.1"
    description = "A modules that supplies architecture facts"

    def __init__(self):
        super(ArchitectureFacts,self).__init__()

    def architecture(self):
        for line in file("/proc/cpuinfo"):
            if line.startswith("flags"):
                flags = line.split(":", 1)[1].strip().split()

        if flags.__contains__("lm"):
            return "x86_64"
        else:
            return "x86"
    
    architecture.tag = "arch"
