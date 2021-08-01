import uuid,string,json,base64
import ray
import barcode,pyqrcode,csv
from pathlib import Path
ray.init()



class GenSKU:
    fields=['SKU','Name','Price']
    @ray.remote
    def generate_sku(self)->str:
        return str(uuid.uuid4())

    def get_ready(self):
        obj=self.generate_sku.remote([])
        ready,notready=ray.wait([obj,])
        while notready:
            print(notready)
            ready,notready=ray.wait([obj,])
        for i in ready:
            yield ray.get(i)

    def write(self,fname,path,mode="a"):
        if Path(path).exists():
            skip_headers=True
            if Path(Path(path)/Path(fname)).exists():
                skip_headers=False
            with open(Path(path)/Path(fname),mode) as output:
                writer=csv.writer(output,delimiter=',')
                if skip_headers:
                    writer.writerow(self.fields)
                for sku in self.get_ready():
                    writer.writerow([sku,'',''])

    def __init__(self,fname,path,write_to_file=True,mode="a"):
        if write_to_file:
            self.write(fname,path,mode)


if __name__ == "__main__":
    GenSKU('holzcrafts.csv','.')
