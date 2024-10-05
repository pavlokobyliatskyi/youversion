# YouVersion

This script allows you to download the audio Bible from the [YouVersion](https://www.bible.com/) website.

### Setup

```bash
git clone https://github.com/pavlokobyliatskyi/youversion
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
   ```

### Usage

Visit [YouVersion](https://www.bible.com/) and navigate to the Bible translation you need. In the URL, you will find an ID. For example, in the URL `https://www.bible.com/bible/111/GEN.1.NIV`, **111** is the **ID**. To check if the scripture has an audio version, modify the URL by replacing **/bible/** with **/audio-bible/** or look for the sound icon on the page, which indicates the availability of the audio version. Perhaps the audio is only found in the New Testament or not at all.

```bash
python main.py 111
```

The downloaded files will be saved to the **downloads** directory. If the translation has several voiceovers, they will be saved separately.