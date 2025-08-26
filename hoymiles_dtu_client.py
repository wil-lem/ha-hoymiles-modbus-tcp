import logging
import asyncio
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException
import time


_LOGGER = logging.getLogger(__name__)


class HoymilesDtuClient:
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.client = None
        self.base_address = 0x2000
        self.microinverters = []
        # self.cache = {}
        
        # Connection settings
        self.connection_timeout = 10
        self.retry_on_empty = True
        self.retries = 3
        self.delay_on_connect = 0.5  # Small delay between requests

    async def connect(self):
        """Establish connection to the DTU."""
        if self.client is None:
            self.client = AsyncModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=self.connection_timeout,
#                retry_on_empty=self.retry_on_empty,
                retries=self.retries
#                delay_on_connect=self.delay_on_connect
            )
        
        if not self.client.connected:
            try:
                await self.client.connect()
                _LOGGER.debug(f"Connected to DTU at {self.host}:{self.port}")
                return True
            except Exception as e:
                _LOGGER.error(f"Failed to connect to DTU: {e}")
                return False
        return True       
 
    async def disconnect(self):
        """Close connection to the DTU."""
        if self.client and self.client.connected:
            self.client.close()
            _LOGGER.debug("Disconnected from DTU")


    def is_connected(self):
        """Check if client is connected."""
        return self.client and self.client.connected

    # def cache_set(self, key, value):
    #     self.cache[key] = {
    #         'value': value,
    #         'timestamp': time.time()
    #     }

    # def cache_get(self, key):
    #     if key in self.cache:
    #         cached_value = self.cache[key]
    #         if time.time() - cached_value['timestamp'] < 60:
    #             return cached_value['value']
    #         del self.cache[key]
    #     return None 

    async def read_address(self, address, count, data_type='uint16'):
        """Read data from modbus address with caching and error handling."""
        # cache_key = f"{address}--{count}--{data_type}"
        # _LOGGER.debug(f"Reading address {hex(address)} ({count} registers) as {data_type}")

        # # Check cache first
        # cached_value = self.cache_get(cache_key)
        # if cached_value is not None:
        #     _LOGGER.debug(f"Cache hit for {cache_key}: {cached_value}")
        #     return cached_value

        # Ensure connection
        if not await self.connect():
            raise Exception("Failed to connect to DTU")

        try:
            # Add small delay between requests to avoid overwhelming DTU
            await asyncio.sleep(0.1)
            
            result = await self.client.read_holding_registers(address, count=count)
            
            if result.isError():
                raise ModbusException(f"Error reading address {hex(address)}: {result}")
            
            v = self.parse_response(result, data_type)

            return v

            # regs = result.registers
            
            # # Parse based on data type
            # if data_type == 'uint16':
            #     v = regs[0]
            # elif data_type == 'int16':
            #     v = regs[0] if regs[0] < 0x8000 else regs[0] - 0x10000
            # elif data_type == 'uint32':
            #     if len(regs) < 2:
            #         raise ValueError("Not enough registers for uint32")
            #     v = (regs[0] << 16) | regs[1]
            # elif data_type == 'ascii':
            #     v_bytes = b''.join(reg.to_bytes(2, 'big') for reg in regs)
            #     v = v_bytes.decode('ascii').strip('\x00')
            # elif data_type == 'ascii_bcd':
            #     v_bytes = b''.join(reg.to_bytes(2, 'big') for reg in regs)
            #     digits = ''.join(f"{(b >> 4) & 0xF}{b & 0xF}" for b in v_bytes)
            #     v = digits.strip('0')
            # elif data_type == 'hex':
            #     v_bytes = b''.join(reg.to_bytes(2, 'big') for reg in regs)
            #     v = v_bytes.hex()
            # else:
            #     raise ValueError(f"Unsupported data type: {data_type}")
            
            # _LOGGER.debug(f"Read value {v} from address {hex(address)}")
            # self.cache_set(cache_key, v)
            # return v
            
        except Exception as e:
            _LOGGER.error(f"Failed to read address {hex(address)}: {e}")
            # Try to reconnect on error
            await self.disconnect()
            raise

    def parse_response(self, response, type):
        """Parse the response from the DTU based on the expected type."""
        if type == 'uint16':
            return response.registers[0]
        elif type == 'int16':
            return response.registers[0] if response.registers[0] < 0x8000 else response.registers[0] - 0x10000
        elif type == 'uint32':
            if len(response.registers) < 2:
                raise ValueError("Not enough registers for uint32")
            return (response.registers[0] << 16) | response.registers[1]
        elif type == 'ascii':
            v_bytes = b''.join(reg.to_bytes(2, 'big') for reg in response.registers)
            return v_bytes.decode('ascii').strip('\x00')
        elif type == 'ascii_bcd':
            v_bytes = b''.join(reg.to_bytes(2, 'big') for reg in response.registers)
            digits = ''.join(f"{(b >> 4) & 0xF}{b & 0xF}" for b in v_bytes)
            return digits.strip('0')
        elif type == 'hex':
            v_bytes = b''.join(reg.to_bytes(2, 'big') for reg in response.registers)
            return v_bytes.hex()
        else:
            raise ValueError(f"Unsupported data type: {type}")
        


    async def test_connection(self):
        """Test connection to DTU by reading serial number."""
        _LOGGER.debug("Testing connection to Hoymiles DTU...")
        try:
            await self.connect()
            await self.read_serial_number()
            return True
        except Exception as e:
            _LOGGER.error(f"Connection test failed: {e}")
            return False
    
    # async def reconnect(self):
    #     _LOGGER.debug("Reconnecting to Hoymiles DTU...")
    #     self.disconnect()
    #     if not self.connect():
    #         raise Exception("Failed to reconnect to Hoymiles DTU")
    #     _LOGGER.debug("Reconnected to Hoymiles DTU.")

    # def test_connection(self):
    #     _LOGGER.debug("Testing connection to Hoymiles DTU...")
    #     try:
    #         self.read_serial_number()
    #     except Exception as e:
    #         logging.error(f"Connection test failed: {e}")
    #         return False
    #     return True

    # def is_connected(self):
    #     return self.client.is_socket_open()

    async def read_serial_number(self):
        return await self.read_address(self.get_address(0), 3,'ascii_bcd')
    
    async def map_microinverters(self):
        for i in range(20):
            base_address = 0x1000 + (i) * 40

            sn = ''
            try: 
              sn = await self.read_address(base_address+1, 3, 'ascii_bcd')
            except Exception as e:
              break
            
            if sn == '':
              break

            mi = self.get_microinverter(sn)
            _LOGGER.debug(f"Microinverter {sn} at address {hex(base_address)}")
            if mi is None:
                self.add_microinverter(base_address, sn)
            else:
                mi.add_panel(base_address)
                continue
        _LOGGER.debug(f"Found {len(self.microinverters)} microinverters")
        return len(self.microinverters)

    def add_microinverter(self, address, serial_number):
       self.microinverters.append(Microinverter(self, address, serial_number))


    def get_address(self,offset):
        return self.base_address + offset
    
    def get_microinverter(self, sn):
        for mi in self.microinverters:
            if mi.serial_number == sn:
                return mi
        return None
    

    # def cache_set(self, key, value):
    #     self.cache[key] = {
    #         'value': value,
    #         'timestamp': time.time()
    #     }

    # def cache_get(self, key):
    #     if key in self.cache:
    #         cached_value = self.cache[key]
    #         if time.time() - cached_value['timestamp'] < 60:
    #             return cached_value['value']
    #         # Invalidate the cache if it's older than 60 seconds
    #         del self.cache[key]
    #     return None

    # def read_address(self, address, count, data_type='uint16'):
        
    #     # cacheKey = '--'.join([str(address), str(count), data_type])
    #     _LOGGER.debug(f"Reading address {hex(address)} ({count} registers) as {data_type} with cache key {cacheKey}")

    #     # # Check if the result is already cached
    #     # cached_value = self.cache_get(cacheKey)
    #     # if cached_value is not None:
    #     #     _LOGGER.debug(f"Cache hit for {cacheKey}: {cached_value}")
    #     #     return cached_value

    #     # Throttle the read requests to avoid overwhelming the device
    #     # now = time.time()

    #     self.callCount += 1
    #     if self.callCount % 5 == 0:
    #         self.disconnect()
    #         self.callCount = 0

    #     elapsed = now - self._last_read_time
    #     if elapsed < self._read_interval:
    #         time.sleep(self._read_interval - elapsed)

    #     if self.is_connected() == False:
    #         self.connect()

    #     self._last_read_time = time.time()

    #     result = self.client.read_holding_registers(address, count)
    #     if result.isError():
    #         raise Exception(f"Error reading address {address} ({hex(address)}): {result}")
        
    #     regs = result.registers

    #     if data_type == 'uint16':
    #         v = regs[0]  # Only use the first register
    #     elif data_type == 'int16':
    #         v = regs[0] if regs[0] < 0x8000 else regs[0] - 0x10000
    #     elif data_type == 'uint32':
    #         if len(regs) < 2:
    #             raise Exception("Not enough registers for uint32")
    #         v = (regs[0] << 16) | regs[1]
    #     elif data_type == 'ascii':
    #         v_bytes = b''.join(reg.to_bytes(2, 'big') for reg in regs)
    #         v = v_bytes.decode('ascii').strip('\x00')
    #     elif data_type == 'ascii_bcd':
    #         v_bytes = b''.join(reg.to_bytes(2, 'big') for reg in regs)
    #         digits = ''.join(f"{(b >> 4) & 0xF}{b & 0xF}" for b in v_bytes)
    #         v = digits.strip('0')
    #     elif data_type == 'hex':
    #         v_bytes = b''.join(reg.to_bytes(2, 'big') for reg in regs)
    #         v = v_bytes.hex()
    #     else:
    #         raise ValueError(f"Unsupported data type: {data_type}")
        
    #     _LOGGER.debug(f"Read value {v} from address {hex(address)} ({count} registers) as {data_type}")
    #     self.cache_set(cacheKey, v)
        
    #     return v
    
    # def close(self):
    #     self.client.close()

    def report(self):
        for mi in self.microinverters:
            mi.report()
            

    async def read_power_level(self):
        port = 0xC001
        if not self.is_connected():
          self.connect()

        result = self.client.read_coils(port, 8)  # Only read 8 bits
        bits = result.bits[:8]  # Ensure we're using exactly 8 bits

        logging.debug(f"Read {len(bits)} bits from {port}: {bits}")

        # Reconstruct integer from bits (LSB first)
        percentage = sum((1 << i) if bit else 0 for i, bit in enumerate(bits))

        return percentage

    async def write_power_level(self, port, percentage):
      """
      Write power level percentage to the specified register.
      
      Args:
          port: The register address to write to
          percentage: Power level percentage (0-255)
      """

        # Ensure the client is connected
      if not self.is_connected():
          self.connect()
      
      # Validate percentage range
      if not (5 <= percentage <= 100):
          raise ValueError("Percentage must be between 0 and 100")
      
      # Convert percentage to 8 bits (LSB first)
      bits = [(percentage >> i) & 1 for i in range(8)]
      logging.debug(f"Writing {percentage}% as bits:", bits)
      
      # Write the coils
      result = await self.client.write_coils(port, bits)
      
      if result.isError():
          logging.error(f"Error writing to register {port}: {result}")
          return False
      else:
          logging.debug(f"Successfully wrote {percentage}% to register {port}")
          return True
      
    async def get_total_power(self):
        total_power = 0
        for mi in self.microinverters:
            total_power += await mi.total_current_power()

        return total_power
    
    async def get_daily_power(self):
        total_power = 0
        for mi in self.microinverters:
            _LOGGER.debug(f"Getting daily production for microinverter {mi.serial_number}")
            for panel in mi.panels:
                total_power += await panel.get_today_production()
        return total_power

