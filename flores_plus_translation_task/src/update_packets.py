import json
import logging
import os.path
from datetime import datetime
from sheets_create import create_translation_spreadsheet
from sheets_create import create_revision_spreadsheet
from sheets_create import create_correction_sheet
from sheets_create import create_revision_sheet
from sheets_create import create_vocab_spreadsheet
from sheets_create import create_report_spreadsheet
from sheets_create import update_report_spreadsheet
from constants import Stage, DATETIME_FORMAT, LOGGER_FORMAT, R
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
                },
                "inactive_translators": {},
                "spent_additional_revisions": 0,
                "translation_complete": False
            } for lang in config['langs'].keys()
        }
    else:
        with open("../data/state.json") as f:
            state = json.loads(f.read())

    # update state file based on config
    for lang in config['langs']:
        if state.get(lang) is None:
            state[lang] = {
                "translators": {translator: [] for translator in config['langs'][lang]['translators']},
                "revisors": {config['langs'][lang]['revisor']: []},
                "packets": {str(i): None for i in range(len(DATASET))},
                "inactive_translators": {},
                "spent_additional_revisions": 0,
                "translation_complete": False
            }
        for translator in config['langs'][lang]['translators']:
            if state[lang]['translators'].get(translator) is None:
                state[lang]['translators'][translator]: []

        if config['langs'][lang]['revisor'] not in state[lang]['revisors'].keys():
            state[lang]['revisors'][config['langs'][lang]['revisor']]: []

    # Authenticate and get credentials object
    creds = authenticate()

    # Check if each language has its own folder and create them if not
    for lang in state.keys():
        if not get_lang_folder(creds, lang):
            logger.warning(f"No folder associated to language '{lang}'. Creating.")
            create_lang_folder(creds, lang)

    # Check vocabulary
    for lang in [lang for lang in state.keys() if state[lang]['translation_complete'] is False]:

        # Check if vocabulary spreadheet is associated with language and create it if not.
        if state[lang].get('vocab_id') is None:
            logger.warning(f"No vocabulary spreadsheet associated to language '{lang}'. Creating.")
            permission_emails = list(state[lang]['translators'].keys()) + list(state[lang]['revisors'].keys())
            state[lang]['vocab_id'] = create_vocab_spreadsheet(creds, lang, permission_emails)

        # Update local vocab file with contents from spreadsheet
        logger.info(f"Checking vocabulary spreadsheet for updates for lang '{lang}'.")

        new_vocab = get_vocab_from_sheet(creds, state[lang]['vocab_id'])
        with open(f"../data/{lang}/vocab.json") as f:
            vocab = json.loads(f.read())

        for key in vocab.keys():
            if vocab[key]['def'] != new_vocab[key]['def'] or vocab[key]['notes'] != new_vocab[key]['notes']:
                vocab.update(new_vocab)
                logger.info(f"Updating vocabulary file for lang '{lang}'.")
                with open(f"../data/{lang}/vocab.json", "w") as f:
                    f.write(json.dumps(vocab, indent=2, ensure_ascii=False))
                logger.info(f"Updating current packets with new vocabulary for language '{lang}'.")
                update_sheet_vocabulary(creds, state, lang)
                break

    if config['start_translation'] is False:
        with open("../data/state.json", "w") as g:
            g.write(json.dumps(state, indent=2))
        logger.info("Translation update task not ready yet. Modify config file to launch.")
        logger.info(f"Update complete.")
        exit()

    # Check if there's at least one packet in state and create one if not
    for lang in [lang for lang in state.keys() if state[lang]['translation_complete'] is False]:
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

    # Check if report spreadsheet exists and create one if  not
    for lang in state.keys():
        if state[lang].get('report') is None:
            logger.info(f"Creating report spreadsheet for lang '{lang}.'")
            state[lang]['report'] = create_report_spreadsheet(creds, state, lang)

    # Iterate over languages in state file
    langs = [lang for lang in state.keys() if state[lang]['translation_complete'] is False]
    for lang in langs:

        # Get translation packets and first check if there are any left to translate
        packets = [(idx, packet) for idx, packet in state[lang]['packets'].items() if packet is not None]

        # Check if translators in config correspond to active translators and update if not
        inactive_translators = {
            translator: state[lang]['translators'][translator] for translator in state[lang]['translators'].keys() if translator not in config['langs'][lang]['translators']
        }
        state[lang]['inactive_translators'].update(inactive_translators)

        if inactive_translators:
            logger.warning(f"Found {len(inactive_translators)} inactive translator(s).")
            for t in inactive_translators:
                state[lang]['translators'].pop(t, None)
            removed_translators = remove_permissions(creds, state)
            logger.info(f"The following translators have been removed from the project: {removed_translators}")

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
                if not packet_idx:
                    logger.info(f"No unassigned packets lefts.")
                    break
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
        logger.info(f"Running update on language: {lang}")
        for idx, packet in packets:
            if packet['stage'] == Stage.FIRST_TRANSLATION.name:

                if is_ready_packet(packet['tra_id'], creds):

                    packet['stage'] = Stage.FIRST_REVISION
                    packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                    logger.info(f"Packet '{packet['title']}': First translation complete by user '{packet['translator']}'. Submitting for revision.")
                    message = f"""Este es un mensaje automatizado notificándote que el paquete de traducción '{packet['title']}' ha sido enviado a revisión. A partir de ahora, seguirás teniendo acceso a este pero ya no podrás editarlo hasta nuevo aviso."""
                    subject = f"FLORES+ Mayas - Notificación automática: Paquete de traducción del idioma '{lang}'"
                    send_email_notification(packet['translator'], message, subject)

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

                    message = f"""Este es un mensaje automatizado notificándote que el paquete de traducción '{packet['title']}' ha sido enviado a segunda revisión. A partir de ahora, seguirás teniendo acceso a este pero ya no podrás editarlo."""
                    subject = f"FLORES+ Mayas - Notificación automática: Paquete de traducción del idioma '{lang}'"
                    send_email_notification(packet['translator'], message, subject)

                    message = f"""Este es un mensaje automatizado notificándote que la segunda traducción del paquete de traducción '{packet['title']}' ha concluido. A partir de ahora, tienes acceso a la segunda hoja de revisión para revisar dicha traducción y, de ser necesario, corregirla y proveer una traducción final.

https://docs.google.com/spreadsheets/d/{packet['rev_id']}"""
                    subject = f"FLORES+ Mayas - Notificación automática: Paquete de traducción del idioma '{lang}'"
                    send_email_notification(packet['revisor'], message, subject)

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
                        state[lang]['translators'][packet['translator']] += tra_sents
                        state[lang]['revisors'][packet['revisor']] += rev_sents

                        # Remove all protections from packet sheets and replace
                        # with single master lock
                        protect_packet_sheets([packet['rev_id'], packet['tra_id']], creds)


                        logger.info(
                            f"Packet '{packet['title']}': First revision complete by user '{packet['revisor']}'. No errors found. Translation complete."
                        )
                        logger.info(f"""Checking to see next available packet for user '{packet["translator"]}.""")

                        message = f"""Este es un mensaje automatizado notificándote que la traducción y la revisión del paquete de traducción '{packet['title']}' han sido aceptadas y este ha sido ingresado al reporte final. A partir de ahora, seguirás teniendo acceso al paquete pero ya no podrás editarlo."""
                        subject = f"FLORES+ Mayas - Notificación automática: Paquete de traducción del idioma '{lang}'"
                        send_email_notification([packet['translator'], packet['revisor']], message, subject)

                        next_packet_idx = [int(idx) for idx in state[lang]['packets'].keys() if state[lang]['packets'][idx] is None] 

                        if not next_packet_idx:
                            logger.info(f"Langage '{lang}' has no unassigned packets left to translate.")
                            open_packets = [p for p in state[lang]['packets'] if state[lang]['packets'][p]['stage'] != "TRANSLATION_COMPLETE"]
                            if not open_packets:
                                logger.info(f"All packets of language '{lang}' have been translated.")
                                state[lang]['translation_complete'] = True
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

                    packet['stage'] = Stage.SECOND_TRANSLATION
                    packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                    state[lang]['packets'][idx] = create_correction_sheet(creds, lang, packet['title'], packet)
                    logger.info(f"Packet '{packet['title']}': First revision complete by user '{packet['revisor']}'. Submitting for second translation.")

                    message = f"""Este es un mensaje automatizado notificándote que la revisión del paquete de traducción '{packet['title']}' ha concluido. A partir de ahora, tienes acceso a la segunda hoja de traducción para trabajar en las correcciones necesarias, siguiendo las anotaciones y sugerencias del revisor.

https://docs.google.com/spreadsheets/d/{packet['tra_id']}"""
                    subject = f"FLORES+ Mayas - Notificación automática: Paquete de traducción del idioma '{lang}'"
                    send_email_notification(packet['translator'], message, subject)

            elif packet['stage'] == Stage.SECOND_REVISION.name:
                if is_ready_packet(packet['rev_id'], creds):
                    packet['stage'] = Stage.TRANSLATION_COMPLETE
                    packet['last_stage_update'] = datetime.now().strftime(DATETIME_FORMAT)
                    state[lang]['packets'][idx] = packet
                    tra_sents, rev_sents = get_translation_ids(creds, packet['rev_id'])
                    state[lang]['translators'][packet['translator']] += tra_sents
                    state[lang]['revisors'][packet['revisor']] += rev_sents

                    # Remove all protections from packet sheets and replace
                    # with single master lock
                    protect_packet_sheets([packet['rev_id'], packet['tra_id']], creds)


                    logger.info(f"Packet '{packet['title']}': Second revision complete by user '{packet['revisor']}'. Translation complete.")
                    message = f"""Este es un mensaje automatizado notificándote que la traducción y la revisión del paquete de traducción '{packet['title']}' han sido aceptadas y este ha sido ingresado al reporte final. A partir de ahora, seguirás teniendo acceso al paquete pero ya no podrás editarlo."""
                    subject = f"FLORES+ Mayas - Notificación automática: Paquete de traducción del idioma '{lang}'"
                    send_email_notification([packet['translator'], packet['revisor']], message, subject)

                    logger.info(f"""Checking to see next available packet for user '{packet["translator"]}""")

                    next_packet_idx = [int(idx) for idx in state[lang]['packets'].keys() if state[lang]['packets'][idx] is None]

                    if not next_packet_idx:
                        logger.info(f"Langage '{lang}' has no unassigned packets left.")
                        open_packets = [p for p in state[lang]['packets'] if state[lang]['packets'][p]['stage'] != "TRANSLATION_COMPLETE"]
                        if not open_packets:
                            logger.info(f"All packets of language '{lang}' have been translated.")
                            state[lang]['translation_complete'] = True
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

        logger.info(f"Updating report on language '{lang}'.")
        update_report_spreadsheet(creds, state, lang)
        logger.info(f"Update on language '{lang}' complete.")
    logger.info(f"Saving state to file.")
    with open("../data/state.json", "w") as g:
        g.write(json.dumps(state, indent=2))
    logger.info(f"Update complete.")
