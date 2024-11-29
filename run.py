import os
import shutil
from YoutubeUploader import YouTubeUploader, YoutubePrivacyStatus
from VideoMerger import VideoMerger
from googleapiclient.errors import ResumableUploadError

VIDEOS_TO_UPLOAD_DIR = "VideosToUpload"
UPLOADED_VIDEOS_DIR = "UploadedVideos"
MERGED_VIDEOS_DIR = "VideosToUpload/Merged"

def upload_videos(videos_to_upload_dir, uploaded_videos_dir):
    uploader = YouTubeUploader()
    ok = uploader.authenticate_youtube(client_secrets_file="client.json")

    if not ok:
        print("Error authenticating")
        return

    for video_file in os.listdir(videos_to_upload_dir):
        video_path = os.path.join(videos_to_upload_dir, video_file)
        if os.path.isfile(video_path):
            title, _ = os.path.splitext(video_file)
            print(f"Uploading {title}...")
            try:
                uploader.upload_video(
                    file_path=video_path,
                    title=title,
                    privacy_status=YoutubePrivacyStatus.UNLISTED.value
                )
            except ResumableUploadError as e:
                print(f"Error uploading {title}: {e}")
                break

            shutil.move(video_path, os.path.join(uploaded_videos_dir, video_file))

def merge_videos(videos_to_upload_dir, merged_videos_dir):
    merger = VideoMerger(input_dir=videos_to_upload_dir, output_dir=merged_videos_dir)
    merger.merge_videos()

def main():
    merger = VideoMerger(input_dir=VIDEOS_TO_UPLOAD_DIR, output_dir=MERGED_VIDEOS_DIR)
    merger.classify_videos()
    
    # merge_videos(VIDEOS_TO_UPLOAD_DIR, MERGED_VIDEOS_DIR)
    # upload_videos(VIDEOS_TO_UPLOAD_DIR, UPLOADED_VIDEOS_DIR)

if __name__ == "__main__":
    main()