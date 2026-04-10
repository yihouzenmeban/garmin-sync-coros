import logging
import os
from enum import Enum, auto
from functools import wraps

import requests

import garth

try:
    from config import GARTH_TOKEN_FILE
    from garmin.generate_garth_token_browser import generate_token_via_browser
    from garmin.garth_auth import (
        apply_browser_user_agent,
        configure_domain,
        remove_garth_user_agent,
    )
    from garmin.garth_token_store import (
        GarthTokenStoreError,
        has_encrypted_token,
        read_encrypted_token,
        write_encrypted_token,
    )
except ModuleNotFoundError:
    from scripts.config import GARTH_TOKEN_FILE
    from scripts.garmin.generate_garth_token_browser import generate_token_via_browser
    from scripts.garmin.garth_auth import (
        apply_browser_user_agent,
        configure_domain,
        remove_garth_user_agent,
    )
    from scripts.garmin.garth_token_store import (
        GarthTokenStoreError,
        has_encrypted_token,
        read_encrypted_token,
        write_encrypted_token,
    )

from .garmin_url_dict import GARMIN_URL_DICT

logger = logging.getLogger(__name__)


class GarminClient:
  def __init__(
      self,
      email,
      password,
      auth_domain,
      newest_num=0,
      token_salt=None,
      token_path=GARTH_TOKEN_FILE,
  ):
        self.auth_domain = auth_domain
        self.email = email
        self.password = password
        self.garthClient = garth
        self.newestNum = int(newest_num)
        self.token_salt = token_salt
        self.token_path = token_path
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "origin": GARMIN_URL_DICT.get("SSO_URL_ORIGIN"),
            "nk": "NT"
        }

  def _configure_domain(self):
      configure_domain(self.garthClient, self.auth_domain)

  def _remove_garth_user_agent(self):
      remove_garth_user_agent(self.garthClient)

  def _apply_browser_user_agent(self):
      apply_browser_user_agent(self.garthClient)

  def _persist_garth_token(self):
      if not self.token_salt:
          logger.warning(
              "GARMIN_TOKEN_SALT is not configured, skip GARTH_TOKEN persistence."
          )
          return
      garth_token = self.garthClient.client.dumps()
      write_encrypted_token(self.token_path, self.token_salt, garth_token)

  def _restore_session_from_token(self):
      if not self.token_salt:
          return False
      if not has_encrypted_token(self.token_path):
          return False

      garth_token = read_encrypted_token(self.token_path, self.token_salt)
      self.garthClient.client.loads(garth_token)
      # Touch a protected resource to confirm the restored token is still usable.
      self.garthClient.client.username
      self._remove_garth_user_agent()
      self._persist_garth_token()
      return True

  def _login_with_password(self):
      if not self.email or not self.password:
          raise GarminNoLoginException(
              "GARMIN_EMAIL and GARMIN_PASSWORD are required when GARTH_TOKEN cannot be restored."
          )
      self._configure_domain()
      self._apply_browser_user_agent()
      self.garthClient.login(self.email, self.password)
      self._remove_garth_user_agent()
      self._persist_garth_token()

  def _should_use_browser_login(self):
      return str(os.environ.get("GARMIN_LOGIN_MODE", "")).strip().lower() == "browser"

  def _login_with_browser(self):
      if not self.token_salt:
          raise GarminNoLoginException(
              "GARMIN_TOKEN_SALT is required when GARMIN_LOGIN_MODE=browser."
          )
      generate_token_via_browser(
          env={
              "GARMIN_AUTH_DOMAIN": self.auth_domain,
              "GARMIN_EMAIL": self.email,
              "GARMIN_PASSWORD": self.password,
              "GARMIN_TOKEN_SALT": self.token_salt,
          },
          timeout_seconds=int(os.environ.get("GARMIN_BROWSER_TIMEOUT_SECONDS", "300")),
      )
      if not self._restore_session_from_token():
          raise GarminNoLoginException(
              "GARTH_TOKEN browser refresh completed, but session restore still failed."
          )

  def ensure_login(self):
      try:
          self.garthClient.client.username
          self._remove_garth_user_agent()
          return
      except Exception:
          logger.warning("Garmin is not logged in or the GARTH_TOKEN has expired.")

      try:
          if self._restore_session_from_token():
              return
      except GarthTokenStoreError as err:
          logger.warning("Failed to restore GARTH_TOKEN: %s", err)
      except Exception as err:
          logger.warning("GARTH_TOKEN validation failed: %s", err)

      if self._should_use_browser_login():
          self._login_with_browser()
          return

      self._login_with_password()

  ## 登录装饰器
  def login(func):
    @wraps(func)
    def ware(self, *args, **kwargs):
      self.ensure_login()
      return func(self, *args, **kwargs)
    return ware
  
  @login 
  def download(self, path, **kwargs):
     return self.garthClient.download(path, **kwargs)
  
  @login 
  def connectapi(self, path, **kwargs):
      return self.garthClient.connectapi(path, **kwargs)
     

  ## 获取运动
  def getActivities(self, start:int, limit:int):
     
     params = {"start": str(start), "limit": str(limit)}
     activities =  self.connectapi(path=GARMIN_URL_DICT["garmin_connect_activities"], params=params)
     return activities;

  # ## 获取所有运动
  # def getAllActivities(self): 
  #   all_activities = []
  #   start = 0
  #   limit=100
  #   if 0 < self.newestNum < 100:
  #     limit = self.newestNum
      
  #   while(True):
  #     activities = self.getActivities(start=start, limit=limit)
  #     if len(activities) > 0:
  #       all_activities.extend(activities)
        
  #       if 0 < self.newestNum < 100 or start > self.newestNum:
  #          return all_activities
  #     else:
  #        return all_activities
  #     start += limit

  ## 获取所有运动
  def getAllActivities(self): 
    all_activities = []
    start = 0
    while(True):
      activities = self.getActivities(start=start, limit=100)
      if len(activities) > 0:
         all_activities.extend(activities)
      else:
         return all_activities
      start += 100

  ## 下载原始格式的运动
  def downloadFitActivity(self, activity):
    download_fit_activity_url_prefix = GARMIN_URL_DICT["garmin_connect_fit_download"]
    download_fit_activity_url = f"{download_fit_activity_url_prefix}/{activity}"
    response = self.download(download_fit_activity_url)
    return response

  @login  
  def upload_activity(self, activity_path: str):
    """Upload activity in fit format from file."""
    # This code is borrowed from python-garminconnect-enhanced ;-)
    file_base_name = os.path.basename(activity_path)
    file_extension = file_base_name.split(".")[-1]
    allowed_file_extension = (
        file_extension.upper() in ActivityUploadFormat.__members__
    )

    if allowed_file_extension:
       status = "UPLOAD_EXCEPTION"
       try:
        with open(activity_path, 'rb') as file:
          file_data = file.read()
          fields = {
              'file': (file_base_name, file_data, 'text/plain')
          }

          url_path = GARMIN_URL_DICT["garmin_connect_upload"]
          upload_url = f"https://connectapi.{self.garthClient.client.domain}{url_path}"
          self.headers['Authorization'] = str(self.garthClient.client.oauth2_token)
          response = requests.post(upload_url, headers=self.headers, files=fields)
          res_code = response.status_code
          result = response.json()
          uploadId =  result.get("detailedImportResult").get('uploadId')
          isDuplicateUpload = uploadId == None or uploadId == ''
          if res_code == 202 and not isDuplicateUpload:
              status = "SUCCESS"
          elif res_code == 409 and result.get("detailedImportResult").get("failures")[0].get('messages')[0].get('content') == "Duplicate Activity.":
              status = "DUPLICATE_ACTIVITY" 
       except Exception as e:
            print(e)
       return status
    else:
        return "UPLOAD_EXCEPTION"
  

class ActivityUploadFormat(Enum):
  FIT = auto()
  GPX = auto()
  TCX = auto()

class GarminNoLoginException(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, status):
        """Initialize."""
        super(GarminNoLoginException, self).__init__(status)
        self.status = status
