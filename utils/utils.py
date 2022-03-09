import yaml
from yaml import SafeLoader


class FileUtils:

    @staticmethod
    def load_file(path: str, ext: str):
        parserMap[ext](path)

    @staticmethod
    def parseYaml(path: str):
        try:
            with open(path) as f:
                return yaml.load(f, Loader=SafeLoader)
        except (OSError, yaml.YAMLError):
            return None


parserMap = {
    'yaml': FileUtils.parseYaml
}

outputMap = {

}
