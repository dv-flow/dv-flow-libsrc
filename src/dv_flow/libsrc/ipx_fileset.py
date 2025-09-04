import xml.etree.ElementTree as ET

class IPXFileSet:
    def __init__(self, file, filesets=None):
        self.file = file
        self.filesets = filesets or []

    def run(self):
        tree = ET.parse(self.file)
        root = tree.getroot()
        ns = {'ipxact': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2014'}

        # Find all fileSets
        file_sets = []
        for fs in root.findall('.//ipxact:fileSet', ns):
            name = fs.find('ipxact:name', ns).text
            files = []
            for f in fs.findall('ipxact:file', ns):
                file_entry = {
                    'name': f.find('ipxact:name', ns).text,
                    'type': f.find('ipxact:fileType', ns).text,
                    'description': (f.find('ipxact:description', ns).text if f.find('ipxact:description', ns) is not None else '')
                }
                files.append(file_entry)
            file_sets.append({'name': name, 'files': files})

        # Filter fileSets if names provided, else use first
        if self.filesets:
            print("IPXFileSet: filtering for filesets =", self.filesets)
            print("IPXFileSet: available fileset names =", [fs['name'] for fs in file_sets])
            selected = [fs for fs in file_sets if fs['name'] in self.filesets]
        else:
            selected = file_sets[:1] if file_sets else []

        return selected