class Microinverter:
  def __init__(self, dtu, base_address, serial_number):
      self.dtu = dtu
      self.base_address = base_address
      self.addresses = [base_address]
      self.serial_number = serial_number
      self.panels = []
      self.add_panel(base_address)

      # self.panels.append(Panel(self.dtu.host, self.dtu.port, self.base_address, unit_id=2))

      # Address list:
      # - 0x1000 Data Type / / Default, 0x3C
      # - 0x1001 Serial Number / / 3 bytes
      # - 0x1004 ??Firmware Version / / 3 bytes
      # - 0x1007 Port Number / / 1 bytes
      # - 0x1008 PV Voltage / / 2 bytes / V
      # - 0x100A PV Current / / 2 bytes / A
      # - 0x100C Grid Voltage / / 2 bytes / V
      # - 0x100E Grid frequency / / 2 bytes / Hz
      # - 0x1010 PV Power / / 2 bytes / W
      # - 0x1012 Today Production / / 2 bytes / Wh
      # - 0x1014 Total Production / / 4 bytes / Wh
      # - 0x1018 Temperature / / 2 bytes / ℃
      # - 0x101A Operating Status / / 2 bytes
      # - 0x101C Alarm Code / / 2 bytes
      # - 0x101E Alarm Count / / 2 bytes
      # - 0x1020 Link Status / / 2 bytes
      # - 0x1021 Fixed / / 1 bytes
      # - 0x1022 Reserved / / 1 bytes
      # - 0x1023 Reserved / / 1 bytes
      # - 0x1024 Reserved / / 1 bytes
      # - 0x1025 Reserved / / 1 bytes
      # - 0x1026 Reserved / / 1 bytes
      # - 0x1027 Reserved / / 1 bytes
      # Next microinverter starts at 0x1028

      self.lookup = {
          'data_type':        (0x1000, 1, 'uint16'),
          'serial_number':    (0x1001, 3, 'ascii_bcd'),
          'unkown_1':         (0x1004, 3, 'ascii'),
          'port_number':      (0x1007, 1, 'uint16'),
          'pv_voltage':       (0x1008, 1, 'uint16'),   # V, often needs scaling (÷10)
          'pv_current':       (0x100A, 1, 'uint16'),   # A, often needs scaling (÷100)
          'grid_voltage':     (0x100C, 1, 'uint16'),   # V, often needs scaling (÷10)
          'grid_frequency':   (0x100E, 1, 'uint16'),   # Hz, often needs scaling (÷100)
          'pv_power':         (0x1010, 1, 'uint16'),   # W
          'today_production': (0x1012, 1, 'uint16'),   # Wh
          'total_production': (0x1014, 2, 'uint32'),   # Wh
          'temperature':      (0x1018, 1, 'int16'),    # °C, often needs scaling (÷10)
          'operating_status': (0x101A, 2, 'uint16'),
          'alarm_code':       (0x101C, 2, 'uint16'),
          'alarm_count':      (0x101E, 2, 'uint16'),
          'link_status':      (0x1020, 2, 'uint16'),
          'fixed':            (0x1021, 1, 'uint16'),
          'reserved_1':       (0x1022, 1, 'uint16'),
          'reserved_2':       (0x1023, 1, 'uint16'),
          'reserved_3':       (0x1024, 1, 'uint16'),
          'reserved_4':       (0x1025, 1, 'uint16'),
          'reserved_5':       (0x1026, 1, 'uint16'),
          'reserved_6':       (0x1027, 1, 'uint16'),
      }

  def add_panel(self, address): 
    for existing_panel in self.panels:
        if existing_panel.address == address:
            _LOGGER.debug(f"Panel at address {hex(address)} already exists, skipping creation.")
            return


    panel = Panel(self, address)
    self.panels.append(panel)

  async def read_value(self, name, index=0):
      address, count, data_type = self.lookup[name]

      address = (address - 0x1000) + self.base_address
      
      return await self.dtu.read_address(address, count, data_type)
      # return self.dtu.read_address(self.base_address+1, 3)
      # return self.dtu.read_address(self.base_address + address + index*0x0028, count)
      
  async def readTemperature(self):
      temperature = await self.read_value('temperature') / 10
      return temperature
  


  async def total_current_power(self):
      total_current = 0
      for panel in self.panels:
          total_current += await panel.get_pv_power()
      return total_current
  
  async def get_today_production(self):
        total_today = 0
        _LOGGER.debug(f"Getting today's production for microinverter {self.serial_number}")
        for panel in self.panels:

            total_today += await panel.get_today_production()
        return total_today

  def report(self):
      print(f"Microinverter {self.serial_number} at address {hex(self.base_address)}:")
      # print(f"  Serial Number: {self.serial_number}")
      # print(f"  Port Number: {self.read_value('port_number')}")
      print(f"  Temperature: {self.readTemperature()} °C")
    #   print(f"  Total Current Output: {self.total_current_power()} W")
      for panel in self.panels:
          panel.report()          

