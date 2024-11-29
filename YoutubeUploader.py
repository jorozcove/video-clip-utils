import os
from enum import Enum
import google_auth_oauthlib.flow
import googleapiclient.discovery

class YoutubePrivacyStatus(Enum):
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"

class YouTubeUploader:
    def __init__(self): 
        self.youtube = None

    def authenticate_youtube(self, client_secrets_file):
        try:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
            scopes = ["https://www.googleapis.com/auth/youtube.upload"]

            if os.path.exists("token.json"):
                os.remove("token.json")

            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file,
                scopes
            )
            credentials = flow.run_local_server()

            self.youtube = googleapiclient.discovery.build(
                "youtube",
                "v3",
                credentials=credentials
            )

            return True
        
        except Exception as e:
            print(f"Error: {e}")
            return False

    def upload_video(self, file_path, title, description="", privacy_status=YoutubePrivacyStatus.PRIVATE.value):
        if not self.youtube:
            raise Exception("You must authenticate first")

        request_body = {
            "snippet": {
                # "categoryId": "22",
                "title": title,
                "description": description,
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }

        request = self.youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=googleapiclient.http.MediaFileUpload(file_path, chunksize=-1, resumable=True)
        )

        response = None 

        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload {int(status.progress()*100)}%")

        print(f"Video uploaded on: https://www.youtube.com/watch?v={response['id']}")
