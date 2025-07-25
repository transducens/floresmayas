import json
import logging
import os.path
from datetime import datetime
from sheets_create import create_translation_spreadsheet
from sheets_create import create_revision_spreadsheet
from sheets_create import create_correction_sheet
from sheets_create import create_revision_sheet
from constants import Stage, DATETIME_FORMAT, LOGGER_FORMAT, DATASET, R
from util import *

logger = logging.getLogger('updat_packets')
logging.getLogger('updat_packets').setLevel(logging.INFO)
handler = logging.FileHandler(filename='update.log')
handler.setFormatter(logging.Formatter(fmt=LOGGER_FORMAT))
logging.getLogger('updat_packets').addHandler(handler)

if __name__ == "__main__":

    # get config
    try:
        with open("../data/config.json") as f:
            config = json.loads(f.read())
    except Exception:
        logger.error("No valid config file found.")
        exit(1)

    # Try to get state file
    if not os.path.exists("../data/state.json"):
        logger.warning("No state file found. Generating from config.")
        state = {
            lang: {
                "translators": {
                    translator: [] for translator in config['langs'][lang]['translators']
                },
                "revisors": {
                    config['langs'][lang]['revisor']: []
                },
                "packets": {
                    str(i): None for i in range(len(DATASET))
                }
            } for lang in config['langs'].keys()
        }
    else:
        with open("../data/state.json") as f:
            state = json.loads(f.read())

    # Authenticate and get credentials object
    creds = authenticate()

    # Check if there's at least one package in state and create one if not
    for lang in state.keys():
        packets = [p for _, p in state[lang]['packets'].items() if p is not None]
        if not packets:
            logger.warning(f"Language '{lang}' has no packages ready to work on.")
            translators = state[lang]['translators']
            if not translators:
                logger.warning(f"No translators available for language '{lang}.")
                continue
            for translator in translators:
                revisor = list(state[lang]['revisors'].keys())[0]
                packet_idx = min(int(idx) for idx in state[lang]['packets'].keys() if state[lang]['packets'][idx] is None)
                state[lang]['packets'][str(packet_idx)] = create_translation_spreadsheet(
                    creds=creds,
                    sents=DATASET[packet_idx],
                    lang_code=lang,
                    title=f"{lang}_{packet_idx}",
                    tra_email=translator,
                    rev_email=revisor,
                    packet_idx=packet_idx,
                )
                logger.info(f"""New packet '{lang}_{packet_idx}' created for language '{lang}' and assigned to translator '{translator}' and revisor '{revisor}'""")

    # Iterate over languages in state file
    for lang in state.keys():
        logger.info(f"Running update on language: {lang}")

        # Check if translators in config correspond to active translators and update if not
        inactive_translators = {
            translator: state[lang]['translators'][translator] for translator in state[lang]['translators'].keys() if translator not in config['langs'][lang]['translators']
        }

        if inactive_translators:
            logger.warning(f"Found {len(inactive_translators)} inactive translator(s).")
            state[lang]['inactive_translators'] = inactive_translators
            for t in inactive_translators:
                state[lang]['translators'].pop(t, None)

        new_translators = [t for t in config['langs'][lang]['translators'] if t not in state[lang]['translators']]
        for t in new_translators:
            logger.info(f"Found new translator '{t}'. Adding them to roster of language '{lang}'.")
            state[lang]['translators'][t] = []

        # Check if all translators of current language are assigned to a packet
        busy_translators = [
            packet['translator'] for _, packet in state[lang]['packets'].items() if packet is not None
            and packet['stage'] != Stage.TRANSLATION_COMPLETE.name
            and packet['translator'] not in state[lang]['inactive_translators']
        ]
        free_translators = [translator for translator in state[lang]['translators'].keys() if translator not in busy_translators]
        if free_translators:
            logger.info(f"Found {len(free_translators)} unassigned translator(s). Assigning them a packet to work on.")
            revisor = list(state[lang]['revisors'].keys())[0]
            for translator in free_translators:
                packet_idx = [int(idx) for idx in state[lang]['packets'].keys() if state[lang]['packets'][idx] is None]
                packet_idx = min(packet_idx)
                state[lang]['packets'][str(packet_idx)] = create_translation_spreadsheet(
                    creds=creds,
                    sents=DATASET[packet_idx],
                    lang_code=lang,
                    title=f"{lang}_{packet_idx}",
                    tra_email=translator,
                    rev_email=revisor,
                    packet_idx=packet_idx,
                )
                logger.info(f"""New packet '{lang}_{packet_idx}' created for language '{lang}' and assigned to translator '{translator}' and revisor '{revisor}'.""")

        # Iterate over packets checking status
        packets = [(idx, packet) for idx, packet in state[lang]['packets'].items() if packet is not None]
        for idx, packet in packets:
            if packet['stage'] == Stage.FIRST_TRANSLATION.name:

                if is_ready_packet(packet['tra_id'], creds):

                    packet['stage'] = Stage.FIRST_REVISION
                    packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                    logger.info(f"Packet '{packet['title']}': First translation complete by user '{packet['translator']}'. Submitting for revision.")
                    state[lang]['packets'][idx] = create_revision_spreadsheet(creds, lang, packet['title'], packet)

            elif packet['stage'] == Stage.SECOND_TRANSLATION.name:
                if is_ready_packet(packet['tra_id'], creds):
                    t = len([key for key in state[lang]['packets'].keys() if state[lang]['packets'][key] is not None])
                    c = get_c(
                        R=R,
                        k=state[lang]['spent_additional_revisions'],
                        n=len(state[lang]['packets']),
                        t=t
                    )

                    r_max = get_r_max(c=c, t=t)

                    packet['stage'] = Stage.SECOND_REVISION
                    packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                    logger.info(f"Packet '{packet['title']}': Second translation complete by user '{packet['translator']}'. Submitting for second revision.")
                    state[lang]['packets'][idx], k = create_revision_sheet(creds, lang, packet['title'], packet, r_max)
                    state[lang]['spent_additional_revisions'] += k

            elif packet['stage'] == Stage.FIRST_REVISION.name:
                if is_ready_packet(packet['rev_id'], creds):
                    if is_complete_translation(packet['rev_id'], creds):

                        # update state with stage, completed packet, and the sentences translated by
                        # both the translator and the revisor
                        packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                        packet['stage'] = Stage.TRANSLATION_COMPLETE
                        state[lang]['packets'][idx] = packet
                        tra_sents, rev_sents = get_translation_ids(creds, packet['rev_id'])
                        state[lang]['translators'][packet['translator']][idx] = tra_sents
                        state[lang]['revisors'][packet['revisor']][idx] = rev_sents

                        logger.info(
                            f"Packet '{packet['title']}': First revision complete by user '{packet['revisor']}'. No errors found. Translation complete."
                        )
                        logger.info(f"""Checking to see next available packet for user '{packet["translator"]}.""")

                        next_packet_idx = min(int(idx) for idx in state[lang]['packets'].keys() if state[lang]['packets'][idx] is None)

                        if not next_packet_idx:
                            logger.info(f"No new packets available for language '{lang}'")
                            continue

                        state[lang]['packets'][str(next_packet_idx)] = create_translation_spreadsheet(
                            creds=creds,
                            sents=DATASET[next_packet_idx],
                            lang_code=lang,
                            title=f"{lang}_{next_packet_idx}",
                            tra_email=packet['translator'],
                            rev_email=packet['revisor'],
                            packet_idx=next_packet_idx,
                        )
                        logger.info(f"""New packet '{lang}_{next_packet_idx}' created for language '{lang}' and assigned to translator '{packet['translator']}' and revisor '{packet['revisor']}'.""")
                        continue

                    packet['stage'] = Stage.SECOND_TRANSLATION
                    packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                    state[lang]['packets'][idx] = create_correction_sheet(creds, lang, packet['title'], packet)
                    logger.info(f"Packet '{packet['title']}': First revision complete by user '{packet['revisor']}'. Submitting for second translation.")

            elif packet['stage'] == Stage.SECOND_REVISION.name:
                if is_ready_packet(packet['rev_id'], creds):
                    packet['stage'] = Stage.TRANSLATION_COMPLETE
                    packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                    state[lang]['packets'][idx] = packet
                    tra_sents, rev_sents = get_translation_ids(creds, packet['rev_id'])
                    state[lang]['translators'][packet['translator']] += tra_sents
                    state[lang]['revisors'][packet['revisor']] += rev_sents

                    logger.info(f"Packet '{packet['title']}': Second revision complete by user '{packet['revisor']}'. Translation complete.")
                    logger.info(f"""Checking to see next available packet for user '{packet["translator"]}""")

                    next_packet_idx = [int(idx) for idx in state[lang]['packets'].keys() if state[lang]['packets'][idx] is None]
                    if not next_packet_idx:
                        logger.info(f"No new packets available for language '{lang}'")
                        continue

                    next_packet_idx = min(next_packet_idx)
                    state[lang]['packets'][str(next_packet_idx)] = create_translation_spreadsheet(
                        creds=creds,
                        sents=DATASET[next_packet_idx],
                        lang_code=lang,
                        title=f"{lang}_{next_packet_idx}",
                        tra_email=packet['translator'],
                        rev_email=packet['revisor'],
                        packet_idx=next_packet_idx,
                    )
                    logger.info(f"""New packet '{lang}_{next_packet_idx}' created for language '{lang}' and assigned to translator '{packet['translator']}' and revisor '{packet['revisor']}'.""")
                    continue

        logger.info(f"Update on language '{lang}' complete.")
    logger.info(f"Saving state to file.")
    with open("../data/state.json", "w") as g:
        g.write(json.dumps(state, indent=2))
    logger.info(f"Update complete.")
