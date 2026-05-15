from ftplib import FTP, all_errors
import os
from pathlib import Path


class SELFTP:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def upload_file(self, local_file_path, remote_file_path):

        ftp = None

        try:
            # Check if the local file exists
            if not os.path.isfile(local_file_path):
                raise FileNotFoundError(f"Local file '{local_file_path}' does not exist.")
            
            print(f"Connecting to FTP server...{self.host}")
            ftp = FTP(self.host, timeout=10)

            print(f"Authenticating with FTP server...{self.user}")
            ftp.login(self.user, self.password)
            print("Conected and authenticated successfully.")

            # Obtain the file name from the local file path and construct the remote file path
            file_name = os.path.basename(local_file_path)
            remote_file_path = os.path.join(remote_file_path, file_name).replace("\\", "/")

            # Upload
            print(f"Uploading file '{local_file_path}' to '{remote_file_path}'...")
            with open(local_file_path, 'rb') as local_file_obj:
                ftp.storbinary(f'STOR {remote_file_path}', local_file_obj)

            print(f"File uploaded successfully. Saved in: {remote_file_path}")
            return True

        except all_errors as e:
            print(f"FTP error: {e}")
            return False
        
        finally:
            if ftp:
                try:
                    ftp.quit()
                    print("FTP connection closed.")
                except:
                    ftp.close()
    

    def download_file(self, remote_file_path, local_file_path):
        ftp = None

        try:
            print(f"Connecting to FTP server...{self.host}")
            ftp = FTP(self.host, timeout=10)

            print(f"Authenticating with FTP server...{self.user}")
            ftp.login(self.user, self.password)
            print("Conected and authenticated successfully.")
            
            file_name = os.path.basename(remote_file_path)
            local_file_path_download = os.path.join(local_file_path, file_name)

            # Download
            print(f"Downloading file '{remote_file_path}' to '{local_file_path}'...")
            with open(local_file_path_download, 'wb') as local_file_obj:
                ftp.retrbinary(f'RETR {remote_file_path}', local_file_obj.write)

            print(f"File downloaded successfully. Saved in: {local_file_path_download}")
            return True

        except all_errors as e:
            print(f"FTP error: {e}")
            return False
        
        finally:
            if ftp:
                try:
                    ftp.quit()
                    print("FTP connection closed.")
                except:
                    ftp.close()
                    
