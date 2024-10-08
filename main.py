import argparse
import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
from colorama import init, Fore

init(autoreset=True)


def clear_console():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


async def get_scripture(id: int):
    url = f"https://www.bible.com/api/bible/version/{id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
    except Exception:
        raise Exception(f'Failed to find the Bible with ID: "{id}".')


async def get_html_content(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
    except Exception:
        raise Exception(f'Failed to retrieve HTML content from "{url}".')


async def get_audio_chapter_info(
    scripture_id: str, chapter_usfm: str, abbreviation: str
):
    url = f"https://www.bible.com/audio-bible/{scripture_id}/{chapter_usfm}.{abbreviation}"
    html_content = await get_html_content(url)

    try:
        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            next_data = soup.find("script", id="__NEXT_DATA__")
            json_data = json.loads(next_data.string)
            audio_chapter_info = json_data["props"]["pageProps"]["chapterInfo"][
                "audioChapterInfo"
            ]
            return audio_chapter_info
    except Exception:
        raise Exception(f"Failed to retrieve audio info for chapter.")


async def download_file(url: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                with open(path, "wb") as file:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        file.write(chunk)

    except Exception:
        raise Exception(f"Failed to download file from {url}.")


async def calculate_progress(total_books: int, loaded_books: int):
    if total_books == 0:
        return 0.0

    progress = (loaded_books / total_books) * 100
    return progress


async def print_info_message(
    scripture_title: str, skip_old_testment: bool, progress: int
):
    clear_console()

    testament_parts = []

    if skip_old_testment:
        testament_parts.append("Old Testament")

    testament_parts.append("New Testament")

    testament_info = " + ".join(testament_parts)

    print(
        f"{Fore.BLUE}{scripture_title} ({testament_info}): {Fore.GREEN}{progress:.2f}%"
    )


async def main():
    try:
        parser = argparse.ArgumentParser(description="")
        parser.add_argument("id", type=int, help="The Scripture ID")
        args = parser.parse_args()

        scripture_id = args.id

        scripture = await get_scripture(scripture_id)
        scripture_title = scripture["title"]

        abbreviation = scripture["abbreviation"]
        books = scripture["books"]

        is_old_testament_audio = True

        loaded_books = 0

        for book in books:
            book_name = book["human"]
            chapters = book["chapters"]
            book_usfm = book["usfm"]

            if not is_old_testament_audio and not book_usfm == "MAT":
                continue

            for chapter in chapters:
                chapter_usfm = chapter["usfm"]
                chapter_number = chapter["human"]

                if not chapter_number.isdigit():
                    continue

                audio_chapter_info = await get_audio_chapter_info(
                    scripture_id, chapter_usfm, abbreviation
                )

                if not audio_chapter_info and book_usfm == "GEN":
                    is_old_testament_audio = False
                    break

                if not audio_chapter_info:
                    raise Exception(
                        f'The Bible with ID: "{scripture_id}" does not have an audio version.'
                    )

                for audio_chapter in audio_chapter_info:
                    mp3_url = (
                        f"https:{audio_chapter['download_urls']['format_mp3_32k']}"
                    )
                    chapter_title = audio_chapter["title"]
                    download_path = (
                        f"downloads/{chapter_title}/{book_name}/{chapter_number}.mp3"
                    )

                    await download_file(mp3_url, download_path)

                    progress = await calculate_progress(len(books), loaded_books)

                    await print_info_message(
                        scripture_title, is_old_testament_audio, progress
                    )

            loaded_books += 1
        await print_info_message(scripture_title, is_old_testament_audio, 100)
    except Exception as e:
        print(f"{Fore.RED}{e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
