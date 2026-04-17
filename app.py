import os
import sys
import tempfile
from typing import Optional

import streamlit as st
import yt_dlp

FORMAT_MAP = {
    "Best available": "best",
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "Audio only": "bestaudio/best",
}


def get_streamlit_context() -> Optional[object]:
    try:
        from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

        return get_script_run_ctx()
    except Exception:
        return None


def is_streamlit_mode() -> bool:
    if get_streamlit_context() is not None:
        return True
    if os.environ.get("STREAMLIT_RUN") or os.environ.get("STREAMLIT_SERVER"):
        return True
    return "streamlit" in " ".join(sys.argv).lower()


def download_media(source_url: str, format_option: str) -> tuple[str, dict]:
    temp_dir = tempfile.mkdtemp(prefix="yt_dl_")
    ydl_opts = {
        "format": format_option,
        "outtmpl": os.path.join(temp_dir, "%(title).200s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(source_url, download=True)

    filename = ydl.prepare_filename(info)
    return filename, info


def main() -> None:
    st.set_page_config(page_title="Universal Downloader", page_icon="📥")

    st.title("📥 All-in-One Downloader")
    st.write("Duniya ke kisi bhi kone se Reels aur Shorts download karein.")

    url = st.text_input("Paste Link Here:", placeholder="https://...")
    quality = st.selectbox(
        "Select quality:",
        list(FORMAT_MAP.keys()),
    )

    if st.button("Download High Quality"):
        if not url:
            st.warning("Pehle link toh dalo!")
            return

        with st.spinner("Processing..."):
            try:
                file_path, info = download_media(url, FORMAT_MAP[quality])
                st.success("Download ready!")

                if info.get("ext") in {"mp4", "mkv", "webm", "mov"}:
                    st.video(file_path)
                elif info.get("ext") in {"mp3", "m4a", "wav", "aac"}:
                    st.audio(file_path)

                if os.path.exists(file_path):
                    with open(file_path, "rb") as file_obj:
                        st.download_button(
                            label="Download file",
                            data=file_obj,
                            file_name=os.path.basename(file_path),
                            mime="application/octet-stream",
                        )
                else:
                    st.error("Download failed: file not found.")
            except yt_dlp.utils.DownloadError:
                st.error("Link invalid hai ya video private hai. Ek aur baar check karein.")
            except Exception:
                st.error("Kuch galat ho gaya. Please thoda der baad dobara koshish karein.")


if is_streamlit_mode():
    main()
else:
    if __name__ == "__main__":
        print("Please run this app with Streamlit:")
        print("  streamlit run app.py")

