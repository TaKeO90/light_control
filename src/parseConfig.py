from typing import NamedTuple

class Config(NamedTuple):
    start_time: str
    stop_time: str

    def write_config_file(self, filename:str):
        data = f"""start_time: {self.start_time}
stop_time: {self.stop_time}
"""
        with open(filename, "w") as f:
            f.writelines(data)


def load_config(filename:str):
    with open(filename,"r") as f:
        content = f.readlines()

    content = map(lambda x: x.strip("\n"), content)
    
    d = dict.fromkeys(list(Config.__dict__['_fields']), "")

    for c in content:
        k, v = c.split(":")[0].strip(), (":").join(c.split(":")[1:]).strip()
        d[k] = v


    start, stop = [d[k] for k in d]

    return Config(start, stop)
