import PySimpleGUI as sg
import sys
import model_generator
import configparser
import validation

"""
    Generates Open API Specification from an XMI design model
"""


def runGUI():
    path_guid = ''
    type_guid = ''
    f_in = ''
    f_out = ''

    if not sys.platform.startswith('win'):
        sg.popup_error('Sorry, you gotta be on Windows')
        sys.exit(0)
    sg.change_look_and_feel('Dark Blue 3')      # because gray windows are boring

    config = configparser.RawConfigParser()
    with open('config.ini', 'r+') as configfile:
        config.read_file(configfile)

    layout = [
        [sg.Text('Reverse Open API Specification', auto_size_text=True)],
        [sg.Text('Path GUID', size=(12, 1)),
         sg.Input(key="i-1", size=(80, 1), default_text=config['default']['path_guid'])],
        [sg.Text('Types GUID', size=(12, 1)),
         sg.Input(key='i-2', size=(80, 1), default_text=config['default']['type_guid'])],
        [sg.Text('Yaml file', size=(12, 1)),
         sg.Input(key="i-3", size=(80, 1), default_text=config['default']['f_in']),
         sg.FileBrowse()],
        [sg.Text('Sparx DB file', size=(12, 1)),
         sg.Input(key='i-4', size=(80, 1), default_text=config['default']['f_out']),
         sg.FileBrowse()],
        [sg.Button('Generate', key="Generate"),
         sg.Button('Exit', key="Exit")]]

    window = sg.Window('Reverse Open API Specification',
                       layout, auto_size_text=False, default_element_size=(22, 1),
                       text_justification='right')

    while True:     # Event Loop
        event, values = window.read()
        if(event == "Generate"):
            config['default'] = {}
            config['default']["path_guid"] = values["i-1"]
            config['default']['type_guid'] = values["i-2"]
            config['default']['f_in'] = values["i-3"]
            config['default']['f_out'] =  values["i-4"]
            # update config file
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            
            path_guid = values["i-1"]
            type_guid = values["i-2"]
            f_in = values["i-3"]
            f_out = values["i-4"]
            # verify input data
            msg = validation.is_valid_input(f_in, f_out, path_guid, type_guid)
            if (msg != ""):
                sg.popup_error(f"There are validation errors: \n{msg}", title="Validation Error")
            else:
                try:
                    model_generator.generate_model(f_in, f_out, path_guid, type_guid)
                    sg.popup_auto_close('Model has been generated', title="Completed", auto_close_duration=10)
                except Exception as e:
                    sg.popup_error(f"An error has been encountered: \n {e}", title="Error")

        elif(event == "Exit"):
            config['default'] = {}
            config['default']["path_guid"] = values["i-1"]
            config['default']['type_guid'] = values["i-2"]
            config['default']['f_in'] = values["i-3"]
            config['default']['f_out'] =  values["i-4"]
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            sys.exit(0)
        elif event is None:
            break

    window.close()

if __name__ == '__main__':
    runGUI()
