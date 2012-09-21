from enthought.traits.api import Str, Float, Range, Int, Bool, on_trait_change
from enthought.traits.ui.api import View, Item

import time
import socket

from io_driver import IODriver

class TCPDriver(IODriver):
  """
      TCP input driver.
  """
  
  name = Str('TCP Driver')
  view = View(
    Item(name='port', label='Port'),
    Item(name='show_debug_msgs', label='Show debug messages'),
    Item(name='buffer_size', label='Buffer size / kb'),
    Item(name='timeout', label='Timeout / s'),
    title='TCP input driver'
  )

  
  _sock = socket.socket()

  port = Range(1024, 65535, 34443)
  buffer_size = Range(1, 4096, 10) # no reason not to go above 4MB but there should be some limit.
  timeout = Float(10.0)
  ip = Str('0.0.0.0')
  show_debug_msgs = Bool(False)

  def open(self):
    print "Opening"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(self.timeout) # seconds
    s.setblocking(True)
    s.bind((self.ip, self.port))
    print "Listening..."
    s.listen(1)
    self._sock, (addr, _) = s.accept()
    print addr, " connected!"

  def close(self):
    print "Closing"
    self._sock.close()
  
  def receive(self):
    try:
        (data, _) = self._sock.recvfrom(1024*self.buffer_size)
        if self.show_debug_msgs:
            print "TCP driver: packet size %u bytes" %  len(data)
    except socket.timeout:
        return None
    return data

  def rebind_socket(self):
    self.close()
    self.open()

  @on_trait_change('port')
  def change_port(self):
    self.rebind_socket()
    
  @on_trait_change('address')
  def change_address(self):
    self.rebind_socket()

  @on_trait_change('timeout')
  def change_timeout(self):
    self.rebind_socket()
    