class Panel:
  def __init__(self, microinverter, address):
      self.microinverter = microinverter
      self.address = address
      self.lookup = {
          'serial_number':    (0x1001, 3, 'ascii_bcd'),
          'pv_voltage':       (0x1008, 1, 'uint16'),   # V, often needs scaling (÷10)
          'pv_current':       (0x100A, 1, 'uint16'),   # A, often needs scaling (÷100)
          'grid_voltage':     (0x100C, 1, 'uint16'),   # V, often needs scaling (÷10)
          'grid_frequency':   (0x100E, 1, 'uint16'),   # Hz, often needs scaling (÷100)
          'pv_power':         (0x1010, 1, 'uint16'),   # W
          'today_production': (0x1012, 1, 'uint16'),   # Wh
          'total_production': (0x1014, 2, 'uint32'),   # Wh
          'temperature':      (0x1018, 1, 'int16'),    # °C, often needs scaling (÷10)
          'operating_status': (0x101A, 1, 'uint16'),
          'alarm_code':       (0x101C, 1, 'uint16'),
          'alarm_count':      (0x101E, 1, 'uint16'),
          'link_status':      (0x1020, 1, 'uint16'),
      }
      
  async def get_pv_voltage(self):
      return await self.read_value('pv_voltage') / 10
  async def get_pv_current(self):
      return await self.read_value('pv_current') / 100
  async def get_grid_voltage(self):
      return await self.read_value('grid_voltage') / 10
  async def get_grid_frequency(self):
      return await self.read_value('grid_frequency') / 100
  async def get_pv_power(self):
      return await self.read_value('pv_power') / 10
  async def get_today_production(self):
      _LOGGER.debug(f"Getting today's production for panel at address {hex(self.address)}")
      val = await self.read_value('today_production')
      _LOGGER.debug(f"Today's production for panel at address {hex(self.address)}: {val} Wh")
      return val
  async def get_total_production(self):
      return await self.read_value('total_production')
  async def get_temperature(self):
      return await self.read_value('temperature') / 10
  async def get_operating_status(self):
      return await self.read_value('operating_status')
  async def get_alarm_code(self):
      return await self.read_value('alarm_code')
  async def get_alarm_count(self):
      return await self.read_value('alarm_count')
  async def get_link_status(self):
      return await self.read_value('link_status')

  async def read_value(self, name):
      address, count, data_type = self.lookup[name]
      address = (address - 0x1000) + self.address
      return await self.microinverter.dtu.read_address(address, count, data_type)
      
  def report(self):
      # print(f"  Panel {self.address}:")
      # print(f"    PV Voltage: {self.get_pv_voltage()} V")
      # print(f"    PV Current: {self.get_pv_current()} A")
      # print(f"    Grid Voltage: {self.get_grid_voltage()} V")
      # print(f"    Grid Frequency: {self.get_grid_frequency()} Hz")
      print(f"    PV Power: {self.get_pv_power()} W")
      # print(f"    Today Production: {self.get_today_production()} Wh")
      # print(f"    Total Production: {self.get_total_production()} Wh")
      # print(f"    Temperature: {self.get_temperature()} °C")
      # print(f"    Operating Status: {self.get_operating_status()}")
      # print(f"    Alarm Code: {self.get_alarm_code()}")
      # print(f"    Alarm Count: {self.get_alarm_count()}")
      # print(f"    Link Status: {self.get_link_status()}")
