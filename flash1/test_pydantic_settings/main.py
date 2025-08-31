import pydantic
import enum

class StrelaControllerSettings(pydantic.BaseModel):
    class BaudRates(int, enum.Enum):
        BaudRate9600 = 9600
        BaudRate115200 = 115200

    port: str
    baud_rate: BaudRates
class StrelaApplicationSettings(pydantic.BaseModel):
    machine_name: pydantic.constr(min_length = 5) | None
    controller: StrelaControllerSettings

if __name__ == '__main__':
    settings = StrelaApplicationSettings.model_validate_json(open('./config.json', 'r').read())
    print(settings)
    settings.machine_name = "qwerty"
    print(settings)
    settings.machine_name = "qwe"
    print(settings)


