"""Module to initializes global setting for the plugin"""

from __future__ import absolute_import, division, unicode_literals
import os
import sys
import hashlib
from urllib.parse import urlencode, urlsplit
import dataclasses
import xbmcaddon
import xbmcvfs, xbmcgui
from .loggers import Logger
home = xbmcgui.Window(10000)


@dataclasses.dataclass
class PortalConfig:
	"""Portal config"""
	mac_cookie: str = None
	portal_url: str = None
	device_id: str = None
	device_id_2: str = None
	signature: str = None
	serial_number: str = None
	portal_base_url: str = None
	server_address: str = None
	alternative_context_path: bool = False


@dataclasses.dataclass
class AddOnConfig:
	"""Addon config"""
	url: str = None
	addon_id: str = None
	name: str = None
	handle: str = None
	addon_data_path: str = None
	max_page_limit: int = 30
	max_retries: int = 3
	token_path: str = None


class GlobalVariables:
	"""Class initializes global settings used by the plugin"""

	def __init__(self):
		"""Init class"""
		self.__addon = xbmcaddon.Addon()
		self.__is_addd_on_first_run = None
		self.addon_config = AddOnConfig()
		self.portal_config = PortalConfig()

	def init_globals(self):
		"""Init global settings"""
		self.__is_addd_on_first_run = self.__is_addd_on_first_run is None
		self.addon_config.url = sys.argv[0]
		if self.__is_addd_on_first_run or home.getProperty("change"):
			Logger.debug("First run, loading global variables")
			home.clearProperty("change")
			self.addon_config.addon_id = self.__addon.getAddonInfo('id')
			self.addon_config.name = self.__addon.getAddonInfo('name')
			self.addon_config.addon_data_path = self.__addon.getAddonInfo('path')
			token_path = xbmcvfs.translatePath(self.__addon.getAddonInfo('profile'))
			if not xbmcvfs.exists(token_path):
				xbmcvfs.mkdirs(token_path)
			self.addon_config.token_path = token_path
			self.addon_config.handle = int(sys.argv[1])
			self.portal_config.mac_cookie = 'mac=' + self.__addon.getSetting('mac_address')
			self.portal_config.device_id = self.generate_device_id()
			self.portal_config.device_id_2 = self.portal_config.device_id
			self.portal_config.signature = self.__addon.getSetting('signature')
			self.portal_config.serial_number = self.generate_serial()
			self.portal_config.alternative_context_path = self.__addon.getSetting('alternative_context_path') == 'true'
			self.__set_portal_addresses()

	def get_handle(self):
		"""Get addon handle"""
		return self.addon_config.handle

	def get_custom_thumb_path(self, thumb_file_name):
		"""Get thumb file path"""
		return os.path.join(self.addon_config.addon_data_path, 'resources', 'media', thumb_file_name)

	def get_plugin_url(self, params):
		"""Get plugin url"""
		return '{}?{}'.format(self.addon_config.url, urlencode(params))

	def __get_portal_base_url(self):
		"""Get portal base url"""
		split_url = urlsplit(self.portal_config.server_address)
		return split_url.scheme + '://' + split_url.netloc

	def __set_portal_addresses(self):
		"""Set portal urls"""
		self.portal_config.server_address = self.__addon.getSetting('server_address')
		self.portal_config.portal_base_url = self.__get_portal_base_url()
		self.portal_config.portal_url = self.get_portal_url()

	def get_portal_url(self):
		"""Get portal url"""
		context_path = '/portal.php' if self.portal_config.alternative_context_path else '/server/load.php'
		portal_url = self.portal_config.portal_base_url + '/stalker_portal' + context_path
		if self.portal_config.server_address.endswith('/c/'):
			portal_url = self.portal_config.server_address.replace('/c/', '') + context_path
		elif self.portal_config.server_address.endswith('/c'):
			portal_url = self.portal_config.server_address.replace('/c', '') + context_path
		return portal_url

	def generate_serial(self):
		"""
		Generate a 13-character serial based on the MD5 hash of the MAC address.

		Parameters:
			mac (str): MAC address.

		Returns:
			str: Generated serial.
		"""
		# Create an MD5 hash of the MAC address
		mac = self.__addon.getSetting('mac_address')
		md5_hash = hashlib.md5(mac.encode()).hexdigest()
		
		# Use the first 13 characters of the hash as the serial
		serial = md5_hash[:13].upper()  # Convert to uppercase for consistency
		
		#logger.debug(f"Generated serial from MAC {mac}: {serial}")
		return serial

	def generate_device_id(self):
		"""
		Generate a 64-character hexadecimal device ID based on the MAC address.

		Returns:
			str: Generated device ID.
		"""
		#mac_exact = self.mac.strip()
		mac_exact = self.__addon.getSetting('mac_address')
		sha256_hash = hashlib.sha256(mac_exact.encode()).hexdigest().upper()
		#logger.debug(f"Generated device_id using MAC {mac_exact}: {sha256_hash}")
		return sha256_hash


G = GlobalVariables()
