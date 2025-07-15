import json
import logging
from datetime import datetime
from sheets_create import create_revision_spreadsheet
from sheets_create import create_correction_sheet
from sheets_create import create_revision_sheet
from constants import Stage, DATETIME_FORMAT, LOGGER_FORMAT
from util import authenticate, is_ready_packet, is_complete_translation
from icecream import ic

logger = logging.getLogger('updat_packets')
logging.getLogger('updat_packets').setLevel(logging.INFO)
handler = logging.FileHandler(filename='update.log')
handler.setFormatter(logging.Formatter(fmt=LOGGER_FORMAT))
logging.getLogger('updat_packets').addHandler(handler)

if __name__ == "__main__":

    creds = authenticate()
    try:
        with open("../data/packets.json") as f:
            packets = json.loads(f.read())
    except Exception:
        print("No valid packets file found.")
        exit(1)

    for lang in packets.keys():
        logger.info(f"Running update on language: {lang}")
        for packet in [p for p in packets[lang] if p['stage'] != Stage.TRANSLATION_COMPLETE.name]:
            if packet['stage'] == Stage.FIRST_TRANSLATION.name:

                if is_ready_packet(packet['tra_id'], creds):

                    packet['stage'] = Stage.FIRST_REVISION
                    packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                    logger.info(f"Packet '{packet['title']}': First translation complete by user '{packet['translator']}'. Submitting for revision.")
                    packets = create_revision_spreadsheet(creds, lang, packet['title'], packets)

            elif packet['stage'] == Stage.SECOND_TRANSLATION.name:
                if is_ready_packet(packet['tra_id'], creds):

                    packet['stage'] = Stage.SECOND_REVISION
                    packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                    logger.info(f"Packet '{packet['title']}': Second translation complete by user '{packet['translator']}'. Submitting for second revision.")
                    packets = create_revision_sheet(creds, lang, packet['title'], packets)
            elif packet['stage'] == Stage.FIRST_REVISION.name:
                if is_ready_packet(packet['rev_id'], creds):
                    if is_complete_translation(packet['rev_id'], creds):

                        packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                        packet['stage'] = Stage.TRANSLATION_COMPLETE

                        logger.info(
                            f"Packet '{packet['title']}': First revision complete by user '{packet['revisor']}'. No errors found. Translation complete."
                        )
                        # logger.info(f'Creating next package')
                        continue

                    packet['stage'] = Stage.SECOND_TRANSLATION
                    packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                    logger.info(f"Packet '{packet['title']}': First revision complete by user '{packet['revisor']}'. Submitting for second translation")
                    packets = create_correction_sheet(creds, lang, packet['title'], packets)

            elif packet['stage'] == Stage.SECOND_REVISION.name:
                logger.info(f"Packet '{packet['title']}': Second revision complete by user '{packet['revisor']}'. Translation complete.")
                packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                packet['stage'] = Stage.TRANSLATION_COMPLETE
                # TODO add step to go to next package
                # TODO lock spreadsheet once it is finished
                pass

        logger.info(f"Update on language '{lang}' complete.")

    with open("../data/packets.json", "w") as f:
        f.write(json.dumps(packets, indent=2))
    logger.info(f"Update complete.")
