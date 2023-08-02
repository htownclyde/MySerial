import queue
import serial
import threading
import dearpygui.dearpygui as dpg
import serial.tools.list_ports as port_list

ports = {}

def connect(port=None, baudrate=None, bytesize=None, parity=None, stopbits=None, timeout=None):
    if port == "" or None: port = "COM0"
    if baudrate == "" or None: baudrate = 115200
    if bytesize == "" or None: bytesize = 8
    if parity == "" or None: parity = "N"
    if stopbits == "" or None: stopbits = 1
    if timeout == "": timeout = None
    try: ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout)
    except: return
    ser.close()
    ser.open()
    ser_thread = threading.Thread(name="ser_thread", target=serial_connection(ser))
    ser_thread.start()

def input_handler():
    global command_queue
    while 1:
        command_queue.put(input(''))

def serial_connection(ser):
    global command_queue
    rx_buffer = []
    try:
        if not command_queue.empty():
            command_string = command_queue.get()+'\r\n'
            ser.write(bytes(command_string, 'utf-8'))
        while 1:
            rx = ser.read()
            print(rx.decode('utf-8'), end='', flush=True)
    except KeyboardInterrupt:
        ser.close()

def connect_callback():
    global ports
    connect(ports[dpg.get_value("port_listbox")], dpg.get_value("input_baudrate"), dpg.get_value("input_bytesize"), dpg.get_value("input_parity"),
            dpg.get_value("input_stopbits"), dpg.get_value("input_timeout"))

def update_callback():
    global ports
    for port_string in port_list.comports():
        port_string = str(port_string)
        port = port_string.split(" ")[0]
        ports[port_string] = port
    dpg.configure_item("port_listbox", items=list(ports.keys()))

def dpg_thread():
    global gui_width, gui_height
    gui_width = 800
    gui_height = 600
    input_width = 100
    dpg.create_context()
    dpg.create_viewport(title='Serial Communication Tool', width=gui_width, height=gui_height)
    with dpg.window(tag="command_window", label="Serial Command Panel", width=gui_width, height=gui_height):
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False):
                dpg.add_listbox(tag="port_listbox", num_items=15)
                dpg.add_button(tag="update_button", label="Update", callback=update_callback)
            with dpg.group(horizontal=False):
                dpg.add_button(tag="connect_button", label="Connect", callback=connect_callback)
                with dpg.group(horizontal=False):
                    dpg.add_text(default_value="Baud rate:")
                    dpg.add_input_text(tag="input_baudrate", width=input_width)
                with dpg.group(horizontal=False):
                    dpg.add_text(default_value="Byte Size:")
                    dpg.add_input_text(tag="input_bytesize", width=input_width)
                with dpg.group(horizontal=False):
                    dpg.add_text(default_value="Parity:")
                    dpg.add_input_text(tag="input_parity", width=input_width)
                with dpg.group(horizontal=False):
                    dpg.add_text(default_value="Stop bits:")
                    dpg.add_input_text(tag="input_stopbits", width=input_width)
                with dpg.group(horizontal=False):
                    dpg.add_text(default_value="Timeout:")
                    dpg.add_input_text(tag="input_timeout", width=input_width)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
    dpg.destroy_context()

if __name__ == "__main__":
    command_queue = queue.Queue()
    input_thread = threading.Thread(name="input_thread", target=input_handler)
    input_thread.start()
    gui_thread = threading.Thread(name="gui_thread", target=dpg_thread)
    gui_thread.start()
    while(1):
        ...